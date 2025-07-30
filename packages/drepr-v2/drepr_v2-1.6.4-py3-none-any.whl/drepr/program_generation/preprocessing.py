from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from codegen.models import AST, Program, Var, expr
from codegen.models.var import DeferredVar

import drepr.models.path as dpath
from drepr.models.prelude import (
    Attr,
    Context,
    DRepr,
    PMap,
    PreprocessingType,
    Resource,
    Sorted,
    ValueType,
)
from drepr.program_generation.alignment_fn import PathAccessor
from drepr.program_generation.predefined_fn import DReprPredefinedFn
from drepr.program_generation.program_space import VarSpace
from drepr.utils.udf import SourceTree, UDFParsedResult, UDFParser

PreprocessingId = int


@dataclass
class NormedUserDefinedFn:
    name: str
    fnvar: expr.Expr
    udf: UDFParsedResult
    use_context: bool


class GenPreprocessing:
    """Generate preprocessing code for the given D-REPR."""

    def __init__(self, program: Program, desc: DRepr, call_preproc_ast: AST):
        self.program = program
        self.call_preproc_ast = call_preproc_ast
        self.desc = desc

        self.user_defined_fn: dict[PreprocessingId, NormedUserDefinedFn] = {}

    def generate(self):
        for i in range(len(self.desc.preprocessing)):
            self._generate_preprocessing(i)

    def _generate_preprocessing(self, prepro_id: PreprocessingId):
        preprocessing = self.desc.preprocessing[prepro_id]
        genfn_name = f"preprocess_{prepro_id}"

        self.program.root.linebreak()
        prepro_fn = self.program.root.func(
            genfn_name,
            [
                DeferredVar(
                    name="resource_data",
                    key=VarSpace.resource_data(preprocessing.value.resource_id),
                ),
            ],
        )
        self.program.root.linebreak()

        if preprocessing.type == PreprocessingType.pmap:
            value = preprocessing.value
            assert isinstance(value, PMap)

            # generate the necessary function (user defined fn & our preprocessing fn)
            self._init_user_defined_fn(prepro_id, value.code)
            self._generate_preprocessing_pmap(prepro_id, prepro_fn, value)

            prepro_invoke_expr = expr.ExprFuncCall(
                expr.ExprIdent(genfn_name),
                [
                    expr.ExprVar(
                        self.program.get_var(
                            key=VarSpace.resource_data(preprocessing.value.resource_id),
                            at=self.call_preproc_ast.next_child_id(),
                        )
                    ),
                ],
            )
            # call preprocessing fn in the main program and assign if needed
            if value.output is not None:
                if value.output.attr is None:
                    raise NotImplementedError()

                prepro_resource_id = self.desc.get_attr_by_id(
                    value.output.attr
                ).resource_id
                self.call_preproc_ast.assign(
                    DeferredVar(
                        name=f"resource_data_{prepro_resource_id}",
                        key=VarSpace.resource_data(prepro_resource_id),
                    ),
                    prepro_invoke_expr,
                )
            else:
                self.call_preproc_ast.expr(prepro_invoke_expr)
            return None

        raise NotImplementedError(preprocessing.type)

    def _generate_preprocessing_pmap(self, prepro_id: int, prepro_fn: AST, value: PMap):
        if not value.change_structure:
            if value.output is not None:
                if value.output.attr is None:
                    raise NotImplementedError()

                prepro_resource_id = self.desc.get_attr_by_id(
                    value.output.attr
                ).resource_id
                # create a variable to store the preprocess results
                output_attr_id = value.output.attr
                output_attr = DeferredVar(
                    name=output_attr_id, key=VarSpace.preprocessing_output(prepro_id)
                )

                # we use a special class called AttributeData that can store data as if it is in the resource data (same index, etc -- but the
                # real location in memory is different)
                self.program.import_("drepr.utils.attr_data.AttributeData", True)
                prepro_fn.assign(
                    output_attr,
                    expr.ExprFuncCall(
                        expr.ExprIdent("AttributeData.from_raw_path"),
                        [
                            expr.ExprConstant(value.path.to_lang_format()),
                        ],
                    ),
                )

                def on_step(
                    ast: AST,
                    dim: int,
                    collection: expr.Expr,
                    key: expr.Expr,
                    result: DeferredVar | Var,
                ):
                    # everytime we step into a new dimension, we step into the output variable as well.
                    if dim == 0:
                        # this is better than `output_attr.get_var()` as we can ensure the scope is correct
                        output_collection = expr.ExprVar(
                            self.program.get_var(
                                key=output_attr.key, at=ast.next_child_id()
                            )
                        )
                    else:
                        output_collection = expr.ExprVar(
                            self.program.get_var(
                                key=VarSpace.attr_value_dim(
                                    prepro_resource_id, output_attr_id, dim - 1
                                ),
                                at=ast.next_child_id(),
                            )
                        )

                    itemvalue = DeferredVar(
                        name=f"{output_attr_id}_value_{dim}",
                        key=VarSpace.attr_value_dim(
                            prepro_resource_id, output_attr_id, dim
                        ),
                    )
                    ast.assign(
                        itemvalue, DReprPredefinedFn.item_getter(output_collection, key)
                    )

                on_step_callback = on_step
            else:
                on_step_callback = None

            # the idea is to loop through the path without the last index, get the value, apply the function, and set
            # the value of the last index to the new value
            pseudo_attr = Attr(
                id=f"preproc_{prepro_id}_path",
                resource_id=value.resource_id,
                path=value.path,
                missing_values=[],
                unique=False,
                sorted=Sorted.Null,
                value_type=ValueType.UnspecifiedSingle,
            )
            ast = PathAccessor(self.program).iterate_elements(
                ast=prepro_fn,
                attr=pseudo_attr,
                on_step_callback=on_step_callback,
                on_missing_key=(
                    lambda tree: (
                        PathAccessor.skip_on_missing_key(prepro_fn, tree)
                        if pseudo_attr.path.has_optional_steps()
                        else None
                    )
                ),
            )

            # get item value & item context
            item_value = self.program.get_var(
                key=VarSpace.attr_value_dim(
                    pseudo_attr.resource_id,
                    pseudo_attr.id,
                    len(pseudo_attr.path.steps) - 1,
                ),
                at=ast.next_child_id(),
            )
            if self.user_defined_fn[prepro_id].use_context:
                context_index: list[expr.Expr] = []
                for dim in range(len(pseudo_attr.path.steps)):
                    step = pseudo_attr.path.steps[dim]
                    if isinstance(step, dpath.IndexExpr):
                        if isinstance(step.val, dpath.Expr):
                            # I don't know about recursive path expression yet -- what usecase and how to use them -- so I can't implement.
                            raise Exception(
                                f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.vals}"
                            )
                        context_index.append(expr.ExprConstant(step.val))
                    else:
                        context_index.append(
                            expr.ExprVar(
                                self.program.get_var(
                                    key=VarSpace.attr_index_dim(
                                        pseudo_attr.resource_id, pseudo_attr.id, dim
                                    ),
                                    at=ast.next_child_id(),
                                )
                            )
                        )

                self.program.import_(
                    "drepr.program_generation.preprocessing.ContextImpl", True
                )
                item_context = expr.ExprFuncCall(
                    expr.ExprIdent("ContextImpl"),
                    [
                        expr.ExprVar(
                            self.program.get_var(
                                key=VarSpace.resource_data(value.resource_id),
                                at=prepro_fn.next_child_id(),
                            )
                        ),
                        DReprPredefinedFn.tuple(context_index),
                    ],
                )
            else:
                item_context = None

            # then we call the user defined fn to get the new item value
            new_item_value = self._call_user_defined_fn(
                prepro_id,
                ast,
                expr.ExprVar(item_value),
                item_context,
            )

            # get the parent item value & index to assign the new value
            # if output new data, we need to retrieve the parent item value from correct location
            if value.output is not None:
                if len(pseudo_attr.path.steps) > 1:
                    parent_item_value = self.program.get_var(
                        key=VarSpace.attr_value_dim(
                            prepro_resource_id,
                            output_attr_id,
                            len(pseudo_attr.path.steps) - 2,
                        ),
                        at=ast.next_child_id(),
                    )
                else:
                    # this is better than `output_attr.get_var()` as we can ensure the scope is correct
                    parent_item_value = self.program.get_var(
                        key=output_attr.key,
                        at=ast.next_child_id(),
                    )
            else:
                if len(pseudo_attr.path.steps) > 1:
                    parent_item_value = self.program.get_var(
                        key=VarSpace.attr_value_dim(
                            pseudo_attr.resource_id,
                            pseudo_attr.id,
                            len(pseudo_attr.path.steps) - 2,
                        ),
                        at=ast.next_child_id(),
                    )
                else:
                    parent_item_value = self.program.get_var(
                        key=VarSpace.resource_data(pseudo_attr.resource_id),
                        at=ast.next_child_id(),
                    )

            if isinstance(pseudo_attr.path.steps[-1], dpath.IndexExpr):
                parent_item_index = expr.ExprConstant(pseudo_attr.path.steps[-1].val)
            else:
                parent_item_index = expr.ExprVar(
                    self.program.get_var(
                        key=VarSpace.attr_index_dim(
                            pseudo_attr.resource_id,
                            pseudo_attr.id,
                            len(pseudo_attr.path.steps) - 1,
                        ),
                        at=ast.next_child_id(),
                    )
                )

            # then, we set the new item value to the parent item value
            ast.expr(
                DReprPredefinedFn.item_setter(
                    expr.ExprVar(parent_item_value),
                    parent_item_index,
                    new_item_value,
                )
            )

            if value.output is not None:
                prepro_fn.return_(
                    expr.ExprVar(
                        self.program.get_var(
                            key=output_attr.key,
                            at=prepro_fn.next_child_id(),
                        )
                    )
                )
        else:
            # haven't considered the case of changing structure yet
            raise NotImplementedError()

    def _init_user_defined_fn(self, prepro_id: PreprocessingId, code: str):
        """First, import statements are moved to the top of the file. The rest of the code can be either
        wrapped in a function (as expected in DRepr design), or directly embedded whenever it is used.

        The later option (embedding code) yields more performance, but it is harder because of potential variable name conflicts.
        To implement the embedding code, we need to parse the code to find all variables that are used in the code and
        ensure that they are not used or overwrite previous variables (potential renaming may require). Also, we need to rewrite
        the return statement.
        """
        # detect indentation & remove it
        parsed_udf = UDFParser(code).parse(["context"])

        # now create a function containing the user-defined function
        fnname = f"preproc_{prepro_id}_customfn"
        fnargs = [
            DeferredVar(
                name="value",
                key=VarSpace.preprocessing_udf_value(
                    self.desc.preprocessing[prepro_id].value.resource_id
                ),
                force_name="value",
            )
        ]
        use_context = "context" in parsed_udf.monitor_variables

        if use_context:
            fnargs.append(
                DeferredVar(
                    name="context",
                    key=VarSpace.preprocessing_udf_context(
                        self.desc.preprocessing[prepro_id].value.resource_id
                    ),
                    force_name="context",
                )
            )

        if len(parsed_udf.imports) > 0:
            # create a function that will be used to create the user-defined function
            create_udf = self.program.root.func("get_" + fnname, [])
            self.program.root.linebreak()

            for import_stmt in parsed_udf.imports:
                create_udf.python_stmt(import_stmt)

            inner_udf = create_udf.func(fnname, fnargs)
            create_udf.return_(expr.ExprIdent(fnname))

            def insert_source_tree(ast: AST, tree: SourceTree):
                assert tree.node != ""
                ast = ast.python_stmt(tree.node)
                for child in tree.children:
                    insert_source_tree(ast, child)

            assert parsed_udf.source_tree.node == ""
            assert len(parsed_udf.source_tree.children) > 0
            for child in parsed_udf.source_tree.children:
                insert_source_tree(inner_udf, child)

            # now we create the user-defined function
            fnvar = DeferredVar(fnname, key=VarSpace.preprocessing_udf(fnname))
            self.program.root.assign(
                fnvar,
                expr.ExprFuncCall(expr.ExprIdent("get_" + fnname), []),
            )
            fnvar = expr.ExprVar(fnvar.get_var())
        else:
            inner_udf = self.program.root.func(fnname, fnargs)
            self.program.root.linebreak()

            def insert_source_tree(ast: AST, tree: SourceTree):
                assert tree.node != ""
                ast = ast.python_stmt(tree.node)
                for child in tree.children:
                    insert_source_tree(ast, child)

            assert parsed_udf.source_tree.node == ""
            assert len(parsed_udf.source_tree.children) > 0
            for child in parsed_udf.source_tree.children:
                insert_source_tree(inner_udf, child)

            # now we create the user-defined function
            fnvar = expr.ExprIdent(fnname)

        self.user_defined_fn[prepro_id] = NormedUserDefinedFn(
            name=fnname, udf=parsed_udf, use_context=use_context, fnvar=fnvar
        )

    def _call_user_defined_fn(
        self,
        prepro_id: PreprocessingId,
        ast: AST,
        value: expr.Expr,
        context: Optional[expr.Expr],
    ) -> expr.Expr:
        """Call the user-defined function"""
        return expr.ExprFuncCall(
            self.user_defined_fn[prepro_id].fnvar,
            [value, context] if context is not None else [value],
        )


class ContextImpl(Context):
    def __init__(self, resource_data, index: tuple):
        self.resource_data = resource_data
        self.index = index

    def get_index(self) -> tuple:
        return self.index

    def get_value(self, index: tuple):
        ptr = self.resource_data
        for i in index:
            ptr = ptr[i]
        return ptr


class GenerateDataStorage:
    pass
