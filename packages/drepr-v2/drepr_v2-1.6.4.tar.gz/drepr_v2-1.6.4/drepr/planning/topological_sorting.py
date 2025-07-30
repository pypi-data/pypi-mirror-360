from __future__ import annotations

from dataclasses import dataclass

from drepr.models.sm import ClassNode, SemanticModel


@dataclass
class ReversedTopoSortResult:
    # list of class node ids
    topo_order: list[str]
    # list of edge ids that are removed
    removed_outgoing_edges: dict[int, bool]


def topological_sorting(sm: SemanticModel) -> ReversedTopoSortResult:
    """
    suppose we have a semantic model, that may contains circle, our task is to
    generate a topological order from the directed cyclic graph, and a set of edges
    involved in the cycles that are removed in order to generate the topo-order
    """
    visited_nodes = {uid: False for uid in sm.nodes}
    tmp_visited_nodes = {uid: False for uid in sm.nodes}
    removed_outgoing_edges = {eid: False for eid in sm.edges}

    while True:
        # pick a node from the remaining nodes and do reverse dfs. if we found a cycle,
        # then we break the cycle and repeat the process until we no cycle left
        random_start_node = next(iter(sm.nodes))
        has_unvisited_node = False
        for uid, u in sm.nodes.items():
            if not visited_nodes[uid] and isinstance(u, ClassNode):
                random_start_node = uid
                has_unvisited_node = True
                break

        if not has_unvisited_node:
            # we don't have any unvisited node left, so we finish!
            break

        # loop until it breaks all cycles
        while dfs_breaking_cycle(sm, random_start_node, [], removed_outgoing_edges):
            pass

        # mark visited nodes so that we can just skip them
        reverse_dfs(sm, random_start_node, visited_nodes, removed_outgoing_edges)

    # now we get acyclic graph, determine the topo-order
    reversed_topo_order = []
    for uid in sm.nodes:
        visited_nodes[uid] = False
        tmp_visited_nodes[uid] = False

    for uid, u in sm.nodes.items():
        if not visited_nodes[uid] and isinstance(u, ClassNode):
            dfs_reverse_topo_sort(
                sm,
                reversed_topo_order,
                uid,
                visited_nodes,
                tmp_visited_nodes,
                removed_outgoing_edges,
            )

    return ReversedTopoSortResult(
        topo_order=reversed_topo_order, removed_outgoing_edges=removed_outgoing_edges
    )


def dfs_reverse_topo_sort(
    sm: SemanticModel,
    topo_order: list[str],
    node: str,
    visited_nodes: dict[str, bool],
    tmp_visited_nodes: dict[str, bool],
    removed_outgoing_edges: dict[int, bool],
):
    """
    Generate a topological order of class nodes in the semantic model. The graph must be acyclic
    before using this function

    Based on DFS algorithm in here: https://en.wikipedia.org/wiki/Topological_sorting
    """
    if visited_nodes[node]:
        return

    if tmp_visited_nodes[node]:
        raise Exception("The graph has cycle!")

    tmp_visited_nodes[node] = True

    for e in sm.iter_outgoing_edges(node):
        if not removed_outgoing_edges[e.edge_id] and isinstance(
            sm.nodes[e.target_id], ClassNode
        ):
            dfs_reverse_topo_sort(
                sm,
                topo_order,
                e.target_id,
                visited_nodes,
                tmp_visited_nodes,
                removed_outgoing_edges,
            )

    tmp_visited_nodes[node] = False
    visited_nodes[node] = True
    topo_order.append(node)


def dfs_breaking_cycle(
    sm: SemanticModel,
    node: str,
    visited_path: list[str],
    removed_outgoing_edges: dict[int, bool],
) -> bool:
    """
    Try to break cycles using invert DFS. It returns true when break one cycle, and it terminates
    immediately. Thus, requires you to run this function many times until it return false
    """
    visited_path.append(node)

    for e in sm.iter_incoming_edges(node):
        if not removed_outgoing_edges[e.edge_id]:
            if e.source_id in visited_path:
                # this node is visited before in the path, and it is visited by traveling through `e`, we can drop `e` and move on
                removed_outgoing_edges[e.edge_id] = True
                return True

            if dfs_breaking_cycle(
                sm, e.source_id, visited_path, removed_outgoing_edges
            ):
                return True

    visited_path.pop()
    return False


def reverse_dfs(
    sm: SemanticModel,
    node: str,
    visited_nodes: dict[str, bool],
    removed_outgoing_edges: dict[int, bool],
) -> bool:
    """Reverse DFS to visit all ancestors of a node"""
    visited_nodes[node] = True
    for e in sm.iter_incoming_edges(node):
        if not removed_outgoing_edges[e.edge_id]:
            reverse_dfs(sm, e.source_id, visited_nodes, removed_outgoing_edges)
