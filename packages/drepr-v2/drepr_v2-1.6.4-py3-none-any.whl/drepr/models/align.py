from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

from drepr.models.attr import AttrId

if TYPE_CHECKING:
    from drepr.models.drepr import DRepr


@dataclass
class AlignedStep:
    source_idx: int
    target_idx: int


@dataclass
class RangeAlignment:
    source: AttrId
    target: AttrId
    aligned_steps: list[AlignedStep]

    def swap(self) -> RangeAlignment:
        return RangeAlignment(
            self.target,
            self.source,
            [AlignedStep(s.target_idx, s.source_idx) for s in self.aligned_steps],
        )

    def compute_cardinality(self, desc: DRepr) -> Cardinality:
        """
        Compute the cardinality of an alignment

        The cardinality between attribute `x` and attribute `y` are defined as follows:

        1. one-to-one: one item of `x` can only link to one item of `y` and vice versa.
        2. one-to-many: one item of `x` can link to multiple items of `y`, but one item of `y` can only
           link to one item of `x`.
        3. many-to-one: the reversed case of one-to-many
        4. many-to-many: multiple items of `x` can link to multiple items of `y` and vice versa.

        The cardinality depends on the number of unfixed dimensions of each attribute, if an attribute
        has no unfixed steps, it will be one-to-*, otherwise many-to-*
        """
        source = desc.get_attr_by_id(self.source)
        target = desc.get_attr_by_id(self.target)

        source_nary_steps = set(source.path.get_nary_steps())
        target_nary_steps = set(target.path.get_nary_steps())
        for step in self.aligned_steps:
            source_nary_steps.discard(step.source_idx)
            target_nary_steps.discard(step.target_idx)

        if len(source_nary_steps) == 0:
            if len(target_nary_steps) == 0:
                return Cardinality.OneToOne
            else:
                return Cardinality.OneToMany
        else:
            if len(target_nary_steps) == 0:
                return Cardinality.ManyToOne
            else:
                return Cardinality.ManyToMany


@dataclass
class ValueAlignment:
    source: AttrId
    target: AttrId

    def swap(self) -> ValueAlignment:
        return ValueAlignment(self.target, self.source)

    def compute_cardinality(self, desc: DRepr) -> Cardinality:
        """
        Compute the cardinality of an alignment

        The cardinality between attribute `x` and attribute `y` are defined as follows:

        1. one-to-one: one item of `x` can only link to one item of `y` and vice versa.
        2. one-to-many: one item of `x` can link to multiple items of `y`, but one item of `y` can only
           link to one item of `x`.
        3. many-to-one: the reversed case of one-to-many
        4. many-to-many: multiple items of `x` can link to multiple items of `y` and vice versa.

        The cardinality of the join will be one-to-* or *-to-one if values of source & target are unique.
        """
        source = desc.get_attr_by_id(self.source)
        target = desc.get_attr_by_id(self.target)

        if source.unique:
            if target.unique:
                return Cardinality.OneToOne
            else:
                return Cardinality.OneToMany
        else:
            if target.unique:
                return Cardinality.ManyToOne
            else:
                return Cardinality.ManyToMany


@dataclass
class IdenticalAlign:
    source: AttrId
    target: AttrId

    def compute_cardinality(self, desc: DRepr) -> Cardinality:
        return Cardinality.OneToOne

    def swap(self) -> IdenticalAlign:
        return IdenticalAlign(self.target, self.source)


@dataclass
class AutoAlignment:
    attrs: Optional[list[str]] = None

    def compute_cardinality(self, desc: DRepr) -> Cardinality:
        raise NotImplementedError(
            """Auto alignment will be preprocessed to turn into Range/Value alignment, so it should not be used to compute cardinality"""
        )


Alignment = Union[RangeAlignment, ValueAlignment, IdenticalAlign, AutoAlignment]


class AlignmentType(Enum):
    Range = "range"
    Value = "value"
    Ident = "identical"
    Auto = "auto"


class Cardinality(Enum):
    OneToOne = "one-to-one"
    OneToMany = "one-to-many"
    ManyToOne = "many-to-one"
    ManyToMany = "many-to-many"

    def is_star_to_many(self) -> bool:
        return self == Cardinality.OneToMany or self == Cardinality.ManyToMany

    def is_one_to_star(self) -> bool:
        return self == Cardinality.OneToOne or self == Cardinality.OneToMany

    def is_many_to_star(self) -> bool:
        return self == Cardinality.ManyToOne or self == Cardinality.ManyToMany
