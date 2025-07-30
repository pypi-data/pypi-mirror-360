from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Literal, NotRequired, Optional, Sequence, TypedDict

from duneflow.ops.reader import RawCell, RawTable
from libactor.actor import make_key
from libactor.cache import IdentObj
from libactor.misc import orjson_dumps
from sm.misc.funcs import group_by

RowIndex = Annotated[int, "row index"]
ColIndex = Annotated[int, "column index"]


class HorizontalProp(TypedDict):
    name: NotRequired[Annotated[str, "Name of the property"]]
    row: RowIndex
    col: Annotated[tuple[int, int], "range of columns [start, end) (exclusive)"]


class MatrixProp(TypedDict):
    name: NotRequired[Annotated[str, "Name of the matrix property"]]
    row: RowIndex
    vertical_col_name: NotRequired[Annotated[str, "Name of the vertical property"]]
    vertical_col: Annotated[
        tuple[int, int], "range of columns [start, end) (exclusive)"
    ]
    horizontal_col_name: NotRequired[Annotated[str, "Name of the horizontal property"]]
    horizontal_col: Annotated[
        tuple[int, int], "range of columns [start, end) (exclusive)"
    ]
    repeat: NotRequired[
        Annotated[int, "repeat the vertical & horizontal cols (default 1)"]
    ]


@dataclass
class MatrixColumn:
    """A column containing values of a matrix variable. Typically, a matrix variable will span multiple columns"""

    col: Annotated[ColIndex, "index of the new column in the new table"]
    original_col: Annotated[
        ColIndex, "index of the original column in the original table"
    ]
    horizontal_props: Annotated[
        list[MatrixHorizontalProp],
        "the horizontal property associated with this column",
    ]
    vertical_props: Annotated[
        list[MatrixVerticalProp], "the vertical property associated with this column"
    ]


@dataclass
class MatrixHorizontalProp:
    """The horizontal property of a matrix variable."""

    col: Annotated[
        ColIndex, "index of the new column of this property in the new table"
    ]
    original_row: Annotated[
        RowIndex, "index of the original row containing this property"
    ]


@dataclass
class MatrixVerticalProp:
    """The vertical property of a matrix variable."""

    col: Annotated[
        ColIndex, "index of the new column of this property in the new table"
    ]
    original_col: Annotated[
        ColIndex, "index of the original column containing this property"
    ]


@dataclass
class ExistingVerticalColumn:
    """Vertical properties"""

    col: Annotated[ColIndex, "index of the new column in the new table"]
    original_col: Annotated[
        ColIndex, "index of the original column in the original table"
    ]


@dataclass
class NewVerticalColumn:
    """New vertical column that is created to store the horizontal properties"""

    name: RawCell
    row: Annotated[RowIndex, "row of the original horizontal property"]
    col: Annotated[ColIndex, "index of the new column in the new table"]
    start_original_col: Annotated[
        ColIndex, "index of the begin column in the original table"
    ]


