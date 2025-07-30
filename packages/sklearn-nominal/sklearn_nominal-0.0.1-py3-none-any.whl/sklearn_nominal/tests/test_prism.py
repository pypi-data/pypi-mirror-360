from pathlib import Path

import numpy as np

from sklearn_nominal.backend.conditions import AndCondition, Condition, ValueCondition
from sklearn_nominal.rules.model import RuleModel
from sklearn_nominal.sklearn.rule_prism import PRISMClassifier
from sklearn_nominal.tests.test_classification import read_classification_dataset


def test_basic():
    path = Path("datasets/classification/baloons.csv")
    x, y, class_names = read_classification_dataset(path, reencode_y=False)
    sk_model = PRISMClassifier(min_rule_support=1)
    sk_model.fit(x, y)

    print(sk_model.pretty_print())

    model: RuleModel = sk_model.model_
    assert len(model.rules) == 4
    c1, c2 = np.array([1.0, 0]), np.array([0, 1.0])
    reference = RuleModel(
        rules=[
            (
                AndCondition(
                    [
                        ValueCondition(column="Stretchs", value="Yes"),
                        ValueCondition(column="Color", value="Yellow"),
                    ]
                ),
                c1,
            ),
            (
                AndCondition(
                    [
                        ValueCondition(column="Stretchs", value="Yes"),
                        ValueCondition(column="Age", value="Adult"),
                    ]
                ),
                c1,
            ),
            (AndCondition([ValueCondition(column="Stretchs", value="No")]), c2),
            (
                AndCondition(
                    [
                        ValueCondition(column="Color", value="Red"),
                        ValueCondition(column="Age", value="Children"),
                    ]
                ),
                c2,
            ),
        ],
        default_prediction=np.array([0.375, 0.625]),
    )
    print(reference.pretty_print())
    assert reference == model


if __name__ == "__main__":
    test_basic()
