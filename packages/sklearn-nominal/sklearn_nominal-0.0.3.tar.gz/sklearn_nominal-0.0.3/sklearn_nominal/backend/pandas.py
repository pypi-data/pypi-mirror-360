from __future__ import annotations

from typing import Generator, Iterable

import numpy as np
import pandas as pd
from numpy import dtype, ndarray
from scipy.special import y1

from . import ColumnID
from .conditions import (
    AndCondition,
    Condition,
    NotCondition,
    RangeCondition,
    TrueCondition,
    ValueCondition,
)
from .core import ColumnType, Dataset


class PandasDataset(Dataset):
    def __init__(self, x: pd.DataFrame, y: np.ndarray, idx=None):
        super().__init__()
        self._x: pd.DataFrame = x
        self._y: np.ndarray = y
        self.idx = idx
        # already filtered if idx is None
        self._x_subset = idx is None
        self._y_subset = self._x_subset

    @property
    def x(self) -> pd.DataFrame:
        if not self._x_subset:
            self._x = self._x.loc[self.idx]
            self._x_subset = True
            if self._y_subset:  # if filtered both, free idx
                self.idx = None
        return self._x

    @property
    def y(self) -> pd.ndarray:
        if not self._y_subset:
            self._y = self._y[self.idx]
            self._y_subset = True
        if self._x_subset:  # if filtered both, free idx
            self.idx = None
        return self._y

    def split(self, conditions: list[Condition]):
        return [self.filter(c) for c in conditions]

    def values(self, column: ColumnID):
        result: pd.Series = self.x[column].dropna()
        return result

    def unique_values(self, column: ColumnID, sorted=False) -> np.ndarray:
        result = self.values(column).unique()
        if sorted:
            result.sort()
        return result

    def indices(self, condition: Condition):
        if isinstance(condition, RangeCondition):
            rc: RangeCondition = condition
            if rc.less:
                idx = self.x[rc.column] <= rc.value
            else:
                idx = self.x[rc.column] > rc.value
            idx.fillna(False, inplace=True)
            return idx
        elif isinstance(condition, ValueCondition):
            vc: ValueCondition = condition
            idx = self.x[vc.column] == vc.value
            idx.fillna(False, inplace=True)
            return idx
        elif isinstance(condition, TrueCondition):
            return None
        elif isinstance(condition, NotCondition):
            return ~self.indices(condition.condition)
        elif isinstance(condition, AndCondition):
            idx = None
            for c in condition.conditions:
                c_idx = self.indices(c)
                if idx is None:
                    idx = c_idx
                else:
                    idx = idx & c_idx
            return idx
        else:
            raise ValueError(f"Invalid condition: {condition}")

    def filter(self, condition: Condition):
        idx = self.indices(condition)
        return PandasDataset(self.x, self.y, idx=idx)

    @property
    def n(self):
        return self.y.shape[0]

    @property
    def types_dict(self) -> dict[ColumnID, ColumnType]:
        return dict(zip(self.columns, self.types))

    @property
    def types(self) -> list[ColumnType]:
        numeric = self.x.select_dtypes(include="number").columns

        def to_type(column):
            if column in numeric:
                return ColumnType.Numeric
            else:
                return ColumnType.Nominal

        return list(map(to_type, self.columns))

    @property
    def columns(self) -> list[ColumnID]:
        return self.x.columns

    def drop(self, columns: list[ColumnID]) -> PandasDataset:
        x = self.x.drop(columns=columns)
        return PandasDataset(x, self.y)

    def classes(self):
        values = np.unique(self.y)
        values.sort()
        return values

    def filter_by_class(self, c) -> Dataset:
        idx = self.y == c
        idx = np.nan_to_num(idx, nan=False)
        # idx.fillna(False, inplace=True)
        return PandasDataset(self.x, self.y, idx)

    def class_distribution(self, class_weight: np.ndarray) -> np.ndarray:
        classes = len(class_weight)
        p: np.ndarray = np.bincount(self.y, minlength=classes)
        result = p
        result = result * class_weight
        result /= result.sum()
        return result

    def mean_y(
        self,
    ) -> np.ndarray:
        return self.y.mean(axis=0)

    def std_y(
        self,
    ) -> float:
        if self.y.shape[0] == 0:
            return np.inf
        return np.sum(np.std(self.y, axis=0))

    def mean_x(self, col: ColumnID) -> float:
        return self.x[col].mean()

    def std_x(self, col: ColumnID, ddof=1) -> float:
        return self.x[col].std(ddof=ddof)

    def count_class(self, klass: int) -> int:
        return np.sum(self.y == klass)
