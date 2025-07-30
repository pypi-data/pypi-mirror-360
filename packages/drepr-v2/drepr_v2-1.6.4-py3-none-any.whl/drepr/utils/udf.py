from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceTree:
    node: str
    children: list[SourceTree]

    def get_simplified_dict(self):
        children = [
            child.get_simplified_dict() if len(child.children) > 0 else child.node
            for child in self.children
        ]

        if self.node == "":
            return children

        return {
            "node": self.node,
            "children": children,
        }


@dataclass
class UDFParsedResult:
    # import statements
    imports: list[str]
    # set of variables that we opt to monitor during parsing (e.g., we want to detect a variable named context)
    monitor_variables: set[str]
    # the source code of the UDF -- without import statements
    source_tree: SourceTree


class UDFParser:

    def __init__(self, source_code: str):
        if source_code.strip() == "":
            raise ValueError(f"Cannot parse an empty code")

        self.source_code = self.remove_prefix_spaces(source_code)
        self.source_code_lines = self.source_code.split("\n")
        self.source_tree = ast.parse(self.source_code)

    def parse(self, monitor_vars: Optional[list[str]] = None) -> UDFParsedResult:
        imports = []
        tree = SourceTree("", [])
        for stmt in self.source_tree.body:
            tree.children.extend(self._parse_ast(stmt, imports))

        found_vars = set()
        if monitor_vars is not None and len(monitor_vars) > 0:
            # we need to find all variables that we want to monitor
            for node in ast.walk(self.source_tree):
                if isinstance(node, ast.Name) and node.id in monitor_vars:
                    found_vars.add(node.id)

        return UDFParsedResult(
            imports=imports,
            monitor_variables=found_vars,
            source_tree=tree,
        )

    def _parse_ast(self, tree: ast.AST, imports: list[str]) -> list[SourceTree]:
        if isinstance(tree, (ast.Import, ast.ImportFrom)):
            imports.append(self._get_node_code(tree))
            return []

        if isinstance(
            tree,
            (
                ast.Expr,
                ast.Return,
                ast.Yield,
                ast.YieldFrom,
                ast.Assign,
                ast.Assert,
                ast.AugAssign,
            ),
        ):
            return [SourceTree(self._get_node_code(tree), [])]

        if isinstance(tree, ast.If):
            content = f"if {self._get_node_code(tree.test)}:"
            out = [SourceTree(content, [])]
            for stmt in tree.body:
                out[0].children.extend(self._parse_ast(stmt, imports))
            if len(tree.orelse) > 0:
                out.append(SourceTree("else:", []))
                for stmt in tree.orelse:
                    out[1].children.extend(self._parse_ast(stmt, imports))
            return out

        if isinstance(tree, ast.For):
            content = f"for {self._get_node_code(tree.target)} in {self._get_node_code(tree.iter)}:"
            out = [SourceTree(content, [])]
            for stmt in tree.body:
                out[0].children.extend(self._parse_ast(stmt, imports))
            if len(tree.orelse) > 0:
                out.append(SourceTree("else:", []))
                for stmt in tree.orelse:
                    out[1].children.extend(self._parse_ast(stmt, imports))
            return out

        if isinstance(tree, ast.Continue):
            return [SourceTree("continue", [])]

        if isinstance(tree, ast.Break):
            return [SourceTree("break", [])]

        if isinstance(tree, ast.Try):
            out = [SourceTree("try:", [])]
            for stmt in tree.body:
                out[0].children.extend(self._parse_ast(stmt, imports))

            if len(tree.handlers) > 0:
                for handler in tree.handlers:
                    except_args = ["except"]
                    if handler.type is not None:
                        except_args.append(self._get_node_code(handler.type))
                    if handler.name is not None:
                        except_args.append(handler.name)

                    out.append(SourceTree(" ".join(except_args) + ":", []))
                    for stmt in handler.body:
                        out[-1].children.extend(self._parse_ast(stmt, imports))
            if len(tree.orelse) > 0:
                out.append(SourceTree("else:", []))
                for stmt in tree.orelse:
                    out[-1].children.extend(self._parse_ast(stmt, imports))
            if len(tree.finalbody) > 0:
                out.append(SourceTree("finally:", []))
                for stmt in tree.finalbody:
                    out[-1].children.extend(self._parse_ast(stmt, imports))
            return out

        if isinstance(tree, ast.FunctionDef):
            fnargs = ", ".join([self._get_node_code(arg) for arg in tree.args.args])
            if tree.returns is not None:
                returns = f" -> {self._get_node_code(tree.returns)}"
            else:
                returns = ""
            out = [SourceTree(f"def {tree.name}({fnargs}){returns}:", [])]
            for stmt in tree.body:
                out[0].children.extend(self._parse_ast(stmt, imports))
            return out
        raise NotImplementedError(type(tree))

    def _get_node_code(self, node: ast.AST) -> str:
        lines = self.source_code_lines[node.lineno - 1 : node.end_lineno]
        if len(lines) == 1:
            return lines[0][node.col_offset : node.end_col_offset]
        lines[0] = lines[0][node.col_offset :]
        lines[-1] = lines[-1][: node.end_col_offset]
        return "\n".join(lines)

    def remove_prefix_spaces(self, code: str) -> str:
        lines = [x.rstrip() for x in code.splitlines()]
        non_empty_line_no = next(i for i in range(len(lines)) if lines[i] != "")
        lines = lines[non_empty_line_no:]
        assert len(lines) > 0

        m = re.match(r"^([ \t]*)", lines[0])
        assert m is not None
        indentation = m.group(1)

        if not all(x.startswith(indentation) or x.strip() == "" for x in lines):
            raise ValueError(
                f"The code has inconsistent prefix spaces. The first line has {indentation} spaces, but the following lines do not have the same prefix spaces"
            )

        return "\n".join(x[len(indentation) :] for x in lines)
