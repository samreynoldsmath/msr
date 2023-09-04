import json
import logging
import os
from itertools import permutations

from .graph.graph import graph


def isomorphism_equivalence_class(G: graph) -> set[int]:
    """
    Returns the isomorphism equivalence class of a graph.
    """
    hashes: set[int] = set()
    for perm in permutations(range(G.num_verts)):
        G_perm = G.permute_verts(list(perm))
        hashes.add(hash(G_perm))
    return hashes


def isomorphism_equivalence_class_representative(G: graph) -> int:
    """
    Returns the representative of the isomorphism equivalence class of a graph.
    """
    n = G.num_verts
    min_hash: int = 2 ** (n * (n - 1) // 2) - 1
    for perm in permutations(range(G.num_verts)):
        G_perm = G.permute_verts(list(perm))
        min_hash = min(min_hash, hash(G_perm))
    return min_hash


def soln_directory(n: int) -> str:
    """
    Returns the directory where solutions are saved.
    """
    return os.path.dirname(__file__) + f"/soln/n{n}/"


def bounds_filename(G: graph) -> str:
    """
    Returns the filename where the MSR bounds for a graph are saved.
    """
    directory = soln_directory(G.num_verts)
    id = isomorphism_equivalence_class_representative(G)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + str(id) + ".json"


def save_msr_bounds(G: graph, d_lo: int, d_hi: int) -> None:
    """
    Saves the MSR bounds for a graph to a file.
    """
    if d_lo > d_hi:
        logging.warning("d_lo > d_hi, not saving bounds")
        return
    logging.info(f"saving bounds {d_lo}, {d_hi} for graph {hash(G)}")
    filename = bounds_filename(G)
    with open(filename, "w") as f:
        json.dump({"d_lo": int(d_lo), "d_hi": int(d_hi)}, f)


def load_msr_bounds(G: graph) -> tuple[int, int]:
    """
    Loads the MSR bounds for a graph from a file, if it exists.
    """
    filename = bounds_filename(G)
    if not os.path.exists(filename):
        return 0, G.num_verts
    with open(filename, "r") as f:
        data = json.load(f)
        d_lo = data["d_lo"]
        d_hi = data["d_hi"]
    return d_lo, d_hi