from io import StringIO
from typing import Optional

import pandas as pd

import relationalai.early_access.builder as qb
from relationalai.early_access.builder import define, where
from relationalai.early_access.builder.std.decimals import parse_decimal64, parse_decimal128
from relationalai.early_access.dsl.bindings.common import BindableColumn, AbstractBindableTable
from relationalai.early_access.dsl.snow.common import CsvColumnMetadata
from relationalai.early_access.dsl.utils import normalize
from relationalai.early_access.rel.rel_utils import DECIMAL64_SCALE, DECIMAL128_SCALE


class BindableCsvColumn(BindableColumn):
    _metadata: CsvColumnMetadata
    _column_basic_type: str

    def __init__(self, metadata: CsvColumnMetadata, table: 'CsvTable', model):
        super().__init__(metadata.name, metadata.datatype, table, model)
        self._metadata = metadata
        self._column_basic_type = "Int64" if metadata.datatype._name == qb.Integer._name else "string"

    @property
    def metadata(self):
        return self._metadata

    def basic_type(self):
        return self._column_basic_type

    def decimal_scale(self) -> Optional[int]:
        if self.type() is qb.Decimal64:
            return DECIMAL64_SCALE
        elif self.type() is qb.Decimal128:
            return DECIMAL128_SCALE
        else:
            return None

    def decimal_size(self) -> Optional[int]:
        if self.type() is qb.Decimal64:
            return 64
        elif self.type() is qb.Decimal128:
            return 128
        else:
            return None

    def __repr__(self):
        return f"CSV:{self._source.physical_name()}.{self.physical_name()}"


class CsvTable(AbstractBindableTable[BindableCsvColumn]):
    _basic_type_schema: dict[str, str]
    _csv_data: list[str]

    def __init__(self, name: str, schema: dict[str, qb.Concept], model):
        super().__init__(name, model, set())
        self._initialize(schema, model)

    def _initialize(self, schema: dict[str, qb.Concept], model):
        self._csv_data = list()
        self._cols = {column_name: BindableCsvColumn(CsvColumnMetadata(column_name, column_type), self, model)
                      for column_name, column_type in schema.items()}
        self._basic_type_schema = {col.metadata.name: col.basic_type() for col in self._cols.values()}

    def __str__(self):
        # returns the name of the table, as well as the columns and their types
        return self.physical_name() + ':\n' + '\n'.join(
            [f' {col.metadata.name} {col.metadata.datatype}' for _, col in self._cols.items()]
        ) + '\n' + '\n'.join(
            [f' {fk.source_columns} -> {fk.target_columns}' for fk in self._foreign_keys]
        )

    @property
    def csv_data(self) -> list[str]:
        return self._csv_data

    def physical_name(self) -> str:
        return self._table.lower()

    def data(self, csv_data: str):
        self._csv_data.append(csv_data)
        CsvSourceModule.generate(self, pd.read_csv(StringIO(normalize(csv_data)), dtype=self._basic_type_schema))

class CsvSourceModule:

    @staticmethod
    def generate(table: CsvTable, data: pd.DataFrame):
        for index, row in data.iterrows():
            for column_name in data.columns:
                value = row[column_name]
                if pd.notna(value):
                    column = table.__getattr__(column_name)
                    column_type = column.type()
                    if column_type._name == qb.Date._name:
                        CsvSourceModule._row_to_date_value_rule(column, index, value)
                    elif column_type._name == qb.DateTime._name:
                        CsvSourceModule._row_to_date_time_value_rule(column, index, value)
                    elif column_type._name == qb.Decimal64._name:
                        CsvSourceModule._row_to_decimal64_value_rule(column, index, value)
                    elif column_type._name == qb.Decimal128._name:
                        CsvSourceModule._row_to_decimal128_value_rule(column, index, value)
                    else:
                        CsvSourceModule._row_to_value_rule(column, index, value)

    @staticmethod
    def _row_to_value_rule(column, row, value):
        define(column(row, value))

    @staticmethod
    def _row_to_date_value_rule(column, row, value):
        parse_date = qb.Relationship.builtins['parse_date']
        rez = qb.Date.ref()
        where(parse_date(value, 'Y-m-d', rez)).define(column(row, rez))

    @staticmethod
    def _row_to_date_time_value_rule(column, row, value):
        parse_datetime = qb.Relationship.builtins['parse_datetime']
        rez = qb.DateTime.ref()
        where(parse_datetime(value, 'Y-m-d HH:MM:SS z', rez)).define(column(row, rez))

    @staticmethod
    def _row_to_decimal64_value_rule(column, row, value):
        define(column(row, parse_decimal64(value)))

    @staticmethod
    def _row_to_decimal128_value_rule(column, row, value):
        define(column(row, parse_decimal128(value)))
