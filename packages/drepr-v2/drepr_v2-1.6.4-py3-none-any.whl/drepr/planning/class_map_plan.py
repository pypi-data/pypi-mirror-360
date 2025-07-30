from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Optional, TypeAlias, cast
from uuid import uuid4

from drepr.models.prelude import (
    DREPR_URI,
    MISSING_VALUE_TYPE,
    Alignment,
    Attr,
    AttrId,
    Cardinality,
    ClassNode,
    DataNode,
    DRepr,
    EdgeId,
    LiteralNode,
    NodeId,
    Resource,
)
from drepr.models.resource import PreprocessResourceOutput
from drepr.models.sm import DREPR_BLANK
from drepr.planning.drepr_model_alignments import DReprModelAlignments
from drepr.planning.topological_sorting import topological_sorting


@dataclass
class ClassesMapExecutionPlan:
    desc: DRepr
    # read_plans: list[ReadPlan]
    # write_plan: WritePlan
    class_map_plans: list[ClassMapPlan]

    @classmethod
    def create(cls, desc: DRepr):
        desc = cls.rewrite_desc_for_preprocessing_output(desc)

        reversed_topo_orders = topological_sorting(desc.sm)
        alignments = DReprModelAlignments.create(desc)
        edges_optional = {e.edge_id: not e.is_required for e in desc.sm.edges.values()}
        edges_has_missing_values: dict[EdgeId, bool] = {}
        class_map_plans = []
        class2plan = {}

        # find subject attribute of each class
        class2subj: dict[str, AttrId | SingletonSubject] = {}
        for class_id in reversed_topo_orders.topo_order:
            class2subj[class_id] = ClassMapPlan.find_subject(
                desc, class_id, class2subj, alignments
            )

        # figure out if an edge may contain missing values
        n_miss_edges = -1
        while n_miss_edges != len(edges_has_missing_values):
            n_miss_edges = len(edges_has_missing_values)
            for e in desc.sm.edges.values():
                if e.edge_id in edges_has_missing_values:
                    continue
                v = desc.sm.nodes[e.target_id]
                if isinstance(v, DataNode):
                    v_attr = desc.get_attr_by_id(v.attr_id)
                    edges_has_missing_values[e.edge_id] = (
                        len(v_attr.missing_values) > 0
                    ) or v_attr.path.has_optional_steps()
                elif isinstance(v, ClassNode):
                    if any(
                        ve.edge_id not in edges_has_missing_values
                        for ve in desc.sm.iter_outgoing_edges(v.node_id)
                        if not reversed_topo_orders.removed_outgoing_edges[ve.edge_id]
                    ):
                        continue

                    if v.is_blank_node(desc.sm):
                        # it can have missing values when:
                        # (1) at least one edge is mandatory & the edge have missing values
                        # (2) all edges are optional and all of them have missing values
                        have_missing_values = False

                        # (1) at least one edge is mandatory & the edge have missing values
                        for ve in desc.sm.iter_outgoing_edges(v.node_id):
                            if reversed_topo_orders.removed_outgoing_edges[ve.edge_id]:
                                continue

                            if (
                                not edges_optional[ve.edge_id]
                                and edges_has_missing_values[ve.edge_id]
                            ):
                                have_missing_values = True
                                break

                        # (2) all edges are optional and all of them have missing values
                        if not have_missing_values:
                            if all(
                                edges_optional[ve.edge_id]
                                and edges_has_missing_values[ve.edge_id]
                                for ve in desc.sm.iter_outgoing_edges(v.node_id)
                                if not reversed_topo_orders.removed_outgoing_edges[
                                    ve.edge_id
                                ]
                            ):
                                have_missing_values = True
                    else:
                        # it can have missing values when:
                        # (1) at least one edge is mandatory & the edge have missing values
                        # (2) the URI edge have missing values
                        have_missing_values = False

                        # (1) at least one edge is mandatory & the edge have missing values
                        for ve in desc.sm.iter_outgoing_edges(v.node_id):
                            if reversed_topo_orders.removed_outgoing_edges[ve.edge_id]:
                                continue

                            if (
                                not edges_optional[ve.edge_id]
                                and edges_has_missing_values[ve.edge_id]
                            ):
                                have_missing_values = True
                                break

                        # (2) the URI edge have missing values
                        if not have_missing_values:
                            ve_attr = desc.get_attr_by_id(class2subj[v.node_id])
                            if (
                                len(ve_attr.missing_values) > 0
                                or ve_attr.path.has_optional_steps()
                            ):
                                have_missing_values = True

                    edges_has_missing_values[e.edge_id] = have_missing_values
                else:
                    assert isinstance(v, LiteralNode)
                    edges_has_missing_values[e.edge_id] = False

        assert len(edges_has_missing_values) == len(desc.sm.edges) - sum(
            reversed_topo_orders.removed_outgoing_edges.values()
        ), f"{len(edges_has_missing_values)} == {len(desc.sm.edges)} - {sum(reversed_topo_orders.removed_outgoing_edges.values())}"

        # generate plans
        for class_id in reversed_topo_orders.topo_order:
            classplan = ClassMapPlan.create(
                desc,
                class_id,
                class2plan,
                class2subj,
                alignments,
                edges_optional,
                edges_has_missing_values,
                reversed_topo_orders.removed_outgoing_edges,
            )
            class2plan[class_id] = classplan
            class_map_plans.append(classplan)

        return ClassesMapExecutionPlan(desc, class_map_plans)

    @classmethod
    def rewrite_desc_for_preprocessing_output(cls, desc: DRepr):
        if all(pre.get_output() is None for pre in desc.preprocessing):
            return desc

        desc = deepcopy(desc)
        assert all(not isinstance(r, PreprocessResourceOutput) for r in desc.resources)
        for i, pre in enumerate(desc.preprocessing):
            pre_output = pre.get_output()
            if pre_output is None:
                continue
            if pre_output.resource_id is None:
                assert pre_output.attr is not None
                newresource_id = f"dynres_{pre_output.attr}"
                assert desc.get_resource_by_id(newresource_id) is None
            else:
                newresource_id = pre_output.resource_id
            newresource = PreprocessResourceOutput(
                resource_id=newresource_id,
                original_resource_id=pre.get_resource_id(),
            )

            if pre_output.attr is not None:
                newattr = Attr(
                    id=pre_output.attr,
                    resource_id=newresource.id,
                    path=(
                        pre_output.attr_path
                        if pre_output.attr_path is not None
                        else pre.value.path
                    ),
                    missing_values=[None],
                )
                desc.add_attr(newattr)
            desc.add_resource(newresource)

        return desc


