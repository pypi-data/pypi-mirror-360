from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable

from codegen.models import AST, PredefinedFn, Program, expr, stmt
from codegen.models.var import DeferredVar
from drepr.models.prelude import (
    DRepr,
    IndexExpr,
    OutputFormat,
    PreprocessResourceOutput,
)
from drepr.planning.class_map_plan import (
    BlankObject,
    BlankSubject,
    ClassesMapExecutionPlan,
    ClassMapPlan,
    DataProp,
    ExternalIDSubject,
    IDObject,
    InternalIDSubject,
    LiteralProp,
    ObjectProp,
    SingletonObject,
    SingletonSubject,
)
from drepr.program_generation.alignment_fn import AlignmentFn, PathAccessor
from drepr.program_generation.predefined_fn import DReprPredefinedFn
from drepr.program_generation.preprocessing import GenPreprocessing
from drepr.program_generation.program_space import VarSpace
from drepr.program_generation.writers import Writer
from drepr.utils.misc import assert_true
from slugify import slugify


@dataclass
class FileOutput:
    fpath: Path
    format: OutputFormat


@dataclass
class MemoryOutput:
    format: OutputFormat


Output = FileOutput | MemoryOutput


def gen_program(
    desc: DRepr, exec_plan: ClassesMapExecutionPlan, output: Output, debuginfo: bool
) -> AST:
    """Generate a program to convert the given D-REPR to a target format"""
    program = Program()
    writer = Writer(desc, output.format, program)

    func_args = [
        DeferredVar(
            name="resource" if len(desc.resources) == 1 else f"resource_{res.id}",
            key=VarSpace.resource(res.id),
        )
        for res in desc.resources
        if not isinstance(res, PreprocessResourceOutput)
    ]
    if isinstance(output, FileOutput):
        output_file = DeferredVar(name="output_file", key=VarSpace.output_file())
        func_args.append(output_file)
    else:
        output_file = None

    program.root.linebreak()
    main_fn = program.root.func("main", func_args)

    for resource in desc.resources:
        if isinstance(resource, PreprocessResourceOutput):
            continue
        var = DeferredVar(
            name=(
                "resource_data"
                if len(desc.resources) == 1
                else f"resource_data_{resource.id}"
            ),
            key=VarSpace.resource_data(resource.id),
        )
        main_fn.assign(
            var,
            DReprPredefinedFn.read_source(
                program,
                resource.type,
                program.get_var(
                    key=VarSpace.resource(resource.id), at=main_fn.next_child_id()
                ),
            ),
        )

    # define missing values of attributes
    main_fn.linebreak()
    for attr in desc.attrs:
        if len(attr.missing_values) > 0:
            main_fn.assign(
                DeferredVar(
                    name=f"{get_varname_for_attr(attr.id)}_missing_values",
                    key=VarSpace.attr_missing_values(attr.id),
                ),
                expr.ExprConstant(set(attr.missing_values)),
            )

    # create transformation
    GenPreprocessing(program, desc, main_fn).generate()

    # create a writer
    writer.create_writer(main_fn)

    # for each class node, we generate a plan for each of them.
    for classplan in exec_plan.class_map_plans:
        main_fn.linebreak()
        main_fn.comment(f"Transform records of class {classplan.class_id}")
        # generate the code to execute the plan
        gen_classplan_executor(
            program, main_fn.block(), writer, desc, classplan, debuginfo
        )

    main_fn.linebreak()
    # we write the output to the file
    if isinstance(output, FileOutput):
        assert output_file is not None
        writer.write_to_file(main_fn, expr.ExprVar(output_file.get_var()))
    else:
        content = DeferredVar(name="output")
        writer.write_to_string(main_fn, content)
        main_fn.return_(expr.ExprVar(content.get_var()))

    invok_main = expr.ExprFuncCall(
        expr.ExprIdent("main"), [expr.ExprIdent("*sys.argv[1:]")]
    )

    program.root.linebreak()
    program.root.if_(
        expr.ExprEqual(expr.ExprIdent("__name__"), expr.ExprConstant("__main__"))
    )(
        stmt.ImportStatement("sys", False),
        stmt.LineBreak(),
        stmt.SingleExprStatement(
            expr.ExprFuncCall(expr.ExprIdent("print"), [invok_main])
            if isinstance(output, MemoryOutput)
            else invok_main
        ),
    )
    return program.root


