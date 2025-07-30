import copy
import re
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from drepr.models.attr import Attr
from drepr.models.parsers.interface import PathParser
from drepr.models.parsers.v1.attr_parser import AttrParser, ParsedAttrs
from drepr.models.resource import Resource
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


@dataclass
class SMParseContext:
    nodes: dict[str, ClassNode | DataNode | LiteralNode] = field(default_factory=dict)
    edges: dict[int, Edge] = field(default_factory=dict)
    prefixes: dict[str, str] = field(default_factory=dict)


class SMParser:
    """
    This SemanticModel parser supports various ways to define a semantic model.

    ```
    semantic_model:
      <class_id>:
        [id]: <class_id>
        [uri]: <uri>
        [properties]: <properties>
        [links]: <links>
        [static_properties]: <static_properties>
        [inverse_static_properties]: <inverse_static_properties>
        [subject]: <attr>
      prefixes:
        <prefix>: <absolute uri>
    ```

    where:

    * <class_id>: (optional) is the id of the class. It can be specified via the key or as in a separate field named <id>
    * <uri> (optional): if not provided, we extract the URI from the class_id and the class id
    must have the following format: <prefix>:<name>:<alphanumeric & _> where <prefix>:<name> is
    used to create the URI.
    * <properties>: (optional)
        1. If it is a list, each item can be either:
            a. [<predicate>, <attr>]
            b. [<predicate>, <attr>, <data_type>]
            c. [<predicate>, <attr>, <is_required>]
            d. [<predicate>, <attr>, <data_type>, <is_required>]
        2. If it is a tuple, each item is (<predicate>, value) where value can be either:
            a. { attr: <attr>, [data_type: <data_type=none>], [is_required: <is_required=false>] }
            b. <attr>

        * `<predicate>` is either relative or absolute URI.
        * `<data_type>` is either relative or absolute URI specifying the data type of the property.
        * `<is_required>` is a boolean value specifying whether the property is required or not.
        * `<attr>` is the attribute of the property. It can be either a string for the attribute id or a dictionary
            to construct the attribute on fly. The dictionary will comply with the schema of the attribute.

    * <static_properties>: (optional)
        1. If it is a list, each item can be either:
            a. [<predicate>, <value>]
            b. [<predicate>, <value>, <data_type>]
        2. If it is a dictionary, each item is (<predicate>, item-value) where item-value can be either:
            a. { value: <value>, data_type: <data_type> }
            b. <value>

        * `<predicate>` is either relative or absolute URI.
        * `<data_type>` is either relative or absolute URI specifying the data type of the property.
        * `<value>` is the value of the property. It must be either a string, integer, float, or boolean.

    * <inverse_static_properties>: (optional)
        1. If it is a list, each item can be either:
            a. [<predicate>, <value>]
        2. If it is a tuple, each item is (<predicate>, item-value) where item-value must be a string, integer, float, or boolean.

    * <links>: (optional)
        1. If it is a list, each item can be either:
            a. [<predicate>, <target>]
            a. [<predicate>, <target>, <is_required>]
        2. If it is a tuple, each item is (<predicate>, item-value) where item-value can be either:
            a. { target: <target>, is_required: <is_required> }
            b. <target>
        3. If it is a dict, then it is:
            a. { prop: <predicate>, target: <target>, [is_required: <is_required=false>] }

        * `<predicate>` is either relative or absolute URI.
        * `<is_required>` is a boolean value specifying whether the link is required or not.
        * `<target>` is the target of the link. It can be either a string for the class id or a dictionary
            to construct the class on fly. The dictionary will comply with the schema of the class.

    * <subject> (optional): is the attribute that can be used as subject attribute of the class. It can be either a string
        for the attribute id or a dictionary to construct the attribute on fly. The dictionary will comply with the schema of the attribute.
    """

    CLS_KEYS = {
        "id",
        "uri",
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

    def __init__(
        self,
        default_resource_id: str,
        resources: list[Resource],
        attrs: ParsedAttrs,
        path_parser: PathParser,
        attr_parser: AttrParser,
    ):
        self.default_resource_id = default_resource_id
        self.resources = resources
        self.attrs = attrs
        self.path_parser = path_parser
        self.attr_parser = attr_parser

    def parse(self, sm: dict) -> SemanticModel:
        # deep copy
        sm = copy.deepcopy(sm)
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

        context = SMParseContext(prefixes=prefixes)

        for class_id, class_conf in sm.items():
            self.parse_class(context, class_id, class_conf)

        sm = SemanticModel(context.nodes, context.edges, prefixes)
        # print(sm.nodes)
        # print(sm.edges)

        return sm

    def parse_class(
        self,
        context: SMParseContext,
        class_id: str,
        class_conf: dict,
    ):
        trace0 = f"Parsing class `{class_id}` of the semantic model"
        Validator.must_be_dict(class_conf, trace0)
        Validator.must_be_subset(
            self.CLS_KEYS, class_conf.keys(), "keys of ontology class", trace0
        )

        if "id" in class_conf:
            Validator.must_be_str(class_conf["id"], f"{trace0}\nParsing id")
            if class_id != class_conf["id"]:
                raise InputError(
                    f"{trace0}\nERROR: `id` is different from the class id. Expect to be the same"
                )

        if "uri" in class_conf:
            class_name = class_conf["uri"]
        else:
            try:
                m = self.REG_SM_CLASS.match(class_id)
                assert m is not None
                class_name = m.group(2)
            except Exception as e:
                raise InputError(
                    f"{trace0}\nERROR: invalid class_id `{class_id}`. Expect to be <string>:<alphanumeric & _>"
                )

        classnode = ClassNode(class_id, class_name)
        context.nodes[class_id] = classnode

        clsinfo_keys = [
            "properties",
            "static_properties",
            "inverse_static_properties",
            "links",
        ]
        for key in clsinfo_keys:
            values = class_conf.get(key, [])
            if isinstance(values, dict):
                values = ((k, (k, v)) for k, v in values.items())
            else:
                Validator.must_be_list(values, f"{trace0}\nParsing {key}")
                values = enumerate(values)
            for subkey, val in values:
                trace1 = f"{trace0}\nParsing {key}: {subkey}"

                if key == "properties":
                    self.parse_property(context, class_id, val, trace1)
                elif key == "static_properties":
                    self.parse_static_property(context, class_id, val, trace1)
                elif key == "inverse_static_properties":
                    self.parse_inverse_static_property(context, class_id, val, trace1)
                else:
                    assert key == "links"
                    self.parse_link(context, class_id, val, trace1)

        if "subject" in class_conf:
            trace1 = f"{trace0}\nParsing subject"
            subj_attr = self.create_attr_if_needed(class_conf["subject"], trace1)
            classnode.subject = subj_attr

    def parse_static_property(
        self,
        context: SMParseContext,
        class_id: str,
        prop: tuple | list,
        trace: str,
    ):
        """Parse a static property of a class. Can parse the following format:

        1. If prop is a list, it can be either:
            a. [<predicate>, <value>]
            b. [<predicate>, <value>, <data_type>]
        2. If prop is a tuple, it must be a tuple of (key, val), where val can be either:
            a. { value: <value>, data_type: <data_type> }
            b. <value>

        * `<predicate>` is either relative or absolute URI.
        * `<data_type>` is either relative or absolute URI specifying the data type of the property.
        * `<value>` is the value of the property. It must be either a string, integer, float, or boolean.
        """
        if isinstance(prop, list):
            if len(prop) == 2:
                predicate, value = prop
                data_type = None
            elif len(prop) == 3:
                predicate, value, data_type = prop
            else:
                raise InputError(
                    f"{trace}\nERROR: Expect each value of `static_properties` to be an array of two "
                    f"or three items (<predicate>, <value>, [data_type=none])"
                )
        else:
            if not isinstance(prop, tuple):
                raise InputError(
                    f"{trace}\nERROR: Parser Error. This is not your fault."
                )

            predicate, conf = prop
            if isinstance(conf, dict):
                Validator.must_be_subset(
                    {
                        "value",
                        "data_type",
                    },
                    conf.keys(),
                    "keys of property",
                    trace,
                )
                Validator.must_have(conf, "value", f"{trace}\n`value` is required")
                value = conf["value"]
                data_type = conf.get("data_type", None)
            else:
                value = conf
                data_type = None

        if not isinstance(value, (str, int, float, bool)):
            raise InputError(
                f"{trace}\nERROR: Value of the static property must be either a string, integer, float, or boolean"
            )
        if isinstance(value, str):
            value = str(value)
        elif isinstance(value, int):
            value = int(value)
        elif isinstance(value, float):
            value = float(value)

        if data_type is not None:
            Validator.must_be_str(data_type, f"{trace}\nParsing data type")
            try:
                data_type = DataType(data_type, context.prefixes)
            except Exception as e:
                raise InputError(f"{trace}\nERROR: {str(e)}")

        if data_type == DREPR_URI:
            assert isinstance(value, str)
            # test if the value is relative uri, if so, convert it to absolute uri
            if NamespaceMixin.is_rel_iri(value):
                value = get_abs_iri(context.prefixes, value)

        node = LiteralNode(
            node_id=f"lnode:{len(context.nodes)}", value=value, data_type=data_type
        )
        context.nodes[node.node_id] = node
        context.edges[len(context.edges)] = Edge(
            len(context.edges), class_id, node.node_id, predicate
        )

    def parse_property(
        self,
        context: SMParseContext,
        class_id: str,
        prop: tuple | list,
        trace: str,
    ):
        """Parse a property of a class. Can parse the following format:

        1. If prop is a list, it can be either:
            a. [<predicate>, <attr>]
            b. [<predicate>, <attr>, <data_type>]
            c. [<predicate>, <attr>, <is_required>]
            d. [<predicate>, <attr>, <data_type>, <is_required>]
        2. If prop is a tuple, it must be a tuple of (key, value), where value can be either:
            a. { attr: <attr>, [data_type: <data_type=none>], [is_required: <is_required=false>] }
            b. <attr>

        * `<predicate>` is either relative or absolute URI.
        * `<data_type>` is either relative or absolute URI specifying the data type of the property.
        * `<is_required>` is a boolean value specifying whether the property is required or not.
        * `<attr>` is the attribute of the property. It can be either a string for the attribute id or a dictionary
            to construct the attribute on fly. The dictionary will comply with the schema of the attribute.
        """
        if isinstance(prop, list):
            if len(prop) == 2:
                predicate, attr = prop
                data_type = None
                is_required = False
            elif len(prop) == 3:
                predicate, attr, data_type = prop
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
                predicate, attr, data_type, is_required = prop
            else:
                raise InputError(
                    f"{trace}\nERROR: Expect each value of `properties` to be an array of two "
                    f"three or four items (<predicate>, <attribute_id>[, data_type=none][, is_required=false])"
                )
        else:
            if not isinstance(prop, tuple):
                raise InputError(
                    f"{trace}\nERROR: Parser Error. This is not your fault."
                )

            predicate, conf = prop
            if isinstance(conf, (str, list)):
                attr = conf
                data_type = None
                is_required = False
            else:
                Validator.must_be_dict(conf, trace)
                if "attr" in conf:
                    Validator.must_be_subset(
                        {
                            "attr",
                            "data_type",
                            "is_required",
                        },
                        conf.keys(),
                        "keys of property",
                        trace,
                    )
                    Validator.must_have(conf, "attr", f"{trace}\n`attr` is required")
                    attr = conf["attr"]
                    data_type = conf.get("data_type", None)
                    is_required = conf.get("is_required", False)
                else:
                    Validator.must_be_subset(
                        AttrParser.CLS_KEYS, conf.keys(), "keys of attribute", trace
                    )
                    attr = conf
                    data_type = None
                    is_required = False

        if data_type is not None:
            Validator.must_be_str(data_type, f"{trace}\nParsing data type")
            try:
                data_type = DataType(data_type, context.prefixes)
            except Exception as e:
                raise InputError(f"{trace}\nERROR: {str(e)}")

        Validator.must_be_bool(is_required, f"{trace}\nParsing is_required")

        attr_id = self.create_attr_if_needed(attr, trace)
        node = DataNode(
            node_id=f"dnode:{attr_id}", attr_id=attr_id, data_type=data_type
        )
        context.nodes[node.node_id] = node
        context.edges[len(context.edges)] = Edge(
            len(context.edges),
            class_id,
            node.node_id,
            predicate,
            is_required=is_required,
        )

    def parse_inverse_static_property(
        self,
        context: SMParseContext,
        class_id: str,
        prop: tuple | list,
        trace: str,
    ):
        """Parse an inverse static property of a class. Can parse the following format:

        1. If prop is a list, it can be either:
            a. [<predicate>, <value>]
        2. If prop is a tuple, it must be a tuple of (key, value).

        * `<predicate>` is either relative or absolute URI.
        * `<value>` is the value of the property. It must be either a string, integer, float, or boolean.
        """
        if isinstance(prop, list):
            if len(prop) == 2:
                predicate, value = prop
            else:
                raise InputError(
                    f"{trace}\nERROR: Expect each value of `inverse_static_properties` to be an array of two (<predicate>, <value>)"
                )
        else:
            if not isinstance(prop, tuple):
                raise InputError(
                    f"{trace}\nERROR: Parser Error. This is not your fault."
                )

            predicate, value = prop

        Validator.must_be_str(value, f"{trace}\nParsing value")
        if NamespaceMixin.is_rel_iri(value):
            value = get_abs_iri(context.prefixes, value)

        node = LiteralNode(
            node_id=f"lnode:{len(context.nodes)}",
            value=value,
            data_type=PredefinedDataType.drepr_uri.value,
        )
        context.nodes[node.node_id] = node
        context.edges[len(context.edges)] = Edge(
            len(context.edges), class_id, node.node_id, predicate
        )

    def parse_link(
        self,
        context: SMParseContext,
        class_id: str,
        link: tuple | list | dict,
        trace: str,
    ):
        """Parse a link of a class. Can parse the following format:

        1. If link is a list, it can be either:
            a. [<predicate>, <target>]
            a. [<predicate>, <target>, <is_required>]
        2. If link is a tuple, it must be a tuple of (key, value), where value can be either:
            a. { target: <target>, is_required: <is_required> }
            b. <target>

        * `<predicate>` is either relative or absolute URI.
        * `<is_required>` is a boolean value specifying whether the link is required or not.
        * `<target>` is the target of the link. It can be either a string for the class id or a dictionary
            to construct the class on fly. The dictionary will comply with the schema of the class.
        """
        if isinstance(link, list):
            if len(link) == 2:
                predicate, target = link
                is_required = False
            elif len(link) == 3:
                predicate, target, is_required = link
            else:
                raise InputError(
                    f"{trace}\nERROR: Expect each value of `links` to be an array of two "
                    f"or three items (<predicate>, <target>[, is_required=false])"
                )
        elif isinstance(link, dict):
            Validator.must_be_subset(
                {
                    "prop",
                    "target",
                    "is_required",
                },
                link.keys(),
                "keys of link",
                trace,
            )
            Validator.must_have(link, "prop", f"{trace}\n`prop` is required")
            Validator.must_have(link, "target", f"{trace}\n`target` is required")
            predicate = link["prop"]
            target = link["target"]
            is_required = link.get("is_required", False)
        else:
            if not isinstance(link, tuple):
                raise InputError(
                    f"{trace}\nERROR: Parser Error. This is not your fault."
                )

            predicate, conf = link
            if isinstance(conf, dict):
                if "target" in conf:
                    Validator.must_be_subset(
                        {
                            "target",
                            "is_required",
                        },
                        conf.keys(),
                        "keys of link",
                        trace,
                    )
                    Validator.must_have(
                        conf, "target", f"{trace}\n`target` is required"
                    )
                    target = conf["target"]
                    is_required = conf.get("is_required", False)
                else:
                    # construct the class on fly
                    Validator.must_be_subset(
                        self.CLS_KEYS, conf.keys(), "keys of class", trace
                    )
                    target = conf
                    is_required = False
            else:
                Validator.must_be_str(conf, f"{trace}\nParsing target")
                target = conf
                is_required = False

        Validator.must_be_bool(is_required, f"{trace}\nParsing is_required")

        if not isinstance(target, str):
            Validator.must_be_dict(target, f"{trace}\nParsing target")
            # construct the class on fly
            if "id" in target:
                target_class_id = target["id"]
            else:
                target_class_id = f'{target["uri"]}:{len(context.nodes)}'

            self.parse_class(context, target_class_id, target)
        else:
            target_class_id = target

        context.edges[len(context.edges)] = Edge(
            len(context.edges),
            class_id,
            target_class_id,
            predicate,
            is_required=is_required,
        )

    def create_attr_if_needed(self, attr: Any, trace: str):
        if isinstance(attr, str) and attr[0] != "$":
            if not self.attrs.has_been_reference_before(attr):
                raise InputError(
                    f"{trace}\nAttribute {attr} is not defined yet. If you want to create it on fly with only `path`, please use list format for the attribute path"
                )
            return attr

        # construct the attribute on fly
        if isinstance(attr, str):
            # attribute path -- only work if only a single resource
            if len(self.resources) > 1:
                raise InputError(
                    f"{trace}\nERROR: Cannot create an attribute only from path in a multi-resource environment"
                )

            path = self.path_parser.parse(self.resources[0], attr, trace)
            newattr = Attr(
                str(uuid4()).replace("-", "_"),
                self.default_resource_id,
                path,
                missing_values=[],
            )
        else:
            trace1 = f"{trace}\nParsing attribute"
            Validator.must_be_dict(attr, trace1)
            Validator.must_have(attr, "id", trace1)
            Validator.must_be_str(attr["id"], f"{trace1}\nParsing attribute id")

            attr_id = attr["id"]
            if self.attrs.has_been_reference_before(attr_id):
                raise InputError(f"{trace1}\nERROR: Duplicated attribute id: {attr_id}")
            newattr = self.attr_parser.parse_expanded_def(
                self.default_resource_id, self.resources, attr_id, attr, trace1
            )

        self.attrs.add(newattr)
        return newattr.id
