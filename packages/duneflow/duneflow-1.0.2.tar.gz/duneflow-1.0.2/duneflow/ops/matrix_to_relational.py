from __future__ import annotations

from typing import Annotated, NotRequired, Optional, Sequence, TypedDict

from duneflow.ops.reader import RawCell, RawTable
from libactor.actor import make_key
from libactor.cache import IdentObj
from libactor.misc import orjson_dumps
from sm.misc.funcs import group_by

RowIndex = Annotated[int, "row index"]
ColIndex = Annotated[int, "column index"]


class HorizontalProp(TypedDict):
    name: NotRequired[Annotated[str, "Name of the property"]]
    row: NotRequired[Annotated[int, "row, default = 0"]]
    col: (
        Annotated[list[int], "list of columns (sorted)"]
        | Annotated[tuple[int, int], "range of columns [start, end) (exclusive)"]
    )


def matrix_to_relational_table(
    table_: IdentObj[RawTable],
    horizontal_props: Sequence[HorizontalProp],
    drop_cols: Optional[Sequence[int]] = None,
    matrix_prop_names: Optional[str | Sequence[Optional[str]]] = None,
) -> IdentObj[RawTable]:
    """The table have vertical and horizontal properties. There can be multiple horizontal properties.

        |  H1  |  H2  |  H3  | <- Horizontal Properties
    ----+------+------+------+
    V1  | M11  | M12  | M13  |
    ----+------+------+------+
    V2  | M21  | M22  | M23  | <- Matrix Variables
    ----+------+------+------+
    V3  | M31  | M32  | M33  |
        |      |      |      |
    ^
    Vertical Properties


    """
    table = table_.value
    actor_key = make_key(
        matrix_to_relational_table,
        100,
        orjson_dumps(
            dict(
                horizontal_props=horizontal_props,
                drop_cols=drop_cols,
                matrix_prop_names=matrix_prop_names,
            )
        ).decode(),
    )

    nrows, ncols = table.shape()

    horizontal_prop_cols = set()
    for prop in horizontal_props:
        if isinstance(prop["col"], tuple):
            start_col, end_col = prop["col"]
            horizontal_prop_cols.update(range(start_col, end_col))
            # normalize to the list of columns
            prop["col"] = list(range(start_col, end_col))
        else:
            prop["col"] = sorted(prop["col"])
            horizontal_prop_cols.update(prop["col"])

    start_data_row = max(prop.get("row", 0) for prop in horizontal_props) + 1
    output_header_loc = []

    set_drop_cols = set(drop_cols) if drop_cols is not None else set()
    for col in range(ncols):
        if col in horizontal_prop_cols:
            continue
        if col in set_drop_cols:
            continue
        output_header_loc.append({"type": "vertical", "col": col, "order": 0})

    # partition the horizontal properties so that the one have the same start column are aligned.
    col2horizontal_props = group_by(horizontal_props, key=lambda prop: prop["col"][0])
    if matrix_prop_names is None:
        matrix_prop_names = [None] * len(col2horizontal_props)
    elif isinstance(matrix_prop_names, str):
        matrix_prop_names = [matrix_prop_names]
    assert len(matrix_prop_names) == len(col2horizontal_props)

    for col, group_props in col2horizontal_props.items():
        # validate that these group_props shared the same column
        for prop in group_props[1:]:
            assert (
                prop["col"] == group_props[0]["col"]
            ), "Mis-aligned between horizontal properties of the same matrix."
        for gi in range(len(group_props) + 1):
            output_header_loc.append({"type": "horizontal", "col": col, "order": gi})

    output_header_loc.sort(key=lambda x: (x["col"], x["order"]))
    vertical_cols: list[tuple[int, int]] = [
        (ci, loc["col"])
        for ci, loc in enumerate(output_header_loc, start=1)
        if loc["type"] == "vertical"
    ]
    # mapping from (column, order) to new column index
    horizontal_prop_headermap: dict[tuple[int, int], int] = {
        (loc["col"], loc["order"]): ci
        for ci, loc in enumerate(output_header_loc, start=1)
        if loc["type"] == "horizontal"
    }

    # init the table with the header
    output_table_ncols = len(output_header_loc) + 1
    output_table: list[list[RawCell]] = [
        [RawCell() for _ in range(output_table_ncols)] for _ in range(start_data_row)
    ]

    # copy header of the vertical properties over to the output table
    output_table[start_data_row - 1][0] = RawCell(value="row index")
    for newci, ci in vertical_cols:
        for ri in range(start_data_row):
            output_table[ri][newci] = table[ri, ci]
    # assign the header for the horizontal properties
    for group_idx, (col, group_horizontal_props) in enumerate(
        col2horizontal_props.items()
    ):
        for order, prop in enumerate(group_horizontal_props):
            newci = horizontal_prop_headermap[col, order]
            colname = prop.get("name", f"Column {newci}")
            output_table[start_data_row - 1][newci] = RawCell(value=colname)

        newci = horizontal_prop_headermap[col, len(group_horizontal_props)]
        if matrix_prop_names[group_idx] is None:
            colname = f"Column {newci}"
        else:
            colname = matrix_prop_names[group_idx]
        output_table[start_data_row - 1][newci] = RawCell(value=colname)

    # copy the data
    for start_col, group_horizontal_props in col2horizontal_props.items():
        _join(
            table,
            output_table,
            (
                start_data_row,
                nrows,
                start_col,
                group_horizontal_props[-1]["col"][-1] + 1,
            ),
            horizontal_prop_headermap[start_col, len(group_horizontal_props)],
            vertical_cols,
            [
                (horizontal_prop_headermap[start_col, order], prop.get("row", 0))
                for order, prop in enumerate(group_horizontal_props)
            ],
        )
        newci += len(group_horizontal_props) + 1

    return IdentObj(
        key=table_.key + f"__matrix2rel({actor_key})",
        value=RawTable(id=table.id, data=output_table),
    )


def _join(
    table: RawTable,
    output_table: list[list[RawCell]],
    matrix_prop: tuple[RowIndex, RowIndex, ColIndex, ColIndex],
    matrix_prop_col: ColIndex,
    vertical_props: list[tuple[ColIndex, ColIndex]],
    horizontal_props: list[tuple[ColIndex, RowIndex]],
) -> list[list[RawCell]]:
    """Create new relational table by joining the matrix with vertical and horizontal properties."""
    default_row = [RawCell() for _ in range(len(output_table[0]))]

    for ri in range(matrix_prop[0], matrix_prop[1]):
        for ci in range(matrix_prop[2], matrix_prop[3]):
            cell = table[ri, ci]
            if cell.is_missing():
                continue

            row = default_row.copy()
            row[0] = RawCell(value=ri - matrix_prop[0] + 1)
            for newci, aci in vertical_props:
                row[newci] = table[ri, aci]
            for newci, ari in horizontal_props:
                row[newci] = table[ari, ci]
            row[matrix_prop_col] = cell
            output_table.append(row)

    return output_table
