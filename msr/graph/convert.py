"""
Module for converting between native and networkx graphs.
"""

from networkx import Graph as NetworkXGraph

from .graph import SimpleGraph


def convert_native_to_networkx(G: SimpleGraph) -> NetworkXGraph:
    """Converts a graph to a networkx SimpleGraph.

    Args:
            graph (graph): The graph to convert.

    Returns:
            SimpleGraph: The converted graph.
    """
    nx_graph = NetworkXGraph()
    for i in range(G.num_verts):
        nx_graph.add_node(i)
    for edge in G.edges:
        i, j = edge.endpoints
        nx_graph.add_edge(i, j)
    return nx_graph


def convert_networkx_to_native(nx_graph: NetworkXGraph) -> SimpleGraph:
    """Converts a networkx SimpleGraph to a graph.

    Args:
            nx_graph (NetworkXGraph): The graph to convert.

    Returns:
            graph: The converted graph.
    """
    G = SimpleGraph(nx_graph.number_of_nodes())
    for i in range(G.num_verts):
        for j in nx_graph.neighbors(i):
            G.add_edge(i, j)
    return G
