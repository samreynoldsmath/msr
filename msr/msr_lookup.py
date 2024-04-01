"""
Module for looking up MSR bounds for graphs. The bounds are saved in JSON files
in the soln/ directory. The files are named by the minimum hash of the
isomorphism equivalence class of the graph.
"""

import json
import os
from itertools import permutations
from logging import Logger

from .graph.graph import SimpleGraph


def isomorphism_equivalence_class(G: SimpleGraph) -> set[int]:
    """
    Returns the isomorphism equivalence class of a graph.
    """
    hashes: set[int] = set()
    for perm in permutations(range(G.num_verts)):
        G_perm = G.permute_verts(list(perm))
        hashes.add(hash(G_perm))
    return hashes


def isomorphism_equivalence_class_representative(G: SimpleGraph) -> int:
    """
    Returns the representative of the isomorphism equivalence class of a graph.
    """
    n = G.num_verts
    min_hash: int = 2 ** (n * (n - 1) // 2) - 1
    for perm in permutations(range(G.num_verts)):
        G_perm = G.permute_verts(list(perm))
        min_hash = min(min_hash, hash(G_perm))
    return min_hash


def soln_directory(num_verts: int, num_edges) -> str:
    """
    Returns the directory where solutions are saved. To reduce the number of
    files in a directory, we save solutions in subdirectories based on the
    number of vertices and edges.
    """
    return os.path.dirname(__file__) + f"/soln/n{num_verts}/e{num_edges}/"


def bounds_filename(G: SimpleGraph) -> str:
    """
    Returns the filename where the MSR bounds for a graph are saved.
    """
    directory = soln_directory(G.num_verts, G.num_edges())
    h = isomorphism_equivalence_class_representative(G)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.abspath(directory + str(h) + ".json")


def save_msr_bounds(
    G: SimpleGraph, d_lo: int, d_hi: int, logger: Logger
) -> None:
    """
    Saves the MSR bounds for a graph to a file.
    """
    if d_lo > d_hi:
        logger.warning("d_lo > d_hi, not saving bounds")
        return
    logger.info(f"saving bounds {d_lo}, {d_hi} for {G.hash_id()}")
    filename = bounds_filename(G)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"d_lo": int(d_lo), "d_hi": int(d_hi)}, f)


def load_msr_bounds(G: SimpleGraph, logger: Logger) -> tuple[int, int]:
    """
    Loads the MSR bounds for a graph from a file, if it exists.
    """
    filename = bounds_filename(G)
    if not os.path.exists(filename):
        logger.info("no saved bounds found, returning 0, n")
        return 0, G.num_verts
    logger.info(f"loading bounds from {filename}")
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        d_lo = data["d_lo"]
        d_hi = data["d_hi"]
    return d_lo, d_hi
