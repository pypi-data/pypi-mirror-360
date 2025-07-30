import numpy as np
import pandas as pd

from sklearn_nominal.backend.core import Dataset
from sklearn_nominal.backend.pandas import PandasDataset

DEFAULT_BACKEND = "pandas"


def pyarrow_backed_pandas(x: pd.DataFrame) -> pd.DataFrame:
    import pyarrow as pa

    pa_table = pa.Table.from_pydict(x)
    df = pa_table.to_pandas(types_mapper=pd.ArrowDtype)
    return df


def make_dataset(backend: str, x: np.ndarray, y: np.ndarray, columns: list[str], dtype) -> Dataset:
    if backend == "pandas":
        x = pd.DataFrame(x, columns=columns)
        if dtype is not None:
            x = x.astype(dtype)
        assert isinstance(y, np.ndarray)
        df = PandasDataset(x, y)
        return df
    if backend == "pandas_pyarrow":
        x = pd.DataFrame(x, columns=columns)
        if dtype is not None:
            x = x.astype(dtype)
        assert isinstance(y, np.ndarray)
        x = pyarrow_backed_pandas(x)
        return PandasDataset(x, y)
    else:
        raise ValueError(f"Backend {backend} not supported")
