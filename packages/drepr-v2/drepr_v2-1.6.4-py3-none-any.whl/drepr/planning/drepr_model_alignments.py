from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from graph.retworkx import RetworkXStrDiGraph

from drepr.models.prelude import (
    AlignedStep,
    Alignment,
    Attr,
    AttrId,
    AutoAlignment,
    Cardinality,
    DRepr,
    IdenticalAlign,
    IndexExpr,
    PreprocessResourceOutput,
    RangeAlignment,
    RangeExpr,
    SetIndexExpr,
    ValueAlignment,
)


@dataclass
class DReprModelAlignments:
    desc: DRepr
    aligns: dict[tuple[AttrId, AttrId], list[Alignment]]

    @staticmethod
    def create(desc: DRepr) -> DReprModelAlignments:
        """Infer all possible alignments from the model."""
        aligns = {(src.id, tgt.id): [] for src in desc.attrs for tgt in desc.attrs}

        for a in desc.aligns:
            if isinstance(a, RangeAlignment):
                aligns[(a.source, a.target)] = [a]
                aligns[(a.target, a.source)] = [a.swap()]
            elif isinstance(a, ValueAlignment):
                aligns[(a.source, a.target)] = [a]
                aligns[(a.target, a.source)] = [a.swap()]
            elif isinstance(a, AutoAlignment):
                if a.attrs is None:
                    attrs = desc.attrs
                else:
                    attrs = [desc.get_attr_by_id(attr) for attr in a.attrs]

                # now for each pair of attributes, we look at there steps and align them one by one
                for source in attrs:
                    for target in attrs:
                        if (
                            source.id == target.id
                            or len(aligns[source.id, target.id]) > 0
                        ):
                            continue

                        if source.resource_id != target.resource_id:
                            # check if source & target is derived from the same resource
                            source_resource = desc.get_resource_by_id(
                                source.resource_id
                            )
                            assert source_resource is not None
                            if not (
                                isinstance(source_resource, PreprocessResourceOutput)
                                and source_resource.get_preprocessing_original_resource_id()
                                == target.resource_id
                            ):
                                continue

                        new_align = DReprModelAlignments.auto_align(source, target)
                        if new_align is not None:
                            aligns[(source.id, target.id)] = [new_align]
                            aligns[(target.id, source.id)] = [new_align.swap()]
            elif isinstance(a, IdenticalAlign):
                raise Exception(
                    "Unreachable! Users should not provide identical alignment in the model"
                )

        for a in desc.attrs:
            aligns[(a.id, a.id)] = [IdenticalAlign(a.id, a.id)]

        inf = DReprModelAlignments(desc, aligns)
        inf.inference()
        return inf

    def get_alignments(self, source: AttrId, target: AttrId) -> list[Alignment]:
        return self.aligns[(source, target)]

    def inference(self):
        ig: dict[str, dict[str, int]] = {
            attr.id: {attr.id: 0} for attr in self.desc.attrs
        }
        for (source, target), aligns in self.aligns.items():
            assert len(aligns) <= 1, aligns
            if source == target or len(aligns) == 0:
                continue
            if isinstance(aligns[0], (RangeAlignment, ValueAlignment, IdenticalAlign)):
                ig[source][target] = sum(
                    self.score_alignment(align) for align in aligns
                )
            elif not isinstance(aligns[0], IdenticalAlign):
                print(aligns)
                raise Exception("Unreachable")

        ig_2nd = ig
        while True:
            ig_3rd = defaultdict(dict)
            for u0 in ig_2nd:
                # for updated neighbors of u0
                for u1 in ig_2nd[u0]:
                    for u2 in ig[u1]:
                        afuncs = self.infer_func(u0, u1, u2)
                        if afuncs is not None:
                            score = sum(self.score_alignment(align) for align in afuncs)
                            if u2 not in ig[u0] or ig[u0][u2] > score:
                                # we found a better alignment
                                self.aligns[u0, u2] = afuncs
                                ig_3rd[u0][u2] = score

            for u0 in ig_3rd:
                for u2, score in ig_3rd[u0].items():
                    ig[u0][u2] = score
            ig_2nd = ig_3rd
            if len(ig_2nd) == 0:
                break

    def infer_subject(self, attrs: list[AttrId]) -> list[AttrId]:
        """
        Find all attributes that can be the subject of these attributes

        The subject must has one to one mapping to all attrs and:
        (1) have no missing path
        (2) have missing path, but the missing path is the same for all attrs.

        (1) has higher priority than (2).
        """
        subjs = []

        # if one or these attributes has *-to-one, then that is the subjects
        for a in attrs:
            is_subj = True
            for ai in attrs:
                if len(self.aligns[(a, ai)]) == 0:
                    # no alignment
                    is_subj = False
                    break

                cardin = self.estimate_cardinality(self.aligns[(a, ai)])
                if cardin == Cardinality.ManyToMany:
                    is_subj = False
                    break
                elif cardin == Cardinality.OneToMany:
                    is_subj = False
                    break
            if is_subj:
                subjs.append(a)

        if len(subjs) == 0:
            attr_ids = set(attrs)

            # we have to try the external attributes
            for attr in self.desc.attrs:
                if attr.id in attr_ids:
                    continue

                is_candidate_subj = True
                covered_dims = set()

                for ai in attrs:
                    # we can only infer if there are any duplications if the alignments are dimensional
                    # if they are dimension alignment, then the optimization engine must compress them into
                    # just one alignment
                    if len(self.aligns[attr.id, ai]) != -1 or not isinstance(
                        self.aligns[attr.id, ai][0], RangeAlignment
                    ):
                        is_candidate_subj = False
                        break

                    align = self.aligns[attr.id, ai][0]
                    assert isinstance(align, RangeAlignment)
                    align_cardin = align.compute_cardinality(self.desc)
                    if align_cardin == Cardinality.ManyToMany:
                        is_candidate_subj = False
                        break
                    elif align_cardin == Cardinality.OneToMany:
                        is_candidate_subj = False
                        break
                    else:
                        for ad in align.aligned_steps:
                            covered_dims.add(ad.source_idx)

                if is_candidate_subj and covered_dims == set(
                    attr.path.get_nary_steps()
                ):
                    # the second condition detect if there is duplication
                    subjs.append(attr.id)

        if len(subjs) > 0:
            # now, we filter the missing path condition, if there is subject that have no missing path, we use them.
            if any(
                not self.desc.get_attr_by_id(subj).path.has_optional_steps()
                for subj in subjs
            ):
                return [
                    subj
                    for subj in subjs
                    if not self.desc.get_attr_by_id(subj).path.has_optional_steps()
                ]

            # check if we have subject with missing path, but the missing path is the same or less restricted for all attrs
            filtered_subjs = []

            for subj_id in subjs:
                subj = self.desc.get_attr_by_id(subj_id)

                # now we need to check if this subject has the same or less restricted missing path to all attrs.
                if all(
                    subj.path.has_same_or_less_optional_steps(
                        self.desc.get_attr_by_id(ai).path
                    )
                    for ai in attrs
                ):
                    filtered_subjs.append(subj_id)

            subjs = filtered_subjs

        return subjs

    def infer_func(
        self, xid: AttrId, yid: AttrId, zid: AttrId
    ) -> Optional[list[Alignment]]:
        """Infer an alignment function of xid and zid given alignments between (xid, yid) and (yid, zid)

        If there is only one way to join values of xid and zid, then the chain join will be the correct one
        """

        f = self.aligns[xid, yid]
        g = self.aligns[yid, zid]

        f_cardin = self.estimate_cardinality(f)
        g_cardin = self.estimate_cardinality(g)

        # filter the case where we cannot chain these alignments
        can_chain_alignments = (
            f_cardin == Cardinality.OneToOne or f_cardin == Cardinality.OneToMany
        ) or (g_cardin == Cardinality.OneToOne or g_cardin == Cardinality.ManyToOne)

        if not can_chain_alignments:
            return None

        # chain them together
        return self.optimize_chained_alignments(f + g)

    def estimate_cardinality(self, aligns: list[Alignment]) -> Cardinality:
        cardin = aligns[0].compute_cardinality(self.desc)
        # must always be > 0
        if len(aligns) <= 1 or cardin == Cardinality.ManyToMany:
            return cardin

        for i in range(1, len(aligns)):
            cardin_i = aligns[i].compute_cardinality(self.desc)

            if cardin_i == Cardinality.OneToOne:
                # do nothing, as this does not change the cardin
                pass
            elif cardin_i == Cardinality.OneToMany:
                if cardin == Cardinality.OneToOne:
                    cardin = Cardinality.OneToMany
                elif cardin == Cardinality.OneToMany:
                    cardin = Cardinality.OneToMany
                elif cardin == Cardinality.ManyToOne:
                    # we don't know whether it is going to be M2M, O2O, O2M, M2O so we do a conservative prediction
                    return Cardinality.ManyToMany
                else:
                    raise Exception("Unreachable")
            elif cardin_i == Cardinality.ManyToOne:
                if cardin == Cardinality.OneToOne:
                    cardin = Cardinality.ManyToOne
                elif cardin == Cardinality.OneToMany:
                    return Cardinality.ManyToMany
                elif cardin == Cardinality.ManyToOne:
                    cardin = Cardinality.ManyToOne
                else:
                    raise Exception("Unreachable")
            elif cardin_i == Cardinality.ManyToMany:
                return cardin_i

        return cardin

    def optimize_chained_alignments(self, aligns: list[Alignment]) -> list[Alignment]:
        if len(aligns) == 0:
            return []

        joins = []

        # rule 1: consecutive dimension alignments are combined together
        joins.append(aligns[0])

        for align in aligns[1:]:
            lastjoin = joins[-1]
            if isinstance(lastjoin, RangeAlignment) and isinstance(
                align, RangeAlignment
            ):
                # we merge them together
                a0 = lastjoin
                a1 = align
                a1map = {ad.source_idx: ad.target_idx for ad in a1.aligned_steps}

                joins[-1] = RangeAlignment(
                    source=a0.source,
                    target=a1.target,
                    aligned_steps=[
                        AlignedStep(
                            source_idx=ad.source_idx, target_idx=a1map[ad.target_idx]
                        )
                        for ad in a0.aligned_steps
                        if ad.target_idx in a1map
                    ],
                )
            else:
                joins.append(align)

        return joins

    @staticmethod
    def auto_align(
        source: Attr, target: Attr
    ) -> Optional[RangeAlignment | IdenticalAlign]:
        # TODO: fix auto-alignment
        source_range_steps = [
            i for i, step in enumerate(source.path.steps) if isinstance(step, RangeExpr)
        ]
        target_range_steps = [
            i for i, step in enumerate(target.path.steps) if isinstance(step, RangeExpr)
        ]

        if len(source_range_steps) == 0 or len(target_range_steps) == 0:
            # mapping between two single values is identical mapping
            is_source_single_val = all(
                isinstance(step, IndexExpr) for step in source.path.steps
            )
            is_target_single_val = all(
                isinstance(step, IndexExpr) for step in target.path.steps
            )
            if is_source_single_val and is_target_single_val:
                return IdenticalAlign(source.id, target.id)

            if is_source_single_val or is_target_single_val:
                return RangeAlignment(source.id, target.id, [])
            return None

        end = min(source_range_steps[-1], target_range_steps[-1]) + 1
        assert end > 0

        if source.path.steps[:end] == target.path.steps[:end]:
            # we can align all of them as long as all the steps are index
            if all(
                isinstance(step, (RangeExpr, IndexExpr, SetIndexExpr))
                for step in source.path.steps
            ) and all(
                isinstance(step, (RangeExpr, IndexExpr, SetIndexExpr))
                for step in target.path.steps
            ):
                return RangeAlignment(
                    source=source.id,
                    target=target.id,
                    aligned_steps=[
                        AlignedStep(source_idx=dim, target_idx=dim)
                        for dim in source_range_steps[
                            : min(len(target_range_steps), len(source_range_steps))
                        ]
                    ],
                )

        return None

    def score_alignment(self, align: Alignment) -> int:
        """Score an alignment function so we can justify if an alignment is new/better or not. Lower score is better."""
        if isinstance(align, RangeAlignment):
            card = align.compute_cardinality(self.desc)
            if card == Cardinality.OneToOne:
                return 1
            elif card == Cardinality.OneToMany or card == Cardinality.ManyToOne:
                return 2
            else:
                return 3
        if isinstance(align, ValueAlignment):
            card = align.compute_cardinality(self.desc)
            if card == Cardinality.OneToOne:
                return 4
            elif card == Cardinality.OneToMany or card == Cardinality.ManyToOne:
                return 5
            else:
                return 6
        assert isinstance(align, IdenticalAlign)
        return 0


