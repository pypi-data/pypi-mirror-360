from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from sys import prefix
from typing import Any, NamedTuple, Optional, TypeAlias, Union

from drepr.models.attr import Attr, AttrId
from drepr.utils.namespace_mixin import NamespaceMixin
from rdflib import OWL, RDF, RDFS, XSD

DREPR_URI = "https://purl.org/drepr/1.0/uri"
DREPR_BLANK = "https://purl.org/drepr/1.0/blank"
NodeId: TypeAlias = str
EdgeId: TypeAlias = int


class PredefinedNamespace(Enum):
    drepr = "https://purl.org/drepr/1.0/"
    rdf = str(RDF)
    rdfs = str(RDFS)
    owl = str(OWL)
    xsd = str(XSD)


class DataType(str):
    prefixes: dict[str, str]

    def __new__(cls, value, prefixes: dict[str, str]):
        if value.find("://") == -1 and value.find(":") != -1:
            # this is relative uri
            prefix, ns = value.split(":", 1)
            assert (
                prefix in prefixes
            ), f"The datatype `{value}` isn't grounded as it's a relative URI and the prefix is unknown {prefix}"
            obj = str.__new__(cls, f"{prefixes[prefix]}{ns}")
        else:
            obj = str.__new__(cls, value)

        obj.prefixes = prefixes
        return obj

    def __getnewargs__(self) -> tuple[str, dict[str, str]]:
        return str(self), self.prefixes

    def get_rel_uri(self):
        for prefix, uri in self.prefixes.items():
            if self.startswith(uri):
                return f"{prefix}:{self.replace(uri, '')}"
        raise ValueError(
            "Cannot create relative URI because there is no suitable prefix"
        )


class PredefinedDataType(Enum):
    xsd_decimal = DataType("xsd:decimal", {"xsd": PredefinedNamespace.xsd.value})
    xsd_anyURI = DataType("xsd:anyURI", {"xsd": PredefinedNamespace.xsd.value})
    xsd_gYear = DataType("xsd:gYear", {"xsd": PredefinedNamespace.xsd.value})
    xsd_date = DataType("xsd:date", {"xsd": PredefinedNamespace.xsd.value})
    xsd_dateTime = DataType("xsd:dateTime", {"xsd": PredefinedNamespace.xsd.value})
    xsd_int = DataType("xsd:int", {"xsd": PredefinedNamespace.xsd.value})
    xsd_string = DataType("xsd:string", {"xsd": PredefinedNamespace.xsd.value})
    drepr_uri = DataType(DREPR_URI, {"drepr": PredefinedNamespace.drepr.value})


@dataclass
class ClassNode:
    node_id: NodeId
    label: str  # relative iri
    subject: Optional[AttrId] = None

    def get_abs_iri(self, sm: SemanticModel):
        """Get the absolute IRI of this node"""
        if sm.is_rel_iri(self.label):
            return sm.get_abs_iri(self.label)
        return self.label

    def get_rel_iri(self, sm: SemanticModel):
        if sm.is_rel_iri(self.label):
            return self.label
        return sm.get_rel_iri(self.label)

    def is_blank_node(self, sm: SemanticModel) -> bool:
        for e in sm.iter_outgoing_edges(self.node_id):
            if e.get_abs_iri(sm) == DREPR_URI:
                return False
        return True


@dataclass
class DataNode:
    node_id: NodeId
    attr_id: AttrId
    data_type: Optional[DataType] = None


@dataclass
class LiteralNode:
    node_id: NodeId
    # you should rely on data_type to get the type of value right. The parser may be wrong about it.
    value: Any
    data_type: Optional[DataType] = None
    # whether to always generate values of the literal node, even if all the other non-literal nodes are missing
    # however, if the parent class node has URI and the URI is missing, we won't generate the literal node
    always_generate: bool = False


@dataclass
class Edge:
    edge_id: EdgeId
    source_id: NodeId
    target_id: NodeId
    label: str  # rel uri
    is_subject: bool = False
    is_required: bool = False

    def get_abs_iri(self, sm: SemanticModel):
        """Get the absolute IRI of the predicate"""
        if sm.is_rel_iri(self.label):
            return sm.get_abs_iri(self.label)
        return self.label

    def get_rel_iri(self, sm: SemanticModel):
        if sm.is_rel_iri(self.label):
            return self.label
        return sm.get_rel_iri(self.label)


Node = Union[LiteralNode, DataNode, ClassNode]


