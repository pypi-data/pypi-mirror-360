import numpy as np
import pandas as pd

from sklearn_nominal.tree.tree import Tree

from ..shared.column_error import ColumnErrorResult


class PruneCriteria:
    def __init__(
        self,
        min_error_decrease: float = 0.00001,
        min_samples_leaf: int = 1,
        min_samples_split: int = 2,
        max_height: int = None,
        error_tolerance: float = 1e-16,
    ):
        if max_height is not None:
            assert max_height > 0
        assert min_samples_leaf > 0
        assert min_error_decrease >= 0

        self.min_error_decrease = min_error_decrease
        self.min_samples_leaf = min_samples_leaf
        self.min_samples_split = min_samples_split
        self.max_height = max_height
        self.error_tolerance = error_tolerance

    def params(self):
        return {
            "min_error_decrease": self.min_error_decrease,
            "min_samples_leaf": self.min_samples_leaf,
            "min_samples_split": self.min_samples_split,
            "max_height": self.max_height,
            "error_tolerance": self.error_tolerance,
        }

    def __repr__(self):
        params_str = ", ".join([f"{k}={v}" for k, v in self.params().items()])
        return f"Prune({params_str})"

    def pre_split_prune(self, x: pd.DataFrame, y: np.ndarray, height: int, tree: Tree):
        # BASE CASE: max_height reached
        if self.max_height is not None and height == self.max_height:
            return True
        # BASE CASE: not enough samples to split
        if len(y) < self.min_samples_split:
            return True

        # BASE CASE: no more columns to split
        if len(x.columns) == 0:
            return True

        # BASE CASE: the achieved error is within tolerance
        if tree.error <= self.error_tolerance:
            return True

        return False

    def post_split_prune(self, tree: Tree, best_column: ColumnErrorResult):
        error_improvement = tree.error - best_column.error
        return error_improvement <= self.min_error_decrease
