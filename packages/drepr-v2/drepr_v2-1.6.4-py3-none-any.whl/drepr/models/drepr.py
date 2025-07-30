from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any, Optional, Union

import orjson
from drepr.models.align import (
    AlignedStep,
    Alignment,
    AlignmentType,
    AutoAlignment,
    IdenticalAlign,
    RangeAlignment,
    ValueAlignment,
)
from drepr.models.attr import Attr
from drepr.models.parsers.v1 import ReprV1Parser
from drepr.models.parsers.v2 import ReprV2Parser
from drepr.models.parsers.v3 import ReprV3Parser
from drepr.models.preprocessing import PFilter, PMap, Preprocessing, PSplit, RMap
from drepr.models.resource import CSVProp, Resource, ResourceType
from drepr.models.sm import ClassNode, DataNode, LiteralNode, SemanticModel
from drepr.utils.validator import InputError, Validator
from ruamel.yaml import YAML

yaml = YAML()
yaml.Representer.add_representer(OrderedDict, yaml.Representer.represent_dict)


@dataclass
class EngineFormat:
    model: dict[str, Any]
    edges_optional: list[bool]
    resource_idmap: dict[str, int]
    attribute_idmap: dict[str, int]
    sm_node_idmap: dict[str, int]


@dataclass
class DRepr:
    resources: list[Resource]
    preprocessing: list[Preprocessing]
    attrs: list[Attr]
    aligns: list[Alignment]
    sm: SemanticModel

    @staticmethod
    def parse(raw: dict) -> "DRepr":
        Validator.must_have(raw, "version", "Parsing D-REPR configuration")
        raw["version"] = str(raw["version"])
        if raw["version"] == "1":
            model = ReprV1Parser.parse(raw)
            model.assert_valid()
            return model
        elif raw["version"] == "2":
            model = ReprV2Parser.parse(raw)
            model.assert_valid()
            return model
        elif raw["version"] == "3":
            model = ReprV3Parser.parse(raw)
            model.assert_valid()
            return model
        raise InputError(f"Parsing error, get unknown version: {raw['version']}")

    @staticmethod
    def parse_from_file(fpath: Union[Path, str]) -> "DRepr":
        fpath = str(fpath)
        if fpath.endswith(".json"):
            with open(fpath, "rb") as f:
                return DRepr.parse(orjson.loads(f.read()))

        if fpath.endswith(".yml") or fpath.endswith(".yaml"):
            with open(fpath, "r") as f:
                return DRepr.parse(yaml.load(f))

        raise Exception(
            f"Does not supported this file: {fpath}. Only support json or yaml file"
        )

    @staticmethod
    def empty() -> "DRepr":
        return DRepr([], [], [], [], SemanticModel({}, {}, {}))

    @staticmethod
    def deserialize(raw: dict) -> "DRepr":
        resources = [Resource.deserialize(o) for o in raw["resources"]]
        preprocessing = [Preprocessing.deserialize(o) for o in raw["preprocessing"]]
        attrs = [Attr.deserialize(o) for o in raw["attrs"]]
        aligns = []

        for align in raw["aligns"]:
            if align["type"] == AlignmentType.Range.value:
                aligns.append(
                    RangeAlignment(
                        align["source"],
                        align["target"],
                        [
                            AlignedStep(step["source_idx"], step["target_idx"])
                            for step in align["aligned_steps"]
                        ],
                    )
                )
            elif align["type"] == AlignmentType.Value.value:
                aligns.append(ValueAlignment(align["source"], align["target"]))
            else:
                raise NotImplementedError()
        sm = SemanticModel.deserialize(raw["sm"])

        return DRepr(resources, preprocessing, attrs, aligns, sm)

    def serialize(self) -> dict:
        obj = asdict(self)
        # post-process the enum
        for res in obj["resources"]:
            res["type"] = res["type"].value
        for prepro in obj["preprocessing"]:
            prepro["type"] = prepro["type"].value
            for i, step in enumerate(prepro["value"]["path"]["steps"]):
                if isinstance(step, Enum):
                    prepro["value"]["path"]["steps"][i] = step.value

        for attr in obj["attrs"]:
            attr["sorted"] = attr["sorted"].value
            for i, step in enumerate(attr["path"]["steps"]):
                if isinstance(step, Enum):
                    attr["steps"][i] = step.value

            attr["value_type"] = attr["value_type"].value
        for node in obj["sm"]["nodes"].values():
            if node.get("data_type", None) is not None:
                node["data_type"] = node["data_type"].get_rel_uri()

        # adding a bit of meta-data about the alignment
        for align, raw_align in zip(self.aligns, obj["aligns"]):
            if isinstance(align, RangeAlignment):
                raw_align["type"] = AlignmentType.Range.value
            elif isinstance(align, ValueAlignment):
                raw_align["type"] = AlignmentType.Value.value
            else:
                raise NotImplementedError()

        # similarly, add meta-data about the nodes
        for node in obj["sm"]["nodes"].values():
            if isinstance(self.sm.nodes[node["node_id"]], ClassNode):
                node["type"] = "class_node"
            elif isinstance(self.sm.nodes[node["node_id"]], DataNode):
                node["type"] = "data_node"
            elif isinstance(self.sm.nodes[node["node_id"]], LiteralNode):
                node["type"] = "literal_node"
            else:
                raise NotImplementedError()

        return obj

    def assert_valid(self):
        """
        Perform a check to see if this D-REPR is valid. Raise AssertionError if this is not valid
        """
        # CHECK 1: all references (resource id, attribute ids) are valid
        resource_ids = {r.id for r in self.resources}

        attr_ids = {attr.id for attr in self.attrs}
        assert len(attr_ids) == len(self.attrs), "Duplicate attribute ids"
        for attr in self.attrs:
            assert (
                attr.resource_id in resource_ids
            ), f"Attribute {attr.resource_id} does not belong to any resources"

        for pref in self.preprocessing:
            if pref.value.output is not None:
                if pref.value.output.resource_id is not None:
                    assert (
                        pref.value.output.resource_id not in resource_ids
                    ), f"Preprocessing {pref} overwrite existence resource: {pref.value.output.resource_id}"
                if pref.value.output.attr is not None:
                    # preprocessing create new attribute
                    assert (
                        pref.value.output.attr not in attr_ids
                    ), f"Cannot overwrite existing attribute: {pref.value.output.attr}"
                    attr_ids.add(pref.value.output.attr)

        for align in self.aligns:
            if isinstance(align, AutoAlignment):
                if align.attrs is not None:
                    assert all(
                        attr_id in attr_ids for attr_id in align.attrs
                    ), f"The alignment {align} links to non-existence attributes"
            else:
                assert (
                    not isinstance(align, IdenticalAlign)
                    and align.source in attr_ids
                    and align.target in attr_ids
                ), f"The alignment {align} links to non-existence attributes"

        for node in self.sm.nodes.values():
            if isinstance(node, DataNode):
                assert node.attr_id in attr_ids, (
                    f"The semantic model has a link to "
                    f"a non-existence attribute: {node.attr_id}"
                )

        # CHECK 2: check class and predicates are valid
        for node in self.sm.nodes.values():
            if isinstance(node, ClassNode):
                if self.sm.is_rel_iri(node.label):
                    prefix = node.label.split(":", 1)[0]
                    assert prefix in self.sm.prefixes, (
                        f"Unknown prefix `{prefix}` of the "
                        f"ontology class {node.label}"
                    )
        for edge in self.sm.edges.values():
            if self.sm.is_rel_iri(edge.label):
                prefix = edge.label.split(":", 1)[0]
                assert prefix in self.sm.prefixes, (
                    f"Unknown prefix `{prefix}` of the "
                    f"ontology predicate {edge.label}"
                )
            assert edge.source_id in self.sm.nodes, edge
            assert edge.target_id in self.sm.nodes, edge

    def to_lang_format(
        self, simplify: bool = True, use_json_path: bool = False
    ) -> dict:
        return ReprV2Parser.dump(self, simplify, use_json_path)

    def to_lang_yml(self, simplify: bool = True, use_json_path: bool = False) -> str:
        model = self.to_lang_format(simplify, use_json_path)
        out = StringIO()
        yaml.dump(model, out)
        return out.getvalue()

    def _serde_engine_value(self, value: Any):
        """Serialize a python value to a json representation of the Value struct in the Rust engine"""
        if value is None:
            return {"t": "Null"}
        elif isinstance(value, bool):
            return {"t": "Bool", "c": value}
        elif isinstance(value, int):
            return {"t": "I64", "c": value}
        elif isinstance(value, float):
            return {"t": "F64", "c": value}
        elif isinstance(value, str):
            return {"t": "Str", "c": value}
        elif isinstance(value, list):
            return {"t": "Array", "c": [self._serde_engine_value(v) for v in value]}
        elif isinstance(value, (dict, OrderedDict)):
            return {
                "t": "Object",
                "c": {k: self._serde_engine_value(v) for k, v in value.items()},
            }
        else:
            raise InputError(
                f"Cannot serialize the value of type: {type(value)} to JSON"
            )

    def remove_resource(self, resource_id: str):
        self.resources = [r for r in self.resources if r.id != resource_id]
        for i in range(len(self.preprocessing) - 1, -1, -1):
            if self.preprocessing[i].value.resource_id == resource_id:
                self.preprocessing.pop(i)

        for i in range(len(self.attrs) - 1, -1, -1):
            if self.attrs[i].resource_id == resource_id:
                self.remove_attribute(self.attrs[i].id, idx=i)

    def get_resource_by_id(self, resource_id: str) -> Optional[Resource]:
        for r in self.resources:
            if r.id == resource_id:
                return r
        return None

    def add_resource(self, resource: Resource):
        assert self.get_resource_by_id(resource.id) is None
        self.resources.append(resource)

    def has_attr(self, attr_id: str) -> bool:
        return any(a.id == attr_id for a in self.attrs)

    def add_attr(self, attr: Attr):
        if self.has_attr(attr.id):
            raise KeyError(f"Attribute with id {attr.id} already exists")
        self.attrs.append(attr)

    def get_attr_index_by_id(self, attr_id: str) -> int:
        for i, a in enumerate(self.attrs):
            if a.id == attr_id:
                return i
        raise KeyError(f"Attribute with id {attr_id} does not exist")

    def get_attr_by_id(self, attr_id: str) -> Attr:
        for a in self.attrs:
            if a.id == attr_id:
                return a
        raise KeyError(f"Attribute with id {attr_id} does not exist")

    def remove_attribute(self, attr_id: str, idx: Optional[int] = None):
        if idx is None:
            idx = next(
                i for i in range(len(self.attrs), -1, -1) if self.attrs[i].id == attr_id
            )

        self.attrs.pop(idx)
        for i in range(len(self.aligns) - 1, -1, -1):
            align = self.aligns[i]
            if not isinstance(align, AutoAlignment):
                if align.source == attr_id or align.target == attr_id:
                    self.aligns.pop(i)

        for node in self.sm.nodes:
            if isinstance(node, DataNode) and node.attr_id == attr_id:
                self.sm.remove_node(node.node_id)

    def update_attribute(self, attr_id: str, new_attr: Attr):
        for i, attr in enumerate(self.attrs):
            if attr.id == attr_id:
                self.attrs[i] = new_attr

        for align in self.aligns:
            if isinstance(align, AutoAlignment):
                if align.attrs is not None:
                    align.attrs = [
                        new_attr.id if a == attr_id else a for a in align.attrs
                    ]
            else:
                if align.source == attr_id:
                    align.source = new_attr.id
                elif align.target == attr_id:
                    align.target = new_attr.id

        for node in self.sm.nodes:
            if isinstance(node, DataNode) and node.attr_id == attr_id:
                node.attr_id = new_attr.id