def gen_classplan_executor(
    program: Program,
    parent_ast: AST,
    writer: Writer,
    desc: DRepr,
    classplan: ClassMapPlan,
    debuginfo: bool,
):
    """Generate the code to execute the given class plan.
    Below is the pseudo code:

    1. Iterate over the subject values
        1. If the subject is uri and it has missing values, if the uri is missing, we skip this
           record
        2. Begin record
        3. Iterate over target property & value
            1. If not target.can_have_missing_values:
                1. Iterate over objprop values:
                    1. Write property
            2. Else:
                1. If target edge is optional:
                    iterate over objprop values:
                        if objprop value is not missing:
                            write  property
                else:
                    (1) ----
                    has_record = False
                    iterate over objprop values:
                        if objprop value is not missing:
                            has_record = True
                            write property
                    if not has_record:
                        abort the record
                    ---- (2)
        4. End the record -- if the subject is blank node,
            and we do not write any data, we abort, otherwise, we commit
    """
    class_uri = expr.ExprConstant(
        desc.sm.get_abs_iri(desc.sm.get_class_node(classplan.class_id).label)
    )
    get_subj_val: Callable[[AST], expr.Expr]
    classplan_subject = classplan.subject
    if isinstance(classplan_subject, SingletonSubject):
        ast = parent_ast
        is_subj_blank = classplan_subject.is_blank
        is_buffered = False
        can_class_missing = False
        get_subj_val = lambda ast: get_subj_val_for_static_class(classplan.class_id)
    else:
        ast = PathAccessor(program).iterate_elements(
            parent_ast,
            classplan_subject.attr,
            None,
            None,
            validate_path=debuginfo,
            on_missing_key=(
                lambda tree: (
                    PathAccessor.skip_on_missing_key(parent_ast, tree)
                    if classplan_subject.attr.path.has_optional_steps()
                    else None
                )
            ),
        )
        is_subj_blank = isinstance(classplan_subject, BlankSubject)
        can_class_missing = (
            any(
                not dprop.is_optional and dprop.can_target_missing
                for dprop in classplan.data_props
            )
            or any(
                not oprop.is_optional and oprop.can_target_missing
                for oprop in classplan.object_props
            )
            or any(
                not oprop.is_optional and oprop.can_target_missing
                for oprop in classplan.buffered_object_props
            )
        )
        is_buffered = can_class_missing

        if isinstance(classplan_subject, (InternalIDSubject, ExternalIDSubject)):
            get_subj_val = lambda ast: expr.ExprVar(
                program.get_var(
                    key=VarSpace.attr_value_dim(
                        classplan_subject.attr.resource_id,
                        classplan_subject.attr.id,
                        len(classplan_subject.attr.path.steps) - 1,
                    ),
                    at=ast.next_child_id(),
                )
            )
        else:
            assert isinstance(classplan_subject, BlankSubject)
            if classplan_subject.use_attr_value:
                get_subj_val = lambda ast: PredefinedFn.tuple(
                    [
                        expr.ExprConstant(classplan.class_id),
                        expr.ExprConstant(
                            desc.get_attr_index_by_id(classplan_subject.attr.id)
                        ),
                        expr.ExprVar(
                            program.get_var(
                                key=VarSpace.attr_value_dim(
                                    classplan_subject.attr.resource_id,
                                    classplan_subject.attr.id,
                                    len(classplan_subject.attr.path.steps) - 1,
                                ),
                                at=ast.next_child_id(),
                            )
                        ),
                    ]
                )
            else:
                # if we don't use attr value, the subj_val is the entire index that leads to the last value
                get_subj_val = lambda ast: (
                    PredefinedFn.tuple(
                        [
                            expr.ExprConstant(classplan.class_id),
                            expr.ExprConstant(
                                desc.get_attr_index_by_id(classplan_subject.attr.id)
                            ),
                        ]
                        + [
                            expr.ExprVar(
                                program.get_var(
                                    key=VarSpace.attr_index_dim(
                                        classplan_subject.attr.resource_id,
                                        classplan_subject.attr.id,
                                        dim,
                                    ),
                                    at=ast.next_child_id(),
                                )
                            )
                            for dim, step in enumerate(
                                classplan_subject.attr.path.steps
                            )
                            if not isinstance(step, IndexExpr)
                        ]
                    )
                )

        if (
            isinstance(classplan_subject, (InternalIDSubject, ExternalIDSubject))
            and len(classplan_subject.attr.missing_values) > 0
        ) or (
            isinstance(classplan_subject, BlankSubject)
            and classplan_subject.use_attr_value
            and len(classplan_subject.attr.missing_values) > 0
        ):
            # we know immediately that it's missing if the subject value is missing

            if ast.id == parent_ast.id:
                # same ast because of a single value, we can't use continue
                # so we wrap it with if -- if not missing, continue to generate the instance
                ast = ast.if_(
                    expr.ExprNegation(
                        PredefinedFn.set_contains(
                            expr.ExprVar(
                                program.get_var(
                                    key=VarSpace.attr_missing_values(
                                        classplan_subject.attr.id
                                    ),
                                    at=ast.next_child_id(),
                                )
                            ),
                            get_subj_val(ast),
                        )
                    )
                )
            else:
                ast.if_(
                    PredefinedFn.set_contains(
                        expr.ExprVar(
                            program.get_var(
                                key=VarSpace.attr_missing_values(
                                    classplan_subject.attr.id
                                ),
                                at=ast.next_child_id(),
                            )
                        ),
                        get_subj_val(ast),
                    )
                )(stmt.ContinueStatement())

    writer.begin_record(
        ast,
        class_uri,
        get_subj_val(ast),
        expr.ExprConstant(is_subj_blank),
        is_buffered,
    )

    for dataprop in classplan.data_props:
        ast.linebreak()
        ast.comment(f"Retrieve value of data property: {dataprop.attr.id}")

        gen_classprop_body(
            program,
            desc,
            parent_ast,
            ast.block(),
            writer,
            is_buffered,
            is_subj_blank,
            dataprop,
            debuginfo,
        )

    for objprop in classplan.object_props:
        ast.linebreak()
        if isinstance(objprop, SingletonObject):
            ast.comment(
                f"Link object property to a singleton object: {objprop.target_class_id}"
            )
        else:
            ast.comment(f"Retrieve value of object property: {objprop.attr.id}")

        gen_classprop_body(
            program,
            desc,
            parent_ast,
            ast.block(),
            writer,
            is_buffered,
            is_subj_blank,
            objprop,
            debuginfo,
        )

    if len(classplan.literal_props) > 0:
        ast.linebreak()
        ast.comment("Set static properties")

        for litprop in classplan.literal_props:
            gen_classprop_body(
                program,
                desc,
                parent_ast,
                ast.block(),
                writer,
                is_buffered,
                is_subj_blank,
                litprop,
                debuginfo,
            )

    assert len(classplan.buffered_object_props) == 0, "Not implemented yet"

    # we can end the record even if we abort it before. the end record code should handle this.
    ast.linebreak()

    if isinstance(classplan_subject, BlankSubject) and can_class_missing:
        ast.if_(writer.is_record_empty(ast))(lambda ast00: writer.abort_record(ast00))
        ast.else_()(lambda ast00: writer.end_record(ast00))
    else:
        writer.end_record(ast)

    return ast


