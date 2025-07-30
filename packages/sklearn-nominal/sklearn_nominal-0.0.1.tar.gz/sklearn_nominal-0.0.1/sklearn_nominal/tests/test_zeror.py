from pathlib import Path

import numpy as np

from sklearn_nominal.backend.conditions import AndCondition, Condition, ValueCondition
from sklearn_nominal.rules.model import RuleModel
from sklearn_nominal.sklearn.rule_zeror import ZeroRClassifier
from sklearn_nominal.tests.test_classification import read_classification_dataset


def test_basic():
    path = Path("datasets/classification/baloons.csv")
    x, y, class_names = read_classification_dataset(path, reencode_y=False)
    sk_model = ZeroRClassifier()
    sk_model.fit(x, y)

    print(sk_model.pretty_print())

    model: RuleModel = sk_model.model_
    assert len(model.rules) == 0
    reference = RuleModel(rules=[], default_prediction=np.array([0.375, 0.625]))
    print(reference.pretty_print())
    assert reference == model


if __name__ == "__main__":
    test_basic()
