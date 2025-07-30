import numpy as np
import pandas as pd

from sklearn_nominal.backend.core import Model

from ..backend.conditions import Condition

type Branches = dict[Condition, Tree]


class TreeInfo:
    def __init__(self, column_names: list[str], categorical_values: dict[str, dict[int, str]]):
        self.column_names = column_names
        self.categorical_values = categorical_values


class Tree(Model):
    def __init__(
        self,
        prediction: np.ndarray,
        error: float,
        samples: int,
        branches: Branches = None,
    ):
        if branches is None:
            branches = {}
        self.branches = branches
        self.prediction = prediction
        self.samples = samples
        self.error = error

    def output_size(self):
        return len(self.prediction)

    @property
    def columns(
        self,
    ):
        return list(set([c.column for c in self.conditions()]))

    def predict_sample(self, x: pd.Series):
        for condition, child in self.branches.items():
            result = condition(x)
            if result:
                return child.predict_sample(x)
        return self.prediction

    def children(self):
        return list(self.branches.values())

    def conditions(self):
        return list(self.branches.keys())

    @property
    def leaf(self):
        return len(self.branches) == 0

    def __repr__(self):
        if self.leaf:
            return f"🍁({self.prediction},n={self.samples})"
        else:
            columns_str = ", ".join(self.columns)
            return f"🪵({columns_str})"

    def n_leafs(self):
        if self.leaf:
            return 1
        else:
            return sum([t.n_leafs() for t in self.children()])

    def n_nodes(self):
        return 1 + sum([t.n_nodes() for t in self.children()])

    def height(self):
        return 1 + max([t.height() for t in self.children()])

    def complexity(self):
        return self.n_leafs()

    def pretty_print(self, class_names=None, height=0, max_height=np.inf):
        result = ""
        if height == 0:
            result = "🫚 Root"
        if self.leaf:
            result = f"☘︎ {self.prediction}"
            if class_names is not None:
                klass = self.prediction.argmax()
                result = f"☘︎ {class_names[klass]}"

        if height >= max_height:
            return ""
        base_sep = "|   "
        indent = base_sep * height
        if self.leaf:
            children = ""
        else:

            def format(c, t):
                node = f"{indent}{base_sep}🪵 {c}"
                children = t.pretty_print(height=height + 1, max_height=max_height, class_names=class_names)
                return f"{node} => {children}"

            children = "\n" + "\n".join([format(c, t) for c, t in self.branches.items()])
        return f"{result}{children}"

    def __eq__(self, x):
        if not isinstance(x, Tree):
            return False
        if not np.allclose(self.prediction, x.prediction, atol=1e-8):
            return False
        if len(self.branches) != len(x.branches):
            return False
        for c in self.branches.keys():
            if c not in x.branches.keys():
                return False
            if self.branches[c] != x.branches[c]:
                return False
        return True

    def __hash__(self):
        return hash((self.columns, self.prediction))
