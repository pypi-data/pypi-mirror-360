# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Sequence

# from duneflow.ops.readers._table_file_reader import RawTable
# from libactor.actor import Actor


# @dataclass
# class TableSimpleSelectArgs: ...


# class TableSimpleSelectActor(Actor[TableSimpleSelectArgs]):

#     def forward(self, tables: Sequence[RawTable]) -> RawTable:
#         return tables[0]
