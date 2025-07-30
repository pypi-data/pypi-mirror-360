from pathlib import Path

import numpy as np

from sklearn_nominal.backend.conditions import AndCondition, Condition, ValueCondition
from sklearn_nominal.rules.model import RuleModel
from sklearn_nominal.sklearn.rule_oner import OneRClassifier
from sklearn_nominal.tests.test_classification import read_classification_dataset


def test_basic():
    path = Path("datasets/classification/baloons.csv")
    x, y, class_names = read_classification_dataset(path, reencode_y=False)
    sk_model = OneRClassifier()
    sk_model.fit(x, y)
    print("Trained")
    print(sk_model.pretty_print())

    model: RuleModel = sk_model.model_
    assert len(model.rules) == 2
    c1, c2 = np.array([0.75, 0.25]), np.array([0, 1.0])
    reference = RuleModel(
        rules=[
            (ValueCondition(column="Stretchs", value="Yes"), c1),
            (ValueCondition(column="Stretchs", value="No"), c2),
        ],
        default_prediction=np.array([0.375, 0.625]),
    )
    print("Reference")
    print(reference.pretty_print())
    assert reference == model


if __name__ == "__main__":
    test_basic()
