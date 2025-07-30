from __future__ import annotations

from dataclasses import dataclass

from codegen.models import PredefinedFn, Program, Var, expr

from drepr.models.resource import ResourceType


class DReprPredefinedFn(PredefinedFn):

    @dataclass
    class _safe_item_getter(expr.Expr):
        collection: expr.Expr
        item: expr.Expr
        msg: expr.Expr

        def to_python(self):
            return f"safe_item_getter({self.collection.to_python()}, {self.item.to_python()}, {self.msg.to_python()})"

    @dataclass
    class _safe_len(expr.Expr):
        collection: expr.Expr
        msg: expr.Expr

        def to_python(self):
            return f"safe_len({self.collection.to_python()}, {self.msg.to_python()})"

    @staticmethod
    def safe_item_getter(
        program: Program,
        collection: expr.Expr,
        item: expr.Expr,
        msg: expr.Expr,
    ):
        program.import_("drepr.utils.safe.safe_item_getter", True)
        return DReprPredefinedFn._safe_item_getter(collection, item, msg)

    @staticmethod
    def safe_len(program: Program, collection: expr.Expr, msg: expr.Expr):
        program.import_("drepr.utils.safe.safe_len", True)
        return DReprPredefinedFn._safe_len(collection, msg)

    @staticmethod
    def read_source(program: Program, source_type: ResourceType, input_file: Var):
        program.import_(f"drepr.readers.prelude.read_source_{source_type.value}", True)
        return expr.ExprFuncCall(
            expr.ExprIdent(f"read_source_{source_type.value}"),
            [expr.ExprVar(input_file)],
        )
