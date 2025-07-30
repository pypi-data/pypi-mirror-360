from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, TypeAlias, Union

from drepr.models.path import Path
from drepr.models.resource import ResourceId


class Sorted(Enum):
    Null = "none"
    Ascending = "ascending"
    Descending = "descending"


class ValueType(Enum):
    UnspecifiedSingle = "unspecified-single"
    Int = "int"
    Float = "float"
    String = "str"
    List_Int = "list[int]"
    List_Float = "list[float]"
    List_String = "list[str]"

    def is_list(self) -> bool:
        return self in (
            ValueType.List_Int,
            ValueType.List_Float,
            ValueType.List_String,
        )


MISSING_VALUE_TYPE = Optional[Union[str, int, float]]
AttrId: TypeAlias = str


@dataclass
class Attr:
    id: AttrId
    resource_id: ResourceId
    path: Path
    missing_values: list[MISSING_VALUE_TYPE]
    unique: bool = False
    sorted: Sorted = Sorted.Null
    value_type: ValueType = ValueType.UnspecifiedSingle

    @staticmethod
    def deserialize(raw: dict) -> "Attr":
        attr = Attr(**raw)
        attr.path = Path.deserialize(raw["path"])
        attr.sorted = Sorted(attr.sorted)
        attr.value_type = ValueType(attr.value_type)

        return attr
