from __future__ import annotations

import abc
import enum

import numpy as np
import pandas as pd

from sklearn_nominal.backend import ColumnID, Input, InputSample

from .conditions import Condition


class ColumnType(enum.Enum):
    Numeric = 0
    Nominal = 1


type Partition = list[Dataset]


class Dataset(abc.ABC):
    @abc.abstractmethod
    def split(self, conditions: list[Condition]) -> Partition:
        pass

    @abc.abstractmethod
    def filter(self, condition: Condition) -> Dataset:
        pass

    @property
    @abc.abstractmethod
    def x(
        self,
    ) -> pd.DataFrame:
        pass

    @property
    @abc.abstractmethod
    def y(
        self,
    ) -> np.ndarray:
        pass

    @property
    @abc.abstractmethod
    def n(
        self,
    ) -> int:
        pass

    @property
    @abc.abstractmethod
    def types(
        self,
    ) -> list[ColumnType]:
        pass

    @property
    @abc.abstractmethod
    def types_dict(
        self,
    ) -> dict[ColumnID, ColumnType]:
        pass

    @property
    @abc.abstractmethod
    def columns(
        self,
    ) -> list[str]:
        pass

    @abc.abstractmethod
    def drop(self, columns: list[str]) -> Dataset:
        pass

    @abc.abstractmethod
    def values(self, column: str) -> np.ndarray:
        pass

    @abc.abstractmethod
    def unique_values(self, column: str, sorted: bool) -> np.ndarray:
        pass

    @abc.abstractmethod
    def classes(self) -> list:
        pass

    @abc.abstractmethod
    def filter_by_class(self, c) -> Dataset:
        pass

    @abc.abstractmethod
    def class_distribution(self, class_weight: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def mean_x(self, col: ColumnID) -> float:
        pass

    @abc.abstractmethod
    def std_x(self, col: ColumnID, ddof=1) -> float:
        pass

    @abc.abstractmethod
    def mean_y(
        self,
    ) -> np.ndarray:
        pass

    @abc.abstractmethod
    def std_y(self) -> float:
        pass

    @abc.abstractmethod
    def count_class(self, klass: int) -> int:
        pass


class Model(abc.ABC):
    @abc.abstractmethod
    def predict_sample(self, x: InputSample):
        pass

    @abc.abstractmethod
    def output_size(self) -> int:
        pass

    def predict(self, x: Input):
        n = x.shape[0]
        predictions = np.zeros((n, self.output_size()))
        for i, (idx, row) in enumerate(x.iterrows()):
            predictions[i, :] = self.predict_sample(row)
        return predictions

    @abc.abstractmethod
    def pretty_print(self, class_names: list[str] = None) -> str:
        pass

    @abc.abstractmethod
    def complexity(self) -> int:
        pass


class Trainer(abc.ABC):
    def fit(self, d: Dataset) -> Model:
        pass
