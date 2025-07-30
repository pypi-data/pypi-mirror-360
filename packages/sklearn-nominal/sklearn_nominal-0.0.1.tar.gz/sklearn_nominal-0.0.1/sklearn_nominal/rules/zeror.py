from sklearn_nominal.backend.core import Dataset
from sklearn_nominal.rules.model import RuleModel
from sklearn_nominal.shared.target_error import TargetError


class ZeroR:
    def __init__(self, error_function: TargetError):
        self.error_function = error_function

    def fit(self, d: Dataset):
        return RuleModel([], default_prediction=self.error_function.prediction(d))
