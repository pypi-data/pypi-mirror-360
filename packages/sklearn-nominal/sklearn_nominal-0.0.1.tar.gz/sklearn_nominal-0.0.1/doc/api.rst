.. _api:

#############
API Reference
#############


.. currentmodule:: sklearn_nominal

`scikit-learn` compatible classifiers
======================================

.. autosummary::
   :toctree: generated/
   :template: class.rst

   TreeClassifier
   NaiveBayesClassifier
   ZeroRClassifier
   OneRClassifier
   CN2Classifier
   PRISMClassifier

`scikit-learn` compatible regressors
=====================================

.. autosummary::
   :toctree: generated/
   :template: class.rst

   TreeRegressor
   ZeroRRegressor
   OneRRegressor
   CN2Regressor

Base classes 
============================


`BaseTree` defines the pruning parameters for both `TreeRegressor`
and `TreeClassifier`. `Nominal*` classes define base methods to support inference with nominal attributes

Same thing with 

.. autosummary::
   :toctree: generated/
   :template: class.rst

   sklearn.tree_base.BaseTree
   sklearn.nominal_model.NominalModel
   sklearn.nominal_model.NominalClassifier
   sklearn.nominal_model.NominalRegressor


`Dataset` classes
============================

In order to support nominal attributes, and facilitate the implementation of various estimators, `sklearn_nominal` abstracts away the details of a dataset with the corresponding `Dataset` class and implementations, including many common method such as filtering datasets on attribute-value conditions. Currently, only a `pandas` backend is available, but future versions may include `polars` or pure `numpy` backends.


.. autosummary::
   :toctree: generated/
   :template: class.rst

   backend.Dataset
   backend.PandasDataset
   backend.Condition