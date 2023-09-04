import multiprocessing

from tqdm import tqdm

from .graph.file_io import files_in_directory, load_graph
from .graph.graph import graph
from .msr_bounds import msr_bounds


def msr_batch_from_directory(
    path: str, quiet: bool = False
) -> list[tuple[int, int, int]]:
    """
    Computes the MSR bounds for graphs in a directory with multiprocessing.
    """
    filenames = files_in_directory(path)
    if quiet:
        return _msr_batch_from_directory_quiet(filenames)
    else:
        return _msr_batch_from_directory_loud(filenames)


def _msr_batch_from_directory_loud(
    filenames: list[str],
) -> list[tuple[int, int, int]]:
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
) -> list[tuple[int, int, int]]:
    """Does not use tqdm to show progress."""
    with multiprocessing.Pool() as pool:
        return list(
            pool.imap_unordered(_msr_bounds_with_id_from_file, filenames)
        )


def _msr_bounds_with_id_from_file(filename: str) -> tuple[int, int, int]:
    """Helper function for msr_batch_from_directory."""
    G = load_graph(filename)
    return _msr_bounds_with_id(G)


def msr_batch(
    graphs: list[graph], quiet: bool = False
) -> list[tuple[int, int, int]]:
    """Computes the MSR bounds for a batch of graphs with multiprocessing."""
    if quiet:
        return _msr_batch_quiet(graphs)
    else:
        return _msr_batch_loud(graphs)


def _msr_batch_loud(graphs: list[graph]) -> list[tuple[int, int, int]]:
    """Uses tqdm to show progress."""
    N = len(graphs)
    with multiprocessing.Pool() as pool:
        return list(
            tqdm(pool.imap_unordered(_msr_bounds_with_id, graphs), total=N)
        )


def _msr_batch_quiet(graphs: list[graph]) -> list[tuple[int, int, int]]:
    """Does not use tqdm to show progress."""
    with multiprocessing.Pool() as pool:
        return list(pool.imap_unordered(_msr_bounds_with_id, graphs))


def _msr_bounds_with_id(G: graph) -> tuple[int, int, int]:
    """Helper function for msr_batch."""
    d_lo, d_hi = msr_bounds(G)
    return d_lo, d_hi, hash(G)
