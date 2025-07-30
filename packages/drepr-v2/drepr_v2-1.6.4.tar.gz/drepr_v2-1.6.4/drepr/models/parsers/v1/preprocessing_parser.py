from __future__ import annotations

from typing import Any, List, Type, Union

from drepr.models.parsers.v1.attr_parser import ParsedAttrs
from drepr.models.parsers.v1.path_parser import PathParser
from drepr.models.path import Path
from drepr.models.preprocessing import (
    PFilter,
    PMap,
    POutput,
    Preprocessing,
    PreprocessingType,
    PSplit,
    RMap,
)
from drepr.models.resource import Resource
from drepr.utils.validator import Validator


class PreprocessingParser:
    """
    Preprocessing are defined as a list

    ```
    - type: <preprocessing_type>
      # other properties
    ```

    1. If <preprocessing_type> is `pmap`, its other properties are:

        ```
        - type: pmap
          [resource_id]: <resource_id>
          path: <path>
          [output]: <output> (default is None)
          [change_structure]: null|true|false (default is null)
          code: str
        ```

    2. If <preprocessing_type> is `pfilter`, its properties are:

        ```
        - type: pfilter
          [resource_id]: <resource_id>
          path: <path>
          [output]: <output> (default is None)
          code: str
        ```

    3. If <preprocessing_type> is `rmap`, its properties are:

        ```
        - type: rmap
          resource_id: <resource_id>
          path: <path>
          func_id: <func_id>
          [output]: <output> (default is None)
        ```

    where `output` is either <resource_id> or an object of
        resource_id: <resource_id>
        attr: <attr_id>
        [attr_path]: <path>

    """

    PREPRO_TYPES = {x.value for x in PreprocessingType}

    def __init__(self, path_parser: PathParser):
        self.path_parser = path_parser

    def parse(
        self,
        default_resource_id: str,
        resources: List[Resource],
        attrs: ParsedAttrs,
        conf: list,
    ) -> List[Preprocessing]:
        Validator.must_be_list(conf, "Parsing preprocessing")
        result: list[Preprocessing] = []

        for i, prepro in enumerate(conf):
            trace0 = f"Parsing preprocessing at position {i}"
            Validator.must_be_dict(prepro, trace0)
            Validator.must_have(prepro, "type", trace0)
            Validator.must_in(
                prepro["type"], self.PREPRO_TYPES, f"{trace0}\nParsing property `type`"
            )
            prepro_type = PreprocessingType(prepro["type"])

            if "resource_id" in prepro:
                Validator.must_be_str(
                    prepro["resource_id"], f"{trace0}\nParsing property `resource_id`"
                )
                resource_id = prepro["resource_id"]
            else:
                resource_id = default_resource_id

            trace1 = f"{trace0}\nParsing property `path`"
            Validator.must_have(prepro, "path", trace1)
            path = self.path_parser.parse(
                self.path_parser.get_resource(resources, resource_id, trace0),
                prepro["path"],
                trace1,
            )

            if prepro_type == PreprocessingType.pmap:
                value = self.parse_pmap(resource_id, path, prepro, trace0)
            elif prepro_type == PreprocessingType.pfilter:
                value = self.parse_pfilter_psplit(
                    resource_id, path, prepro, trace0, PFilter
                )
            elif prepro_type == PreprocessingType.psplit:
                value = self.parse_pfilter_psplit(
                    resource_id, path, prepro, trace0, PSplit
                )
            elif prepro_type == PreprocessingType.rmap:
                value = self.parse_rmap(resource_id, path, prepro, trace0)
            else:
                raise NotImplemented(
                    f"Not implement the parser for preprocessing function with type {prepro_type}"
                )

            if value.output is not None and value.output.attr is not None:
                attrs.add_preprocessing_attr(value.output.attr)
            result.append(Preprocessing(prepro_type, value))

        return result

    def parse_pmap(
        self, resource_id: str, path: Path, prepro: dict, trace0: str
    ) -> PMap:
        trace1 = f"{trace0}\nParsing property `code`"
        Validator.must_have(prepro, "code", trace1)
        Validator.must_be_str(prepro["code"], trace1)
        code = prepro["code"]

        if "output" in prepro and prepro["output"] is not None:
            trace1 = f"{trace0}\nParsing property `output`"
            output = self.parse_output(prepro["output"], trace1)
        else:
            output = None

        if "change_structure" in prepro and prepro["change_structure"] is not None:
            trace1 = f"{trace0}\nParsing property `change_structure`"
            Validator.must_be_bool(prepro["change_structure"], trace1)
            change_structure = prepro["change_structure"]
        else:
            change_structure = None

        return PMap(resource_id, path, code, output, change_structure)

    def parse_pfilter_psplit(
        self,
        resource_id: str,
        path: Path,
        prepro: dict,
        trace0: str,
        cls: Union[Type[PFilter], Type[PSplit]],
    ) -> PFilter | PSplit:
        trace1 = f"{trace0}\nParsing property `code`"
        Validator.must_have(prepro, "code", trace1)
        Validator.must_be_str(prepro["code"], trace1)
        code = prepro["code"]

        if "output" in prepro:
            trace1 = f"{trace0}\nParsing property `output`"
            output = self.parse_output(prepro["output"], trace1)
        else:
            output = None

        return cls(resource_id, path, code, output)

    def parse_rmap(
        self, resource_id: str, path: Path, prepro: dict, trace0: str
    ) -> RMap:
        trace1 = f"{trace0}\nParsing property `func_id`"
        Validator.must_have(prepro, "func_id", trace1)
        Validator.must_be_str(prepro["func_id"], trace1)
        func_id = prepro["func_id"]

        if "output" in prepro:
            trace1 = f"{trace0}\nParsing property `output`"
            output = self.parse_output(prepro["output"], trace1)
        else:
            output = None

        return RMap(resource_id, path, func_id, output)

    def parse_output(self, output: Any, trace: str) -> POutput:
        if isinstance(output, str):
            return POutput(resource_id=output, attr=None, attr_path=None)
        else:
            Validator.must_be_dict(
                output, f"{trace}\nParsing output. Must be either string or dictionary"
            )
            Validator.must_be_subset(
                {"resource_id", "attr", "attr_path"},
                output.keys(),
                "keys of preprocessing output",
                trace,
            )

            if "resource_id" in output:
                Validator.must_be_str(
                    output["resource_id"], f"{trace}\nParsing output's resource id"
                )

            attr_path = None
            if "attr_path" in output:
                attr_path = self.path_parser.parse(
                    resource=None,
                    path=output["attr_path"],
                    parse_trace=f"{trace}\nParsing output's attr_path",
                )

            if "attr" in output:
                Validator.must_be_str(
                    output["attr"], f"{trace}\nParsing output's attribute"
                )

            return POutput(
                resource_id=output.get("resource_id"),
                attr=output.get("attr"),
                attr_path=attr_path,
            )
