from __future__ import annotations

from typing import Sequence, Union

from duneflow.ops.reader import RawTable
from libactor.actor import make_key
from libactor.cache import IdentObj
from sm.dataset import ColumnBasedTable


def to_column_based_table(
    table: IdentObj[RawTable], num_header_rows: int = 1
) -> IdentObj[ColumnBasedTable]:
    key = make_key(to_column_based_table, 100, str(num_header_rows))

    if num_header_rows > 0:
        nrows, ncols = table.value.shape()
        header = [
            " ".join(
                (str(table.value[ri, ci].value or "") for ri in range(num_header_rows))
            ).strip()
            for ci in range(ncols)
        ]
        data = table.value.data[num_header_rows:]
    else:
        header = [f"Column {i}" for i in range(len(table.value.data[0]))]
        data = table.value.data

    rows = [[cell.value or "" for cell in row] for row in data]
    return IdentObj(
        key=table.key + f"__to_column_based_table({key})",
        value=ColumnBasedTable.from_rows(rows, table.value.id, headers=header),
    )
