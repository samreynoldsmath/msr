"""
Module drawing graphs using matplotlib.
"""

import os
from multiprocessing import Pool

import matplotlib.pyplot as plt
from tqdm import tqdm

from .embed import embed
from .graph import SimpleGraph


def draw_graphs(
    graphs: list[SimpleGraph],
    embedding: str = "circular",
    labels=False,
    directory: str = "",
) -> None:
    """Uses multiprocessing to draw a list of graphs."""

    m = len(graphs)

    if len(directory) == 0:
        filenames = ["" for _ in range(len(graphs))]
    else:
        filenames = [f"{directory}/{hash(G)}.png" for G in graphs]

    with Pool() as pool:
        list(
            tqdm(
                pool.imap_unordered(
                    _draw_graph,
                    zip(graphs, [embedding] * m, [labels] * m, filenames),
                ),
                total=len(graphs),
            )
        )


def _draw_graph(args: tuple[SimpleGraph, str, bool, str]) -> None:
    """Draws a graph."""
    G, embedding, labels, filename = args
    draw_graph(G, embedding, labels, filename)


def draw_graph(
    G: SimpleGraph,
    embedding: str = "circular",
    labels=False,
    filename: str = "",
    title: str = "",
) -> None:
    """Draw a planar embedding of the vector graph G."""

    n = G.num_verts

    # embed the graph
    x, y, diam = embed(G, embedding)

    # draw the vertices
    for i in range(n):
        plt.plot(x[i], y[i], "ko")
        if labels:
            plt.text(x[i] * (1 + 0.05 * diam), y[i] * (1 + 0.05 * diam), i)

    # draw the edges
    for e in G.edges:
        i, j = e.endpoints
        plt.plot([x[i], x[j]], [y[i], y[j]], "k-")

    # draw the graph
    plt.axis("off")
    plt.axis("equal")
    if len(title) > 0:
        plt.title(title)
    if len(filename) > 0:
        # create directory if none exists
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        plt.savefig(filename)
        plt.clf()
    else:
        plt.show()
