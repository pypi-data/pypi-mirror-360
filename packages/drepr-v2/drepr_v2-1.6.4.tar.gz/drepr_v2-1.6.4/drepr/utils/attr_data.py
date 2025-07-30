from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import drepr.models.path as dpath
from drepr.models.parsers.v2.path_parser import PathParserV2


class Container:

    def __init__(self, attrs: Optional[dict[str, AttributeData]] = None):
        self.attr = attrs or {}

    def __setitem__(self, id: str, attr: AttributeData):
        assert id not in self.attr
        self.attr[id] = attr

    def __getitem__(self, id: str) -> AttributeData:
        return self.attr[id]


@dataclass
class AttributeData:
    """Storing data of an attribute in the same location as in its origin resource.

    Since we cannot pre-populate the size of the attribute data, it has to built dynamically, so we need to store
    the data metadata along for rebuilding
    """

    steps: list[dpath.StepExpr]
    current_step_index: int
    value_step_index: int
    # can be an attribute data or real data (anything but it)
    value: dict[int | str, AttributeData | Any]

    @staticmethod
    def from_raw_path(raw_path: list):
        path = PathParserV2().parse(None, raw_path, "")
        attrdata = AttributeData.from_path(path.steps)
        assert attrdata is not None
        return attrdata

    @staticmethod
    def from_path(steps: list[dpath.StepExpr], idx: int = 0):
        if idx == len(steps):
            return None

        next_idx = idx
        while next_idx < len(steps) - 1:
            step = steps[next_idx]
            if not isinstance(step, dpath.IndexExpr):
                break

            if isinstance(step.val, dpath.Expr):
                # I don't know about recursive path expression yet -- what usecase and how to use them -- so I can't implement.
                raise Exception(
                    f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.val}"
                )

            next_idx += 1

        step = steps[next_idx]
        if isinstance(step, dpath.IndexExpr):
            if isinstance(step.val, dpath.Expr):
                # I don't know about recursive path expression yet -- what usecase and how to use them -- so I can't implement.
                raise Exception(
                    f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.val}"
                )

            # this is the end of the step, we just store it in a dictionary for simplicity (one-item dict)
            # this simply the implementation although we can do better
            return AttributeData(steps, idx, next_idx, {step.val: None})

        if isinstance(step, dpath.SetIndexExpr):
            # we know the keys, so we can pre-populate the data
            value = {}
            for val in step.vals:
                if isinstance(val, dpath.Expr):
                    # I don't know about recursive path expression yet -- what usecase and how to use them -- so I can't implement.
                    raise Exception(
                        f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.vals}"
                    )
                value[val] = AttributeData.from_path(steps, next_idx + 1)
            return AttributeData(steps, idx, next_idx, value)

        if isinstance(step, dpath.RangeExpr):
            if isinstance(step.start, dpath.Expr):
                # I don't know about recursive path expression yet -- what usecase and how to use them -- so I can't implement.
                raise Exception(
                    f"Recursive path expression is not supported yet. Please raise a ticket to notify us for future support! Found: {step.start}"
                )
            if step.start > 0:
                return AttributeData(
                    steps, idx, next_idx, {i: None for i in range(step.start)}
                )

        return AttributeData(steps, idx, next_idx, {})

    def __len__(self):
        if self.current_step_index == self.value_step_index:
            return len(self.value)
        assert self.current_step_index < self.value_step_index
        return 1

    def __getitem__(self, key: int | str) -> AttributeData | Any:
        if self.current_step_index == self.value_step_index:
            if key not in self.value:
                if self.current_step_index == len(self.steps) - 1:
                    # this is the last one
                    self.value[key] = None
                else:
                    next_value_step_index = self._next_non_index_step_idx(
                        self.steps, self.value_step_index + 1
                    )
                    if next_value_step_index == len(self.steps):
                        # the rest of them are all index steps
                        self.value[key] = AttributeData(
                            self.steps,
                            self.current_step_index + 1,
                            len(self.steps) - 1,
                            {},
                        )
                    else:
                        self.value[key] = AttributeData(
                            self.steps,
                            self.current_step_index + 1,
                            next_value_step_index,
                            {},
                        )
            return self.value[key]
        assert self.current_step_index < self.value_step_index
        current_step = self.steps[self.current_step_index]
        assert isinstance(current_step, dpath.IndexExpr) and current_step.val == key
        return AttributeData(
            self.steps,
            self.current_step_index + 1,
            self.value_step_index,
            self.value,
        )

    def __setitem__(self, key: int | str, val: Any):
        if self.current_step_index == self.value_step_index:
            self.value[key] = val
            return
        assert self.current_step_index < self.value_step_index
        current_step = self.steps[self.current_step_index]
        assert isinstance(current_step, dpath.IndexExpr) and current_step.val == key

    @staticmethod
    def _next_non_index_step_idx(steps: list[dpath.StepExpr], start: int = 0):
        for i in range(start, len(steps)):
            if not isinstance(steps[i], dpath.IndexExpr):
                return i
        return len(steps)
