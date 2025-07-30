from __future__ import annotations

import re
import uuid

import relationalai as rai

from pandas import DataFrame
from typing import Any, Union, cast, Optional

from .. import Compiler
from relationalai import debugging
from relationalai.early_access.metamodel.util import ordered_set
from relationalai.early_access.metamodel import ir, executor as e, factory as f

class SnowflakeExecutor(e.Executor):
    """Executes SQL using the RAI client."""

    def __init__(
            self,
            database: str,
            schema: str,
            dry_run: bool = False,
            skip_denormalization: bool = False,
            config: rai.Config | None = None,
    ) -> None:
        super().__init__()
        self.database = database
        self.schema = schema
        self.dry_run = dry_run
        self._last_model = None
        self._last_model_sql = None
        self.config = config or rai.Config()
        self.compiler = Compiler(skip_denormalization)
        self.provider = cast(rai.clients.snowflake.Provider, rai.Provider(config=config))

    def execute(self, model: ir.Model, task:ir.Task, result_cols:Optional[list[str]]=None,
                export_to:Optional[str]=None, update:bool=False) -> Union[DataFrame, Any]:
        """ Execute the SQL query directly. """

        if self._last_model != model:
            with debugging.span("compile", metamodel=model) as model_span:
                model_sql = self.compiler.compile(model)
                model_span["compile_type"] = "model"
                model_span["sql"] = model_sql
                self._last_model = model
                self._last_model_sql = model_sql

        with debugging.span("compile", metamodel=task) as compile_span:
            # TODO: find the way how to compile task instead of building model with one root task
            query_model = f.model(ordered_set(), ordered_set(), ordered_set(), task)
            query_sql = self.compiler.compile(query_model)
            compile_span["compile_type"] = "query"
            compile_span["sql"] = query_sql

        if self.dry_run:
            return DataFrame()

        _replace_pattern = re.compile(r"[ /-]")

        def sanitize_name(value: str) -> str:
            return _replace_pattern.sub("_", value)

        database = sanitize_name(self.database)
        schema = sanitize_name(self.schema)
        unique_id = sanitize_name(str(uuid.uuid4()).lower())
        db_name = f"{database}_{unique_id}"
        db_query = f"CREATE OR REPLACE DATABASE {db_name};"
        schema_query = f"CREATE OR REPLACE SCHEMA {db_name}.{schema};"
        use_schema_query = f"USE SCHEMA {db_name}.{schema};"

        full_model_sql = f"{db_query}\n{schema_query}\n{use_schema_query}\n{self._last_model_sql}\n{query_sql}"

        try:
            result = self.provider.resources._session.connection.execute_string(full_model_sql) # type: ignore
            # Assuming that `task` is a single SQL query per model, and we have it always at the end of the generated SQL.
            return cast(DataFrame, result[-1].fetch_pandas_all())
        finally:
            self.provider.sql(f"DROP DATABASE IF EXISTS {db_name};")