from pathlib import Path

import numpy as np

from sklearn_nominal.backend.conditions import Condition, RangeCondition, ValueCondition
from sklearn_nominal.sklearn.tree_classification import TreeClassifier
from sklearn_nominal.tests.test_classification import read_classification_dataset
from sklearn_nominal.tree.tree import Tree


def test_jobs():
    path = Path("datasets/classification/jobs.csv")
    x, y, class_names = read_classification_dataset(path, reencode_y=False)
    sk_model = TreeClassifier(min_samples_split=1, splitter="best")
    sk_model.fit(x, y)

    print("Trained")
    print(sk_model.pretty_print())

    model: Tree = sk_model.model_
    assert model.n_leafs() == 5
    assert model.n_nodes() == 9

    c1, c2 = np.array([1.0, 0]), np.array([0, 1.0])
    p_ref = np.array([0.5625, 0.4375])
    p_degree = np.array([0.75, 0.25])
    p_past_jobs_6 = np.array([0.25, 0.75])
    p_past_jobs_8 = np.array([0.5, 0.5])

    past_jobs_8 = Tree(
        prediction=p_past_jobs_8,
        error=0,
        samples=0,
        branches={
            ValueCondition(column="Experience", value="HIGH"): Tree(prediction=c2, error=0, samples=0),
            ValueCondition(column="Experience", value="MID"): Tree(prediction=c1, error=0, samples=0),
        },
    )

    past_jobs_6 = Tree(
        prediction=p_past_jobs_6,
        error=0,
        samples=0,
        branches={
            RangeCondition(column="Past_Jobs", value=8, less=True): past_jobs_8,
            RangeCondition(column="Past_Jobs", value=8, less=False): Tree(prediction=c2, error=0, samples=0),
        },
    )

    degree_no = Tree(
        prediction=p_degree,
        error=0,
        samples=0,
        branches={
            RangeCondition(column="Past_Jobs", value=6, less=True): Tree(prediction=c1, error=0, samples=0),
            RangeCondition(column="Past_Jobs", value=6, less=False): past_jobs_6,
        },
    )

    reference = Tree(
        prediction=p_ref,
        error=0,
        samples=0,
        branches={
            ValueCondition(column="Degree", value="YES"): Tree(prediction=c2, error=0, samples=0),
            ValueCondition(column="Degree", value="NO"): degree_no,
        },
    )
    print("Reference")
    print(reference.pretty_print())
    assert model == reference


def test_basic():
    path = Path("datasets/classification/baloons.csv")
    x, y, class_names = read_classification_dataset(path, reencode_y=False)
    sk_model = TreeClassifier(min_samples_split=1, splitter="best")
    sk_model.fit(x, y)

    print("Trained")
    print(sk_model.pretty_print())

    model: Tree = sk_model.model_
    assert model.n_leafs() == 4
    assert model.n_nodes() == 7

    c1, c2 = np.array([1.0, 0]), np.array([0, 1.0])
    p_ref = np.array([0.375, 0.625])
    p_color = np.array([0.75, 0.25])
    p_age = np.array([0.5, 0.5])
    color_red = Tree(
        prediction=p_age,
        error=0,
        samples=0,
        branches={
            ValueCondition(column="Age", value="Adult"): Tree(prediction=c1, error=0, samples=0),
            ValueCondition(column="Age", value="Children"): Tree(prediction=c2, error=0, samples=0),
        },
    )

    stretch_yes = Tree(
        prediction=p_color,
        error=0,
        samples=0,
        branches={
            ValueCondition(column="Color", value="Yellow"): Tree(prediction=c1, error=0, samples=0),
            ValueCondition(column="Color", value="Red"): color_red,
        },
    )

    reference = Tree(
        prediction=p_ref,
        error=0,
        samples=0,
        branches={
            ValueCondition(column="Stretchs", value="No"): Tree(prediction=c2, error=0, samples=0),
            ValueCondition(column="Stretchs", value="Yes"): stretch_yes,
        },
    )
    print("Reference")
    print(reference.pretty_print())
    assert model == reference


if __name__ == "__main__":
    test_jobs()
    test_basic()
