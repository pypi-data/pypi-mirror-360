from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Union

from drepr.models.path import Path
from drepr.models.resource import Resource
from drepr.utils.validator import InputError


class PathParser(ABC):
    @abstractmethod
    def parse(
        self, resource: Optional[Resource], path: Union[str, list], parse_trace: str
    ) -> Path:
        pass

    # noinspection PyMethodMayBeStatic
    def get_resource(
        self, resources: List[Resource], resource_id: str, trace: str
    ) -> Resource:
        for res in resources:
            if res.id == resource_id:
                return res
        raise InputError(
            f"{trace}\nERROR: Refer to path of an nonexistent resource: {resource_id}"
        )
