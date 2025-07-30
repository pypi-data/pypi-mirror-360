import copy
import re

from drepr.models.sm import (
    DREPR_URI,
    ClassNode,
    DataNode,
    DataType,
    Edge,
    LiteralNode,
    PredefinedDataType,
    SemanticModel,
)
from drepr.utils.misc import F, get_abs_iri
from drepr.utils.namespace_mixin import NamespaceMixin
from drepr.utils.validator import InputError, Validator


class SMParser:
    """
    SM has the following schema

    ```
    semantic_model:
      <class_id>:
        properties:
            - [<predicate>, <attr_id>, (<data_type>, (<is_required=false>)?)?]
        links:
            - [<predicate>, <class_id>, (<is_required=false>)?]
        static_properties:
            - [<predicate>, <value>, (<data_type>)?]
        inverse_static_properties:
            - [<predicate>, <uri>]
      prefixes:
        <prefix>: <uri>
    ```
    """

    CLS_KEYS = {
        "properties",
        "subject",
        "links",
        "static_properties",
        "inverse_static_properties",
    }

    REG_SM_CLASS = re.compile(r"^((.+):[a-zA-Z0-9_]+)$")
    REG_SM_DNODE = re.compile(r"^((?:(?!--).)+:\d+)--((?:(?!\^\^).)+)(?:\^\^(.+))?$")
    REG_SM_LNODE = re.compile(
        r"^((?:(?!--).)+:\d+)--((?:(?!--).)+)--((?:(?!\^\^).)+)(?:\^\^(.+))?$"
    )
    REG_SM_REL = re.compile(r"^((?:(?!--).)+:\d+)--((?:(?!--).)+)--((?:(?!--).)+:\d+)$")

    @classmethod
    def parse(cls, sm: dict) -> SemanticModel:
        nodes = {}
        edges = {}
        # shallow copy
        sm = copy.copy(sm)
        prefixes = sm.pop("prefixes", {})

        trace0 = f"Parsing `prefixes` of the semantic model"
        Validator.must_be_dict(prefixes, trace0)
        for prefix, uri in prefixes.items():
            Validator.must_be_str(uri, f"{trace0}\nParse prefix {prefix}")

        for prefix, uri in SemanticModel.get_default_prefixes().items():
            if prefix not in prefixes:
                prefixes[prefix] = uri
            elif prefixes[prefix] != uri:
                raise InputError(
                    f"{trace0}\nERROR: Prefix `{prefix}` is conflicting with predefined value `{uri}`."
                )

        for class_id, class_conf in sm.items():
            trace0 = f"Parsing class `{class_id}` of the semantic model"
            Validator.must_be_dict(class_conf, trace0)
            Validator.must_be_subset(
                cls.CLS_KEYS, class_conf.keys(), "keys of ontology class", trace0
            )

            try:
                m = cls.REG_SM_CLASS.match(class_id)
                assert m is not None
                class_name = m.group(2)
            except Exception as e:
                raise InputError(
                    f"{trace0}\nERROR: invalid class_id `{class_id}`. Expect to be <string>:<alphanumeric & _>"
                )

            nodes[class_id] = ClassNode(class_id, class_name)

        for class_id, class_conf in sm.items():
            trace0 = f"Parsing class `{class_id}` of the semantic model"

            for i, prop in enumerate(class_conf.get("properties", [])):
                trace1 = f"{trace0}\nParsing property {i}: {prop}"
                if len(prop) == 2:
                    predicate, attr_id = prop
                    data_type = None
                    is_required = False
                elif len(prop) == 3:
                    predicate, attr_id, data_type = prop
                    if isinstance(data_type, bool) or data_type.lower() in {
                        "true",
                        "false",
                    }:
                        is_required = (
                            data_type
                            if isinstance(data_type, bool)
                            else data_type == "true"
                        )
                        data_type = None
                    else:
                        is_required = False
                elif len(prop) == 4:
                    predicate, attr_id, data_type, is_required = prop
                else:
                    raise InputError(
                        f"{trace1}\nERROR: Expect value of the property to be an array of two "
                        f"three or four items (<predicate>, <attribute_id>[, data_type='auto'][, is_required=false])"
                    )

                if data_type is not None:
                    try:
                        data_type = DataType(data_type, prefixes)
                    except Exception as e:
                        raise InputError(f"{trace1}\nERROR: {str(e)}")

                node = DataNode(
                    node_id=f"dnode:{attr_id}", attr_id=attr_id, data_type=data_type
                )
                nodes[node.node_id] = node
                edges[len(edges)] = Edge(
                    len(edges),
                    class_id,
                    node.node_id,
                    predicate,
                    is_required=is_required,
                )

            for i, link_conf in enumerate(class_conf.get("links", [])):
                trace1 = f"{trace0}\nParsing link {i}: {link_conf}"
                if not (2 <= len(link_conf) <= 3):
                    raise InputError(
                        f"{trace1}\nERROR: Expect value of the link to be an array of two or three"
                        f"items (<predicate>, <class_id>, <is_required=false>)"
                    )

                if len(link_conf) == 2:
                    predicate, object_class_id = link_conf
                    is_required = False
                else:
                    predicate, object_class_id, is_required = link_conf

                edges[len(edges)] = Edge(
                    len(edges),
                    class_id,
                    object_class_id,
                    predicate,
                    is_required=is_required,
                )

            for i, prop in enumerate(class_conf.get("static_properties", [])):
                trace1 = f"{trace0}\nParsing static properties {i}: {prop}"
                if len(prop) == 2:
                    predicate, value = prop
                    data_type = None
                elif len(prop) == 3:
                    predicate, value, data_type = prop
                else:
                    raise InputError(
                        f"{trace1}\nERROR: Expect value of the property to be an array of two "
                        f"or three items (<predicate>, <value>, [data_type])"
                    )

                if data_type is not None:
                    try:
                        data_type = DataType(data_type, prefixes)
                    except Exception as e:
                        raise InputError(f"{trace1}\nERROR: {str(e)}")

                # normalize value's type (e.g., ruamel.yaml read float into ScalarFloat)
                if isinstance(value, str):
                    value = str(value)
                elif isinstance(value, int):
                    value = int(value)
                elif isinstance(value, float):
                    value = float(value)

                if data_type == DREPR_URI:
                    assert isinstance(value, str)
                    # test if the value is relative uri, if so, convert it to absolute uri
                    if NamespaceMixin.is_rel_iri(value):
                        value = get_abs_iri(prefixes, value)

                node = LiteralNode(
                    node_id=f"lnode:{len(nodes)}", value=value, data_type=data_type
                )
                nodes[node.node_id] = node
                edges[len(edges)] = Edge(len(edges), class_id, node.node_id, predicate)

            for i, prop in enumerate(class_conf.get("inverse_static_properties", [])):
                trace1 = f"{trace0}\nParsing inverse static properties {i}: {prop}"
                if len(prop) == 2:
                    predicate, value = prop
                    data_type = PredefinedDataType.xsd_anyURI.value
                else:
                    raise InputError(
                        f"{trace1}\nERROR: Expect value of the property to be an array of two "
                        f"items (<predicate>, <uri>)"
                    )

                if not isinstance(value, str):
                    raise InputError("Value of inverse static property must be an uri")
                value = str(value)
                node = LiteralNode(
                    node_id=f"lnode:{len(nodes)}", value=value, data_type=data_type
                )
                nodes[node.node_id] = node
                edges[len(edges)] = Edge(len(edges), node.node_id, class_id, predicate)

        for class_id, class_conf in sm.items():
            trace0 = f"Parsing class `{class_id}` of the semantic model"
            if "subject" in class_conf:
                trace1 = f"{trace0}\nParsing subject"
                attr_id = class_conf["subject"]
                nodes[class_id].subject = attr_id

        return SemanticModel(nodes, edges, prefixes)
