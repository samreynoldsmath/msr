"""
Module for specific graphs, such as the complete graph, path graph, etc.
"""

from .graph import graph

### variable number of vertices ###############################################


def empty(num_vert: int) -> graph:
    return graph(num_vert)


def complete(num_vert: int) -> graph:
    G = empty(num_vert)
    for i in range(num_vert):
        for j in range(i + 1, num_vert):
            G.add_edge(i, j)
    return G


def path(num_vert: int) -> graph:
    G = empty(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, i + 1)
    return G


def cycle(num_vert: int) -> graph:
    G = path(num_vert)
    G.add_edge(0, num_vert - 1)
    return G


def wheel(num_vert: int) -> graph:
    G = cycle(num_vert - 1)
    G.set_num_verts(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, num_vert - 1)
    return G


def star(num_vert: int) -> graph:
    G = empty(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, num_vert - 1)
    return G


### fixed number of vertices ##################################################


def house() -> graph:
    G = cycle(num_vert=5)
    G.add_edge(1, 4)
    return G


def petersen() -> graph:
    G = empty(num_vert=10)
    for i in range(5):
        G.add_edge(i, (i + 1) % 5)
        G.add_edge(i + 5, (i + 2) % 5 + 5)
        G.add_edge(i, i + 5)
    return G


def triforce() -> graph:
    G = cycle(num_vert=6)
    G.add_edge(0, 2)
    G.add_edge(2, 4)
    G.add_edge(4, 0)
    return G
