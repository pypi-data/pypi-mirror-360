from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from sklearn_nominal.sklearn.tree_regression import TreeRegressor
from sklearn_nominal.tests.models_regression import (
    get_cn2,
    get_oner,
    get_sklearn_tree,
    get_tree,
    get_zeror,
)

from .utils import get_model_complexity


def read_regression_dataset(path: Path):
    df = pd.read_csv(path)
    x = df.iloc[:, :-1]
    y = df.iloc[:, -1].to_numpy().reshape(-1, 1)
    return x, y


def train_test_regression_model(model_name: str, model_generator, dataset: Path):
    dataset_name = dataset.name.split(".")[0]
    x, y = read_regression_dataset(dataset)
    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, shuffle=True, random_state=0)
    model = model_generator(x_train, y_train)
    model.fit(x_train, y_train)

    y_pred_train = model.predict(x_train)
    score_train = mean_absolute_error(y_train, y_pred_train)
    y_pred_test = model.predict(x_test)
    score_test = mean_absolute_error(y_test, y_pred_test)
    return {
        "Model": model_name,
        "Dataset": dataset_name,
        "Train": score_train,
        "Test": score_test,
        "Complexity": get_model_complexity(model),
    }


path = Path("datasets/regression")
dataset_names = [
    "golf_regression_nominal.csv",
    "study_regression_small.csv",
    "study_regression_2d_small.csv",
    "who_no_missing_numeric.csv",
]


def check_results(at_most_percent: float, results: dict[str, dict[str, float]], reference_model: str):
    results = results.copy()
    reference = results.pop(reference_model)

    for model_name, model_results in results.items():
        for set in ["Train", "Test"]:
            reference_score = reference[set]
            model_score = model_results[set]
            percent = model_score / reference_score
            amp = at_most_percent[model_name]
            message = f"{set} score of {model_name} ({model_score:.2f}) should be at most {amp * 100:.2f}% of sklearn.tree ({reference_score:.2f}) on dataset {reference['Dataset']}, was {percent * 100:.2f}% instead."  # noqa: E501
            assert percent <= amp, message
            # f"{set} score of {model_name} ({model_score:.2g}) should be at least {alp*100:.2g}% of {reference_model} ({reference_score:.2g}) on dataset {reference["Dataset"]}, was only {percent*100:.2g}%."  # noqa: E501


def test_performance_similar_sklearn(at_most_percent=0.8, dataset_names=dataset_names):
    models = {
        "sklearn.tree": get_sklearn_tree,
        "cn2[std]": get_cn2("std"),
        "tree[std]": get_tree("std"),
        "oner[std]": get_oner("std"),
        "zeror[std]": get_zeror("std"),
    }
    at_most_percent = {
        "cn2[std]": 4,
        "tree[std]": 4,
        "oner[std]": 5.0,
        "zeror[std]": 5.0,
    }
    datasets = [path / name for name in dataset_names]
    results_all = []
    for dataset in tqdm(datasets, desc="Datasets"):
        results = {k: train_test_regression_model(k, m, dataset) for k, m in models.items()}
        check_results(at_most_percent, results, "sklearn.tree")
        results_all += list(results.values())
    with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.width", 120):
        print(pd.DataFrame.from_records(results_all))


if __name__ == "__main__":
    test_performance_similar_sklearn()
