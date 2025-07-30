from sklearn_nominal.backend.core import Dataset
from sklearn_nominal.rules.model import RuleModel
from sklearn_nominal.shared.global_error import DefaultSplitter
from sklearn_nominal.shared.target_error import TargetError


class OneR:
    def __init__(self, error_function: TargetError):
        self.error_function = error_function
        self.splitter = DefaultSplitter(error_function)

    def fit(self, d: Dataset):
        def pred(d: Dataset):
            return self.error_function.prediction(d)

        # choose the best column to split the dataset and generate predictions
        e = self.splitter.split_columns(d)

        if e is None:
            # No column available; no rules, use default prediction
            rules = []
        else:
            # Generate rules for best column based on its values
            rules = [(e, pred(p)) for e, p in zip(e.conditions, e.partition)]

        return RuleModel(rules, default_prediction=pred(d))
