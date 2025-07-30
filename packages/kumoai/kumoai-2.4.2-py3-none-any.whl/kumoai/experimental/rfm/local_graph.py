import os
import tempfile
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Set, Union

import pandas as pd

from kumoai.connector import FileUploadConnector
from kumoai.connector.utils import upload_table
from kumoai.experimental.rfm import LocalTable
from kumoai.experimental.rfm.utils import dtype_to_family
from kumoai.graph import Edge, Graph, Table

MAX_TABLE_SIZE_MB = 10 * 1024  # 10GB in MB


class LocalGraph:
    r"""A graph of :class:`LocalTable` objects, akin to relationships between
    tables in a relational database.

    Creating a graph is the final step of data definition; after a
    :class:`LocalGraph` is created, you can use it to initialize the
    Kumo Relational Foundation Model (:class:`KumoRFM`).

    .. code-block:: python

        import kumoai.experimental.rfm as rfm

        # dataframes
        df1 = pd.DataFrame(...)
        df2 = pd.DataFrame(...)
        df3 = pd.DataFrame(...)

        # define tables
        table1 = kumoai.LocalTable(name="table1", data=df1)
        table2 = kumoai.LocalTable(name="table2", data=df2)
        table3 = kumoai.LocalTable(name="table3", data=df3)

        # create a graph from a list of tables
        graph = kumoai.LocalGraph(
            tables={
                "table1": table1,
                "table2": table2,
                "table3": table3,
            },
            edges=[],
        )

        # infer links
        graph.infer_links()

        # remove edges between tables
        graph.unlink(table1, table2, fkey="id1")

        # infer metadata
        graph.infer_metadata()

        # validate graph
        graph.validate()

        # construct a graph from dataframes
        graph = rfm.LocalGraph.from_data(data={
            "table1": df1,
            "table2": df2,
            "table3": df3,
        })

        # remove edge between tables
        graph.unlink(table1, table2, fkey="id1")

        # validate graph
        graph.validate()

        # re-link tables
        graph.link(table1, table2, fkey="id1")
    """

    # Constructors ############################################################

    def __init__(
        self,
        tables: List[LocalTable],
        edges: Optional[List[Edge]] = None,
    ) -> None:
        self._tables: Dict[str, LocalTable] = {}
        self._edges: List[Edge] = []

        if len(tables) != len(set([table.table_name for table in tables])):
            raise ValueError("Table names must be globally unique within a "
                             "graph.")

        for table in tables:
            self._tables[table.table_name] = table

        for edge in (edges or []):
            self.link(Edge._cast(edge))

    @staticmethod
    def from_data(
        data: Dict[str, pd.DataFrame],
        edges: Optional[List[Edge]] = None,
    ) -> 'LocalGraph':
        r"""Creates a :class:`LocalGraph` from a dictionary of
        :class:`pandas.DataFrame` objects.

        Args:
            data: A dictionary of data frames, where the keys are the names of
                the tables and the values hold table data.
            edges: An optional list of :class:`~kumoai.graph.Edge` objects to
                add to the graph. If not provided, edges will be automatically
                inferred from the data.

        Note:
            This method will automatically infer metadata and links for the
            graph.

        Example:
            >>> import kumoai.experimental.rfm as rfm
            >>> df1 = pd.DataFrame(...)
            >>> df2 = pd.DataFrame(...)
            >>> df3 = pd.DataFrame(...)
            >>> graph = rfm.LocalGraph.from_data(data={
            ...     "table1": df1,
            ...     "table2": df2,
            ...     "table3": df3,
            ... })
            ... graph.validate()  # doctest: +SKIP
        """
        tables = [
            LocalTable(df=df, table_name=name) for name, df in data.items()
        ]

        graph = LocalGraph(tables=tables, edges=edges or []).infer_metadata()

        if edges is None:
            graph.infer_links()

        return graph

    # Tables ##############################################################

    def has_table(self, name: str) -> bool:
        r"""Returns ``True`` if this graph has a table with name
        ``name``; ``False`` otherwise.
        """
        return name in self.tables

    def table(self, name: str) -> LocalTable:
        r"""Returns the table with name ``name`` in this graph.

        Raises:
            KeyError: If ``name`` is not present in this graph.

        """
        if not self.has_table(name):
            raise KeyError(f"Table '{name}' not found in graph")
        return self.tables[name]

    @property
    def tables(self) -> Dict[str, LocalTable]:
        r"""Returns the dictionary of table objects."""
        return self._tables

    def infer_metadata(self) -> 'LocalGraph':
        r"""Infers metadata for the tables in this :class:`LocalGraph`, by
        inferring the metadata of each :class:`LocalTable` in the graph.

        Note:
            For more information, please see
            :meth:`kumoai.experimental.rfm.LocalTable.infer_metadata`.
        """
        for table in self.tables.values():
            table.infer_metadata(inplace=True)

        return self

    # Edges ###################################################################

    @property
    def edges(self) -> List[Edge]:
        r"""Returns the edges of this graph."""
        return self._edges

    def link(
        self,
        *args: Optional[Union[str, Edge]],
        **kwargs: str,
    ) -> 'LocalGraph':
        r"""Links two tables (``src_table`` and ``dst_table``) from the foreign
        key ``fkey`` in the source table to the primary key in the destination
        table.

        These edges are treated as bidirectional.

        Args:
            *args: Any arguments to construct an :class:`~kumoai.graph.Edge`,
                or an :class:`~kumoai.graph.Edge` object itself.
            **kwargs: Any keyword arguments to construct an
                :class:`~kumoai.graph.Edge`.

        Raises:
            ValueError: if the edge is already present in the graph, if the
                source table does not exist in the graph, if the destination
                table does not exist in the graph, if the source key does not
                exist in the source table, or if the primary key of the source
                table is being treated as a foreign key.
        """
        edge = Edge._cast(*args, **kwargs)
        if edge is None:
            raise ValueError("Cannot add a 'None' edge to a graph.")

        (src_table, fkey, dst_table) = edge

        if edge in self.edges:
            raise ValueError(f"Cannot add edge {edge} to graph; edge is "
                             f"already present.")

        if not self.has_table(src_table):
            raise ValueError(
                f"Source table '{src_table}' does not exist in the graph.")

        if not self.has_table(dst_table):
            raise ValueError(
                f"Destination table '{dst_table}' does not exist in the "
                f"graph.")

        if not self.table(src_table).has_column(fkey):
            raise ValueError(
                f"Source key '{fkey}' does not exist in source table "
                f"'{src_table}'; please check that you have added it as a "
                f"column.")

        # Backend limitations: ensure the source is not its primary key:
        src_pkey = self.table(src_table).primary_key
        src_is_pkey = src_pkey is not None and src_pkey.name == fkey
        if src_is_pkey:
            raise ValueError(f"Cannot treat the primary key of table "
                             f"'{src_table}' as a foreign key; please "
                             f"select a different key.")

        self._edges.append(edge)
        return self

    def unlink(self, *args: Optional[Union[str, Edge]],
               **kwargs: str) -> 'LocalGraph':
        r"""Removes an :class:`~kumoai.graph.Edge` from the graph.

        Args:
            *args: Any arguments to construct an :class:`~kumoai.graph.Edge`,
                or an :class:`~kumoai.graph.Edge` object itself.
            **kwargs: Any keyword arguments to construct an
                :class:`~kumoai.graph.Edge`.

        Raises:
            ValueError: if the edge is not present in the graph.
        """
        edge = Edge._cast(*args, **kwargs)
        if edge not in self.edges:
            raise ValueError(f"Edge {edge} is not present in {self.edges}")
        self._edges.remove(edge)
        return self

    def infer_links(self) -> 'LocalGraph':
        r"""Infers links for the tables and adds them as edges to the graph.

        Note:
            This function expects graph edges to be undefined upfront.

        Raises:
            ValueError: If edges are not empty.
        """
        if self.edges is not None and len(self.edges) > 0:
            raise ValueError(
                "Cannot infer links if graph edges are not empty.")

        # TODO(blaz): expand logic for more elaborate inference
        self._infer_links_by_name()
        return self

    def _infer_links_by_name(self) -> 'LocalGraph':
        r"""Infers links for the tables in the graph by matching column
        names.
        """
        pk_index: DefaultDict[str, List[str]] = defaultdict(list)
        for table_name, table in self.tables.items():
            if table.has_primary_key():
                assert table.primary_key is not None
                pk_index[table.primary_key.name].append(table_name)

        # go through all non-pk columns and look up in the index
        for src_name, src in self.tables.items():
            src_pk_name: Optional[str] = (pk.name if (pk := src.primary_key)
                                          is not None else None)

            for col in src.columns:
                col_name = col.name

                # Skip the source PK itself
                if col_name == src_pk_name:
                    continue

                for dst_name in pk_index.get(col_name, ()):
                    self.link(Edge(src_name, col_name, dst_name))

        return self

    # Metadata ################################################################

    def validate(self) -> 'LocalGraph':
        r"""Validates the graph to ensure that all relevant metadata is
        specified for its tables and edges.

        Concretely, validation ensures that all tables are valid (see
        :meth:`kumoai.experimental.rfm.LocalTable.validate` for more
        information), and that edges properly link primary keys and foreign
        keys between valid tables.
        It additionally ensures that primary and foreign keys between tables
        in an :class:`~kumoai.graph.Edge` are of the same data type.

        Example:
            >>> import kumoai
            >>> graph = kumoai.LocalGraph(...)  # doctest: +SKIP
            >>> graph.validate()  # doctest: +SKIP
            ValueError: ...

        Raises:
            ValueError: if validation fails.
        """
        # TODO(blaz): lift restriction on isolated tables & conected components
        # validate tables
        for table in self.tables.values():
            table.validate()

        # validate edges
        self._validate_edges()

        # validate isolated tables and isolated components
        if len(self.tables) > 1:  # Only check if we have multiple tables
            self._validate_isolated_tables()
            self._validate_single_connected_component()

        return self

    def _validate_edges(self) -> None:
        r"""Validates that all edges in the graph are valid.

        Raises:
            ValueError: if the graph has invalid edges.
        """
        # validate edges fkey -> pkey
        for edge in self.edges:
            (src_table, fkey, dst_table) = edge
            dst_pkey = self.table(dst_table).primary_key
            # check that fkey exists in src_table

            if not self.table(src_table).has_column(fkey):
                raise ValueError(f"Edge {edge} is invalid as source table "
                                 f"'{src_table}' does not have a column with "
                                 f"name '{fkey}'.")
            # check that fkey is the primary key of dst_table
            if dst_pkey is None:
                raise ValueError(f"Edge {edge} is invalid since table "
                                 f"'{dst_table}' does not have a primary key.")

            # check that fkey/pkey are from either numerical or string family
            if (dtype_to_family(self.table(src_table)[fkey].dtype) not in [
                    "number", "string"
            ] or dtype_to_family(dst_pkey.dtype) not in ["number", "string"]):
                raise ValueError(f"Edge {edge} is invalid as foreign key "
                                 f"'{fkey}' and primary key '{dst_pkey.name}' "
                                 f"must be from be either 'numbers' or "
                                 f"'strings' (fkey.dtype: "
                                 f"{self.table(src_table)[fkey].dtype}, "
                                 f"pkey.dtype: {dst_pkey.dtype})")

            # check that fkey and pkey are from the same data type family
            if (dtype_to_family(self.table(src_table)[fkey].dtype)
                    != dtype_to_family(dst_pkey.dtype)):
                raise ValueError(f"Edge {edge} is invalid as foreign key "
                                 f"'{fkey}' and primary key '{dst_pkey.name}' "
                                 f"have incompatible data types. "
                                 f"(fkey.dtype: "
                                 f"{self.table(src_table)[fkey].dtype} "
                                 f"!= pkey.dtype: {dst_pkey.dtype})")

    def _validate_isolated_tables(self) -> None:
        r"""Validates that all tables in the graph are connected to at least
        one other table.

        Raises:
            ValueError: if the graph has isolated tables.
        """
        connected_tables = {edge.src_table for edge in self.edges} | \
            {edge.dst_table for edge in self.edges}

        for table_name in self.tables:
            if table_name not in connected_tables:
                raise ValueError(f"Table '{table_name}' is not connected to "
                                 f"any other tables in the graph (no incoming "
                                 f"or outgoing edges).")

    def _validate_single_connected_component(self) -> None:
        r"""Validates that all tables in the graph form a single connected
        component using breadth-first search.

        Raises:
            ValueError: if the graph has multiple disconnected components.
        """
        if not self.tables:
            return

        # Build adjacency list for undirected graph
        adjacency: Dict[str, Set[str]] = {
            table_name: set()
            for table_name in self.tables.keys()
        }
        for edge in self.edges:
            src, _, dst = edge
            adjacency[src].add(dst)
            adjacency[dst].add(src)  # Treat edges as bidirectional

        # BFS to find all reachable tables from the first table
        start_table = next(iter(self.tables.keys()))
        visited = set()
        queue = [start_table]
        visited.add(start_table)

        while queue:
            current = queue.pop(0)
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Check if all tables are reachable
        unreachable_tables = set(self.tables.keys()) - visited
        if unreachable_tables:
            raise ValueError(
                f"Graph contains disconnected components. Tables "
                f"{list(unreachable_tables)} are not reachable from the main "
                f"component. All tables must be connected in a single "
                f"component.")

    # Class properties ########################################################

    def __hash__(self) -> int:
        return hash((tuple(self.edges), tuple(sorted(self.tables.keys()))))

    def __contains__(self, name: str) -> bool:
        return self.has_table(name)

    def __getitem__(self, name: str) -> LocalTable:
        return self.table(name)

    def __repr__(self) -> str:
        table_names = str(list(self.tables.keys())).replace("'", "")
        return (f'{self.__class__.__name__}(\n'
                f'  tables={table_names},\n'
                f'  edges={self.edges},\n'
                f')')

    # Conversion helpers ######################################################

    def _calculate_total_table_size_mb(self) -> float:
        """Calculate the total size of all tables in MB by
        temporarily serializing to parquet.

        Returns:
            Total size of all tables in megabytes
        """
        total_size_bytes = 0
        with tempfile.TemporaryDirectory() as tmp_dir:
            for table_name, local_table in self.tables.items():
                tmp_path = os.path.join(tmp_dir,
                                        f'{table_name}_size_check.parquet')
                local_table._data.to_parquet(tmp_path, index=False)
                total_size_bytes += os.path.getsize(tmp_path)

        return total_size_bytes / (1024 * 1024)  # Convert to MB

    def _upload_tables(self) -> None:
        """Upload LocalTable data using FileUploadConnector"""
        # TODO(blaz): upload with table_name_fpid instead of table_name
        with tempfile.TemporaryDirectory() as tmp_dir:
            for table_name, local_table in self.tables.items():
                tmp_path = os.path.join(tmp_dir, f'{table_name}.parquet')
                local_table._data.to_parquet(tmp_path, index=False)
                try:
                    upload_table(name=table_name, path=tmp_path)
                except Exception as e:
                    raise e

    def to_kumo_graph(self) -> Graph:
        """Upload tables and convert LocalGraph to kumo.graph.Graph

        This method handles both uploading the table data and converting
        the LocalGraph to a kumo Graph object.

        Returns:
            A kumo Graph object ready for use

        Raises:
            ValueError: If the total size of all tables exceeds 10GB
        """
        # Check total size before uploading
        total_size_mb = self._calculate_total_table_size_mb()

        if total_size_mb > MAX_TABLE_SIZE_MB:
            raise ValueError(
                f"Total size of all tables ({total_size_mb:.2f} MB) exceeds "
                f"the maximum allowed size of {MAX_TABLE_SIZE_MB} MB (10 GB). "
                f"Please reduce the data size before uploading.")

        self._upload_tables()
        return self._convert_to_kumo_graph()

    def _convert_to_kumo_graph(self) -> Graph:
        """Convert LocalGraph to kumo.graph.Graph using uploaded tables"""
        connector = FileUploadConnector(file_type="parquet")
        kumo_tables: Dict[str, Table] = {}

        for table_name, local_table in self.tables.items():
            source_table = connector[table_name]

            primary_key = (local_table.primary_key.name
                           if local_table.primary_key is not None else None)
            time_column = (local_table.time_column.name
                           if local_table.time_column is not None else None)
            kumo_table = Table.from_source_table(
                source_table=source_table,
                primary_key=primary_key,
                time_column=time_column,
            )

            # apply column metadata from local table to kumo table
            for local_col in local_table.columns:
                if kumo_table.has_column(local_col.name):
                    kumo_col = kumo_table.column(local_col.name)
                    if local_col.dtype:
                        kumo_col.dtype = local_col.dtype
                    if local_col.stype:
                        kumo_col.stype = local_col.stype

            kumo_tables[table_name] = kumo_table

        kumo_graph = Graph(tables=kumo_tables, edges=list(self.edges))

        return kumo_graph
