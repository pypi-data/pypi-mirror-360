import abc

import numpy as np
import pandas as pd
import scipy
from pandas import DataFrame
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.calibration import LabelEncoder
from sklearn.exceptions import NotFittedError
from sklearn.utils import compute_class_weight, validation
from sklearn.utils._tags import (
    ClassifierTags,
    RegressorTags,
    Tags,
    TargetTags,
    TransformerTags,
    get_tags,
)
from sklearn.utils.multiclass import check_classification_targets
from sklearn.utils.validation import _check_y, validate_data

from sklearn_nominal.backend import Input, Output
from sklearn_nominal.backend.factory import make_dataset
from sklearn_nominal.shared.target_error import TargetError

from .. import shared, tree
from ..backend.core import Dataset, Model
from ..backend.pandas import PandasDataset


def atleast_2d(x):
    x = np.asanyarray(x)
    if x.ndim == 0:
        result = x.reshape(1, 1)
    elif x.ndim == 1:
        result = x[:, np.newaxis]
    else:
        result = x
    return result


class NominalModel(metaclass=abc.ABCMeta):
    check_parameters = {"dtype": None}

    def __init__(self, backend: str = "pandas", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = backend

    def complexity(self):
        self.check_is_fitted()
        return self.model_.complexity()

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.non_deterministic = False
        tags.input_tags.sparse = False
        tags.input_tags.allow_nan = True
        tags.input_tags.string = True
        return tags

    def pretty_print(self, class_names: list[str] = None):
        self.check_is_fitted()
        return self.model_.pretty_print(class_names=class_names)

    def check_is_fitted(self) -> bool:
        validation.check_is_fitted(self)
        if not self.is_fitted_:
            raise NotFittedError()

    def get_dtypes(self, x):
        if isinstance(x, pd.DataFrame):
            dtypes = x.dtypes.to_dict()
        else:
            dtypes = None
        return dtypes

    def get_feature_names(self):
        if not hasattr(self, "feature_names_in_"):
            return None
        else:
            return self.feature_names_in_

    def set_dtypes(self, x):
        if isinstance(x, pd.DataFrame):
            self.dtypes_ = x.dtypes
        elif isinstance(x, np.ndarray) or scipy.sparse.issparse(x):
            assert len(x.shape) == 2, f"Expected 2d input, actual shape {x.shape}"
            self.dtypes_ = [x.dtype] * x.shape[1]
        else:
            raise ValueError(f"Only pd.Dataframe or np.ndarray supported, received: {x}")

    def set_model(self, model):
        self.model_: Model = model
        self.is_fitted_ = True


class NominalUnsupervisedModel(NominalModel):
    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.target_tags.single_output = False
        tags.target_tags.required = False
        return tags


class NominalSupervisedModel(NominalModel):
    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.target_tags.single_output = False
        tags.target_tags.required = True
        return tags

    def validate_data_predict(self, x):
        dtypes = self.get_dtypes(x)
        self.check_is_fitted()
        x = validate_data(
            self,
            x,
            reset=False,
            dtype=None,
            ensure_all_finite=False,
            accept_sparse=False,
        )
        n = len(x)
        if n == 0:
            raise ValueError(f"Input contains 0 samples.")
        df = pd.DataFrame(x, columns=self.get_feature_names())
        if dtypes is not None:
            df = df.astype(dtypes)
        return df


class NominalClassifier(NominalSupervisedModel):
    def __init__(self, class_weight=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.class_weight = class_weight

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.estimator_type = "classifier"
        tags.classifier_tags = ClassifierTags()
        tags.classifier_tags.multi_class = True

        return tags

    def validate_data_fit_classification(self, x, y) -> Dataset:
        check_classification_targets(y)
        dtypes = self.get_dtypes(x)
        x, y = validate_data(
            self,
            x,
            y,
            reset=True,
            multi_output=True,
            y_numeric=False,
            ensure_all_finite=False,
            dtype=None,
            accept_sparse=False,
        )
        self.classes_ = np.unique(y)
        if len(self.classes_) < 2:
            raise ValueError("Can't train classifier with one class.")
        # dtype = x_original.dtype
        class_weight = self.get_class_weights(y)
        dataset = make_dataset(self.backend, x, self.get_y(y), self.get_feature_names(), dtypes)
        return dataset, class_weight

    def get_y(self, y):
        y = _check_y(y, multi_output=True, y_numeric=False, estimator=self)
        # TODO make pure numpy
        self.le_ = LabelEncoder()
        y = self.le_.fit_transform(y)
        return y

    @abc.abstractmethod
    def make_model(self, d: Dataset, class_weight: np.ndarray):
        pass

    def fit(self, x: Input, y: Output):
        d, class_weight = self.validate_data_fit_classification(x, y)

        trainer = self.make_model(d, class_weight)
        model = trainer.fit(d)
        self.set_model(model)
        return self

    def get_class_weights(self, y):
        return compute_class_weight(class_weight=self.class_weight, classes=self.classes_, y=y)

    def build_error(self, criterion: str, class_weight: np.array) -> TargetError:
        classes = len(class_weight)
        errors = {
            "entropy": shared.EntropyError(classes, class_weight),
            "gini": shared.GiniError(classes, class_weight),
            "gain_ratio": shared.EntropyError(classes, class_weight),
        }
        if criterion not in errors.keys():
            raise ValueError(f"Unknown error function {criterion}")
        return errors[criterion]

    def predict_proba(self, x: Input) -> Output:
        self.check_is_fitted()

        # print("nominal predict proba",self.model_)
        x = self.validate_data_predict(x)
        # print("nominal predict proba after validate",x)
        y = self.model_.predict(x)
        # print("nominal predict proba after predict",y,self.model_)
        return y

    def predict(self, x: Input) -> Output:
        p = self.predict_proba(x)
        c = p.argmax(axis=1)
        y = self.le_.inverse_transform(c)
        return y


class NominalRegressor(NominalSupervisedModel, RegressorMixin):
    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.estimator_type = "regressor"
        tags.regressor_tags = RegressorTags()
        tags.target_tags.required = True
        return tags

    def validate_data_fit_regression(self, x, y) -> Dataset:
        dtypes = self.get_dtypes(x)
        x, y = validate_data(
            self,
            x,
            y,
            reset=True,
            multi_output=True,
            y_numeric=True,
            ensure_all_finite=False,
            dtype=None,
            accept_sparse=False,
        )
        y = _check_y(y, multi_output=True, y_numeric=True, estimator=self)
        self._y_original_shape = y.shape
        y = atleast_2d(y)
        return make_dataset(self.backend, x, y, self.get_feature_names(), dtypes)

    def build_error(self, criterion: str):
        errors = {
            "std": shared.DeviationError(),
        }
        if criterion not in errors.keys():
            raise ValueError(f"Unknown error function {criterion}")
        return errors[criterion]

    def predict(self, x: Input):
        self.check_is_fitted()
        x = self.validate_data_predict(x)
        y = self.model_.predict(x)
        if len(self._y_original_shape) == 1:
            y = y.squeeze()
        return y

    @abc.abstractmethod
    def make_model(self, d: Dataset):
        pass

    def fit(self, x: Input, y: Output):
        d = self.validate_data_fit_regression(x, y)
        trainer = self.make_model(d)
        model = trainer.fit(d)
        self.set_model(model)
        return self
