from __future__ import annotations

from dataclasses import dataclass, field
from typing import NotRequired, Optional, Sequence, TypedDict

from rsoup.core import ContentHierarchy
from sm.misc.matrix import Matrix


class RawLink(TypedDict):
    start: int
    end: int
    url: str


class RawCellMetadata(TypedDict):
    colspan: NotRequired[int]
    rowspan: NotRequired[int]
    is_header: NotRequired[bool]
    links: NotRequired[Sequence[RawLink]]


class RawTableMetadata(TypedDict):
    url: NotRequired[str]
    caption: NotRequired[str]


@dataclass
class RawCell:
    value: Optional[str | int | float] = None
    metadata: RawCellMetadata = field(default_factory=RawCellMetadata)

    def to_dict(self):
        return {
            "value": self.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, obj: dict):
        return RawCell(
            value=obj.get("value"),
            metadata=obj.get("metadata", {}),
        )

    def update_value(self, value: Optional[str | int | float]) -> RawCell:
        return RawCell(value=value, metadata=self.metadata)

    def is_missing(self):
        return self.value is None


@dataclass
class RawTable(Matrix[RawCell]):
    id: str
    context: list[ContentHierarchy] = field(default_factory=list)
    metadata: RawTableMetadata = field(default_factory=RawTableMetadata)

    def to_dict(self):
        return {
            "id": self.id,
            "rows": [[cell.to_dict() for cell in row] for row in self.data],
            "context": [c.to_dict() for c in self.context],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            id=obj["id"],
            data=[[RawCell.from_dict(cell) for cell in row] for row in obj["rows"]],
            context=[ContentHierarchy.from_dict(c) for c in obj.get("context", [])],
            metadata=obj.get("metadata", {}),
        )

    def update_data(self, data: list[list[RawCell]]) -> RawTable:
        return RawTable(
            id=self.id,
            data=data,
            context=self.context,
            metadata=self.metadata,
        )
