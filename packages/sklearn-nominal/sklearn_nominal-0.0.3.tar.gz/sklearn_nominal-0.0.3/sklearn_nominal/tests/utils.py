from sklearn.pipeline import Pipeline
from sklearn.tree import BaseDecisionTree, _tree

from sklearn_nominal.sklearn.nominal_model import NominalSupervisedModel


def get_model_complexity(model: NominalSupervisedModel | BaseDecisionTree) -> int:
    if isinstance(model, NominalSupervisedModel):
        return model.model_.complexity()
    elif isinstance(model, Pipeline):
        estimator_model = model[-1]
        if isinstance(estimator_model, BaseDecisionTree):
            tree: _tree.Tree = model[-1].tree_
            return tree.n_leaves

    raise ValueError(f"Unsupported model {model}")