def gen_classprop_body(
    program: Program,
    desc: DRepr,
    parent_ast: AST,
    ast: AST,
    writer: Writer,
    is_buffered: bool,
    is_subj_blank: bool,
    classprop: DataProp | ObjectProp | LiteralProp,
    debuginfo: bool,
):
    """
    Args:
        parent_ast: the parent AST that above iterating subject values -- this is good to detect continue statement is okay to skip to the next subject/record
    """
    iter_final_list = False
    get_prop_val: Callable[[AST], expr.Expr]
    if isinstance(classprop, (DataProp, IDObject)):
        attr = classprop.attr
        if isinstance(classprop, DataProp) and classprop.attr.value_type.is_list():
            # for a list, we need to iterate over the list.
            get_prop_val = lambda ast: expr.ExprVar(
                program.get_var(
                    key=VarSpace.attr_value_dim(
                        attr.resource_id,
                        attr.id,
                        len(
                            attr.path.steps
                        ),  # not -1 because the last dimension is now a list
                    ),
                    at=ast.next_child_id(),
                )
            )
            iter_final_list = True
        else:
            get_prop_val = lambda ast: expr.ExprVar(
                program.get_var(
                    key=VarSpace.attr_value_dim(
                        attr.resource_id,
                        attr.id,
                        len(attr.path.steps) - 1,
                    ),
                    at=ast.next_child_id(),
                )
            )
    elif isinstance(classprop, BlankObject):
        attr = classprop.attr
        if classprop.use_attr_value:
            get_prop_val = lambda ast: PredefinedFn.tuple(
                [
                    expr.ExprConstant(classprop.object_id),
                    expr.ExprConstant(desc.get_attr_index_by_id(attr.id)),
                    expr.ExprVar(
                        program.get_var(
                            key=VarSpace.attr_value_dim(
                                attr.resource_id,
                                attr.id,
                                len(attr.path.steps) - 1,
                            ),
                            at=ast.next_child_id(),
                        )
                    ),
                ]
            )
        else:
            get_prop_val = lambda ast: (
                PredefinedFn.tuple(
                    [
                        expr.ExprConstant(classprop.object_id),
                        expr.ExprConstant(desc.get_attr_index_by_id(classprop.attr.id)),
                    ]
                    + [
                        expr.ExprVar(
                            program.get_var(
                                key=VarSpace.attr_index_dim(
                                    classprop.attr.resource_id,
                                    classprop.attr.id,
                                    dim,
                                ),
                                at=ast.next_child_id(),
                            )
                        )
                        for dim, step in enumerate(classprop.attr.path.steps)
                        if not isinstance(step, IndexExpr)
                    ]
                )
            )
    elif isinstance(classprop, LiteralProp):
        get_prop_val = lambda ast: expr.ExprConstant(classprop.value)
        attr = (
            None  # we are not going to have an attribute because it is a static value
        )
    else:
        assert isinstance(classprop, SingletonObject)
        get_prop_val = lambda ast: get_subj_val_for_static_class(
            classprop.target_class_id
        )
        attr = (
            None  # we are not going to have an attribute because it is a static value
        )

    is_prop_val_not_missing: Callable[[AST], expr.Expr]
    if isinstance(classprop, DataProp):
        assert attr is not None, "attr should not be None for non-static value"
        if len(attr.missing_values) == 0:
            # leverage the fact that if True will be optimized away
            is_prop_val_not_missing = lambda ast: expr.ExprConstant(True)
        else:
            is_prop_val_not_missing = lambda ast: expr.ExprNegation(
                PredefinedFn.set_contains(
                    expr.ExprVar(
                        program.get_var(
                            key=VarSpace.attr_missing_values(attr.id),
                            at=ast.next_child_id(),
                        )
                    ),
                    get_prop_val(ast),
                ),
            )
        write_fn = partial(
            writer.write_data_property, dtype=expr.ExprConstant(classprop.datatype)
        )
    elif isinstance(classprop, ObjectProp):
        is_prop_val_not_missing = lambda ast: writer.has_written_record(
            ast,
            get_prop_val(ast),
        )
        write_fn = partial(
            writer.write_object_property,
            is_subject_blank=expr.ExprConstant(is_subj_blank),
            is_object_blank=expr.ExprConstant(classprop.is_object_blank()),
            is_new_subj=expr.ExprConstant(False),
        )
    else:
        assert isinstance(classprop, LiteralProp)
        is_prop_val_not_missing = lambda ast: expr.ExprConstant(True)
        write_fn = partial(
            writer.write_data_property, dtype=expr.ExprConstant(classprop.datatype)
        )

    if isinstance(classprop, (LiteralProp, SingletonObject)):
        write_fn(ast, expr.ExprConstant(classprop.predicate), get_prop_val(ast))
    else:
        if not classprop.can_target_missing:
            AlignmentFn(desc, program).align(
                ast, classprop.alignments, debuginfo, None, iter_final_list
            )(
                lambda ast_l0: write_fn(
                    ast_l0,
                    expr.ExprConstant(classprop.predicate),
                    get_prop_val(ast_l0),
                )
            )
        else:
            if classprop.is_optional:
                AlignmentFn(desc, program).align(
                    ast,
                    classprop.alignments,
                    debuginfo,
                    # if the value is missing, we just ignore it.
                    on_missing_key=lambda astxx: astxx(stmt.NoStatement()),
                    iter_final_list=iter_final_list,
                )(
                    lambda ast00: ast00.if_(is_prop_val_not_missing(ast00))(
                        lambda ast01: write_fn(
                            ast01,
                            expr.ExprConstant(classprop.predicate),
                            get_prop_val(ast01),
                        )
                    )
                )
            else:
                assert attr is not None, "attr should not be None for non-static value"
                if classprop.alignments_cardinality.is_star_to_many():
                    has_dataprop_val = DeferredVar(
                        name=f"{get_varname_for_attr(attr.id)}_has_value_d{len(attr.path.steps) - 1}",
                        key=VarSpace.has_attr_value_dim(
                            attr.resource_id,
                            attr.id,
                            len(attr.path.steps) - 1,
                        ),
                    )
                    ast.assign(has_dataprop_val, expr.ExprConstant(False))
                    has_dataprop_val = has_dataprop_val.get_var()

                    AlignmentFn(desc, program).align(
                        ast,
                        classprop.alignments,
                        debuginfo,
                        lambda astxx: astxx(stmt.NoStatement()),
                        iter_final_list,
                    )(
                        lambda ast00: ast00.if_(is_prop_val_not_missing(ast00))(
                            lambda ast01: ast01.assign(
                                has_dataprop_val, expr.ExprConstant(True)
                            ),
                            lambda ast02: write_fn(
                                ast02,
                                expr.ExprConstant(classprop.predicate),
                                get_prop_val(ast02),
                            ),
                        )
                    )
                    ast.if_(expr.ExprNegation(expr.ExprVar(has_dataprop_val)))(
                        lambda ast00: (
                            assert_true(
                                is_buffered,
                                "We should only abort record if we are buffering",
                            )
                            and writer.abort_record(ast00)
                        ),
                        (
                            stmt.ContinueStatement()
                            if parent_ast.has_statement_between_ast(
                                stmt.ForLoopStatement, ast.id
                            )
                            else stmt.NoStatement()
                        ),
                    )
                else:

                    def on_missing_key(tree: AST):
                        assert_true(
                            is_buffered,
                            "We should only abort record if we are buffering",
                        )
                        writer.abort_record(tree)
                        if parent_ast.has_statement_between_ast(
                            stmt.ForLoopStatement, tree.id
                        ):
                            tree(stmt.ContinueStatement())
                        else:
                            # same ast because of a single value, we can't use continue
                            # however, we use pass as it's a single-level if/else -- the else part
                            # will handle the instance generation if there is no missing value.
                            tree(stmt.NoStatement())

                    AlignmentFn(desc, program).align(
                        ast,
                        classprop.alignments,
                        debuginfo,
                        # on_missing_key=lambda astxx: assert_true(
                        #     is_buffered,
                        #     "We should only abort record if we are buffering",
                        # )
                        # and writer.abort_record(astxx),
                        on_missing_key=on_missing_key,
                        iter_final_list=iter_final_list,
                    )(
                        lambda ast00: ast00.if_(is_prop_val_not_missing(ast00))(
                            lambda ast01: write_fn(
                                ast01,
                                expr.ExprConstant(classprop.predicate),
                                get_prop_val(ast01),
                            ),
                        ),
                        lambda ast10: ast10.else_()(
                            lambda ast11: (
                                assert_true(
                                    is_buffered,
                                    "We should only abort record if we are buffering",
                                )
                                and writer.abort_record(ast11)
                            ),
                            (
                                stmt.ContinueStatement()
                                if parent_ast.has_statement_between_ast(
                                    stmt.ForLoopStatement, ast10.id
                                )
                                else stmt.NoStatement()
                            ),
                        ),
                    )


def get_subj_val_for_static_class(class_id):
    return PredefinedFn.tuple(
        [expr.ExprConstant("static-8172a"), expr.ExprConstant(class_id)]
    )


def get_varname_for_attr(attr_id: str):
    varname = slugify(attr_id).replace("-", "_")
    if varname[0].isdigit():
        varname = "a_" + varname
    return varname
