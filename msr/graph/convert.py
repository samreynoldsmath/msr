from networkx import Graph

from .simple_undirected_graph import simple_undirected_graph


def convert_native_to_networkx(G: simple_undirected_graph) -> Graph:
    """Converts a simple_undirected_graph to a networkx Graph.

    Args:
            graph (simple_undirected_graph): The graph to convert.

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


def convert_networkx_to_native(nx_graph: Graph) -> simple_undirected_graph:
    """Converts a networkx Graph to a simple_undirected_graph.

    Args:
            nx_graph (Graph): The graph to convert.

    Returns:
            simple_undirected_graph: The converted graph.
    """
    G = simple_undirected_graph(nx_graph.number_of_nodes())
    for i in range(G.num_verts):
        for j in nx_graph.neighbors(i):
            G.add_edge(i, j)
    return G
