"""
Module for converting between native and networkx graphs.
"""

from networkx import Graph

from .graph import graph


def convert_native_to_networkx(G: graph) -> Graph:
    """Converts a graph to a networkx Graph.

    Args:
            graph (graph): The graph to convert.

    Returns:
            Graph: The converted graph.
    """
    nx_graph = Graph()
    for i in range(G.num_verts):
        nx_graph.add_node(i)
    for edge in G.edges:
        i, j = edge.endpoints
        nx_graph.add_edge(i, j)
    return nx_graph


def convert_networkx_to_native(nx_graph: Graph) -> graph:
    """Converts a networkx Graph to a graph.

    Args:
            nx_graph (Graph): The graph to convert.

    Returns:
            graph: The converted graph.
    """
    G = graph(nx_graph.number_of_nodes())
    for i in range(G.num_verts):
        for j in nx_graph.neighbors(i):
            G.add_edge(i, j)
    return G
