from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import pyarrow as pa
from kumoapi.typing import Dtype, Stype
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_list_like,
    is_object_dtype,
)

from kumoai.experimental.rfm.infer import (
    contains_categorical,
    contains_id,
    contains_multicategorical,
    contains_timestamp,
)

# Maximum number of rows to check for dtype inference in object columns
_MAX_NUM_ROWS_FOR_DTYPE_INFERENCE = 100

# Mapping from pandas/numpy dtypes to Kumo Dtypes
PANDAS_TO_DTYPE: Dict[Any, Dtype] = {
    np.dtype('bool'): Dtype.bool,
    pd.BooleanDtype(): Dtype.bool,
    pa.bool_(): Dtype.bool,
    np.dtype('byte'): Dtype.int32,
    pd.UInt8Dtype(): Dtype.int32,
    np.dtype('int16'): Dtype.int32,
    pd.Int16Dtype(): Dtype.int32,
    np.dtype('int32'): Dtype.int32,
    pd.Int32Dtype(): Dtype.int32,
    np.dtype('int64'): Dtype.int64,
    pd.Int64Dtype(): Dtype.int64,
    np.dtype('float32'): Dtype.float32,
    pd.Float32Dtype(): Dtype.float32,
    np.dtype('float64'): Dtype.float64,
    pd.Float64Dtype(): Dtype.float64,
    np.dtype('object'): Dtype.string,
    pd.StringDtype(storage='python'): Dtype.string,
    pd.StringDtype(storage='pyarrow'): Dtype.string,
    pa.string(): Dtype.string,
    pa.binary(): Dtype.binary,
    np.dtype('datetime64[ns]'): Dtype.date,
    np.dtype('timedelta64[ns]'): Dtype.timedelta,
    pa.list_(pa.float32()): Dtype.floatlist,
    pa.list_(pa.int64()): Dtype.intlist,
    pa.list_(pa.string()): Dtype.stringlist,
}

# Mapping from Kumo Dtype to dtype families
DTYPE_TO_FAMILY: Dict[Dtype, str] = {
    # Number family - includes booleans, integers, floats, and numeric lists
    Dtype.byte:
    "number",
    Dtype.int:
    "number",
    Dtype.int16:
    "number",
    Dtype.int32:
    "number",
    Dtype.int64:
    "number",
    Dtype.float:
    "number",
    Dtype.float32:
    "number",
    Dtype.float64:
    "number",

    # String family - includes text and string lists
    Dtype.string:
    "string",
    Dtype.stringlist:
    "string",

    # Other family - includes binary, dates, and time-related types
    Dtype.bool:
    "other",
    Dtype.floatlist:
    "other",
    Dtype.intlist:
    "other",
    Dtype.binary:
    "other",
    Dtype.date:
    "other",
    Dtype.time:
    "other",
    Dtype.timedelta:
    "other",
    Dtype.unsupported:
    "other",
}


def dtype_to_family(dtype: Dtype) -> str:
    """Convert a Kumo Dtype to its dtype family.

    Args:
        dtype: The Kumo Dtype to convert

    Returns:
        The dtype family as a string: "number", "string", or "other"

    Raises:
        KeyError: If the dtype is not found in the mapping
    """
    return DTYPE_TO_FAMILY[dtype]


def to_dtype(dtype: Any, ser: Optional[pd.Series] = None) -> Dtype:
    """Convert a pandas/numpy/pyarrow dtype to Kumo Dtype.

    Args:
        dtype: The dtype to convert
        ser: Optional pandas Series for additional type inference

    Returns:
        The corresponding Kumo Dtype
    """
    if is_datetime64_any_dtype(dtype):
        return Dtype.date
    if isinstance(dtype, pd.CategoricalDtype):
        return Dtype.string
    if is_object_dtype(dtype) and ser is not None and len(ser) > 0:
        if is_list_like(ser.iloc[0]):
            # the 0-th element might be an empty list or a list of N/A so
            # iterate over the first _MAX_NUM_ROWS_FOR_DTYPE_INFERENCE elements
            # to infer the dtype:
            for i in range(min(len(ser), _MAX_NUM_ROWS_FOR_DTYPE_INFERENCE)):
                # pd.isna can't be called on a list
                if (not isinstance(ser.iloc[i], list)
                        and not isinstance(ser.iloc[i], np.ndarray)
                        and pd.isna(ser.iloc[i])) or len(ser.iloc[i]) == 0:
                    continue
                elif isinstance(ser.iloc[i][0], float):
                    return Dtype.floatlist
                elif np.issubdtype(type(ser.iloc[i][0]), int):
                    return Dtype.intlist
                elif isinstance(ser.iloc[i][0], str):
                    return Dtype.stringlist
    return PANDAS_TO_DTYPE[dtype]


# TODO(blaz): refine and test
# Mapping from Kumo Dtype to Kumo Stype
DTYPE_TO_STYPE: Dict[Dtype, Stype] = {
    # Boolean types - always categorical
    Dtype.bool:
    Stype.categorical,

    # Integer types - numerical by default, but can be ID or categorical
    # based on context
    Dtype.int:
    Stype.numerical,
    Dtype.byte:
    Stype.numerical,
    Dtype.int16:
    Stype.numerical,
    Dtype.int32:
    Stype.numerical,
    Dtype.int64:
    Stype.numerical,

    # Float types - always numerical
    Dtype.float:
    Stype.numerical,
    Dtype.float32:
    Stype.numerical,
    Dtype.float64:
    Stype.numerical,

    # String types - text by default, but can be categorical based on context
    Dtype.string:
    Stype.text,

    # Datetime types - always timestamp
    Dtype.date:
    Stype.timestamp,
    Dtype.time:
    Stype.timestamp,
    Dtype.timedelta:
    Stype.timestamp,

    # List types - sequence
    Dtype.floatlist:
    Stype.sequence,
    Dtype.intlist:
    Stype.sequence,
    Dtype.stringlist:
    Stype.sequence,

    # Binary and unsupported types
    Dtype.binary:
    Stype.unsupported,
    Dtype.unsupported:
    Stype.unsupported,
}


# TODO(blaz): refine and test
def infer_stype(ser: pd.Series, column_name: str, dtype: Dtype) -> Stype:
    r"""Infers the semantic type of a column.

    Args:
        ser: A :class:`pandas.Series` to analyze.
        column_name: The name of the column (used for pattern matching)
        dtype: The data type.

    Returns:
        The semantic type.
    """
    if contains_id(ser, column_name, dtype):
        return Stype.ID

    if contains_timestamp(ser, column_name, dtype):
        return Stype.timestamp

    if contains_multicategorical(ser, column_name, dtype):
        return Stype.multicategorical

    if contains_categorical(ser, column_name, dtype):
        return Stype.categorical

    return dtype.default_stype


# TODO(blaz): refine and test
def detect_primary_key(df: pd.DataFrame) -> Optional[str]:
    """Auto-detect potential primary key column.

    Args:
        df: The pandas DataFrame to analyze

    Returns:
        The name of the detected primary key column, or None if not found
    """
    for col in df.columns:
        col_lower = col.lower()

        # Check naming patterns
        if any(pattern in col_lower for pattern in ['id', 'key', 'primary']):
            # Check if values are unique and non-null
            if df[col].nunique() == len(df) and df[col].notna().all():
                return col

    return None
