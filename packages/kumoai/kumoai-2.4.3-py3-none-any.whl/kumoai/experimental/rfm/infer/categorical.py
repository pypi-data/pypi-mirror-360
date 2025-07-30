import pandas as pd
from kumoapi.typing import Dtype, Stype


def contains_categorical(
    ser: pd.Series,
    column_name: str,
    dtype: Dtype,
) -> bool:

    if not Stype.categorical.supports_dtype(dtype):
        return False

    if Dtype == Dtype.bool:
        return True

    ser = ser.sample(n=1000, random_state=42) if len(ser) > 1000 else ser
    ser = ser.dropna()

    num_unique = ser.nunique()

    if num_unique < 50:
        return True

    if dtype.is_string():
        return num_unique / len(ser) <= 0.5

    return num_unique / len(ser) <= 0.2
