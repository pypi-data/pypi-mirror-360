import re

import pandas as pd
from kumoapi.typing import Dtype, Stype


def contains_timestamp(ser: pd.Series, column_name: str, dtype: Dtype) -> bool:
    if not Stype.timestamp.supports_dtype(dtype):
        return False

    if dtype.is_timestamp():
        return True

    column_name = column_name.lower()

    match = re.search(
        ('(^|_)(date|datetime|dt|time|timedate|timestamp|ts|'
         'created|updated)(_|$)'),
        column_name,
        re.IGNORECASE,
    )

    if match is not None:
        return True

    ser = ser.sample(n=1000, random_state=42) if len(ser) > 1000 else ser
    ser = ser.dropna()
    ser = ser[ser.str.strip() != '']

    if len(ser) == 0:
        return False

    return pd.to_datetime(ser, errors='coerce').notna().all()
