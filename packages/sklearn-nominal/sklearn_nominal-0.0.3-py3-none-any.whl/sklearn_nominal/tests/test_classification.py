from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

from sklearn_nominal.tests.models_classification import (
    get_cn2_classifier,
    get_naive_bayes,
    get_nominal_tree_classifier,
    get_oner_classifier,
    get_prism_classifier,
    get_sklearn_tree,
    get_zeror_classifier,
)

from .utils import get_model_complexity


def read_classification_dataset(path: Path, reencode_y=True):
    df = pd.read_csv(path)
    x = df.iloc[:, :-1]
    if reencode_y:
        le = LabelEncoder().fit(df.iloc[:, -1])
        y = le.transform(df.iloc[:, -1])
        classes = le.classes_
    else:
        y = df.iloc[:, -1].values
        classes = np.unique(y)
    # y = y.reshape(len(y),1)
    return x, y, classes


def train_test_classification_model(model_name: str, model_generator, dataset: Path):
    dataset_name = dataset.name.split(".")[0]
    x, y, class_names = read_classification_dataset(dataset)
    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, stratify=y, shuffle=True, random_state=0)

    model = model_generator(x_train, len(class_names))
    model.fit(x_train, y_train)

    y_pred_train = model.predict(x_train)
    score_train = accuracy_score(y_train, y_pred_train)
    y_pred_test = model.predict(x_test)
    score_test = accuracy_score(y_test, y_pred_test)
    return {
        "Dataset": dataset_name,
        "Model": model_name,
        "Train": score_train,
        "Test": score_test,
        "Complexity": get_model_complexity(model),
    }


path = Path("datasets/classification")
dataset_names = [
    "2_clases_simple.csv",
    "6_clases_dificil.csv",
    "diabetes.csv",
    "ecoli.csv",
    "golf_classification_nominal.csv",
    "golf_classification_numeric.csv",
    "seeds.csv",
    "sonar.csv",
    "titanic.csv",
]


def check_results(at_least_percent: float, results: dict[str, dict[str, float]], reference_model: str):
    results = results.copy()
    reference = results.pop(reference_model)

    for model_name, model_results in results.items():
        for set in ["Train", "Test"]:
            reference_score = reference[set]
            model_score = model_results[set]
            percent = model_score / reference_score
            alp = at_least_percent[model_name]
            message = f"{set} accuracy of {model_name} ({model_score:.2g})"
            message += f"should be at least {alp * 100:.2g}% of \
                {reference_model} ({reference_score:.2g})"
            message += f"on dataset {reference['Dataset']}, was only {percent * 100:.2g}%."
            assert alp <= percent, message


def test_performance_similar_sklearn(at_least_percent=0.8, dataset_names=dataset_names):
    models = {
        "naivebayes": get_naive_bayes(smoothing=0.01),
        "sklearn.tree": get_sklearn_tree,
        "prism": get_prism_classifier(),
        "cn2[entropy]": get_cn2_classifier("entropy"),
        "cn2[gini]": get_cn2_classifier("gini"),
        "tree[entropy]": get_nominal_tree_classifier("entropy"),
        "tree[gini]": get_nominal_tree_classifier("gini"),
        "tree[gain_ratio]": get_nominal_tree_classifier("gain_ratio"),
        "zeror": get_zeror_classifier,
        "oner[entropy]": get_oner_classifier("entropy"),
        "oner[gain_ratio]": get_oner_classifier("gain_ratio"),
    }
    at_least_percent = {
        "naivebayes": 0.3,
        "prism": 0.75,
        "cn2[entropy]": 0.50,
        "cn2[gini]": 0.50,
        "tree[entropy]": 0.8,
        "tree[gini]": 0.8,
        "tree[gain_ratio]": 0.8,
        "zeror": 0.1,
        "oner[entropy]": 0.2,
        "oner[gain_ratio]": 0.2,
    }
    datasets = [path / name for name in dataset_names]
    results_all = []
    for dataset in tqdm(datasets, desc="Datasets"):
        results = {k: train_test_classification_model(k, m, dataset) for k, m in models.items()}
        check_results(at_least_percent, results, "sklearn.tree")
        results_all += list(results.values())
    with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.width", 120):
        print(pd.DataFrame.from_records(results_all))


if __name__ == "__main__":
    test_performance_similar_sklearn()
