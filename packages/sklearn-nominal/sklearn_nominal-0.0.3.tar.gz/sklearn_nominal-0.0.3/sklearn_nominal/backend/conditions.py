from __future__ import annotations

import abc
from multiprocessing import Value

import numpy as np
import pandas as pd

from sklearn_nominal.backend import ColumnID, InputSample



class Condition(abc.ABC):
    """
    A condition to filter rows of a :class: Dataset
    
    """
    def __init__(self, column: ColumnID):
        super().__init__()
        self.column = column

    @abc.abstractmethod
    def __call__(self, x: InputSample) -> bool:
        pass

    @abc.abstractmethod
    def short_description(self) -> str:
        """
        Returns a short description of this Condition for displaying purposes
        """
        pass

    def na_to_false(self, s: bool | any):
        if not isinstance(s, (bool, np.bool_)):
            return False
        else:
            return s

    def is_similar(self, c: Condition):
        """
        returns True if the condition uses the same attributes and values as this condition.
        """
        pass


class ValueCondition(Condition):
    def __init__(self, column: ColumnID, value):
        super().__init__(column)
        self.value = value

    def __call__(self, x: InputSample):
        return self.na_to_false(x[self.column] == self.value)

    def __repr__(self):
        return f"{self.column}={self.value}"

    def short_description(self):
        return f"{self.value}"

    def is_similar(self, c: Condition):
        if isinstance(c, ValueCondition):
            return c.column == self.column
        else:
            return False

    def __eq__(self, x):
        if not isinstance(x, ValueCondition):
            return False
        return self.value == x.value and self.column == x.column

    def __hash__(self):
        return hash((self.column, self.value))


class RangeCondition(Condition):
    def __init__(self, column: ColumnID, value: float, less: bool):
        super().__init__(column)
        self.value = value
        self.less = less

    @classmethod
    def make(cls, column, value):
        return [RangeCondition(column, value, t) for t in [True, False]]

    def __call__(self, x: InputSample):
        if self.less:
            return self.na_to_false(x[self.column] <= self.value)
        else:
            return self.na_to_false(x[self.column] > self.value)

    def __repr__(self):
        op = "<=" if self.less else ">"
        return f"{self.column} {op} {self.value:.4g}"

    def short_description(self):
        op = "<=" if self.less else ">"
        return f"{op} {self.value:.4g}"

    def is_similar(self, c: Condition):
        if isinstance(c, RangeCondition):
            return c.column == self.column and c.less == self.less
        else:
            return False

    def __eq__(self, x):
        if not isinstance(x, RangeCondition):
            return False
        return self.value == x.value and self.column == x.column and self.less == x.less

    def __hash__(self):
        return hash((self.column, self.value, self.less))


class AndCondition(Condition):
    def __init__(self, conditions: list[Condition]):
        column = ",".join([str(c.column) for c in conditions])
        super().__init__(column)
        self.conditions = conditions

    def short_description(self):
        descriptions = [c.short_description() for c in self.conditions]
        descriptions = ",".join(descriptions)
        return f"And({descriptions})"

    def __call__(self, x: InputSample):
        for c in self.conditions:
            if not c(x):
                return False
        return True

    def __repr__(self):
        conditions = [f"({c})" for c in self.conditions]
        descriptions = " AND ".join(conditions)
        return f"{descriptions}"

    def is_similar(self, c: Condition):
        if isinstance(c, AndCondition):
            # must have the same number of conditions
            if len(c.conditions) != len(self.conditions):
                return False
            for child in self.conditions:
                # every child condition must be similar to a condition in c
                if not any([a.is_similar(child) for a in c.conditions]):
                    return False
            return True
        else:
            return False

    def __eq__(self, x):
        if not isinstance(x, AndCondition):
            return False
        if len(x.conditions) != len(self.conditions):
            return False
        for child in self.conditions:
            # every child condition must be similar to a condition in x
            if not any([a == child for a in x.conditions]):
                return False
        return True

    def __hash__(self):
        return hash(self.conditions)


class TrueCondition(Condition):
    def __init__(self):
        super().__init__("")

    def __call__(self, x: InputSample):
        return True

    def short_description(self):
        return "True"

    def __repr__(self):
        return self.short_description()

    def is_similar(self, c: Condition):
        return isinstance(c, TrueCondition)

    def __eq__(self, x):
        return isinstance(x, TrueCondition)

    def __hash__(self):
        return 1


class NotCondition(Condition):
    def __init__(self, condition: Condition):
        super().__init__(condition.column)
        self.condition = condition

    def __call__(self, x: InputSample):
        return not self.condition(x)

    def short_description(self):
        return f"NOT {self.condition.short_description}"

    def __repr__(self):
        return self.short_description()

    def is_similar(self, c: Condition):
        if isinstance(c, NotCondition):
            return self.condition.is_similar(c.condition)
        return False

    def __eq__(self, x):
        if not isinstance(x, NotCondition):
            return False
        return self.condition == x.condition

    def __hash__(self):
        return hash((1, self.condition))
