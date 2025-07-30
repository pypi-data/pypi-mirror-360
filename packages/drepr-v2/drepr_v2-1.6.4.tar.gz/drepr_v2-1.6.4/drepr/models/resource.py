from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, TypeAlias, Union

ResourceId: TypeAlias = str


class ResourceType(Enum):
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    Spreadsheet = "spreadsheet"
    NetCDF4 = "netcdf4"
    NetCDF3 = "netcdf3"
    GeoTIFF = "geotiff"
    NPDict = "np-dict"
    Shapefile = "shapefile"
    Container = "container"


@dataclass
class CSVProp:
    delimiter: str = ","


# @dataclass
# class SpreadsheetProp:
#     worksheet: Optional[str] = None


@dataclass
class Resource:
    id: ResourceId
    type: ResourceType
    prop: Optional[CSVProp] = None

    @staticmethod
    def deserialize(raw: dict):
        if raw["type"] == ResourceType.CSV.value and raw["prop"] is not None:
            prop = CSVProp(raw["prop"]["delimiter"])
        else:
            prop = None
        return Resource(raw["id"], ResourceType(raw["type"]), prop)


@dataclass
class PreprocessResourceOutput(Resource):
    original_resource_id: str = ""

    def __init__(self, resource_id: str, original_resource_id: str):
        super().__init__(id=resource_id, type=ResourceType.Container, prop=None)
        self.original_resource_id = original_resource_id

    def get_preprocessing_original_resource_id(self):
        return self.original_resource_id


class ResourceData(ABC):

    @abstractmethod
    def to_dict(self):
        pass


@dataclass
class ResourceDataFile(ResourceData):
    file: str

    def to_dict(self):
        return {"file": self.file}


@dataclass
class ResourceDataString(ResourceData):
    value: Union[str, bytes]

    def as_str(self):
        if isinstance(self.value, bytes):
            return self.value.decode()
        else:
            assert isinstance(self.value, str)
            return self.value

    def to_dict(self):
        return {
            "string": (
                self.value.decode() if isinstance(self.value, bytes) else self.value
            )
        }


@dataclass
class ResourceDataObject(ResourceData):
    value: dict | list

    def to_dict(self):
        return {"object": self.value}
