import sys
from dataclasses import dataclass
from typing import Generator

import numpy as np
from h11 import Data

from sklearn_nominal.backend import ColumnID
from sklearn_nominal.backend.conditions import (
    AndCondition,
    Condition,
    NotCondition,
    RangeCondition,
    TrueCondition,
    ValueCondition,
)
from sklearn_nominal.backend.core import ColumnType, Dataset
from sklearn_nominal.rules.model import PredictionRule, RuleModel
from sklearn_nominal.shared.target_error import FixedClassAccuracyError, TargetError


@dataclass
class ConditionProposal:
    error: float
    condition: Condition
    dataset: Dataset
    drop: bool


ConditionGenerator = Generator[None, None, tuple[Condition, bool]]


class PRISM:
    def __init__(
        self,
        class_weight: np.ndarray,
        max_length_per_rule: int = 1000,
        max_rules_per_class: int = 10000,
        min_rule_support: int = 1,
        max_error_per_rule: float = 0.1,
    ):
        self.max_length_per_rule = max_length_per_rule
        self.max_rules_per_class = max_rules_per_class
        self.min_rule_support = min_rule_support
        self.max_error_per_rule = max_error_per_rule
        self.class_weight = class_weight

    def fit(self, d: Dataset):
        rules = []
        classes = d.classes()
        for klass in classes:
            error = FixedClassAccuracyError(klass, len(classes), self.class_weight)
            rules += self.fit_dataset(d, error)

        model = RuleModel(rules, d.class_distribution(self.class_weight))
        return model

    def fit_dataset(self, d: Dataset, error: TargetError):
        rules = []
        while d.n > self.min_rule_support and len(rules) < self.max_rules_per_class:
            rule = self.generate_rule(d, error)
            if rule is None:
                break  # unable to generate rule; stop process
            rules.append(rule)
            condition, prediction = rule
            # keep samples that do not match the condition
            d = d.filter(NotCondition(condition))
        return rules

    def remove_similar(condition: Condition, conditions: list[Condition]):
        # remove range conditions that are similar
        if not isinstance(condition, RangeCondition):
            return
        condition: RangeCondition = condition
        conditions = filter(
            lambda c: isinstance(c, RangeCondition),
        )

        def issimilar(c: RangeCondition):
            return c.column == condition.column and c.less == condition.less

        for s in filter(issimilar, conditions):
            conditions.remove(s)

    def generate_rule(self, d: Dataset, target_error: TargetError) -> None | PredictionRule:
        conditions: list[Condition] = []
        error = np.inf
        while len(conditions) < self.max_length_per_rule:
            p = self.propose_condition(d, error, target_error)
            if p is None:
                # could not propose an improvement
                # retain current conditions as is
                break
            d = p.dataset
            if d.n < self.min_rule_support:
                # Adding condition would drop support below minimum
                # retain current conditions as is
                break
            if p.drop:
                d = d.drop(p.condition.column)
            else:
                # remove similar conditions, in the case they overlap
                similars = filter(p.condition.is_similar, conditions)
                for similar in similars:
                    conditions.remove(similar)
            conditions.append(p.condition)
            error = p.error
        if error >= self.max_error_per_rule or len(conditions) == 0:
            # if the generated conditions are not acceptable in terms of error
            # don't generate a rule
            return None
        condition = AndCondition(conditions)
        return (condition, target_error.prediction(d))

    def generate_conditions(self, d: Dataset, column: ColumnID) -> ConditionGenerator:
        column_index = list(d.columns).index(column)
        column_type = d.types[column_index]
        if column_type == ColumnType.Nominal:
            for v in d.values(column):
                yield (ValueCondition(column, v), True)
        elif column_type == ColumnType.Numeric:
            # binary split of numeric column based on mean
            v = d.mean_x(column)
            l = [False, True]
            for less in l:
                yield (RangeCondition(column, v, less), False)
        else:
            raise ValueError(f"Invalid column type")

    def propose_condition(self, d: Dataset, base_error: float, target_error: TargetError):
        best = None
        for column in d.columns:
            for condition, drop in self.generate_conditions(d, column):
                d_condition = d.filter(condition)
                if d_condition.n < self.min_rule_support:
                    continue
                error = target_error(d_condition)
                if error >= base_error:
                    continue
                if (
                    best is None
                    or error < best.error
                    or (abs(error - best.error) < 1e-16 and d_condition.n > best.dataset.n)
                ):
                    best = ConditionProposal(error, condition, d_condition, drop)
        return best