def matrix_to_relational_table_v2(
    table_: IdentObj[RawTable],
    matrix_prop: MatrixProp,
    start_data_row: RowIndex = 1,
    drop_cols: Optional[Sequence[int]] = None,
    horizontal_props: Sequence[HorizontalProp] = [],
) -> IdentObj[RawTable]:
    """The table model of this function is centered around the matrix variables.

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
        matrix_to_relational_table_v2,
        100,
        orjson_dumps(
            dict(
                matrix_prop=matrix_prop,
                start_data_row=start_data_row,
                drop_cols=drop_cols,
                horizontal_props=horizontal_props,
            )
        ).decode(),
    )

    # first compute the mapping to get the header
    # header_map: Sequence[ExistingVerticalColumn | NewVerticalColumn] = []
    header_map, matrix_columns = _process_column_map(
        table, matrix_prop, drop_cols, horizontal_props
    )
    vertical_columns: list[ExistingVerticalColumn] = [
        header for header in header_map if isinstance(header, ExistingVerticalColumn)
    ]

    # then, construct the new table
    new_tbl_cols = len(header_map) + 1
    new_table = [
        [RawCell() for _ in range(new_tbl_cols)] for _ in range(start_data_row)
    ]

    # copy header of vertical columns
    new_table[start_data_row - 1][0] = RawCell("row index")
    for header in header_map:
        if isinstance(header, ExistingVerticalColumn):
            for ri in range(start_data_row):
                new_table[ri][header.col + 1] = table[ri, header.original_col]
        else:
            assert isinstance(header, NewVerticalColumn)
            new_table[start_data_row - 1][header.col + 1] = header.name
            assert header.name is not None, header

    # finally, we loop through each matrix value and assign to the new table
    nrows = table.shape()[0]
    for ri in range(start_data_row, nrows):
        # then we are going to loop through each header and copy
        base_row = [RawCell() for _ in range(new_tbl_cols)]
        base_row[0].value = ri + 1

        # we are going to copy all vertical properties first
        for vercol in vertical_columns:
            base_row[vercol.col + 1] = table[ri, vercol.original_col]

        # then, we are going to loop through each value of the matrix variable
        # in the current row, and assign them to the new row
        for valcol in matrix_columns:
            cell = table[ri, valcol.original_col]
            if cell.is_missing():
                continue

            row = base_row.copy()
            for prop in valcol.horizontal_props:
                row[prop.col + 1] = table[prop.original_row, valcol.original_col]
            for prop in valcol.vertical_props:
                row[prop.col + 1] = table[ri, prop.original_col]
            row[valcol.col + 1] = cell
            new_table.append(row)

    for ri in range(len(new_table)):
        if any(cell is None for cell in new_table[ri]):
            print(f"Row {ri} contains None values: {new_table[ri]}")

    return IdentObj(
        key=table_.key + f"__matrix2rel({actor_key})",
        value=RawTable(id=table.id, data=new_table),
    )


def _process_column_map(
    table: RawTable,
    matrix_prop: MatrixProp,
    drop_cols: Optional[Sequence[int]],
    horizontal_props: Sequence[HorizontalProp],
) -> tuple[list[ExistingVerticalColumn | NewVerticalColumn], list[MatrixColumn]]:
    nrows, ncols = table.shape()
    set_drop_cols = set(drop_cols) if drop_cols is not None else set()

    horizontal_prop_cols = set()
    for prop in horizontal_props:
        if isinstance(prop["col"], tuple):
            start_col, end_col = prop["col"]
            horizontal_prop_cols.update(range(start_col, end_col))
        else:
            horizontal_prop_cols.update(prop["col"])

    new_cols = []
    # add exist vertical columns
    for col in range(ncols):
        # TODO: fix me that we should also ignore the columns in the matrix prop
        if col in horizontal_prop_cols:
            continue
        if col in set_drop_cols:
            continue
        new_cols.append({"type": "old", "original_col": col})

    # add new horizontal columns
    for prop_idx, prop in enumerate(horizontal_props):
        new_cols.append(
            {
                "type": "new-horizontal",
                "name": prop.get("name"),
                "original_col": prop["col"][0],
                "row": prop["row"],
                "horizontal_prop_index": prop_idx,
            }
        )

    # add new columns from matrix prop
    vertical_cols = list(range(*matrix_prop["vertical_col"]))
    horizontal_cols = list(range(*matrix_prop["horizontal_col"]))
    assert set(vertical_cols).isdisjoint(horizontal_cols)
    for col in vertical_cols:
        new_cols.append(
            {
                "type": "new-vertical",
                "name": matrix_prop.get(
                    "vertical_col_name", table[matrix_prop["row"], col]
                ),
                "original_col": col,
                "row": matrix_prop["row"],
            }
        )
    new_cols.append(
        {
            "type": "new-horizontal",
            "name": matrix_prop.get("horizontal_col_name"),
            "original_col": min(horizontal_cols),
            "row": matrix_prop["row"],
            "horizontal_prop_index": len(horizontal_props),
        }
    )
    new_cols.append(
        {
            "type": "new-matrix",
            "name": matrix_prop.get("name"),
            "original_col": min(horizontal_cols),
            "row": matrix_prop["row"],
        }
    )

    # verify that the horizontal properties are valid
    start_ci = min(*vertical_cols, *horizontal_cols)
    assert all(
        prop["col"][0] == start_ci for prop in horizontal_props
    ), "The horizontal properties must cover the matrix variable"
    repeat_size = max(*vertical_cols, *horizontal_cols) + 1 - start_ci
    end_ci = start_ci + repeat_size * matrix_prop.get("repeat", 1)
    assert all(
        prop["col"][-1] == end_ci for prop in horizontal_props
    ), f"The horizontal properties must cover the matrix variable. Expect {end_ci} but got {horizontal_props[0]['col'][-1]}"

    # sort the new columns so that the new column index reflects the original column index
    new_cols.sort(key=lambda x: (x["original_col"], x.get("row", 0)))
    output_header: list[ExistingVerticalColumn | NewVerticalColumn] = []
    for ci, col in enumerate(new_cols):
        if col["type"] == "old":
            output_header.append(
                ExistingVerticalColumn(
                    col=ci,
                    original_col=col["original_col"],
                )
            )
        else:
            assert col["type"].startswith("new-")
            output_header.append(
                NewVerticalColumn(
                    name=col["name"] or RawCell(f"Column {ci}"),
                    row=col["row"],
                    col=ci,
                    start_original_col=col["original_col"],
                )
            )

    # TODO: compute the matrix columns
    new_hor_colmap = {
        col["horizontal_prop_index"]: ci
        for ci, col in enumerate(new_cols)
        if col["type"] == "new-horizontal"
    }
    new_ver_colmap = {
        col["original_col"]: ci
        for ci, col in enumerate(new_cols)
        if col["type"] == "new-vertical"
    }
    matrix_new_col = [
        ci for ci, col in enumerate(new_cols) if col["type"] == "new-matrix"
    ][0]

    matrix_columns: list[MatrixColumn] = []
    for i in range(matrix_prop.get("repeat", 1)):
        for col in horizontal_cols:
            matrix_columns.append(
                MatrixColumn(
                    col=matrix_new_col,
                    original_col=col + i * repeat_size,
                    horizontal_props=[
                        MatrixHorizontalProp(
                            col=new_hor_colmap[prop_idx], original_row=prop["row"]
                        )
                        for prop_idx, prop in enumerate(horizontal_props)
                    ]
                    + [
                        MatrixHorizontalProp(
                            col=new_hor_colmap[len(horizontal_props)],
                            original_row=matrix_prop["row"],
                        )
                    ],
                    vertical_props=[
                        MatrixVerticalProp(
                            col=new_ver_colmap[vercol],
                            original_col=vercol + i * repeat_size,
                        )
                        for vercol in vertical_cols
                    ],
                )
            )

    return output_header, matrix_columns
