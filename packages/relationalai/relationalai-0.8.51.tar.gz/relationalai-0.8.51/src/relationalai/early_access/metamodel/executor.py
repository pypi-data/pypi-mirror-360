from __future__ import annotations

from pandas import DataFrame
from typing import Any, Union

from relationalai.early_access.metamodel import Model, Task

class Executor():
    """ Interface for an object that can execute the program specified by a model. """
    def execute(self, model: Model, task:Task) -> Union[DataFrame, Any]:
        raise NotImplementedError(f"execute: {self}")
