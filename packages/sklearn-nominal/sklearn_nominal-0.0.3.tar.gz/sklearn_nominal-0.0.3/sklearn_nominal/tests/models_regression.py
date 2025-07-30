import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.discriminant_analysis import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

from sklearn_nominal.sklearn.rule_cn2 import CN2Regressor
from sklearn_nominal.sklearn.rule_oner import OneRRegressor
from sklearn_nominal.sklearn.rule_zeror import ZeroRRegressor
from sklearn_nominal.sklearn.tree_regression import TreeRegressor


def get_zeror(criterion: str):
    def build(x: pd.DataFrame, y: np.ndarray):
        model = ZeroRRegressor(criterion)
        return model

    return build


def get_oner(criterion: str):
    def build(x: pd.DataFrame, y: np.ndarray):
        model = OneRRegressor(criterion)
        return model

    return build


def get_cn2(criterion: str):
    def build(x: pd.DataFrame, y: np.ndarray):
        n, m = x.shape
        max_rule_length = min(max(int(np.log(m) * 3), 5), 30)
        min_rule_support = max(2, int(np.log(n) * (0.05 / y.std())))
        max_error_per_rule = 0.99 * y.std()

        return CN2Regressor(
            criterion=criterion,
            max_rule_length=max_rule_length,
            min_rule_support=min_rule_support,
            max_error_per_rule=max_error_per_rule,
            max_rules=max(5, n // 10),
        )

    return build


def get_tree(criterion: str):
    def build(x: pd.DataFrame, y: np.ndarray):
        n, m = x.shape
        max_height = min(max(int(np.log(m) * 3), 5), 30)
        min_samples_leaf = max(2, int(np.log(n) * (0.05 / y.std())))
        min_samples_split = min_samples_leaf
        min_error_improvement = 0.001 * y.std()

        return TreeRegressor(
            criterion=criterion,
            max_depth=max_height,
            min_samples_leaf=min_samples_leaf,
            min_samples_split=min_samples_split,
            min_error_decrease=min_error_improvement,
            splitter="best",
        )

    return build


def get_sklearn_pipeline(x: pd.DataFrame, model):
    numeric_features = x.select_dtypes(include=["int64", "float64"]).columns
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_features = x.select_dtypes(exclude=["int64", "float64"]).columns
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])


def get_sklearn_tree(x: pd.DataFrame, y: np.ndarray):
    n, m = x.shape
    max_height = min(max(int(np.log(m) * 3), 5), 30)
    min_samples_leaf = max(2, int(n * (0.05 / y.std())))
    min_samples_split = min_samples_leaf
    min_error_improvement = 0.001 * y.std()
    model = DecisionTreeRegressor(
        max_depth=max_height,
        min_samples_leaf=min_samples_leaf,
        min_samples_split=min_samples_split,
        min_impurity_decrease=min_error_improvement,
        criterion="squared_error",
    )
    return get_sklearn_pipeline(x, model)
