from dataclasses import dataclass, field
from email.policy import default
from typing import List

from drepr.models.attr import Attr, Sorted, ValueType
from drepr.models.parsers.interface import PathParser
from drepr.models.resource import Resource
from drepr.utils.validator import InputError, Validator


@dataclass
class ParsedAttrs:
    attrs: list[Attr] = field(default_factory=list)
    id2attr: dict[str, Attr] = field(default_factory=dict)
    attrs_created_in_preprocessing: set[str] = field(default_factory=set)

    def add(self, attr: Attr):
        if attr.id in self.attrs:
            raise InputError(f"Duplicated attribute id: {attr.id}")

        self.attrs.append(attr)
        self.id2attr[attr.id] = attr

    def add_preprocessing_attr(self, attr_id: str):
        self.attrs_created_in_preprocessing.add(attr_id)

    def has_been_reference_before(self, attr_id: str):
        return attr_id in self.id2attr or attr_id in self.attrs_created_in_preprocessing

    def __contains__(self, id: str):
        return id in self.id2attr

    def __getitem__(self, id: str):
        return self.id2attr[id]


class AttrParser:
    """
    Attributes have two possible schemas
    1. When an attribute has only one path
        ```
        <attr_id>: <attr_path>
        # .. other attributes ..
        ```
    2.
        ```
        <attribute_id>:
            [resource_id]: <resource_id> (default is "default")
            path: <attr_path>
            [unique]: true|false (default is false)
            [sorted]: none|ascending|descending (default is none)
            [value_type]: unspecified|int|float|str|list[int]|list[str]|list[float] (default is unspecified)
            [missing_values]: [<value0>, <value1>, ...]
        ```
    """

    SORTED_VALUES = {x.value for x in Sorted}
    VALUE_TYPE_VALUES = {x.value for x in ValueType}
    CLS_KEYS = {
        "resource_id",
        "path",
        "unique",
        "sorted",
        "value_type",
        "missing_values",
    }

    def __init__(self, path_parser: PathParser):
        self.path_parser = path_parser

    def parse(
        self,
        default_resource_id: str,
        resources: List[Resource],
        parsed_attrs: ParsedAttrs,
        def_attrs: dict,
    ):
        Validator.must_be_dict(def_attrs, "Parsing attributes")
        for attr_id, attr_conf in def_attrs.items():
            trace = f"Parsing attribute: {attr_id}"

            if attr_id in parsed_attrs:
                raise InputError(f"{trace}\nERROR: Duplicated attribute id: {attr_id}")

            if isinstance(attr_conf, (str, list)):
                attr_path = self.path_parser.parse(
                    self.path_parser.get_resource(
                        resources, default_resource_id, trace
                    ),
                    attr_conf,
                    trace,
                )
                attr = Attr(attr_id, default_resource_id, attr_path, [])
            elif isinstance(attr_conf, dict):
                attr = self.parse_expanded_def(
                    default_resource_id, resources, attr_id, attr_conf, trace
                )
            else:
                raise InputError(
                    f"{trace}\nERROR: The configuration of an attribute can either be string, list, "
                    f"or dictionary. Get {type(attr_conf)} instead"
                )

            parsed_attrs.add(attr)

    def parse_expanded_def(
        self,
        default_resource_id: str,
        resources: List[Resource],
        attr_id: str,
        attr_conf: dict,
        parse_trace: str,
    ) -> Attr:
        resource_id = attr_conf.get("resource_id", default_resource_id)
        Validator.must_be_str(resource_id, f"{parse_trace}\nParsing `resource_id`")

        Validator.must_have(attr_conf, "path", parse_trace)
        path = self.path_parser.parse(
            self.path_parser.get_resource(resources, resource_id, parse_trace),
            attr_conf["path"],
            f"{parse_trace}\nParsing path of the attribute",
        )

        if "unique" in attr_conf and not isinstance(attr_conf["unique"], bool):
            raise InputError(
                f"{parse_trace}\nERROR: invalid value of the `unique` attribute. "
                f"Expected a boolean value. Get: {attr_conf['unique']}"
            )
        unique = attr_conf.get("unique", False)

        if "sorted" in attr_conf:
            Validator.must_in(
                attr_conf["sorted"],
                self.SORTED_VALUES,
                f"{parse_trace}\nParsing `sorted` of the attribute",
            )
        sorted = Sorted(attr_conf.get("sorted", Sorted.Null.value))

        if "value_type" in attr_conf:
            Validator.must_in(
                attr_conf["value_type"],
                self.VALUE_TYPE_VALUES,
                f"{parse_trace}\nParsing `value_type` of the attribute",
            )
        value_type = ValueType(
            attr_conf.get("value_type", ValueType.UnspecifiedSingle.value)
        )

        if "missing_values" in attr_conf:
            trace = f"{parse_trace}\nParsing missing_values of the attribute"
            Validator.must_be_list(attr_conf["missing_values"], trace)
            for val in attr_conf["missing_values"]:
                if val is not None and not isinstance(val, (str, int, bool, float)):
                    raise InputError(
                        f"{trace}\nERROR: invalid value. Expected either one of string, "
                        f"integer, or float. Get f{type(val)} instead"
                    )

        missing_values = attr_conf.get("missing_values", [])
        return Attr(
            attr_id, resource_id, path, missing_values, unique, sorted, value_type
        )
