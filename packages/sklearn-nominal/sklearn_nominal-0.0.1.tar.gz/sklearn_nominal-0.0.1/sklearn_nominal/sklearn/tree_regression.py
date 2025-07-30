import numpy as np
import pandas as pd
from scipy.odr import Output
from sklearn.base import BaseEstimator

from sklearn_nominal import shared, tree
from sklearn_nominal.backend import Input
from sklearn_nominal.backend.core import Dataset

from ..sklearn.nominal_model import NominalRegressor
from ..tree.pruning import PruneCriteria
from .tree_base import BaseTree


class TreeRegressor(NominalRegressor, BaseTree, BaseEstimator):
    """A decision tree regressor that mimics `scikit-learn`'s
    :class:`sklearn.tree.DecisionTreeRegressor` but adds support for nominal
    attributes.


    See also :class:`sklearn_nominal.sklearn.tree_base.BaseTree` for other common parameters.

    Parameters
    ----------
    criterion : {"std"}, default="std"
        The function to measure the error of a split. Supported criteria are
        currently only "std", for standard deviation (equivalent to root MSE), but in the future other error functions may be added.


    Attributes
    ----------
    classes_ : ndarray of shape (n_classes,) or list of ndarray
        The classes labels (single output problem),
        or a list of arrays of class labels (multi-output problem).

    n_classes_ : int or list of int
        The number of classes (for single output problems),

    n_features_in_ : int
        Number of features seen during :term:`fit`.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.

    n_outputs_ : int
        The number of outputs when ``fit`` is performed.

    tree_ : :class:`sklearn_nominal.tree.tree.Tree` instance
        The underlying :class:`sklearn_nominal.tree.tree.Tree` object.

    See Also
    --------
    BaseTree : base class for DecisionTreeRegressor.
    TreeClassifier : A decision tree classifier.

    Examples
    --------
    >>> import pandas as pd
    >>> def read_regression_dataset(url: str):
    >>>     df = pd.read_csv(url)
    >>>     x = df.iloc[:, :-1]
    >>>     y = df.iloc[:, -1]
    >>>     return x, y

    >>> dataset_name = "golf_classification"
    >>> url = "https://raw.githubusercontent.com/facundoq/facundoq.github.io/refs/>>> heads/master/datasets/regression/golf_regression_nominal.csv"

    >>> x, y = read_regression_dataset(url)
    >>> from sklearn_nominal import TreeRegressor
    >>> model = TreeRegressor(criterion="std", max_depth=4, min_samples_leaf=1, min_error_decrease=1e-16)
    >>> from sklearn.metrics import mean_absolute_error
    >>> model.fit(x, y)
    >>> y_pred = model.predict(x)
    >>> print(f"{mean_absolute_error(y, y_pred):.2f}")
    0.07

    """

    def __init__(
        self,
        criterion="std",
        splitter="best",
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_error_decrease=1e-16,
        backend="pandas",
    ):
        super().__init__(
            criterion=criterion,
            splitter=splitter,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_error_decrease=min_error_decrease,
            backend=backend,
        )

    def make_model(self, d: Dataset):
        error = self.build_error(self.criterion)
        column_penalization = self.build_attribute_penalizer()
        scorers = self.build_splitter(error, column_penalization)
        scorer = shared.DefaultSplitter(error, scorers)
        prune_criteria = self.build_prune_criteria(d)
        trainer = tree.BaseTreeTrainer(scorer, prune_criteria)
        return trainer
