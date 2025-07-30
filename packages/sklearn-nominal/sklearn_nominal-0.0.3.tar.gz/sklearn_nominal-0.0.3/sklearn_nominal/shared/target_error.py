import abc

import numpy as np
import pandas as pd

from sklearn_nominal.backend.core import Dataset, Partition


class TargetError(abc.ABC):
    @abc.abstractmethod
    def __call__(self, d: Dataset) -> float:
        pass

    def average_split(self, partition: list[Dataset]):
        error = 0.0
        n = 0
        for d_branch in partition:
            if d_branch.n == 0:
                continue
            branch_error = self(d_branch)
            n_branch = d_branch.n
            error += n_branch * branch_error
            n += n_branch
        if n == 0:
            return np.inf
        else:
            return error / n

    @abc.abstractmethod
    def prediction(self, d: Dataset):
        pass

    def __repr__(self):
        return self.__class__.__name__


eps = 1e-32


def log(x, base):
    x[x < eps] = eps
    if base == 2:
        return np.log2(x)
    elif base == 0:
        return np.log(x)
    elif base == 10:
        return np.log10(x)
    else:
        lb = 1 / np.log(base)
        return np.log(x) * lb


class ClassificationError(TargetError):
    def __init__(self, classes: int, class_weight: np.ndarray):
        self.classes = classes
        self.class_weight = class_weight

    def prediction(self, d: Dataset):
        y = d.y
        if len(y) == 0:
            return self.class_weight / self.class_weight.sum()
        else:
            # Assumes classes start at 0
            return d.class_distribution(self.class_weight)

    def __repr__(self):
        return f"{super().__repr__()}(classes={self.classes})"


class EntropyError(ClassificationError):
    def __init__(self, classes: int, class_weight: np.ndarray, base=2):
        super().__init__(classes, class_weight)
        self.base = base

    def __call__(self, d: Dataset):
        p = self.prediction(d)

        return -np.sum(p * log(p, self.classes))


class AccuracyError(ClassificationError):
    def __init__(self, classes: int, class_weight: np.ndarray):
        super().__init__(classes, class_weight)

    def __call__(self, d: Dataset):
        p = self.prediction(d)
        klass = p.argmax()
        return 1 - d.count_class(klass) / d.n


class FixedClassAccuracyError(ClassificationError):
    """
    This error does not take into consideration samples to generate a prediction
    Instead, it has a fixed prediction based on a specific class
    And the accuracy error is also fixed on that specific class.
    """

    def __init__(self, klass: int, classes: int, class_weight: np.ndarray):
        super().__init__(classes, class_weight)
        self.klass = klass
        self._prediction = np.zeros(classes)
        self._prediction[klass] = 1

    def prediction(self, d: Dataset):
        return self._prediction

    def __call__(self, d: Dataset):
        return 1 - d.count_class(self.klass) / d.n


class GiniError(ClassificationError):
    def __init__(self, classes: int, class_weight: np.ndarray, base=2):
        super().__init__(classes, class_weight)
        self.base = base

    def __call__(self, d: Dataset):
        p = self.prediction(d)
        return 1 - np.sum(p**2)


class RegressionError(TargetError):
    def prediction(self, d: Dataset):
        return d.mean_y()


class DeviationError(RegressionError):
    def __call__(self, d: Dataset):
        if d.n == 0:
            return np.inf
        elif d.n == 1:
            return 0
        else:
            return d.std_y()
