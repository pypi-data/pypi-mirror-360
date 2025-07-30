from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeVar

import orjson
import serde.csv
from duneflow.ops.reader._table_file_reader import RawTable
from libactor.cache import IdentObj
from slugify import slugify
from sm.dataset import FullTable
from sm.inputs.prelude import ColumnBasedTable

T = TypeVar(
    "T",
    ColumnBasedTable,
    RawTable,
    FullTable,
    IdentObj[ColumnBasedTable],
    IdentObj[RawTable],
    IdentObj[FullTable],
)


def write_table_to_file(
    table_: T,
    outdir: Path,
    format: Literal["csv", "json"] = "json",
    suffix: str = "",
) -> T:
    if isinstance(table_, IdentObj):
        table = table_.value
    else:
        table = table_
    table_id = (
        table.table_id
        if isinstance(table, ColumnBasedTable)
        else (table.table.table_id if isinstance(table, FullTable) else table.id)
    )
    outdir.mkdir(exist_ok=True, parents=True)
    outfile = outdir / f"{slugify(table_id)}{suffix}.{format}"

    if format == "json":
        outfile.write_bytes(orjson.dumps(table.to_dict()))
    elif format == "csv":
        if isinstance(table, RawTable):
            serde.csv.ser(
                table.map(
                    lambda cell: str(cell.value) if cell.value is not None else ""
                ).data,
                outfile,
            )
        else:
            if isinstance(table, FullTable):
                df = table.table.df
            else:
                df = table.df
            df.to_csv(outfile, index=False)
    else:
        raise ValueError(f"Unknown format {format}")
    return table_
