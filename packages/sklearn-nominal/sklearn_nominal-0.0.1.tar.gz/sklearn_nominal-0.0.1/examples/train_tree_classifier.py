"""
============================
Train a TreeClassifier
============================

Train and evaluate a TreeClassifier on golf weather data
"""

import pandas as pd
from sklearn.metrics import accuracy_score

from sklearn_nominal import TreeClassifier


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

# custom hiperparameters
model = TreeClassifier(
    criterion="entropy", max_depth=4, min_samples_leaf=1, min_error_decrease=1e-16
)

# Fit and evaluate on training data
model.fit(x, y)
y_pred = model.predict(x)
print(f"Dataset {dataset_name:40} accuracy: {accuracy_score(y, y_pred) * 100:.2f}%")

# Print tree
print(model.pretty_print(class_names=class_names))

# Export tree as png
model.export_image("examples/tree.png", title=f"{model}", class_names=class_names)
