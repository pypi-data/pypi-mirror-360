from __future__ import annotations

import os
from typing import Any, Optional

import orjson
from drepr.models.sm import DREPR_URI
from drepr.utils.namespace_mixin import NamespaceManager
from drepr.writers.base import StreamClassWriter
from rdflib import RDF, XSD, BNode, Literal, URIRef
from rdflib.plugins.serializers.nt import NTSerializer, _quote_encode, _quoteLiteral

SubjVal = str | tuple | int | bool
XSD_string = XSD.string


class MyLiteral(Literal):
    def n3(self, namespace_manager: Optional[NamespaceManager] = None):
        encoded = orjson.dumps(self).decode()

        if self.language:
            return "%s@%s" % (encoded, self.language)
        elif self.datatype:
            if namespace_manager is not None:
                quoted_dt = namespace_manager.normalizeUri(self.datatype)
            else:
                quoted_dt = "<%s>" % self.datatype
            return "%s^^%s" % (encoded, quoted_dt)
        else:
            return encoded


class TurtleWriter(StreamClassWriter):
    def __init__(self, prefixes: dict[str, str], normalize_uri: Optional[bool] = None):
        if normalize_uri is None:
            normalize_uri = bool(
                int(os.environ.get("drepr.writer.turtle_writer.normalize_uri", "1"))
            )

        self.write_stream = []
        if normalize_uri:
            self.namespace_manager = NamespaceManager.from_prefix2ns(prefixes)
            for prefix in prefixes:
                self.write_stream.append(f"@prefix {prefix}: <{prefixes[prefix]}> .\n")
            self.write_stream.append("\n")
        else:
            self.namespace_manager = None
        self.written_records: dict[SubjVal, BNode | URIRef] = {}
        self.origin_subj: SubjVal = ""
        self.subj: Optional[URIRef | BNode] = None
        self.buffer: list[tuple[URIRef, URIRef | BNode | Literal]] = []
        self.is_buffered: bool = False
        # whether the current subject has any data or not
        # if the subject has URI, then it has data
        self.subj_has_data: bool = False

    def has_written_record(self, subj: SubjVal) -> bool:
        return subj in self.written_records

    def begin_record(
        self, class_uri: str, subj: SubjVal, is_blank: bool, is_buffered: bool
    ):
        self.origin_subj = subj
        if is_blank:
            if subj in self.written_records:
                self.subj = self.written_records[subj]
                self.subj_has_data = True
            else:
                self.subj = BNode()
                self.subj_has_data = False
        else:
            # subj will be a string for URIRef
            self.subj = URIRef(subj)  # type: ignore
            self.subj_has_data = True

        if is_buffered:
            self.buffer = [(RDF.type, URIRef(class_uri))]
        else:
            self.write_triple(self.subj, RDF.type, URIRef(class_uri))
        self.is_buffered = is_buffered
        self.subj_has_data = False

    def end_record(self):
        if self.subj is None:
            # has been aborted
            return

        if len(self.buffer) > 0:
            pred, obj = self.buffer[0]
            self.write_triple(self.subj, pred, obj)
            for i in range(1, len(self.buffer)):
                pred, obj = self.buffer[i]
                self.write_pred_obj(pred, obj)
            self.buffer = []
        self.write_stream[-1] = " .\n\n"
        self.written_records[self.origin_subj] = self.subj
        self.subj = None
        self.subj_has_data = False

    def abort_record(self):
        """Abort the record that is being written"""
        self.subj = None
        self.subj_has_data = False
        self.buffer = []

    def is_record_empty(self) -> bool:
        return not self.subj_has_data

    def write_data_property(self, predicate_id: str, value: Any, dtype: Optional[str]):
        if self.subj is None:
            return
        if dtype == DREPR_URI:
            value = URIRef(value)
        else:
            # to handle a bug in RDFlib that does not serialize integer properly.
            if (
                dtype == "http://www.w3.org/2001/XMLSchema#integer"
                or dtype == "http://www.w3.org/2001/XMLSchema#long"
                or dtype == "http://www.w3.org/2001/XMLSchema#int"
            ):
                value = int(float(value))
            value = MyLiteral(value, datatype=dtype)

        self.subj_has_data = True
        if self.is_buffered:
            self.buffer.append((URIRef(predicate_id), value))
        else:
            assert self.subj is not None
            self.write_pred_obj(URIRef(predicate_id), value)

    def write_object_property(
        self,
        predicate_id: str,
        object: SubjVal,
        is_subject_blank: bool,
        is_object_blank: bool,
        is_new_subj: bool,
    ):
        if self.subj is None:
            return
        object = self.written_records[object]
        self.subj_has_data = True
        if self.is_buffered:
            self.buffer.append((URIRef(predicate_id), object))
        else:
            assert self.subj is not None
            self.write_pred_obj(URIRef(predicate_id), object)

    def write_to_string(self):
        return "".join(self.write_stream)

    def write_to_file(self, filepath):
        with open(filepath, "w") as f:
            for s in self.write_stream:
                f.write(s)

    def write_triple(self, subj: URIRef | BNode, pred, obj):
        self.write_stream.append(subj.n3(self.namespace_manager))  # type: ignore
        self.write_stream.append(" ")
        self.write_stream.append(pred.n3(self.namespace_manager))
        self.write_stream.append(" ")
        self.write_stream.append(obj.n3(self.namespace_manager))
        self.write_stream.append(" ;\n")

    def write_pred_obj(self, pred, obj):
        self.write_stream.append("\t")
        self.write_stream.append(pred.n3(self.namespace_manager))
        self.write_stream.append(" ")
        self.write_stream.append(obj.n3(self.namespace_manager))
        self.write_stream.append(" ;\n")
