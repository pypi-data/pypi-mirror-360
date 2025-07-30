from __future__ import annotations

from typing import Any, Callable, Literal, Optional, Protocol

import drepr.models.path as path
from codegen.models import AST, DeferredVar, PredefinedFn, Program, Var, expr, stmt
from drepr.models.align import IdenticalAlign
from drepr.models.prelude import Alignment, Attr, DRepr, RangeAlignment
from drepr.program_generation.predefined_fn import DReprPredefinedFn
from drepr.program_generation.program_space import VarSpace


class AlignmentFn:

    def __init__(self, desc: DRepr, program: Program):
        self.desc = desc
        self.program = program

    def align(
        self,
        ast: AST,
        aligns: list[Alignment],
        validate_path: bool,
        on_missing_key: Optional[Callable[[AST], Any]],
        iter_final_list: bool,
    ):
        for align in aligns:
            if isinstance(align, RangeAlignment):
                ast = self.align_by_range(
                    ast, align, validate_path, on_missing_key, iter_final_list
                )
            elif isinstance(align, IdenticalAlign):
                # if this is the alignment between the same attribute -- do nothing
                if align.source == align.target:
                    continue

                # the two attributes are different, but they have identical align, it means that they are single-value attributes
                # we just need to access the value of the target attribute
                target = self.desc.get_attr_by_id(align.target)
                assert all(
                    isinstance(step, path.IndexExpr) for step in target.path.steps
                )
                ast = PathAccessor(self.program).iterate_elements(
                    ast,
                    target,
                    aligned_attr=None,
                    to_aligned_dim=None,
                    validate_path=validate_path,
                    on_missing_key=on_missing_key,
                    iter_final_list=iter_final_list,
                )
            else:
                raise NotImplementedError(type(align))
        return ast

    def align_by_range(
        self,
        ast: AST,
        align: RangeAlignment,
        validate_path: bool,
        on_missing_key: Optional[Callable[[AST], Any]],
        iter_final_list: bool,
    ) -> AST:
        """Generate a piece of code that will generate variables (of target attr) to
        complete this alignment, if the alignment is one/many to one, then return ast is the same
        as we do not introduce nested statements. If the alignment is one/many to many, then
        we will need to have a for loop, hence, we have nested statements -> nested AST.
        """
        source = self.desc.get_attr_by_id(align.source)
        target = self.desc.get_attr_by_id(align.target)

        to_aligned_dim = {
            step.target_idx: step.source_idx for step in align.aligned_steps
        }
        return PathAccessor(self.program).iterate_elements(
            ast,
            target,
            aligned_attr=source,
            to_aligned_dim=to_aligned_dim,
            validate_path=validate_path,
            on_missing_key=on_missing_key,
            iter_final_list=iter_final_list,
        )


