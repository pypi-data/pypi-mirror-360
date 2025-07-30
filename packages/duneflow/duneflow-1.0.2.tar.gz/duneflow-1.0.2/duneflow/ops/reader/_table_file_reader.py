from __future__ import annotations

from dataclasses import dataclass, field
from email.policy import default
from enum import Enum
from pathlib import Path
from typing import Literal, Sequence, cast

import openpyxl
import serde.csv
from duneflow.models import RawCell, RawTable
from sm.misc.matrix import Matrix


@dataclass
class TableFileReaderArgs:
    format: Literal["auto", "csv", "excel"] = "auto"


class FileFormat(str, Enum):
    CSV = "csv"
    Excel = "excel"


def read_table_from_file(
    infile: Path,
    format: Literal["auto", "csv", "excel"] = "auto",
    name_as_id: bool = True,
) -> Sequence[RawTable]:
    infile = infile.resolve(strict=True)
    table_id = infile.stem if name_as_id else str(infile)

    norm_format = guess_format(infile) if format == "auto" else FileFormat(format)

    output = []
    if norm_format == FileFormat.Excel:
        wb = openpyxl.load_workbook(infile, data_only=True)
        for i, ws in enumerate(wb.worksheets):
            rows = []
            for row in ws.iter_rows():
                rows.append([RawCell(cell.value, {}) for cell in row])  # type: ignore
            tbl = RawTable(id=f"{table_id}[{i}]", data=rows)

            for range in ws.merged_cells.ranges:
                startcol, startrow, endcol, endrow = cast(
                    tuple[int, int, int, int], range.bounds
                )
                startcol -= 1
                startrow -= 1
                cell = tbl[startrow, startcol]
                cell.metadata["colspan"] = endcol - startcol
                cell.metadata["rowspan"] = endrow - startrow

            output.append(tbl)
    elif norm_format == FileFormat.CSV:
        tbl = Matrix(serde.csv.deser(infile)).map(lambda cell: RawCell(cell))
        output.append(RawTable(id=table_id, data=tbl.data))
    else:
        raise NotImplementedError(f"Unknown format {format}")

    return output


def guess_format(file_path: Path) -> FileFormat:
    if file_path.name.endswith(".csv"):
        return FileFormat.CSV
    if file_path.name.endswith(".xlsx"):
        return FileFormat.Excel
    raise NotImplementedError(f"Unknown format for file {file_path}")
    raise NotImplementedError(f"Unknown format for file {file_path}")
