"""GRAPH

This subpackage contains the graph class and functions for generating,
saving/loading, embedding/drawing, and performing operations on graphs. The
`saved/` directory contains a collection of graphs.
"""

from .draw import draw_graph, draw_graphs
from .file_io import (
    SAVED_GRAPH_DIR,
    load_graph,
    load_graphs_from_directory,
    save_graph,
)
from .generate import generate_and_save_all_graphs_on_n_vertices
from .graph import SimpleGraph
from .graph_lib import (
    complete,
    cycle,
    empty,
    house,
    path,
    petersen,
    star,
    triforce,
    wheel,
)

# essential
__all__ = [
    "draw_graph",
    "draw_graphs",
    "generate_and_save_all_graphs_on_n_vertices",
    "SimpleGraph",
    "load_graph",
    "load_graphs_from_directory",
    "save_graph",
    "SAVED_GRAPH_DIR",
]

# graph_lib
__all__ += [
    "complete",
    "cycle",
    "empty",
    "house",
    "path",
    "petersen",
    "star",
    "triforce",
    "wheel",
]
