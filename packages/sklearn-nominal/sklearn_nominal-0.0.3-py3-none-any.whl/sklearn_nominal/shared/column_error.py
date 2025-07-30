import abc
from typing import Callable

import numpy as np
import pandas as pd
from h11 import Data

from sklearn_nominal.backend.conditions import Condition, RangeCondition, ValueCondition
from sklearn_nominal.backend.core import Dataset, Partition
from sklearn_nominal.backend.split import RangeSplit, Split, ValueSplit

from .attribute_penalization import ColumnPenalization, NoPenalization
from .target_error import TargetError

type ColumnCallback = Callable[[ColumnErrorResult], None]


class ColumnErrorResult:
    def __init__(
        self,
        column: str,
        error: float,
        conditions: list[Condition],
        partition: Partition,
        remove: bool = False,
    ):
        self.error = error
        self.conditions = conditions
        self.partition = partition
        self.column = column
        self.remove = remove

    def __repr__(self):
        return f"Score({self.column},{self.error},{len(self.conditions)} branches)"


class ColumnError(abc.ABC):
    def __init__(
        self,
        metric: TargetError,
        penalization: ColumnPenalization = NoPenalization(),
        callback=None,
    ):
        self.penalization = penalization
        self.metric = metric
        self.callback = callback

    def do_callback(self, result: ColumnErrorResult):
        if self.callback is not None:
            self.callback(result)

    @abc.abstractmethod
    def error(self, d: Dataset, column: str) -> ColumnErrorResult | None:
        pass

    def __repr__(self):
        return self.__class__.__name__

    def evaluate_conditions(
        self,
        d: Dataset,
        conditions: list[Condition],
        column: str,
        remove=False,
    ) -> ColumnErrorResult:
        partition = d.split(conditions)
        error = self.metric.average_split(partition)
        error /= self.penalization.penalize(partition)
        return ColumnErrorResult(column, error, conditions, partition, remove)


class NumericColumnError(ColumnError):
    def __init__(
        self,
        metric: TargetError,
        penalization: ColumnPenalization = NoPenalization(),
        callback=None,
        max_evals: int = np.iinfo(np.int64).max,
    ):
        super().__init__(metric, penalization, callback=callback)
        assert max_evals > 0
        self.max_evals = max_evals

    def get_values(self, d: Dataset, column: str):
        values = d.unique_values(column, False)
        n = len(values)
        if self.max_evals is not None:
            if n > self.max_evals:
                # subsample
                step = n // self.max_evals
                values = values[::step]
                n = len(values)
        if n > 1:
            values = values[:-1]
            n -= 1
        return values

    def error(
        self,
        d: Dataset,
        column: str,
    ) -> ColumnErrorResult | None:
        values = self.get_values(d, column)
        # find best split value based on unique values of column
        best = None
        for i, v in enumerate(values):
            conditions = RangeCondition.make(column, v)
            result = self.evaluate_conditions(d, conditions, column)
            self.do_callback(result)
            if best is None or result.error <= best.error:
                best = result
        return best


class NominalColumnError(ColumnError):
    def error(self, d: Dataset, column: str) -> ColumnErrorResult | None:
        conditions: list[Condition] = [ValueCondition(column, v) for v in d.unique_values(column, False)]
        result = self.evaluate_conditions(d, conditions, column, remove=True)
        self.do_callback(result)
        return result
