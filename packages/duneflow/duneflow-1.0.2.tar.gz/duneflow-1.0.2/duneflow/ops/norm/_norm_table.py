from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import orjson
from duneflow.ops.reader import RawCell, RawTable
from libactor.actor import Actor
from libactor.cache import IdentObj
from sm.dataset import ColumnBasedTable
from sm.inputs.column import Column
from sm.misc.matrix import Matrix


@dataclass
class NormTableArgs:
    norm_num_format: bool = True
    remove_empty_rows: bool = True
    remove_empty_cols: bool = True
    missing_values: set[str] = field(
        default_factory=lambda: {"", "NA", "N/A", "NULL", "None"}
    )
    expand_merged_cells: bool = True


class NormTableActor(Actor[NormTableArgs]):
    def forward(self, table: IdentObj[RawTable]) -> IdentObj[RawTable]:
        data = Matrix(table.value.data)
        if self.params.norm_num_format:
            data = data.map(self.norm_num)
        if self.params.expand_merged_cells:
            data = self.expand_merged_cells(data)
        if self.params.remove_empty_rows:
            data = Matrix(
                [
                    row
                    for row in data.data
                    if not all(cell.value is None or cell.value == "" for cell in row)
                ]
            )
        if self.params.remove_empty_cols:
            keep_cols = []
            for ci in range(data.shape()[1]):
                if not all(
                    cell.value is None or cell.value == "" for cell in data[:, ci]
                ):
                    keep_cols.append(ci)
            data = Matrix(data[:, keep_cols])
        if len(self.params.missing_values) > 0:
            data = data.map(
                lambda cell: (
                    cell.update_value(None)
                    if cell.value in self.params.missing_values
                    else cell
                )
            )

        return IdentObj(
            key=table.key + f"_norm({self.key})",
            value=RawTable(id=table.value.id, data=data.data),
        )

    def norm_num(self, cell: RawCell) -> RawCell:
        if (
            isinstance(cell.value, str)
            and re.match("^[0-9,]+$", cell.value) is not None
        ):
            return cell.update_value(cell.value.replace(",", ""))
        return cell

    def expand_merged_cells(self, table: Matrix[RawCell]) -> Matrix[RawCell]:
        """Expand merged cells in the table."""
        for ri, ci, cell in table.enumerate_flat_iter():
            colspan = cell.metadata.get("colspan", 1)
            rowspan = cell.metadata.get("rowspan", 1)
            if colspan > 1:
                for i in range(1, colspan):
                    table[ri, ci + i] = table[ri, ci + i].update_value(cell.value)
            if rowspan > 1:
                for i in range(1, rowspan):
                    table[ri + i, ci] = table[ri + i, ci].update_value(cell.value)
        return table


def norm_column_based_table(
    table: IdentObj[ColumnBasedTable],
    norm_num_format: bool = True,
    remove_empty_rows: bool = True,
    remove_empty_cols: bool = True,
    missing_values: set[str] = {"", "NA", "N/A", "NULL", "None"},
) -> IdentObj[ColumnBasedTable]:
    # newtable = ColumnBasedTable(table.value.table_id, table.value.columns)
    new_columns = table.value.columns
    if norm_num_format:
        for i, col in enumerate(new_columns):
            new_columns[i] = Column(
                col.index, col.name, [norm_num(val) for val in col.values]
            )
    if remove_empty_rows:
        new_columns = (
            ColumnBasedTable(table.value.table_id, new_columns)
            .remove_empty_rows()
            .columns
        )
    if remove_empty_cols:
        new_columns = [
            col
            for col in new_columns
            if not all(val.strip() == "" for val in col.values)
        ]
    if len(missing_values) > 0:
        for i, col in enumerate(new_columns):
            new_columns[i] = Column(
                col.index,
                col.name,
                ["" if val in missing_values else val for val in col.values],
            )
        new_columns = (
            ColumnBasedTable(table.value.table_id, new_columns)
            .remove_empty_rows()
            .columns
        )
    return IdentObj(
        key=table.key
        + f"_norm({norm_num_format}, {remove_empty_rows}, {remove_empty_cols}, {orjson.dumps(sorted(missing_values)).decode()})",
        value=ColumnBasedTable(table.value.table_id, new_columns),
    )


def norm_num(value: Any) -> Any:
    if isinstance(value, str):
        if re.match("^[0-9,]+$", value) is not None:
            return value.replace(",", "")
        if re.match(f"^[0-9-. ]+$", value) is not None:
            return value.replace(" ", "")

    return value
