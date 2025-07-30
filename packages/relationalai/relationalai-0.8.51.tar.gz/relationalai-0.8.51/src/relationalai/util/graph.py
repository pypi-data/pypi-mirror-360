from typing import List, Tuple

import networkx as nx
from networkx.classes import DiGraph


def topological_sort(nodes: List[str], edges: List[Tuple[str, str]]) -> List[str]:
    # Check for cycles
    acyclic, dependency_graph =_is_acyclic_graph(nodes, edges)
    if not acyclic:
        raise ValueError("The graph contains a cycle")
    return list(nx.topological_sort(dependency_graph))

def is_acyclic_graph(nodes: List[str], edges: List[Tuple[str, str]]) -> bool:
    return _is_acyclic_graph(nodes, edges)[0]

def _is_acyclic_graph(nodes, edges) -> tuple[bool, DiGraph]:
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return nx.is_directed_acyclic_graph(graph), graph