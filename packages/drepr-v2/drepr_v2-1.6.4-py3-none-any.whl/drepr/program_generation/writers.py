from __future__ import annotations

from codegen.models import AST, Program, Var, expr
from codegen.models.var import DeferredVar

from drepr.models.prelude import DRepr, OutputFormat
from drepr.program_generation.program_space import VarSpace


class Writer:
    def __init__(self, desc: DRepr, format: OutputFormat, program: Program):
        self.desc = desc
        self.format = format
        self.program = program

    def get_writer_clspath(self):
        if self.format == OutputFormat.TTL:
            return f"drepr.writers.turtle_writer.TurtleWriter"
        else:
            raise NotImplementedError()

    def create_writer(self, ast: AST):
        self.program.import_(self.get_writer_clspath(), True)
        writer_clsname = self.get_writer_clspath().rsplit(".", 1)[-1]
        ast.assign(
            DeferredVar(name="writer", key=VarSpace.writer()),
            expr.ExprFuncCall(
                expr.ExprIdent(writer_clsname),
                [expr.ExprConstant(self.desc.sm.prefixes)],
            ),
        )

    def has_written_record(self, ast: AST, subj: expr.Expr):
        return expr.ExprMethodCall(
            expr.ExprVar(
                self.program.get_var(
                    key=VarSpace.writer(),
                    at=ast.next_child_id(),
                )
            ),
            "has_written_record",
            [subj],
        )

    def begin_record(
        self,
        prog: AST,
        class_uri: expr.Expr,
        subj: expr.Expr,
        is_blank: expr.Expr,
        is_buffered: bool,
    ):
        """whether to bufferef the records because some properties are mandatory."""
        prog.expr(
            expr.ExprMethodCall(
                expr.ExprVar(
                    self.program.get_var(
                        key=VarSpace.writer(),
                        at=prog.next_child_id(),
                    )
                ),
                "begin_record",
                [class_uri, subj, is_blank, expr.ExprConstant(is_buffered)],
            )
        )

    def end_record(self, prog: AST):
        prog.expr(
            expr.ExprMethodCall(
                expr.ExprVar(
                    self.program.get_var(key=VarSpace.writer(), at=prog.next_child_id())
                ),
                "end_record",
                [],
            )
        )

    def abort_record(self, prog: AST):
        prog.expr(
            expr.ExprMethodCall(
                expr.ExprVar(
                    self.program.get_var(key=VarSpace.writer(), at=prog.next_child_id())
                ),
                "abort_record",
                [],
            )
        )

    def is_record_empty(self, prog: AST):
        return expr.ExprMethodCall(
            expr.ExprVar(
                self.program.get_var(key=VarSpace.writer(), at=prog.next_child_id())
            ),
            "is_record_empty",
            [],
        )

    def begin_partial_buffering_record(
        self,
        prog: AST,
    ):
        raise NotImplementedError()

    def write_data_property(
        self,
        prog: AST,
        predicate_id: expr.Expr,
        value: expr.Expr,
        dtype: expr.ExprConstant,
    ):
        prog.expr(
            expr.ExprMethodCall(
                expr.ExprVar(
                    self.program.get_var(key=VarSpace.writer(), at=prog.next_child_id())
                ),
                "write_data_property",
                [predicate_id, value, dtype],
            )
        )

    def write_object_property(
        self,
        prog: AST,
        predicate_id: expr.Expr,
        object: expr.Expr,
        is_subject_blank: expr.Expr,
        is_object_blank: expr.Expr,
        is_new_subj: expr.Expr,
    ):
        prog.expr(
            expr.ExprMethodCall(
                expr.ExprVar(
                    self.program.get_var(key=VarSpace.writer(), at=prog.next_child_id())
                ),
                "write_object_property",
                [predicate_id, object, is_subject_blank, is_object_blank, is_new_subj],
            )
        )

    def buffer_object_property(
        self,
        target_cls: str,
        predicate_id: str,
        object: str,
        is_object_blank: bool,
    ):
        raise NotImplementedError()

    def write_to_file(self, prog: AST, file_path: expr.Expr):
        prog.expr(
            expr.ExprMethodCall(
                expr.ExprVar(
                    self.program.get_var(key=VarSpace.writer(), at=prog.next_child_id())
                ),
                "write_to_file",
                [file_path],
            )
        )

    def write_to_string(self, prog: AST, content: DeferredVar | Var):
        prog.assign(
            content,
            expr.ExprMethodCall(
                expr.ExprVar(
                    self.program.get_var(key=VarSpace.writer(), at=prog.next_child_id())
                ),
                "write_to_string",
                [],
            ),
        )
