"""This file will just show how to write tests for the template classes."""

import pytest
from sklearn.datasets import load_diabetes, load_iris

from sklearn_nominal.sklearn.tree_classification import TreeClassifier
from sklearn_nominal.sklearn.tree_regression import TreeRegressor

# Authors: scikit-learn-contrib developers
# License: BSD 3 clause


@pytest.fixture
def classification_data():
    return load_iris(return_X_y=True, as_frame=True)


def test_classification_tree(classification_data):
    est = TreeClassifier()
    est.fit(*classification_data)
    assert hasattr(est, "is_fitted_")
    assert hasattr(est, "classes_")
    assert hasattr(est, "model_")

    X = classification_data[0]
    y_pred = est.predict(X)
    assert y_pred.shape == (X.shape[0],)


@pytest.fixture
def regression_data():
    return load_diabetes(return_X_y=True, as_frame=True)


def test_regression_tree(regression_data):
    x, y = regression_data
    model = TreeRegressor(max_depth=3)
    model.fit(x, y)
    assert hasattr(model, "is_fitted_")
    assert hasattr(model, "model_")
    y_pred = model.predict(x)
    assert y_pred.shape == (x.shape[0],)
