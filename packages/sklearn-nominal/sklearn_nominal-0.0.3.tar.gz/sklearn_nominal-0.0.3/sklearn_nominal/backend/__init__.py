import numpy as np
import pandas as pd

type Output = np.ndarray
type Input = pd.DataFrame | np.ndarray
type InputSample = pd.Series
type ColumnID = int

from .conditions import Condition, RangeCondition, ValueCondition

from .core import ColumnType, Dataset
from .pandas import PandasDataset


from .factory import make_dataset
