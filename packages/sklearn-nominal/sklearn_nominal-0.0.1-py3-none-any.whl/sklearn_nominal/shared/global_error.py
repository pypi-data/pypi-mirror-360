import abc
from typing import Callable

import numpy as np
import pandas as pd

from sklearn_nominal.backend.conditions import Condition
from sklearn_nominal.backend.core import ColumnType, Dataset

from .column_error import (
    ColumnCallback,
    ColumnError,
    ColumnErrorResult,
    NominalColumnError,
    NumericColumnError,
)
from .target_error import TargetError


# TODO simplify this
class GlobalErrorResult:
    def __init__(
        self,
        prediction: np.ndarray,
        error: float,
    ):
        self.prediction = prediction
        self.error = error


class Splitter(abc.ABC):
    @abc.abstractmethod
    def global_error(self, d: Dataset) -> GlobalErrorResult:
        pass

    @abc.abstractmethod
    def split_columns(self, d: Dataset) -> ColumnErrorResult | None:
        pass


class DefaultSplitter(Splitter):
    def __init__(
        self,
        error_function: TargetError,
        column_splitters: dict[ColumnType, ColumnError] = None,
    ):
        if column_splitters is None:
            column_splitters = {
                ColumnType.Nominal: NominalColumnError(error_function),
                ColumnType.Numeric: NumericColumnError(error_function),
            }
        self.column_splitters = column_splitters
        self.target_error = error_function

    def __repr__(self):
        return f"Error({self.target_error})"

    def global_error(self, d: Dataset):
        global_metric = self.target_error(d)
        global_prediction = self.target_error.prediction(d)
        return GlobalErrorResult(global_prediction, global_metric)

    def split_columns(self, d: Dataset) -> ColumnErrorResult | None:
        best = None
        for c, c_type in zip(d.columns, d.types):
            result = self.column_splitters[c_type].error(d, c)
            update = best is None or (result is not None and result.error < best.error)
            if update:
                best = result
        return best
