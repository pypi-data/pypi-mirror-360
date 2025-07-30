from __future__ import annotations

from typing import TYPE_CHECKING

from drepr.models.parsers.v1.align_parser import AlignParser
from drepr.models.parsers.v1.attr_parser import AttrParser, ParsedAttrs
from drepr.models.parsers.v1.preprocessing_parser import PreprocessingParser
from drepr.models.parsers.v1.resource_parser import ResourceParser
from drepr.models.parsers.v2.path_parser import PathParserV2
from drepr.models.parsers.v3.sm_parser import SMParser
from drepr.models.sm import SemanticModel
from drepr.utils.validator import *

if TYPE_CHECKING:
    from drepr.models.drepr import DRepr


class ReprV3Parser:
    """
    The D-REPR language version 3 has similar to the schema of the second version.

    Difference with previous features:
    1. For spreadsheet columns, they can the letter instead of number
    2. Semantic model configuration offers more flexibility and expressiveness to create attribute/class on the fly
    """

    TOP_KEYWORDS = {
        "version",
        "resources",
        "preprocessing",
        "attributes",
        "alignments",
        "semantic_model",
    }
    DEFAULT_RESOURCE_ID = "default"

    @classmethod
    def parse(cls, raw: dict):
        from drepr.models.drepr import DRepr

        Validator.must_be_subset(
            cls.TOP_KEYWORDS,
            raw.keys(),
            setname="Keys of D-REPR configuration",
            error_msg="Parsing D-REPR configuration",
        )

        for prop in ["version", "resources", "attributes"]:
            Validator.must_have(raw, prop, error_msg="Parsing D-REPR configuration")

        Validator.must_equal(
            raw["version"], "3", "Parsing D-REPR configuration version"
        )
        resources = ResourceParser.parse(raw["resources"])
        attrs = ParsedAttrs()

        if len(resources) == 1:
            default_resource_id = resources[0].id
        else:
            default_resource_id = ResourceParser.DEFAULT_RESOURCE_ID

        path_parser = PathParserV2()
        preprocessing = PreprocessingParser(path_parser).parse(
            default_resource_id, resources, attrs, raw.get("preprocessing", [])
        )
        attr_parser = AttrParser(path_parser)
        attr_parser.parse(default_resource_id, resources, attrs, raw["attributes"])
        aligns = AlignParser.parse(raw.get("alignments", []))

        if "semantic_model" in raw:
            sm = SMParser(
                default_resource_id, resources, attrs, path_parser, attr_parser
            ).parse(raw["semantic_model"])
        else:
            sm = SemanticModel.get_default(attrs.attrs)

        return DRepr(resources, preprocessing, attrs.attrs, aligns, sm)

    @classmethod
    def dump(cls, drepr: "DRepr", simplify: bool = True, use_json_path: bool = False):
        raise NotImplementedError()