@dataclass
class SemanticModel(NamespaceMixin):
    nodes: dict[NodeId, Node]
    edges: dict[EdgeId, Edge]
    prefixes: dict[str, str]

    @staticmethod
    def get_default(attrs: list[Attr]) -> SemanticModel:
        """
        Automatically generate a semantic model from a list of attributes.

        WARNING: the engine may not able to map data to this semantic model if the final output should be
        comprised of multiple tables.
        """
        prefixes = {"eg": "https://example.org/"}
        aids = {attr.id for attr in attrs}
        cid = None
        for i in range(len(attrs)):
            cid = f"c{i}"
            if cid not in aids:
                break
        assert cid is not None
        nodes: dict[str, Node] = {cid: ClassNode(cid, "eg:Record")}
        edges = {}
        for attr in attrs:
            nodes[attr.id] = DataNode(attr.id, attr.id, None)
            edge_id = len(edges)
            edges[edge_id] = Edge(edge_id, cid, attr.id, f"eg:{attr.id}")

        return SemanticModel(nodes, edges, prefixes)

    @staticmethod
    def get_default_prefixes() -> dict[str, str]:
        return {ns.name: ns.value for ns in list(PredefinedNamespace)}

    @staticmethod
    def deserialize(raw: dict) -> SemanticModel:
        nodes = {}
        for nid, n in raw["nodes"].items():
            if n["type"] == "class_node":
                nodes[nid] = ClassNode(n["node_id"], n["label"])
            elif n["type"] == "data_node":
                nodes[nid] = DataNode(
                    n["node_id"],
                    n["attr_id"],
                    (
                        DataType(n["data_type"], raw["prefixes"])
                        if n["data_type"] is not None
                        else None
                    ),
                )
            elif n["type"] == "literal_node":
                nodes[nid] = LiteralNode(
                    n["node_id"],
                    n["value"],
                    (
                        DataType(n["data_type"], raw["prefixes"])
                        if n["data_type"] is not None
                        else None
                    ),
                )
            else:
                raise NotImplementedError()
        edges = {eid: Edge(**e) for eid, e in raw["edges"].items()}
        return SemanticModel(nodes, edges, raw["prefixes"])

    def get_class_node(self, node_id: NodeId) -> ClassNode:
        node = self.nodes[node_id]
        if not isinstance(node, ClassNode):
            raise ValueError(f"The node {node_id} is not a class node")
        return node

    def remove_node(self, node_id: NodeId) -> Node:
        node = self.nodes.pop(node_id)
        removed_edges = []
        for eid, e in self.edges.items():
            if e.source_id == node_id or e.target_id == node_id:
                removed_edges.append(eid)
        for eid in removed_edges:
            self.edges.pop(eid)
        return node

    def remove_edge(self, edge_id: EdgeId):
        return self.edges.pop(edge_id)

    def class2dict(self, class_id: str) -> dict[str, Union[list[int], int]]:
        """
        Get a dictionary that contains information (predicates) about a given class
        """
        info = {}
        for eid, e in self.edges.items():
            if e.source_id != class_id:
                continue

            if e.label in info:
                if not isinstance(info[e.label], list):
                    info[e.label] = [info[e.label], eid]
                else:
                    info[e.label].append(eid)
            else:
                info[e.label] = eid
        return info

    def iter_class_nodes(self):
        for n in self.nodes.values():
            if isinstance(n, ClassNode):
                yield n

    def iter_outgoing_edges(self, node_id: str):
        for e in self.edges.values():
            if e.source_id == node_id:
                yield e

    def iter_incoming_edges(self, node_id: str):
        for e in self.edges.values():
            if e.target_id == node_id:
                yield e

    def iter_child_nodes(self, node_id: str):
        for e in self.edges.values():
            if e.source_id == node_id:
                yield self.nodes[e.source_id]

    def iter_parent_nodes(self, node_id: str):
        for e in self.edges.values():
            if e.target_id == node_id:
                yield self.nodes[e.target_id]

    def get_n_class_nodes(self) -> int:
        return sum(1 for _ in self.iter_class_nodes())

    def get_edge_between_nodes(self, source_id: str, target_id: str) -> Optional[Edge]:
        matched_edges = []
        for e in self.edges.values():
            if e.source_id == source_id and e.target_id == target_id:
                matched_edges.append(e)

        if len(matched_edges) == 0:
            return None
        elif len(matched_edges) == 1:
            return matched_edges[0]
        else:
            raise ValueError(
                f"Found multiple edges between {source_id} and {target_id}"
            )

    def get_edges_between_nodes(self, source_id: str, target_id: str):
        matched_edges: list[Edge] = []
        for e in self.edges.values():
            if e.source_id == source_id and e.target_id == target_id:
                matched_edges.append(e)
        return matched_edges