@dataclass
class ClassMapPlan:
    class_id: str
    subject: Subject
    data_props: list[DataProp]
    literal_props: list[LiteralProp]
    object_props: list[ObjectProp]
    buffered_object_props: list[ObjectProp]

    @staticmethod
    def create(
        desc: DRepr,
        class_id: NodeId,
        class2plan: dict[NodeId, ClassMapPlan],
        class2subj: dict[NodeId, AttrId | SingletonSubject],
        inference: DReprModelAlignments,
        edges_optional: dict[EdgeId, bool],
        edges_missing_values: dict[EdgeId, bool],
        removed_edges: dict[EdgeId, bool],
    ):
        subj = class2subj[class_id]
        uri_dnode: Optional[DataNode] = None
        blank_dnode: Optional[DataNode] = None
        for e in desc.sm.iter_outgoing_edges(class_id):
            e_abs_uri = e.get_abs_iri(desc.sm)
            if e_abs_uri == DREPR_URI:
                assert uri_dnode is None
                tmp = desc.sm.nodes[e.target_id]
                assert isinstance(tmp, DataNode)
                uri_dnode = tmp
            elif e_abs_uri == DREPR_BLANK:
                assert blank_dnode is None
                tmp = desc.sm.nodes[e.target_id]
                assert isinstance(tmp, DataNode)
                blank_dnode = tmp

        assert not (uri_dnode is not None and blank_dnode is not None)

        # generate other properties
        literal_props = []
        data_props: list[DataProp] = []
        object_props = []
        buffered_object_props = []

        for e in desc.sm.iter_outgoing_edges(class_id):
            target = desc.sm.nodes[e.target_id]
            if isinstance(target, DataNode):
                assert not isinstance(
                    subj, SingletonSubject
                ), "Subject cannot be a singleton subject if there is a data node associated with the class"

                attribute = desc.get_attr_by_id(target.attr_id)
                e_abs_iri = e.get_abs_iri(desc.sm)
                if e_abs_iri != DREPR_URI and e_abs_iri != DREPR_BLANK:
                    alignments = inference.get_alignments(subj, target.attr_id)
                    alignments_cardinality = inference.estimate_cardinality(alignments)

                    if attribute.value_type.is_list():
                        if alignments_cardinality.is_one_to_star():
                            alignments_cardinality = Cardinality.OneToMany
                        else:
                            assert (
                                alignments_cardinality.is_many_to_star()
                            ), alignments_cardinality
                            alignments_cardinality = Cardinality.ManyToMany

                    data_props.append(
                        DataProp(
                            alignments=alignments,
                            alignments_cardinality=inference.estimate_cardinality(
                                alignments
                            ),
                            predicate=e.get_abs_iri(desc.sm),
                            attr=attribute,
                            is_optional=edges_optional[e.edge_id],
                            missing_values=set(attribute.missing_values),
                            missing_path=attribute.path.has_optional_steps(),
                            datatype=(target.data_type),
                        )
                    )
            elif isinstance(target, LiteralNode):
                literal_props.append(
                    LiteralProp(
                        predicate=e.get_abs_iri(desc.sm),
                        value=target.value,
                        datatype=target.data_type,
                    )
                )
            elif isinstance(target, ClassNode):
                assert not isinstance(
                    subj, SingletonSubject
                ), "Subject cannot be a singleton subject if there is a class node associated with the class"
                target_subj = class2subj[e.target_id]
                if isinstance(target_subj, SingletonSubject):
                    object_props.append(
                        SingletonObject(
                            target_class_id=e.target_id,
                            predicate=e.get_abs_iri(desc.sm),
                            is_blank=target.is_blank_node(desc.sm),
                        )
                    )
                else:
                    attribute = desc.get_attr_by_id(target_subj)

                    alignments = inference.get_alignments(subj, attribute.id)
                    if len(alignments) == 0:
                        # there is no alignment between the subj and attribute.id
                        raise Exception(
                            f"Cannot find alignment between {subj} and {attribute.id}"
                        )

                    if target.is_blank_node(desc.sm):
                        if any(
                            etmp.get_abs_iri(desc.sm) == DREPR_BLANK
                            for etmp in desc.sm.iter_outgoing_edges(target.node_id)
                        ):
                            # ensure that it is consistent
                            assert (
                                target.node_id in class2plan
                                and isinstance(
                                    (
                                        targetclsplansubj := class2plan[
                                            target.node_id
                                        ].subject
                                    ),
                                    BlankSubject,
                                )
                                and targetclsplansubj.use_attr_value
                            )
                            use_attr_value = True
                        else:
                            use_attr_value = False
                        prop = BlankObject(
                            attr=attribute,
                            alignments_cardinality=inference.estimate_cardinality(
                                alignments
                            ),
                            alignments=alignments,
                            predicate=e.get_abs_iri(desc.sm),
                            class_id=class_id,
                            object_id=target.node_id,
                            is_optional=edges_optional[e.edge_id],
                            can_target_missing=edges_missing_values[e.edge_id],
                            use_attr_value=use_attr_value,
                        )
                    else:
                        prop = IDObject(
                            attr=attribute,
                            alignments_cardinality=inference.estimate_cardinality(
                                alignments
                            ),
                            alignments=alignments,
                            predicate=e.get_abs_iri(desc.sm),
                            class_id=class_id,
                            is_optional=edges_optional[e.edge_id],
                            can_target_missing=edges_missing_values[e.edge_id],
                            missing_values=set(attribute.missing_values),
                        )

                    if removed_edges[e.edge_id]:
                        buffered_object_props.append(prop)
                    else:
                        object_props.append(prop)

        if isinstance(subj, SingletonSubject):
            subject = subj
        else:
            subj_attr = desc.get_attr_by_id(subj)
            if uri_dnode is None:
                if blank_dnode is not None:
                    assert blank_dnode.attr_id == subj
                subject = BlankSubject(
                    attr=subj_attr,
                    use_attr_value=blank_dnode is not None,
                    missing_values=set(subj_attr.missing_values),
                )
            else:
                # get missing values from the real subjects
                missing_values = set(subj_attr.missing_values)
                (uri_dnode_inedge,) = [
                    e
                    for e in desc.sm.get_edges_between_nodes(
                        class_id, uri_dnode.node_id
                    )
                    if e.get_abs_iri(desc.sm) == DREPR_URI
                ]

                if uri_dnode.attr_id == subj:
                    subject = InternalIDSubject(
                        attr=subj_attr,
                        is_optional=edges_optional[uri_dnode_inedge.edge_id],
                        missing_values=missing_values,
                    )
                else:
                    subject = ExternalIDSubject(
                        attr=subj_attr,
                        is_optional=edges_optional[uri_dnode_inedge.edge_id],
                        missing_values=missing_values,
                    )

        return ClassMapPlan(
            class_id=class_id,
            subject=subject,
            data_props=data_props,
            literal_props=literal_props,
            object_props=object_props,
            buffered_object_props=buffered_object_props,
        )

    @staticmethod
    def find_subject(
        desc: DRepr,
        class_id: NodeId,
        class2subj: dict[NodeId, AttrId | SingletonSubject],
        desc_aligns: DReprModelAlignments,
    ):
        """
        Find the subject of the class among the attributes of the class.

        The subject has *-to-one relationship with other attributes.
        """
        # get data nodes, attributes, and the attribute that contains URIs of the class
        data_nodes: list[DataNode] = []
        attrs: list[AttrId] = []
        uri_attr: Optional[AttrId] = None
        blank_attr: Optional[AttrId] = None

        for e in desc.sm.iter_outgoing_edges(class_id):
            target = desc.sm.nodes[e.target_id]

            if isinstance(target, DataNode):
                data_nodes.append(target)
                attrs.append(target.attr_id)

                e_abs_iri = e.get_abs_iri(desc.sm)
                if e_abs_iri == DREPR_URI:
                    assert uri_attr is None
                    uri_attr = target.attr_id
                elif e_abs_iri == DREPR_BLANK:
                    assert blank_attr is None
                    blank_attr = target.attr_id

        assert not (uri_attr is not None and blank_attr is not None)

        if uri_attr is not None:
            # always use the URI attribute because there can be a property that is a list
            return uri_attr

        if blank_attr is not None:
            # always use the blank attribute because there can be a property that is a list
            return blank_attr

        # if the subject attribute is provided, then, we will use it.
        subjs = []
        classnode = desc.sm.get_class_node(class_id)
        if classnode.subject is not None:
            subjs.append(classnode.subject)

        if len(subjs) == 0:
            if len(attrs) == 0:
                # there is a special case where the class has no data node, but only links to other classes
                # we need to get the subject from the other classes
                other_attrs: list[AttrId] = []
                for e in desc.sm.iter_outgoing_edges(class_id):
                    target = desc.sm.nodes[e.target_id]
                    if isinstance(target, ClassNode):
                        # we must have inferred the subject of the target class before (because of the topological sorting)
                        assert target.node_id in class2subj
                        target_subj = class2subj[target.node_id]
                        if not isinstance(target_subj, SingletonSubject):
                            other_attrs.append(target_subj)

                if len(other_attrs) > 0:
                    # there is link to other classes, so we need to infer the subject from the other classes
                    subjs = desc_aligns.infer_subject(other_attrs)
                else:
                    # this happens when it's a static class, only static properties without any data node or links
                    return SingletonSubject(
                        class_id,
                        is_blank=desc.sm.get_class_node(class_id).is_blank_node(
                            desc.sm
                        ),
                    )
            else:
                # invoke the inference to find the subject attribute
                subjs = desc_aligns.infer_subject(attrs)

        if len(subjs) == 0:
            raise Exception(
                "There is no subject attribute of class: {} ({}). Users need to specify it explicitly".format(
                    cast(ClassNode, desc.sm.nodes[class_id]).label, class_id
                )
            )

        return ClassMapPlan.select_subject(desc, class_id, subjs, attrs)

    @staticmethod
    def select_subject(
        desc: DRepr,
        class_id: NodeId,
        subjs: list[AttrId],
        attrs: list[AttrId],
    ) -> AttrId:
        return subjs[0]


