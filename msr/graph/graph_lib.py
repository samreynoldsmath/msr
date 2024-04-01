"""
Module for specific graphs, such as the complete graph, path graph, etc.
"""

from .graph import SimpleGraph

### variable number of vertices ###############################################


def empty(num_vert: int) -> SimpleGraph:
    """Return an empty graph with num_vert vertices."""
    return SimpleGraph(num_vert)


def complete(num_vert: int) -> SimpleGraph:
    """Return a complete graph with num_vert vertices."""
    G = empty(num_vert)
    for i in range(num_vert):
        for j in range(i + 1, num_vert):
            G.add_edge(i, j)
    return G


def path(num_vert: int) -> SimpleGraph:
    """Return a path graph with num_vert vertices."""
    G = empty(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, i + 1)
    return G


def cycle(num_vert: int) -> SimpleGraph:
    """Return a cycle graph with num_vert vertices."""
    G = path(num_vert)
    G.add_edge(0, num_vert - 1)
    return G


def wheel(num_vert: int) -> SimpleGraph:
    """Return a wheel graph with num_vert vertices."""
    G = cycle(num_vert - 1)
    G.set_num_verts(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, num_vert - 1)
    return G


def star(num_vert: int) -> SimpleGraph:
    """Return a star graph with num_vert vertices."""
    G = empty(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, num_vert - 1)
    return G


### fixed number of vertices ##################################################


def house() -> SimpleGraph:
    """Return a house graph."""
    G = cycle(num_vert=5)
    G.add_edge(1, 4)
    return G


def petersen() -> SimpleGraph:
    """Return a Petersen graph."""
    G = empty(num_vert=10)
    for i in range(5):
        G.add_edge(i, (i + 1) % 5)
        G.add_edge(i + 5, (i + 2) % 5 + 5)
        G.add_edge(i, i + 5)
    return G


def triforce() -> SimpleGraph:
    """Return a triforce graph."""
    G = cycle(num_vert=6)
    G.add_edge(0, 2)
    G.add_edge(2, 4)
    G.add_edge(4, 0)
    return G
