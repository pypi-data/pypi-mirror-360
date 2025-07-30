from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List, Optional, Set, Union

from drepr.utils.misc import CacheMethod


@dataclass(frozen=True)
class Expr:
    expr: str


@dataclass
class RangeExpr:
    start: Union[int, Expr]
    end: Optional[Union[int, Expr]]  # exclusive
    step: Union[int, Expr]

    def is_select_all(self) -> bool:
        return self.start == 0 and self.end is None and self.step == 1


@dataclass
class IndexExpr:
    val: Union[str, int, Expr]
    is_optional: bool = field(
        default=False,
        metadata={"help": "Whether this index can be missing in the data source"},
    )


@dataclass
class SetIndexExpr:
    vals: Set[Union[str, int, Expr]]


class WildcardExpr(Enum):
    Values = "*"
    Names = "*~"


StepExpr = Union[RangeExpr, IndexExpr, SetIndexExpr, WildcardExpr]


@dataclass
class Path:
    steps: List[StepExpr]

    @staticmethod
    def deserialize(raw: dict) -> "Path":
        """
        Deserialize a dictionary to get back the Path object
        :param raw:
        :return:
        """
        steps = []
        for step in raw["steps"]:
            if not isinstance(step, dict):
                steps.append(WildcardExpr(step))
            elif "start" in step:
                # range index
                start = (
                    Expr(step["start"]["expr"])
                    if isinstance(step["start"], dict)
                    else step["start"]
                )
                end = (
                    Expr(step["end"]["expr"])
                    if isinstance(step["end"], dict)
                    else step["end"]
                )
                step1 = (
                    Expr(step["step"]["expr"])
                    if isinstance(step["step"], dict)
                    else step["step"]
                )
                steps.append(RangeExpr(start, end, step1))
            elif "val" in step:
                steps.append(
                    IndexExpr(
                        (
                            Expr(step["val"]["expr"])
                            if isinstance(step["val"], dict)
                            else step["val"]
                        ),
                        step["is_optional"],
                    )
                )
            elif "vals" in step:
                steps.append(
                    SetIndexExpr(
                        {
                            Expr(val["expr"]) if isinstance(val, dict) else val
                            for val in step["vals"]
                        }
                    )
                )
        return Path(steps)

    def is_step_optional(self, step_index: int):
        step = self.steps[step_index]
        return isinstance(step, IndexExpr) and step.is_optional

    @CacheMethod.cache(CacheMethod.as_is_posargs)
    def has_optional_steps(self) -> bool:
        """Check if this path has any optional steps, an optional step is a step that the key may not appear in the data source"""
        return any(isinstance(s, IndexExpr) and s.is_optional for s in self.steps)

    @CacheMethod.cache(CacheMethod.as_is_posargs)
    def get_optional_steps(self) -> list[int]:
        """Get the indices of optional steps in this path in sorted order"""
        return [
            i
            for i, s in enumerate(self.steps)
            if isinstance(s, IndexExpr) and s.is_optional
        ]

    def has_same_or_less_optional_steps(self, path: Path) -> bool:
        """Check if another path has the same or less optional steps as this path.

        In order for two paths to share the same optional steps, any previous steps of the optional step must be the same
        and the number of optional steps must be the same.

        In order for this path to have less optional steps than the other path, the number of optional steps must be less
        and the previous steps of the optional steps must be the same.
        """
        self_opt_steps = self.get_optional_steps()
        path_opt_steps = path.get_optional_steps()

        if self_opt_steps != path_opt_steps[: len(self_opt_steps)]:
            return False

        return (
            self.steps[: self_opt_steps[-1] + 1]
            == path.steps[: path_opt_steps[len(self_opt_steps) - 1] + 1]
        )

    def get_nary_steps(self) -> list[int]:
        """Obtain a list of indices of steps that select more than one elements"""
        unfixed_dims = []
        for d, s in enumerate(self.steps):
            if isinstance(s, (RangeExpr, SetIndexExpr, WildcardExpr)):
                unfixed_dims.append(d)

        return unfixed_dims

    def to_lang_format(self, use_json_path: bool = False) -> Union[list, str]:
        """
        Convert this Path object into the path object in the D-REPR language

        :param use_json_path: whether we should use the JSONPath or our new notation
        :return:
        """
        if use_json_path:
            jpath = ["$"]
            for step in self.steps:
                if isinstance(step, RangeExpr):
                    if any(
                        isinstance(v, Expr) for v in [step.start, step.end, step.step]
                    ):
                        raise NotImplementedError(
                            "Haven't supported JSONPath with expression yet"
                        )
                    jpath.append(f"[{step.start}:{step.end or ''}:{step.step}]")
                elif isinstance(step, IndexExpr):
                    if step.is_optional:
                        meta = "?"
                    else:
                        meta = ""
                    if isinstance(step.val, str):
                        jpath.append(f'["{step.val}"{meta}]')
                    else:
                        jpath.append(f"[{step.val}{meta}]")
                elif isinstance(step, SetIndexExpr):
                    raise NotImplementedError()
                else:
                    jpath.append(f".{step.value}")
            return "".join(jpath)

        path = []
        for step in self.steps:
            if isinstance(step, RangeExpr):
                start, end, step = [
                    (
                        ""
                        if v is None
                        else (f"${{{v.expr}}}" if isinstance(v, Expr) else v)
                    )
                    for v in [step.start, step.end, step.step]
                ]
                path.append(f"{start}..{end}:{step}")
            elif isinstance(step, IndexExpr):
                if step.is_optional:
                    path.append([step.val])
                else:
                    path.append(step.val)
            elif isinstance(step, SetIndexExpr):
                path.append(step.vals)
            elif isinstance(step, WildcardExpr):
                path.append(step.value)
            else:
                raise NotImplementedError()
        return path
