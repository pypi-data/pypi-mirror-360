import abc
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from sklearn_nominal.backend.core import Dataset
from sklearn_nominal.tree.pruning import PruneCriteria

from ..shared.column_error import ColumnErrorResult
from ..shared.global_error import Splitter
from .tree import Condition, Tree


class TreeTrainer(abc.ABC):
    @abc.abstractmethod
    def fit(self, d: Dataset) -> Tree:
        pass


class TreeTask:
    def __init__(
        self,
        parent: Tree,
        condition: Condition,
        d: Dataset,
        height: int,
    ):
        self.parent = parent
        self.condition = condition
        self.d = d
        self.height = height


type TreeCreationCallback = Callable[[TreeCreationCallbackResult], None]


@dataclass
class TreeCreationCallbackResult:
    tree: Tree
    task: TreeTask
    prune: bool = False
    best_column: ColumnErrorResult | None = None


class BaseTreeTrainer(TreeTrainer):
    def __init__(
        self,
        error: Splitter,
        prune: PruneCriteria,
        tree_creation_callback: TreeCreationCallback | None = None,
    ):
        self.prune = prune
        self.tree_creation_callback = tree_creation_callback
        self.splitter = error

    def __repr__(self):
        return f"{self.__class__.__name__}({self.splitter},{self.prune})"

    def fit(self, d: Dataset) -> Tree:
        return self.build(d, 1)

    def do_creation_callback(self, r: TreeCreationCallbackResult):
        if self.tree_creation_callback is not None:
            self.tree_creation_callback(r)

    def build(self, d: Dataset, height: int) -> Tree:
        # ROOT
        global_score = self.splitter.global_error(d)
        root = Tree(global_score.prediction, global_score.error, d.n)
        root_task = TreeTask(None, None, d, height)
        subtrees = self.make_tree(root, root_task)

        # OTHER NODES
        while len(subtrees) > 0:
            task = subtrees.pop()
            global_score = self.splitter.global_error(task.d)
            new_tree = Tree(global_score.prediction, global_score.error, task.d.n)
            task.parent.branches[task.condition] = new_tree
            subtree_tasks = self.make_tree(new_tree, task)
            # bfs
            subtree_tasks.reverse()
            subtrees = subtrees + subtree_tasks
        return root

    def make_tree(self, tree: Tree, task: TreeTask) -> list[TreeTask]:
        # BASE CASE: pre_split_prune
        if self.prune.pre_split_prune(task.d.x, task.d.y, task.height, tree):
            r = TreeCreationCallbackResult(tree, task, True)
            self.do_creation_callback(r)
            return []

        # COMPUTE SPLITS
        best_column = self.splitter.split_columns(task.d)

        # BASE CASE: no viable columns to split found
        if best_column is None:
            r = TreeCreationCallbackResult(tree, task)
            self.do_creation_callback(r)
            return []

        # BASE CASE: best gain is not enough to split tree
        if self.prune.post_split_prune(tree, best_column):
            r = TreeCreationCallbackResult(tree, task, True, best_column)
            self.do_creation_callback(r)
            return []

        r = TreeCreationCallbackResult(tree, task, False, best_column)
        self.do_creation_callback(r)

        # RECURSIVE CASE: use best column to split
        subtrees = []

        for i, (d_branch, condition) in enumerate(zip(best_column.partition, best_column.conditions)):
            # avoid branches with low samples
            if d_branch.n < self.prune.min_samples_leaf:
                continue
            # remove column from consideration
            if best_column.remove:
                d_branch = d_branch.drop(columns=[best_column.column])
            # create tree task
            subtask = TreeTask(tree, condition, d_branch, task.height + 1)
            subtrees.append(subtask)

        return subtrees
