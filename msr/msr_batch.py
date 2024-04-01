"""
Functions for computing the MSR bounds for a batch of graphs with
multiprocessing.
"""

import multiprocessing

from tqdm import tqdm

from .graph.file_io import SAVED_GRAPH_DIR, files_in_directory, load_graph
from .graph.graph import SimpleGraph
from .msr_bounds import msr_bounds


def msr_batch_from_directory(
    path: str = SAVED_GRAPH_DIR,
    quiet: bool = False,
    num_verts: int = 0,
) -> list[tuple[int, int, str]]:
    """
    Computes the MSR bounds for graphs in a directory with multiprocessing.
    """
    filenames = files_in_directory(path, num_verts)
    if quiet:
        return _msr_batch_from_directory_quiet(filenames)
    return _msr_batch_from_directory_loud(filenames)


def _msr_batch_from_directory_loud(
    filenames: list[str],
) -> list[tuple[int, int, str]]:
    """Uses tqdm to show progress."""
    with multiprocessing.Pool() as pool:
        return list(
            tqdm(
                pool.imap_unordered(_msr_bounds_with_id_from_file, filenames),
                total=len(filenames),
            )
        )


def _msr_batch_from_directory_quiet(
    filenames: list[str],
) -> list[tuple[int, int, str]]:
    """Does not use tqdm to show progress."""
    with multiprocessing.Pool() as pool:
        return list(
            pool.imap_unordered(_msr_bounds_with_id_from_file, filenames)
        )


def _msr_bounds_with_id_from_file(filename: str) -> tuple[int, int, str]:
    """Helper function for msr_batch_from_directory."""
    G = load_graph(filename)
    return _msr_bounds_with_id(G)


def msr_batch(
    graphs: list[SimpleGraph], quiet: bool = False
) -> list[tuple[int, int, str]]:
    """Computes the MSR bounds for a batch of graphs with multiprocessing."""
    if quiet:
        return _msr_batch_quiet(graphs)
    return _msr_batch_loud(graphs)


def _msr_batch_loud(graphs: list[SimpleGraph]) -> list[tuple[int, int, str]]:
    """Uses tqdm to show progress."""
    num_graphs = len(graphs)
    with multiprocessing.Pool() as pool:
        return list(
            tqdm(
                pool.imap_unordered(_msr_bounds_with_id, graphs),
                total=num_graphs,
            )
        )


def _msr_batch_quiet(graphs: list[SimpleGraph]) -> list[tuple[int, int, str]]:
    """Does not use tqdm to show progress."""
    with multiprocessing.Pool() as pool:
        return list(pool.imap_unordered(_msr_bounds_with_id, graphs))


def _msr_bounds_with_id(G: SimpleGraph) -> tuple[int, int, str]:
    """Helper function for msr_batch."""
    d_lo, d_hi = msr_bounds(G)
    return d_lo, d_hi, G.hash_id()
