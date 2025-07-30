from pathlib import Path

import numpy as np

from sklearn_nominal.bayes.model import (
    CategoricalVariable,
    GaussianVariable,
    NaiveBayes,
    NaiveBayesSingleClass,
)
from sklearn_nominal.sklearn.naive_bayes import NaiveBayesClassifier
from sklearn_nominal.tests.test_classification import read_classification_dataset


def test_basic():
    path = Path("datasets/classification/stars.csv")
    x, y, class_names = read_classification_dataset(path, reencode_y=False)
    sk_model = NaiveBayesClassifier()
    sk_model.fit(x, y)

    print(sk_model.pretty_print(class_names=class_names))

    model: NaiveBayes = sk_model.model_

    assert len(model.models) == 2
    assert len(model.pi) == 2

    class_probabilities = np.array([0.4, 0.6])
    class_models = [
        NaiveBayesSingleClass(
            {
                "Temperature": GaussianVariable(5100.0, 2409.702),
                "Habitable": CategoricalVariable({"No": 0.75, "Yes": 0.25}),
                "Luminosity": GaussianVariable(11.75, 8.808),
            }
        ),
        NaiveBayesSingleClass(
            {
                "Temperature": GaussianVariable(2866.666, 1348.579),
                "Habitable": CategoricalVariable({"No": 0.5, "Yes": 0.5}),
                "Luminosity": GaussianVariable(3.333, 1.633),
            }
        ),
    ]
    reference_model = NaiveBayes(class_models, class_probabilities)
    assert model == reference_model


if __name__ == "__main__":
    test_basic()
