from ..simple_undirected_graph import simple_undirected_graph

### variable number of vertices ###############################################


def empty(num_vert: int) -> simple_undirected_graph:
    return simple_undirected_graph(num_vert)


def complete(num_vert: int) -> simple_undirected_graph:
    G = empty(num_vert)
    for i in range(num_vert):
        for j in range(i + 1, num_vert):
            G.add_edge(i, j)
    return G


def path(num_vert: int) -> simple_undirected_graph:
    G = empty(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, i + 1)
    return G


def cycle(num_vert: int) -> simple_undirected_graph:
    G = path(num_vert)
    G.add_edge(0, num_vert - 1)
    return G


def wheel(num_vert: int) -> simple_undirected_graph:
    G = cycle(num_vert - 1)
    G.set_num_verts(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, num_vert - 1)
    return G


def star(num_vert: int) -> simple_undirected_graph:
    G = empty(num_vert)
    for i in range(num_vert - 1):
        G.add_edge(i, num_vert - 1)
    return G


### fixed number of vertices ##################################################


def house() -> simple_undirected_graph:
    G = cycle(num_vert=5)
    G.add_edge(1, 4)
    return G


def petersen() -> simple_undirected_graph:
    G = empty(num_vert=10)
    for i in range(5):
        G.add_edge(i, (i + 1) % 5)
        G.add_edge(i + 5, (i + 2) % 5 + 5)
        G.add_edge(i, i + 5)
    return G


def triforce() -> simple_undirected_graph:
    G = cycle(num_vert=6)
    G.add_edge(0, 2)
    G.add_edge(2, 4)
    G.add_edge(4, 0)
    return G
