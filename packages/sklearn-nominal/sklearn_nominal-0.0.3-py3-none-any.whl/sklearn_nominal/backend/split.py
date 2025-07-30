import abc
from typing import Iterable

import numpy as np
import pandas as pd

from .conditions import Condition, RangeCondition, ValueCondition
from .core import Dataset, Partition


class Split(abc.ABC):
    @property
    @abc.abstractmethod
    def conditions(self) -> list[Condition]:
        pass

    @property
    @abc.abstractmethod
    def partition(self) -> Partition:
        pass

    @abc.abstractmethod
    def split(self, x: pd.DataFrame, y: np.ndarray):
        pass


class ColumnSplit(Split):
    def __init__(self, column: str):
        super().__init__()
        self.column = column


class RangeSplit(ColumnSplit):
    def __init__(self, column: str, value: float, x: pd.DataFrame, y: np.ndarray):
        super().__init__(column)
        self.value = value
        self._partition = list(self.split(x, y))

    @property
    def partition(self):
        return self._partition

    @property
    def conditions(self):
        return [RangeCondition(self.column, self.value, t) for t in [True, False]]

    def split(self, x: pd.DataFrame, y: np.ndarray):
        idx = x[self.column] <= self.value
        not_idx = (~idx).fillna(False)
        idx = idx.fillna(False)

        yield x.loc[idx], y[idx]
        yield x.loc[not_idx], y[not_idx]


class ValueSplit(ColumnSplit):
    def __init__(self, column: str, values: list, x: pd.DataFrame, y: np.ndarray):
        super().__init__(column)
        self.values = values
        self._partition = list(self.split(x, y))

    @property
    def partition(self):
        return self._partition

    @property
    def conditions(self):
        return [ValueCondition(self.column, v) for v in self.values]

    def split(self, x: pd.DataFrame, y: np.ndarray):
        for value in self.values:
            idx = x[self.column].values == value
            if idx.any():
                yield x.loc[idx], y[idx]
