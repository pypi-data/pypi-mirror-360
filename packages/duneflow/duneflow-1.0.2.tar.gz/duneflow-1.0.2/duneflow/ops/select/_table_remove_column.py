from __future__ import annotations

from dataclasses import dataclass

from duneflow.ops.reader import RawTable
from libactor.actor import Actor


@dataclass
class TableRemoveColumnArgs:
    cols: list[int]


class TableRemoveColumnActor(Actor[TableRemoveColumnArgs]):
    def forward(self, table: RawTable) -> RawTable:
        remove_cols = set(self.params.cols)
        keep_cols = [ci for ci in range(table.shape()[1]) if ci not in remove_cols]
        return RawTable(id=table.id, data=table[:, keep_cols])
