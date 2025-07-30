"""
============================
Nominal classifiers comparison
============================

Compare scikit compatible classifiers available in sklearn_nominal
"""

import pandas as pd
from sklearn.metrics import accuracy_score

from sklearn_nominal import (
    CN2Classifier,
    NaiveBayesClassifier,
    OneRClassifier,
    PRISMClassifier,
    TreeClassifier,
    ZeroRClassifier,
)


def read_classification_dataset(url: str):
    df = pd.read_csv(url)
    x = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    return x, y, y.unique()


dataset_name = "golf_classification"
url_base = (
    "https://raw.githubusercontent.com/facundoq/facundoq.github.io/refs/heads/master/"
)
url = url_base + "datasets/classification/golf_classification_numeric.csv"
x, y, class_names = read_classification_dataset(url)

models = [
    TreeClassifier(),
    TreeClassifier(criterion="gini"),
    TreeClassifier(criterion="gain_ratio"),
    PRISMClassifier(min_rule_support=1),
    CN2Classifier(min_rule_support=1),
    OneRClassifier(),
    ZeroRClassifier(),
    NaiveBayesClassifier(),
]
results = []
for model in models:
    model.fit(x, y)
    y_pred = model.predict(x)
    score = accuracy_score(y, y_pred)

    print("===" * 20)
    print(f"Model {model}")
    print(model.pretty_print(class_names))
    print("---" * 20)
    print(f"Accuracy: {score:.3f}")
    print("===" * 20)
    print()
    result = {"model": str(model), "accuracy": score, "complexity": model.complexity()}
    results.append(result)

results_df = pd.DataFrame.from_records(results)
results_df.to_csv("doc/classifier_comparison.csv", float_format="%4g")
print(results_df.to_markdown())