@dataclass
class BlankSubject:
    attr: Attr
    # whether to use the attribute value as the value of the subject
    use_attr_value: bool
    # only works when use_attr_value is True
    missing_values: set[MISSING_VALUE_TYPE]


@dataclass
class InternalIDSubject:
    attr: Attr
    is_optional: bool
    missing_values: set[MISSING_VALUE_TYPE]


@dataclass
class ExternalIDSubject:
    attr: Attr
    is_optional: bool
    missing_values: set[MISSING_VALUE_TYPE]


@dataclass
class SingletonSubject:
    class_id: str
    is_blank: bool


Subject: TypeAlias = (
    BlankSubject | InternalIDSubject | ExternalIDSubject | SingletonSubject
)


@dataclass
class DataProp:
    alignments: list[Alignment]
    alignments_cardinality: Cardinality
    predicate: str
    attr: Attr
    is_optional: bool
    missing_values: set[MISSING_VALUE_TYPE]
    missing_path: bool
    datatype: Optional[str]

    @property
    def can_target_missing(self):
        return len(self.missing_values) > 0 or self.missing_path


@dataclass
class LiteralProp:
    predicate: str
    value: Any
    datatype: Optional[str]


@dataclass
class BlankObject:
    attr: Attr
    alignments: list[Alignment]
    alignments_cardinality: Cardinality
    predicate: str
    class_id: NodeId
    object_id: NodeId
    is_optional: bool
    # whether an instance of the target class can be missing
    can_target_missing: bool
    # whether to use the attribute value as the value of the blank object
    use_attr_value: bool

    def is_object_blank(self):
        return True


@dataclass
class IDObject:
    attr: Attr
    alignments: list[Alignment]
    alignments_cardinality: Cardinality
    predicate: str
    class_id: NodeId
    is_optional: bool
    # whether an instance of the target class can be missing
    can_target_missing: bool
    missing_values: set[MISSING_VALUE_TYPE]

    def is_object_blank(self):
        return False


@dataclass
class SingletonObject:
    target_class_id: NodeId
    predicate: str
    is_blank: bool

    @property
    def is_optional(self):
        return False

    @property
    def can_target_missing(self):
        return False

    def is_object_blank(self):
        return True


ObjectProp = BlankObject | IDObject | SingletonObject