class PathAccessor:
    """Generate code to access elements (indices & values) of an attribute"""

    def __init__(self, program: Program):
        self.program = program

    def iterate_elements(
        self,
        ast: AST,
        attr: Attr,
        aligned_attr: Optional[Attr] = None,
        to_aligned_dim: Optional[dict[int, int]] = None,
        validate_path: bool = False,
        on_missing_key: Optional[Callable[[AST], Any]] = None,
        iter_final_list: bool = False,
        on_step_callback: Optional[OnStepCallback] = None,
    ):
        ast = ast.update_recursively(
            fn=lambda ast, dim: self.next_dimensions(
                ast,
                attr,
                dim,
                aligned_attr,
                to_aligned_dim,
                validate_path,
                on_missing_key,
                iter_final_list,
                on_step_callback,
            ),
            context=0,
        )
        return ast

    def next_dimensions(
        self,
        ast: AST,
        attr: Attr,
        dim: int,
        aligned_attr: Optional[Attr],
        to_aligned_dim: Optional[dict[int, int]],
        validate_path: bool,
        on_missing_key: Optional[Callable[[AST], Any]] = None,
        iter_final_list: bool = False,
        on_step_callback: Optional[OnStepCallback] = None,
    ):
        """Generate code to access elements of dimensions of attr started at dim.
        Return the next ast, remaining dimension index, and whether it has stopped.

        Args:
            mem: memory to store variables
            ast: current ast
            attr: attribute
            dim: starting dimension
            aligned_attr:
            to_aligned_dim:
            validate_path: whether to generate code to check if values of each dimension is correct. If the attribute
                is annotated with `missing_path = True`, then setting this does not have any effect.
            on_missing_key: a function that will be called when the key does not exist. If it is None, then we will raise an exception.
            iter_final_list: if value type of attribute is a list, and this flag is true, we will iterate over the list to yield each item
            on_step_callback: a function that can be called to generate code at each time we step into a new dimension (except dimension 0, which is the resource data)
        """
        n_dim = len(attr.path.steps)
        if attr.value_type.is_list() and iter_final_list:
            n_dim += 1

        if dim >= n_dim:
            return ast, dim, True

        if dim == 0:
            collection = self.program.get_var(
                key=VarSpace.resource_data(attr.resource_id), at=ast.next_child_id()
            )
        else:
            collection = self.program.get_var(
                key=VarSpace.attr_value_dim(attr.resource_id, attr.id, dim - 1),
                at=ast.next_child_id(),
            )

        if dim == len(attr.path.steps):
            # we are iterating over the value list
            step = path.RangeExpr(0, None, 1)
        else:
            step = attr.path.steps[dim]

        # index expr does not need nested ast.
        while isinstance(step, path.IndexExpr) and dim < len(attr.path.steps):
            if isinstance(step.val, path.Expr):
                # I don't know about recursive path expression yet -- what usecase and how to use them -- so I can't implement.
                raise Exception(
                    f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.val}"
                )

            # we do not need nested loop for index expression as we can just directly access the value
            c1 = DeferredVar(
                name=f"{attr.id}_value_{dim}",
                key=VarSpace.attr_value_dim(attr.resource_id, attr.id, dim),
            )

            if validate_path and not attr.path.is_step_optional(dim):
                handle_missing_key = "safe"
            elif attr.path.is_step_optional(dim):
                assert on_missing_key is not None
                handle_missing_key = on_missing_key
            else:
                handle_missing_key = "no_missing_key"

            ast = self.access_key(
                ast,
                attr,
                expr.ExprVar(collection),
                expr.ExprConstant(step.val),
                c1,
                dim,
                handle_missing_key,
                on_step_callback,
            )

            collection = c1.get_var()
            dim += 1
            if dim == len(attr.path.steps):
                # we have reached the end of the path
                # however, if the value type is a list, and we enable iter_final_list,
                # we need the final iteration
                return ast, dim, not (attr.value_type.is_list() and iter_final_list)
            step = attr.path.steps[dim]

        assert not isinstance(step, path.IndexExpr), (attr, step, dim)

        # other exprs require nested statement (for loop)

        if isinstance(step, path.RangeExpr):
            itemindex = DeferredVar(
                name=f"{attr.id}_index_{dim}",
                key=VarSpace.attr_index_dim(attr.resource_id, attr.id, dim),
            )
            itemvalue = DeferredVar(
                name=f"{attr.id}_value_{dim}",
                key=VarSpace.attr_value_dim(attr.resource_id, attr.id, dim),
            )

            if to_aligned_dim is not None and dim in to_aligned_dim:
                # this attribute has been aligned with other attribute and
                # the dimension is bound to the previously set dimension (of a subject)
                # so we need to copy the value
                assert aligned_attr is not None
                aligned_dim = to_aligned_dim[dim]
                aligned_dim_index = self.program.get_var(
                    key=VarSpace.attr_index_dim(
                        aligned_attr.resource_id, aligned_attr.id, aligned_dim
                    ),
                    at=ast.next_child_id(),
                )

                if step == aligned_attr.path.steps[aligned_dim]:
                    # now if the start, end, and step between the two attrs are the same, we just copy the value
                    # otherwise, we need to readjust the index
                    ast.assign(itemindex, expr.ExprVar(aligned_dim_index))
                else:
                    # recalculate the index
                    raise NotImplementedError()

                itemindex = itemindex.get_var()
                if validate_path:
                    invok_item_getter = DReprPredefinedFn.safe_item_getter(
                        self.program,
                        expr.ExprVar(collection),
                        expr.ExprVar(itemindex),
                        expr.ExprConstant(
                            f"Encounter error while accessing element of attribute {attr.id} via alignment at "
                            + f"dimension = {dim} - full path = {attr.path.to_lang_format()}"
                        ),
                    )
                else:
                    invok_item_getter = PredefinedFn.item_getter(
                        expr.ExprVar(collection), expr.ExprVar(itemindex)
                    )

                ast.assign(itemvalue, invok_item_getter)
                itemvalue = itemvalue.get_var()
                if on_step_callback is not None:
                    on_step_callback(
                        ast,
                        dim,
                        expr.ExprVar(collection),
                        expr.ExprVar(itemindex),
                        itemvalue,
                    )
            else:
                # the dimension is not bound, we are going to generate multiple values
                # using a for loop
                start_var = DeferredVar(
                    name=f"start",
                    key=("local-var", "start", f"attr={attr.id}", f"ast={ast.id}"),
                )
                if isinstance(step.start, path.Expr):
                    # I don't know about recursive path expression yet.
                    raise Exception(
                        f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.start}"
                    )
                ast.assign(start_var, expr.ExprConstant(step.start))
                start_var = start_var.get_var()

                end_var = DeferredVar(
                    name=f"end",
                    key=("local-var", "end", f"attr={attr.id}", f"ast={ast.id}"),
                )
                if step.end is None:
                    if validate_path:
                        invok_len = DReprPredefinedFn.safe_len(
                            self.program,
                            expr.ExprVar(collection),
                            expr.ExprConstant(
                                f"Encounter error while computing number of elements of attribute {attr.id} at "
                                + f"dimension = {dim} - full path = {attr.path.to_lang_format()}"
                            ),
                        )
                    else:
                        invok_len = PredefinedFn.len(expr.ExprVar(collection))
                    ast.assign(end_var, invok_len)
                else:
                    if isinstance(step.end, path.Expr):
                        # I don't know about recursive path expression yet.
                        raise Exception(
                            f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.end}"
                        )

                    if validate_path:
                        invok_len = DReprPredefinedFn.safe_len(
                            self.program,
                            expr.ExprVar(collection),
                            expr.ExprConstant(
                                f"Encounter error while computing number of elements of attribute {attr.id} at "
                                + f"dimension = {dim} - full path = {attr.path.to_lang_format()}"
                            ),
                        )

                        ast.if_(
                            expr.ExprLessThanOrEqual(
                                invok_len, expr.ExprConstant(step.end)
                            )
                        )(
                            stmt.ExceptionStatement(
                                PredefinedFn.base_error(
                                    f"Trying to select out-of-bound elements of attribute {attr.id} at dimension = {dim} - full path = {attr.path.to_lang_format()}"
                                )
                            )
                        )

                    ast.assign(end_var, expr.ExprConstant(step.end))
                end_var = end_var.get_var()

                if isinstance(step.step, path.Expr):
                    # I don't know about recursive path expression yet.
                    raise Exception(
                        f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.step}"
                    )
                elif step.step != 1:
                    step_var = DeferredVar(f"step__local_ast_{ast.id}")
                    ast.assign(step_var, expr.ExprConstant(step.step))
                    step_var = step_var.get_var()
                    expr_step_var = expr.ExprVar(step_var)
                else:
                    expr_step_var = None

                ast = ast.for_loop(
                    item=itemindex,
                    iter=PredefinedFn.range(
                        expr.ExprVar(start_var), expr.ExprVar(end_var), expr_step_var
                    ),
                )
                itemindex = itemindex.get_var()

                ast.assign(
                    itemvalue,
                    PredefinedFn.item_getter(
                        expr.ExprVar(collection), expr.ExprVar(itemindex)
                    ),
                )
                itemvalue = itemvalue.get_var()
                if on_step_callback is not None:
                    on_step_callback(
                        ast,
                        dim,
                        expr.ExprVar(collection),
                        expr.ExprVar(itemindex),
                        itemvalue,
                    )
            return (
                ast,
                dim + 1,
                False,
            )

        raise NotImplementedError(step)

    def access_key(
        self,
        ast: AST,
        attr: Attr,
        collection: expr.Expr,
        key: expr.ExprConstant,
        result: DeferredVar | Var,
        dim: int,
        handle_missing_key: Literal["safe", "no_missing_key"] | Callable[[AST], None],
        on_step_callback: Optional[OnStepCallback] = None,
    ):
        if handle_missing_key == "no_missing_key":
            ast.assign(result, PredefinedFn.item_getter(collection, key))
            if on_step_callback is not None:
                on_step_callback(ast, dim, collection, key, result)
            return ast

        if handle_missing_key == "safe":
            ast.assign(
                result,
                DReprPredefinedFn.safe_item_getter(
                    self.program,
                    collection,
                    key,
                    expr.ExprConstant(
                        f"While traveling elements of attribute {attr.id}, encounter key error: "
                        + f"key {key.constant} does not exist (key position = {dim} - full path = {attr.path.to_lang_format()})"
                    ),
                ),
            )
            if on_step_callback is not None:
                on_step_callback(ast, dim, collection, key, result)
            return ast

        ast.if_(expr.ExprNegation(PredefinedFn.has_item(collection, key)))(
            # if the key does not exist, we call the function to handle it
            # because we do not step in -- we don't invoke the callback here
            handle_missing_key
        )
        inner_ast = ast.else_()
        inner_ast.assign(result, PredefinedFn.item_getter(collection, key))
        if on_step_callback is not None:
            on_step_callback(inner_ast, dim, collection, key, result)
        return inner_ast

    @staticmethod
    def skip_on_missing_key(parent_tree: AST, tree: AST):
        if parent_tree.has_statement_between_ast(stmt.ForLoopStatement, tree.id):
            tree(stmt.ContinueStatement())
        else:
            # same ast because of a single value, we can't use continue
            # however, we use pass as it's a single-level if/else -- the else part
            # will handle the instance generation if there is no missing value.
            tree(stmt.NoStatement())


class OnStepCallback(Protocol):
    def __call__(
        self,
        ast: AST,
        dim: int,
        collection: expr.Expr,
        key: expr.Expr,
        result: DeferredVar | Var,
    ): ...
