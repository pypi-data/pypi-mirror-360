import copy
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from kumoapi.typing import Dtype, Stype
from typing_extensions import Self

from kumoai.experimental.rfm import utils
from kumoai.graph.column import Column

logger = logging.getLogger(__name__)


class LocalTable:
    r"""A table backed by a :class:`pandas.DataFrame`.

    A :class:`LocalTable` fully specifies the relevant metadata, *i.e.*
    selected columns, column semantic types, primary keys and time columns.
    :class:`LocalTable` is used to create a :class:`LocalGraph`.

    .. code-block:: python

        import kumoai.experimental.rfm as rfm
        import pandas as pd

        # Load data from a CSV file:
        df = pd.read_csv("data.csv")

        # Create a table from a `pandas.DataFrame` and infer its metadata:
        table = rfm.LocalTable(df, table_name="my_table").infer_metadata()

        # Create a table explicitly:
        table = rfm.LocalTable(
            df=df,
            table_name="my_table",
            primary_key="id",
            time_column="time",
        )

        # Change the semantic type of a column:
        table[column].stype = "text"

    Args:
        df: The data frame to create the table from.
        table_name: The name of the table.
        primary_key: The name of the primary key of this table, if it exists.
        time_column: The name of the time column of this table, if it exists.
    """
    def __init__(
        self,
        df: pd.DataFrame,
        table_name: str,
        primary_key: Optional[str] = None,
        time_column: Optional[str] = None,
    ) -> None:
        validate_data(df)
        self._data = df
        self.table_name = table_name

        # columns - set without metadata
        self._columns: Dict[str, Column] = {}
        for col_name in df.columns:
            self._columns[col_name] = Column(name=col_name)

        # set special columns
        self._primary_key: Optional[str] = None
        self._time_column: Optional[str] = None
        if primary_key:
            self.primary_key = Column(name=primary_key)
        if time_column:
            self.time_column = Column(name=time_column)

    # Data column #############################################################

    def has_column(self, name: str) -> bool:
        r"""Returns ``True`` if this table holds a column with name ``name``;
        ``False`` otherwise.
        """
        return name in self._columns

    def column(self, name: str) -> Column:
        r"""Returns the data column named with name ``name`` in this table.

        Raises:
            KeyError: If ``name`` is not present in this table.
        """
        if not self.has_column(name):
            raise KeyError(f"Column '{name}' not found "
                           f"in table '{self.table_name}'")
        return self._columns[name]

    @property
    def columns(self) -> List[Column]:
        r"""Returns a list of :class:`~kumoai.graph.Column` objects that
        represent the columns in this table.
        """
        return list(self._columns.values())

    # Primary key #############################################################

    def has_primary_key(self) -> bool:
        r"""Returns ``True``` if this table has a primary key; ``False``
        otherwise.
        """
        return self._primary_key is not None

    @property
    def primary_key(self) -> Optional[Column]:
        r"""The primary key column of this table.

        The getter returns the primary key column of this table, or ``None`` if
        no such primary key is present.

        The setter sets a column as a primary key on this table, and raises a
        :class:`ValueError` if the primary key has a non-ID semantic type or
        if the column name does not match a column in the underlying data
        frame.
        """
        if not self.has_primary_key():
            return None
        assert self._primary_key is not None
        return self._columns[self._primary_key]

    @primary_key.setter
    def primary_key(self, *args: Any, **kwargs: Any) -> Self:
        col = Column._cast(*args, **kwargs)
        if col is None:
            self._primary_key = None
            return self

        if col.name not in self._columns:
            raise ValueError(
                f"Column '{col.name}' does not exist in the underlying "
                f"DataFrame")

        # update stype and set pkey
        self._columns[col.name].stype = Stype.ID
        self._primary_key = col.name
        return self

    def _add_default_primary_key(self) -> Self:
        r"""Adds a default primary key column to the table. The default primary
        key column is an integer (int64) column ranging from 1 to the number of
        rows in the table.

        Returns:
            The table with the default primary key column added, or the table
            if a primary key column already exists.
        """
        if self.has_primary_key():
            return self

        # Check if there is a column with name 'id'
        if 'id' in self._data.columns:
            raise ValueError("Cannot add default primary key column to "
                             f"{self.table_name} because a column with name "
                             "'id' already exists. Is this your primary key?")

        # Add sequential ID column to data
        self._data.insert(0, "id", range(1, len(self._data) + 1))
        self._columns["id"] = Column(
            name="id",
            dtype=Dtype.int64,
            stype=Stype.ID,
        )
        self._primary_key = "id"

        return self

    # Time column #############################################################

    def has_time_column(self) -> bool:
        r"""Returns ``True`` if this table has a time column; ``False``
        otherwise.
        """
        return self._time_column is not None

    @property
    def time_column(self) -> Optional[Column]:
        r"""The time column of this table.

        The getter returns the time column of this table, or ``None`` if no
        such time column is present.

        The setter sets a column as a time column on this table, and raises a
        :class:`ValueError` if the time column has a non-timestamp semantic
        type or if the column name does not match a column in the underlying
        data frame.
        """
        if not self.has_time_column():
            return None
        assert self._time_column is not None
        return self._columns[self._time_column]

    @time_column.setter
    def time_column(self, *args: Any, **kwargs: Any) -> Self:
        col = Column._cast(*args, **kwargs)
        if col is None:
            self._time_column = None
            return self

        if col.name not in self._data.columns:
            raise ValueError(
                f"Column '{col.name}' does not exist in the underlying "
                f"DataFrame")

        if col.stype is not None and col.stype != Stype.timestamp:
            raise ValueError(
                f"The semantic type of a time column must be 'timestamp' (got "
                f"{col.stype}).")

        col.stype = Stype.timestamp
        self._columns[col.name] = col
        self._time_column = col.name
        return self

    # Metadata ################################################################

    @property
    def metadata(self) -> pd.DataFrame:
        r"""Returns a :class:`pandas.DataFrame` object containing metadata
        information about the columns in this table.

        The returned dataframe has columns ``name``, ``dtype``, ``stype``,
        ``is_primary_key``, and ``is_time_column``, which provide an aggregate
        view of the properties of the columns of this table.

        Example:
            >>> import kumoai.experimental.rfm as rfm
            >>> table = rfm.LocalTable(df=..., table_name=...).infer_metadata()
            >>> table.metadata
                name        dtype       stype    is_primary_key is_time_column
            0   CustomerID  float64     ID       True            False
        """
        items = self._columns.items()
        col_names: List[str] = [i[0] for i in items]
        cols: List[Column] = [i[1] for i in items]

        return pd.DataFrame({
            'name':
            pd.Series(dtype=str, data=col_names),
            'dtype':
            pd.Series(
                dtype=str,
                data=[c.dtype if c.dtype is not None else None for c in cols],
            ),
            'stype':
            pd.Series(
                dtype=str,
                data=[c.stype if c.stype is not None else None for c in cols],
            ),
            'is_primary_key':
            pd.Series(dtype=bool, data=[self.primary_key == c for c in cols]),
            'is_time_column':
            pd.Series(dtype=bool, data=[self.time_column == c for c in cols]),
        })

    def infer_metadata(
        self,
        inplace: bool = True,
        verbose: bool = False,
    ) -> Self:
        r"""Infers metadata for all columns in the table.

        Args:
            inplace: Whether to modify the table in place or return a new
              instance.
            verbose: Whether to print verbose output.
        """
        out = self if inplace else copy.deepcopy(self)

        # Infer metadata for each column
        for col in out.columns:
            series = out._data[col.name]
            col.dtype = utils.to_dtype(series.dtype, series)
            col.stype = utils.infer_stype(series, col.name, col.dtype)

        # Try to detect primary key if not set
        if not out.has_primary_key():
            if pk := utils.detect_primary_key(out._data):
                assert pk is not None
                if verbose:
                    logger.info(f"Detected primary key {pk} in "
                                f"{out.table_name}.")
                out.primary_key = out.column(name=pk)
            else:
                if verbose:
                    logger.info(f"Could not detect primary key in "
                                f"{out.table_name}, adding a default primary "
                                "key column 'id'.")
                out = out._add_default_primary_key()

        # Try to detect time column if not set
        if not out.has_time_column():
            for col in out.columns:
                if any(pattern in col.name for pattern in
                       ['date', 'time', 'timestamp', 'created']):
                    if col.dtype == Dtype.date:
                        out.time_column = out.column(name=col.name)
                        break
            else:
                if verbose:
                    logger.info(f"Could not detect time column in "
                                f"{out.table_name}.")

        return out

    def _validate_definition(self) -> None:
        for col in self.columns:
            if col.dtype is None or col.stype is None:
                raise ValueError(
                    f"Column {col.name} is not fully specified. Please "
                    f"specify this column's data type and semantic type "
                    f"before proceeding. {col.name} currently has a "
                    f"data type of {col.dtype} and semantic type of "
                    f"{col.stype}.")

    def validate(self, verbose: bool = False) -> Self:
        r"""Validates the table configuration.

        Args:
            verbose: Whether to print validation messages.

        Raises:
            ValueError: If validation fails.
        """
        # Validate column definitions
        self._validate_definition()

        # Validate primary key
        if self.has_primary_key():
            pk = self.primary_key
            assert pk is not None
            if pk.stype != Stype.ID:
                raise ValueError(
                    f"Primary key {self._primary_key} must have ID semantic "
                    "type")
        else:
            raise ValueError("Table must have a primary key")

        # Validate time columns
        if self.has_time_column():
            tc = self.time_column
            assert tc is not None
            if tc.stype != Stype.timestamp:
                raise ValueError(
                    f"Time column {self._time_column} must have timestamp "
                    "semantic type")

        # Validate column dtypes
        for col in self.columns:
            series = self._data[col.name]
            inferred_dtype = utils.to_dtype(series.dtype, series)
            if (col.dtype != inferred_dtype
                    and not (col.stype == Stype.timestamp
                             and col.dtype == Dtype.date)):
                raise ValueError(
                    f"Column {col.name} has dtype {col.dtype} but data "
                    f"suggests {inferred_dtype}")

        # TODO(blaz) check for dtype<>stype consistency

        return self

    # Class properties ########################################################

    def __hash__(self) -> int:
        return hash(tuple(self.columns + [self.primary_key, self.time_column]))

    def __contains__(self, name: str) -> bool:
        return self.has_column(name)

    def __getitem__(self, name: str) -> Column:
        return self.column(name)

    def __repr__(self) -> str:
        col_names = str(list(self._columns.keys())).replace("'", "")
        pkey_name = self._primary_key if self.has_primary_key() else "None"
        t_name = self._time_column if self.has_time_column() else "None"
        return (f'{self.__class__.__name__}(\n'
                f'  name={self.table_name},\n'
                f'  data={self._data},\n'
                f'  columns={col_names},\n'
                f'  primary_key={pkey_name},\n'
                f'  time_column={t_name},\n'
                f')')


# helpers
def validate_data(data: pd.DataFrame) -> None:
    if data.empty:
        raise ValueError("Input DataFrame must have at least one row")
    if isinstance(data.index, pd.MultiIndex):
        raise ValueError("Input DataFrame must not have a multi-index")
    if isinstance(data.columns, pd.MultiIndex):
        raise ValueError("Input DataFrame must not have a multi-index")
    if not data.columns.is_unique:
        raise ValueError("Input DataFrame must have unique column names")
    if not all(col.replace('_', '').isalnum() for col in data.columns):
        raise ValueError("Input DataFrame must have alphanumeric column names")
    if '' in list(data.columns):
        raise ValueError("Input DataFrame must have non-empty column names")
