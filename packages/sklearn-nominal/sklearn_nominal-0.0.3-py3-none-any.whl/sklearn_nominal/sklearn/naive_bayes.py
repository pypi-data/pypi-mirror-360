import numpy as np
from sklearn.base import BaseEstimator

from sklearn_nominal.backend.core import Dataset
from sklearn_nominal.backend.factory import DEFAULT_BACKEND
from sklearn_nominal.bayes.trainer import NaiveBayesTrainer
from sklearn_nominal.sklearn.nominal_model import NominalClassifier


class NaiveBayesClassifier(NominalClassifier, BaseEstimator):
    """A NaiveBayesClassifier that mimics `scikit-learn`'s
    :class:`sklearn.tree.GaussianNB` but adds support for nominal
    attributes with categorical distributions.

    Parameters
    ----------
    smoothing : float, default=0.0
        The laplace smoothing factor categorical distributions. This value will be added to the count of each value to generate a smoothed categorical distribution. The default value, 0.0, indicates no smoothing.

    class_weight : dict, list of dict or "balanced", default=None
        Weights associated with classes in the form ``{class_label: weight}``.
        If None, all classes are supposed to have weight one.

        The "balanced" mode uses the values of y to automatically adjust
        weights inversely proportional to class frequencies in the input data
        as ``n_samples / (n_classes * np.bincount(y))``

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

    model_ : :class:`sklearn_nominal.bayes.NaiveBayes` instance
        The underlying NaiveBayes that actually holds the distribution parameters and can perform inference.

    See Also
    --------
    TreeClassifier : A decision tree classifier.

    Notes
    -----

    The :meth:`predict` method operates using the :func:`numpy.argmax`
    function on the outputs of :meth:`predict_proba`. This means that in
    case the highest predicted probabilities are tied, the classifier will
    predict the tied class with the lowest index in :term:`classes_`.

    Examples
    --------
    >>> from sklearn.datasets import fetch_openml
    >>> df = fetch_openml("credit-g",version=2).frame
    >>> x,y = df.iloc[:,0:-1], df.iloc[:,-1]
    >>>
    >>> from sklearn_nominal import NaiveBayesClassifier
    >>> model = NaiveBayesClassifier(smoothing = 0.01)
    >>> model.fit(x,y)
    >>>
    >>> from sklearn.metrics import accuracy_score
    >>> y_pred = model.predict(x)
    >>> print(accuracy_score(y,y_pred))
    ... 0.787
    """

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.classifier_tags.poor_score = True
        return tags

    def __init__(self, smoothing=0.0, backend=DEFAULT_BACKEND, class_weight=None):
        super().__init__(backend=backend, class_weight=class_weight)
        self.smoothing = smoothing

    def make_model(self, d: Dataset, class_weight: np.ndarray):
        return NaiveBayesTrainer(class_weight, smoothing=self.smoothing)
