.. project-template documentation master file, created by
   sphinx-quickstart on Mon Jan 18 14:44:12 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:notoc:

#########################################################################################################
`scikit_nominal`: Tree, NaiveBayes, and Rule (PRISM,CN2,OneR) models with nominal features support
#########################################################################################################

**Date**: |today| **Version**: |version|

.. figure:: _static/img/logo.png
   :scale: 25 %
   :alt: scikit_nominal logo

**Useful links**:
`Source Repository <https://github.com/facundoq/sklearn_nominal>`__ |
`Issues & Ideas <https://github.com/facundoq/sklearn_nominal/issues>`__ |

This is the documentation for  `scikit_nominal`, a library that includes drop-in replacements for `scikit-learn` models and a few additional ones. Nonetheless, the models were designed with compliance with the `scikit-learn` API in mind. For example, the `sklearn_nominal.TreeClassifier` model can be used as drop-in replacement for `sklearn.tree.TreeClassifier` without any code changes, and other models follow the `fit`, `predict`, etc, API of `scikit-learn`.




.. grid:: 2
    :gutter: 4
    :padding: 2 2 2 2
    :class-container: sd-text-center

    .. grid-item-card:: Getting started
        :img-top: _static/img/index_getting_started.svg
        :class-card: intro-card
        :shadow: md

        How to install `sklearn_nominal`, load up a dataset and train/test your first model.

        +++

        .. button-ref:: quick_start
            :ref-type: ref
            :click-parent:
            :color: secondary
            :expand:

            To the getting started guideline

    .. grid-item-card::  API reference
        :img-top: _static/img/index_api.svg
        :class-card: intro-card
        :shadow: md

        Detailed reference of our model's API.
        +++

        .. button-ref:: api
            :ref-type: ref
            :click-parent:
            :color: secondary
            :expand:

            To the reference guide


.. toctree::
    :maxdepth: 3
    :hidden:
    :titlesonly:

    quick_start
    api
