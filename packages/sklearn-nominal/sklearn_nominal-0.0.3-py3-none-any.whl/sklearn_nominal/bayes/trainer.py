from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype, is_string_dtype
from pyparsing import col
from scipy.stats import norm
from sklearn.dummy import class_distribution

from sklearn_nominal.backend import ColumnID
from sklearn_nominal.backend.conditions import ValueCondition
from sklearn_nominal.backend.core import ColumnType, Dataset, Trainer
from sklearn_nominal.bayes.model import (
    CategoricalVariable,
    GaussianVariable,
    NaiveBayes,
    NaiveBayesSingleClass,
)


class NaiveBayesTrainer(Trainer):
    def __init__(self, class_weight: np.ndarray, smoothing: float = 0.0):
        self.smoothing = smoothing
        self.class_weight = class_weight

    def fit_column(self, d: Dataset, column: ColumnID, nominal_values: dict):
        if d.types_dict[column] == ColumnType.Numeric:
            return self.fit_numeric(d, column)
        elif d.types_dict[column] == ColumnType.Nominal:
            return self.fit_nominal(d, column, nominal_values[column])
        else:
            raise ValueError(f"Unsupported column {column}")

    def fit_numeric(self, d: Dataset, column: ColumnID):
        # TODO deal with Nas
        mu = d.mean_x(column)
        std = d.std_x(column, ddof=1)
        return GaussianVariable(mu, std, smoothing=self.smoothing)

    def fit_nominal(self, d: Dataset, column: ColumnID, values: list):
        # TODO deal with Nas

        s = self.smoothing
        # TODO move computation to backend
        conditions = [ValueCondition(column, v) for v in values]
        probabilities = np.array([(dv.n + s) / d.n for dv in d.split(conditions)])
        probabilities /= probabilities.sum()
        d_probabilities = {v: p for v, p in zip(values, probabilities)}
        return CategoricalVariable(d_probabilities)

    def fit_class(self, d: Dataset, nominal_values: dict):
        p = {c: self.fit_column(d, c, nominal_values) for c in d.columns}
        return NaiveBayesSingleClass(p)

    def fit(self, d: Dataset):
        nominal_values = {c: d.unique_values(c) for c in d.columns if d.types_dict[c] == ColumnType.Nominal}
        class_models = [self.fit_class(d.filter_by_class(c), nominal_values) for c in d.classes()]
        pi = d.class_distribution(self.class_weight)
        model = NaiveBayes(class_models, pi)
        return model