@dataclass
class CustomedDfs:
    """
    THE FOLLOWING CODE IS ADAPTED FROM: https://docs.rs/petgraph/0.4.13/src/petgraph/visit/traversal.rs.html#38-43
    so that DFS also yield the parent node

    Visit nodes of a graph in a depth-first-search (DFS) emitting nodes in
    preorder (when they are first discovered).

    The traversal starts at a given node and only traverses nodes reachable
    from it.

    `Dfs` is not recursive.

    `Dfs` does not itself borrow the graph, and because of this you can run
    a traversal over a graph while still retaining mutable access to it, if you
    use it like the following example:

    ```
    use petgraph::Graph;
    use petgraph::visit::Dfs;

    let mut graph = Graph::<_,()>::new();
    let a = graph.add_node(0);

    let mut dfs = Dfs::new(&graph, a);
    while let Some(nx) = dfs.next(&graph) {
        // we can access `graph` mutably here still
        graph[nx] += 1;
    }

    assert_eq!(graph[a], 1);
    ```

    **Note:** The algorithm may not behave correctly if nodes are removed
    during iteration. It may not necessarily visit added nodes or edges.
    """

    stack: list[tuple[str, str]]
    discovered: VisitMap

    @staticmethod
    def empty() -> CustomedDfs:
        """Create a new **Dfs** using the graph's visitor map, and no stack."""
        return CustomedDfs([], VisitMap())

    @staticmethod
    def from_graph(graph: RetworkXStrDiGraph, start: str) -> CustomedDfs:
        """
        Create a new **Dfs**, using the graph's visitor map, and put **start**
        in the stack of nodes to visit.
        """
        dfs = CustomedDfs.empty()
        dfs.move_to(start)
        return dfs

    def move_to(self, start: str):
        """
        Keep the discovered map, but clear the visit stack and restart
        the dfs from a particular node.
        """
        self.discovered.visit(start)
        self.stack.clear()
        self.stack.append((start, start))

    def next(
        self, graph: RetworkXStrDiGraph, revisit: set[str]
    ) -> Optional[tuple[str, str]]:
        if len(self.stack) == 0:
            return None

        (parent_node, node) = self.stack.pop()
        for e in graph.out_edges(node):
            succ = e.target
            if self.discovered.visit(succ) or succ in revisit:
                self.stack.append((node, succ))
        return (parent_node, node)


@dataclass
class VisitMap:
    """A mapping for storing the visited status for NodeId `N`."""

    map: set[str] = field(default_factory=set)

    def visit(self, a: str) -> bool:
        """
        Mark `a` as visited.

        Return **true** if this is the first visit, false otherwise.
        """
        if a in self.map:
            return False
        self.map.add(a)
        return True

    def is_visited(self, a: str) -> bool:
        """Return whether `a` has been visited before."""
        return a in self.map
