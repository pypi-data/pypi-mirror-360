from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from drepr.models.attr import Attr
from drepr.models.path import Path
from drepr.models.resource import Resource


@dataclass
class POutput:
    resource_id: Optional[str]
    attr: Optional[str]
    attr_path: Optional[Path]


@dataclass
class PMap:
    resource_id: str
    path: Path
    code: str
    output: Optional[POutput] = None
    change_structure: Optional[bool] = None


@dataclass
class PFilter:
    resource_id: str
    path: Path
    code: str
    output: Optional[POutput] = None


@dataclass
class PSplit:
    resource_id: str
    path: Path
    code: str
    output: Optional[POutput] = None


class RMapFunc(Enum):
    Dict2Items = "dict2items"


@dataclass
class RMap:
    resource_id: str
    path: Path
    func_id: RMapFunc
    output: Optional[POutput] = None


class PreprocessingType(Enum):
    pmap = "pmap"
    pfilter = "pfilter"
    psplit = "psplit"
    rmap = "rmap"


@dataclass
class Preprocessing:
    type: PreprocessingType
    value: Union[PMap, PFilter, PSplit, RMap]

    @staticmethod
    def deserialize(raw: dict):
        type = PreprocessingType(raw["type"])
        raw["value"]["path"] = Path.deserialize(raw["value"]["path"])
        if type == PreprocessingType.pmap:
            value = PMap(**raw["value"])
        elif type == PreprocessingType.pfilter:
            value = PFilter(**raw["value"])
        elif type == PreprocessingType.psplit:
            value = PSplit(**raw["value"])
        elif type == PreprocessingType.rmap:
            value = RMap(**raw["value"])
        else:
            raise NotImplementedError()

        return Preprocessing(type, value)

    def set_output(self, output: POutput):
        if self.type in (
            PreprocessingType.pmap,
            PreprocessingType.pfilter,
            PreprocessingType.psplit,
            PreprocessingType.rmap,
        ):
            self.value.output = output
        else:
            raise NotImplementedError(self.type)

    def get_output(self) -> Optional[POutput]:
        if self.type in (
            PreprocessingType.pmap,
            PreprocessingType.pfilter,
            PreprocessingType.psplit,
            PreprocessingType.rmap,
        ):
            return self.value.output
        else:
            raise NotImplementedError(self.type)

    def is_output_new_data(self) -> bool:
        """Check if the preprocessing will generate new data. The new data is stored in a new variable"""
        if self.type == PreprocessingType.pmap:
            assert isinstance(self.value, PMap)
            return self.value.output is not None
        elif self.type == PreprocessingType.pfilter:
            assert isinstance(self.value, PFilter)
            return self.value.output is not None
        elif self.type == PreprocessingType.psplit:
            assert isinstance(self.value, PSplit)
            return self.value.output is not None
        elif self.type == PreprocessingType.rmap:
            assert isinstance(self.value, RMap)
            return self.value.output is not None
        else:
            raise NotImplementedError()

    def get_resource_id(self):
        if self.type == PreprocessingType.pmap:
            assert isinstance(self.value, PMap)
            return self.value.resource_id
        elif self.type == PreprocessingType.pfilter:
            assert isinstance(self.value, PFilter)
            return self.value.resource_id
        elif self.type == PreprocessingType.psplit:
            assert isinstance(self.value, PSplit)
            return self.value.resource_id
        elif self.type == PreprocessingType.rmap:
            assert isinstance(self.value, RMap)
            return self.value.resource_id
        else:
            raise NotImplementedError()


class Context:
    """A special instance that is accessible when user defined function is called to allow access to
    other information such as the index of the current item, or the nearby items.
    """

    def get_index(self) -> tuple:
        """Get the index of the current item"""
        raise NotImplementedError()

    def get_value(self, index: tuple):
        """Get the value of an item at a specific index"""
        raise NotImplementedError()
