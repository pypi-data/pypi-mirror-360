from __future__ import annotations

from typing import Sequence

from duneflow.ops.reader import RawTable
from libactor.actor import make_key
from libactor.cache import IdentObj
from libactor.misc import orjson_dumps
from sm.misc.matrix import Matrix


def split_repeated_blocks(
    table_: IdentObj[RawTable], start_col: int, repeat_size: int
) -> Sequence[IdentObj[RawTable]]:
    """Split a table into multiple tables based on repeated blocks of columns.

    This function takes a table and splits it based on repeated blocks of columns
    starting from a specified column index. Each block has a fixed size.

    Parameters:
    ----------
    table : IdentObj[RawTable]
        The input table to split.
    start_col : int
        The starting column index from which to begin splitting.
    repeat_size : int
        The size of each repeated block of columns.

    Returns:
    -------
    Sequence[IdentObj[RawTable]]
        A sequence of table objects, each containing a split portion of the original table.

    Example:
    -------
    For a table with columns [A, B, C, D, E, F, G, H], start_col=2, repeat_size=2:

    Original table:
    +---+---+---+---+---+---+---+---+
    | A | B | C | D | E | F | G | H |
    +---+---+---+---+---+---+---+---+

    Result:
    Table 1: [A, B, C, D]
    Table 2: [A, B, E, F]
    Table 3: [A, B, G, H]

    Here, columns A and B are kept in each split table, while the repeated blocks
    (C-D, E-F, G-H) are distributed across the resulting tables.
    """
    table = table_.value
    actor_key = make_key(
        split_repeated_blocks,
        100,
        orjson_dumps(
            dict(
                start_col=start_col,
                repeat_size=repeat_size,
            )
        ).decode(),
    )

    tbls = []
    for i in range(start_col, table.shape()[1], repeat_size):
        cols = list(range(start_col)) + list(range(i, i + repeat_size))
        tbl = table[:, cols]
        tbls.append(
            IdentObj(
                key=table_.key + f"__({actor_key}:{i})",
                value=RawTable(id=table.id + f"_{i}", data=tbl),
            )
        )
    return tbls


def concatenate(
    tables: Sequence[IdentObj[RawTable]], num_header_rows: int = 1
) -> IdentObj[RawTable]:
    """Concatenates a sequence of tables into a single table.

    This function takes a sequence of tables and combines them into a single table, preserving
    the header rows from the first table. It's designed to work with tables that have the same
    structure (number of columns).

    Parameters
    ----------
    tables : Sequence[IdentObj[RawTable]]
        A sequence of tables to concatenate. Each table should have the same structure.
    num_header_rows : int, default=1
        The number of header rows in each table that should be preserved from the first table only.

    Returns
    -------
    IdentObj[RawTable]
        A new table containing all rows from the input tables, with header rows preserved from the first table.

    Notes
    -----
    - The first `num_header_rows` rows from the first table are used as the header for the combined table.
    - Subsequent tables' header rows are omitted from the final result.
    - All tables should have the same number of columns for proper concatenation.
    """
    if len(tables) == 0:
        raise ValueError("No tables provided for concatenation")

    actor_key = make_key(
        split_repeated_blocks,
        100,
        orjson_dumps(
            dict(
                num_header_rows=num_header_rows,
            )
        ).decode(),
    )

    # Extract the header rows from the first table
    first_table = tables[0].value
    header_rows = first_table.data[:num_header_rows]

    # Check if all tables have the same header
    for i, table_obj in enumerate(tables[1:], start=1):
        table = table_obj.value
        current_header = table.data[:num_header_rows]

        # Check if headers have same shape
        if len(current_header) != len(header_rows):
            raise ValueError(
                f"Table {i} has a different header shape than the first table"
            )

        # Check if headers have same content
        for r in range(len(current_header)):
            for c in range(len(current_header[0])):
                if current_header[r][c] != header_rows[r][c]:
                    raise ValueError(
                        f"Table {i} has a different header content than the first table at position ({r}, {c})"
                    )

    # Concatenate the data
    combined_data = header_rows
    for table_obj in tables:
        table = table_obj.value
        data_rows = table.data[num_header_rows:]
        combined_data.extend(data_rows)

    # Create a new table with the combined data
    key = "__".join([table_.key for table_ in tables]) + f"__concatenate({actor_key})"
    return IdentObj(
        key=key,
        value=RawTable(
            id="__".join([tbl.value.id for tbl in tables]), data=combined_data
        ),
    )
