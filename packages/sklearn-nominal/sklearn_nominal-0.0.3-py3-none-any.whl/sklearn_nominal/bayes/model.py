import abc
from abc import ABC
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm

from sklearn_nominal.backend import Input, InputSample
from sklearn_nominal.backend.core import Model


class Variable(ABC):
    @abc.abstractmethod
    def predict(self, x: pd.Series) -> np.ndarray:
        pass

    @abc.abstractmethod
    def complexity(self) -> int:
        pass


atol = 1e-02


class GaussianVariable(Variable):
    def __init__(self, mu: float, std: float, smoothing: float = 0) -> None:
        self.mu = mu
        self.std = std
        self.normal = norm(mu, std + smoothing)

    def predict(self, x: pd.Series) -> np.ndarray:
        result = self.normal.pdf(x.values)
        result[np.isnan(x.values)] = 1
        return result

    def __repr__(self) -> str:
        return f"N({self.mu:.4g},{self.std:.4g})"

    def complexity(self):
        return 1

    def __eq__(self, x):
        if not isinstance(x, GaussianVariable):
            return False
        return np.allclose(self.mu, x.mu, atol=atol) and np.allclose(self.std, x.std, atol=atol)


def dict_allclose(x: dict[Any, float], y: dict[Any, float]):
    def keys(x: dict):
        return sorted(list(x.keys()))

    def values(x: dict):
        return np.array([x[k] for k in keys(x)])

    return len(x) == len(y) and keys(x) == keys(y) and np.allclose(values(x), values(y), atol=atol)


class CategoricalVariable(Variable):
    def __init__(self, probabilities: dict[str, float]) -> None:
        self.probabilities = probabilities

    def p(self, x: str, default: float = 1.0) -> float:
        if x in self.probabilities:
            return self.probabilities[x]
        else:
            return default

    def predict(self, x: pd.Series) -> np.ndarray:
        return np.array(list(map(self.p, x.values)))

    def __repr__(self) -> str:
        variables = ", ".join([f"{k}={v:.4g}" for k, v in self.probabilities.items()])
        return f"C({variables})"

    def complexity(self):
        return len(self.probabilities)

    def __eq__(self, x):
        if not isinstance(x, CategoricalVariable):
            return False
        return dict_allclose(self.probabilities, x.probabilities)


class NaiveBayesSingleClass:
    def __init__(self, variables: dict[str, Variable]):
        self.variables = variables

    def predict(self, x: pd.DataFrame):
        p = 1
        for name, var in self.variables.items():
            value = x[name]
            pi = var.predict(value)
            p *= pi
        return p

    def pretty_print(self) -> str:
        max_name_length = max(map(len, self.variables.keys())) + 2
        variables = "\n".join([f"    {k:{max_name_length}} ~ {v}" for k, v in self.variables.items()])
        return f"{variables}"

    def complexity(self) -> int:
        return max([v.complexity() for v in self.variables.values()])

    def __eq__(self, x):
        if not isinstance(x, NaiveBayesSingleClass):
            return False

        return self.variables == x.variables


class NaiveBayes(Model):
    def __init__(
        self,
        class_models: list[NaiveBayesSingleClass],
        class_probabilities: np.ndarray,
    ):
        self.models = class_models
        self.pi = class_probabilities

    def predict_sample(self, x: InputSample) -> int:
        df = pd.DataFrame([x])
        y = self.predict(df)
        return y[0, :]

    def predict(self, x: Input):
        n = len(x)
        n_classes = len(self.models)
        results = np.zeros((n, n_classes))
        for c in range(n_classes):
            p_x = self.models[c].predict(x)
            p_class = self.pi[c]
            results[:, c] = p_x * p_class

        results /= results.sum(axis=1, keepdims=True)

        return results

    def pretty_print(self, class_names: list[str] = None) -> str:
        n_classes = len(self.models)

        def class_description(i: int):
            name = f"{i}" if class_names is None else class_names[i]
            p_c = self.pi[i]
            return f"Class {name} (p={p_c:.3g}):\n{self.models[i].pretty_print()}"

        class_descriptions = [class_description(i) for i in range(n_classes)]
        class_descriptions = "\n".join(class_descriptions)
        return f"{NaiveBayes.__name__}(classes={n_classes})\n{class_descriptions}"

    def complexity(self) -> int:
        return max([m.complexity() for m in self.models])

    def output_size(self) -> int:
        return len(self.models)

    def __eq__(self, x):
        if not isinstance(x, NaiveBayes):
            return False
        return (
            self.pi.shape == x.pi.shape
            and np.allclose(self.pi, x.pi, atol=atol)
            and len(self.models) == len(x.models)
            and all([a == b for a, b in zip(self.models, x.models)])
        )
