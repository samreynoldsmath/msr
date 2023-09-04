import os
from itertools import permutations
from math import ceil, factorial, log10
from multiprocessing import Pool

import tqdm

from .file_io import save_graph
from .graph import graph


def generate_and_save_all_graphs_on_n_vertices(n: int, path: str) -> None:
    """Generates and saves all graphs on n vertices"""
    nx_graphs = generate_all_graphs_on_n_vertices(n)
    save_graphs(nx_graphs, path)


def generate_all_graphs_on_n_vertices(n: int) -> set[graph]:
    """
    Generates all graphs on n vertices by constructing all graphs isomorphic to
    G and testing if any of these graphs have been seen.

    Idea from https://stackoverflow.com/questions/71597789/generate-all-digraphs-of-a-given-size-up-to-isomorphism
    """

    n_choose_2 = n * (n - 1) // 2
    num_candidates = 2**n_choose_2

    found_hashes: set[int] = set()
    encountered: list[bool] = list([False for _ in range(num_candidates)])

    # hash each graph as an integer k, such that k written in binary represents
    # the edges of the graph, with zero being a non-edge, and one being an edge.
    for k in tqdm.tqdm(range(num_candidates)):
        if encountered[k]:
            continue
        G = construct_graph_from_hash(k, n, n_choose_2)
        if G.num_edges() < n - 1:
            continue
        is_not_new, seen = is_not_new_graph(G, found_hashes)
        for t in seen:
            encountered[t] = True
        if not is_not_new:
            found_hashes.add(hash(G))

    # reconstruct graphs from hashes
    graphs = set()
    for k in found_hashes:
        # G = construct_graph_from_hash(k, n, n_choose_2)
        G = graph(num_verts=n)
        G.build_from_hash(k)
        if G.is_connected():
            graphs.add(G)

    # report number of graphs
    print(f"Number of connected graphs on {n} vertices: {len(graphs)}")

    predicted = num_graphs_on_n_verts(n)
    if len(graphs) != predicted:
        print(f"WARNING: number of graphs on {n} vertices is not {predicted}")

    return graphs


def is_not_new_graph(G: graph, found_hashes: set[int]) -> tuple[bool, set[int]]:
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
    is_not_new = any([H_is_not_new for _, H_is_not_new in res])
    seen = set([k for k, _ in res])
    return is_not_new, seen


def is_not_new_graph_worker(
    G: graph, perm: list[int], found_hashes: set[int]
) -> tuple[int, bool]:
    """
    Permute the vertices of G and check if the resulting graph is in
    found_hashes.
    """
    H = G.permute_verts(perm)
    return hash(H), hash(H) in found_hashes


def construct_graph_from_hash(k: int, n: int, n_choose_2: int) -> graph:
    """Constructs a graph on n vertices from an edge hash k."""

    # convert k to binary, and pad with zeros to the left
    binary = bin(k)[2:].zfill(n_choose_2)

    # convert binary to a list of edges in a graph G
    G = graph(num_verts=n)
    for i in range(n - 1):
        for j in range(i + 1, n):
            ij = j - 1 + (i * (2 * n - 3 - i)) // 2
            if binary[ij] == "1":
                G.add_edge(i, j)

    return G


def save_graphs(graphs: set[graph], path: str) -> None:
    """Saves graphs to disk."""

    # create directory if none exists
    if not os.path.exists(path):
        os.makedirs(path)

    # save graphs
    print(f"Saving graphs to {path}")
    for G in tqdm.tqdm(graphs):
        filename = f"{path}/k{hash(G)}.json"
        save_graph(G, filename)


def num_graphs_on_n_verts(n: int) -> int:
    """
    OEIS A001349: Number of connected graphs with n nodes.
    """
    if n > 20:
        raise ValueError("n must be <= 20")
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
    return a[n]
