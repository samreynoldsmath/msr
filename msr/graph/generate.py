"""
Module for generating all graphs on n vertices up to isomorphism.
"""

from itertools import permutations
from math import factorial
from multiprocessing import Pool
from typing import Optional

import tqdm

from .file_io import SAVED_GRAPH_DIR, save_graphs
from .graph import SimpleGraph


def generate_and_save_all_graphs_on_n_vertices(
    n: int, path: Optional[str] = None
) -> None:
    """Generates and saves all graphs on n vertices"""
    if path is None:
        path = SAVED_GRAPH_DIR + f"n{n}"
    graphs = generate_all_graphs_on_n_vertices(n)
    save_graphs(graphs, path)


def generate_all_graphs_on_n_vertices(n: int) -> list[SimpleGraph]:
    """
    Generates all graphs on n vertices by constructing all graphs isomorphic to
    G and testing if any of these graphs have been seen.

    See doc/MISC.md for a link to the StackOverflow post that inspired this.
    """

    num_candidates = 2 ** (n * (n - 1) // 2)

    found_hashes: set[int] = set()
    encountered: list[bool] = [False for _ in range(num_candidates)]

    # hash each graph as an integer k, such that k written in binary represents
    # the edges of the graph, with zero being a non-edge, and one being an edge.
    for k in tqdm.tqdm(range(num_candidates)):
        if encountered[k]:
            continue
        G = SimpleGraph(num_verts=n)
        G.build_from_hash(k)
        if G.num_edges() < n - 1:
            continue
        is_not_new, seen = is_not_new_graph(G, found_hashes)
        for t in seen:
            encountered[t] = True
        if not is_not_new:
            found_hashes.add(k)

    # reconstruct graphs from hashes
    graphs = []
    for k in found_hashes:
        G = SimpleGraph(num_verts=n)
        G.build_from_hash(k)
        if G.is_connected():
            graphs.append(G)

    # report number of graphs
    print(f"Number of connected graphs on {n} vertices: {len(graphs)}")

    predicted = num_graphs_on_n_verts(n)
    if len(graphs) != predicted:
        print(f"WARNING: number of graphs on {n} vertices is not {predicted}")

    return graphs


def is_not_new_graph(
    G: SimpleGraph, found_hashes: set[int]
) -> tuple[bool, set[int]]:
    """Determines if a graph G is isomorphic to a graph in found_hashes."""
    seen = set()
    perms = permutations(range(G.num_verts))
    num_perms = factorial(G.num_verts)
    with Pool() as pool:
        res = pool.starmap(
            is_not_new_graph_worker,
            [(G, perm, found_hashes) for perm in perms],
            chunksize=max(10, num_perms // 128),
        )
    is_not_new = any(H_is_not_new for _, H_is_not_new in res)
    seen = set(k for k, _ in res)
    return is_not_new, seen


def is_not_new_graph_worker(
    G: SimpleGraph, perm: list[int], found_hashes: set[int]
) -> tuple[int, bool]:
    """
    Permute the vertices of G and check if the resulting graph is in
    found_hashes.
    """
    H = G.permute_verts(perm)
    return hash(H), hash(H) in found_hashes


def num_graphs_on_n_verts(n: int) -> int:
    """
    OEIS A001349: Number of connected graphs with n nodes.
    """
    a = [
        1,
        1,
        1,
        2,
        6,
        21,
        112,
        853,
        11117,
        261080,
        11716571,
        1006700565,
        164059830476,
        50335907869219,
        29003487462848061,
        31397381142761241960,
        63969560113225176176277,
        245871831682084026519528568,
        1787331725248899088890200576580,
        24636021429399867655322650759681644,
    ]
    a_len = len(a)
    if n > a_len - 1:
        print("WARNING: number of graphs on n vertices not found in OEIS table")
    return a[n]
