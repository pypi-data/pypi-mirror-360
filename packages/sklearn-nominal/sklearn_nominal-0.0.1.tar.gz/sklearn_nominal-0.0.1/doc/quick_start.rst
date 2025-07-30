.. _quick_start:

###############
Getting started
###############


Installing `sklearn_nominal`
===================================================

`sklearn_nominal` is provided as a pip package. To install simply use:

.. prompt:: bash $

  pip install sklearn_nominal

Or if using `uv`:

.. prompt:: bash $

  uv add sklearn_nominal


Fitting and evaluating a nominal model
----------------------------------------

This code is the same as with any other `scikit-learn` model:

.. literalinclude :: ../examples/train_tree_classifier.py
   :language: python

In this case, we can inspect the tree that uses the nominal attributes directly afterwards:

.. figure:: ../examples/tree.png
   :scale: 50 %
   :alt: resulting tree

   Tree generated after training on the Golf dataset.


Comparing nominal classifiers
----------------------------------------

We can compare the classifiers in terms of their accuracy for the same task.
We can also `pretty_print` each to visualize their differences.

.. literalinclude :: ../examples/compare_classifiers.py
   :language: python


The results can be compared in this table:

.. csv-table:: Classifier Comparison
   :file: classifier_comparison.csv
   :widths: 5,65,15,15
   :header-rows: 1
