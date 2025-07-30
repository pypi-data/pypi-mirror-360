from __future__ import annotations

from typing import Sequence

from libactor.typing import T


def select_table(tables: Sequence[T], idx: int) -> T:
    return tables[idx]
