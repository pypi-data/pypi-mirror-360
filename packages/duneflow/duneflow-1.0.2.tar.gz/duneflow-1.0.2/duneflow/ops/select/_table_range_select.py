from __future__ import annotations

from typing import Optional

from duneflow.ops.reader import RawTable
from libactor.actor import make_key
from libactor.cache import IdentObj
from libactor.misc import orjson_dumps
from openpyxl.utils import column_index_from_string


def table_range_select(
    table: IdentObj[RawTable],
    start_row: int = 0,
    end_row: Optional[int | str] = None,
    start_col: int | str = 0,
    end_col: Optional[int | str] = None,
) -> IdentObj[RawTable]:
    # convert an Excel column letter (e.g., 'A', 'B', 'AA') to a 0-based index.
    actor_key = make_key(
        table_range_select,
        100,
        orjson_dumps(
            dict(
                start_row=start_row,
                end_row=end_row,
                start_col=start_col,
                end_col=end_col,
            )
        ).decode(),
    )

    if isinstance(start_col, str):
        start_col = column_index_from_string(start_col) - 1
    if isinstance(end_col, str):
        end_col = column_index_from_string(end_col) - 1

    return IdentObj(
        key=table.key + f"__range({actor_key})",
        value=RawTable(
            id=table.value.id,
            data=table.value[
                start_row:end_row,
                start_col:end_col,
            ],
        ),
    )
