"""
Module for reducing the number of vertices in a graph with predictable changes
to the dimension of the graph.
"""

from logging import Logger

from .graph.graph import SimpleGraph


class ReductionError(Exception):
    """Error raised when reduction fails."""


def reduce(G: SimpleGraph, logger: Logger) -> tuple[SimpleGraph, int, int]:
    """
    Attempts to reduce the number of vertices in the graph by
    * removing pendants
    * contracting subdivisions
    * removing redundant vertices (vertices adjacent to every other vertex)
    * removing duplicate pairs (adjacent vertices with the same neighbors)
    The reduction loop halts when either no	updates are made or the graph
    becomes disconnected.

    Returns
    * the reduced graph
    * the change in dimension
    * and the number of	vertices removed
    """

    if not G.is_connected():
        msg = "reduction loop assumes G is connected"
        logger.error(msg)
        raise ReductionError(msg)

    logger.info("performing reduction")

    updated = True  # track whether any updates were made in the last iteration
    d_diff = 0  # track change in dimension
    deletions = 0  # track number of deletions

    # main reduction loop: continue until no updates are made
    while updated:
        # check if time to exit
        if check_stopping_criteria(G, logger):
            reduction_report(deletions, d_diff, updated, logger)
            return G, d_diff, deletions

        # remove pendants
        # NOTE: this is a cheap operation
        # NOTE: deleting a pendant reduces dimension by 1
        G, updated, local_deletions = remove_pendants(G, logger)
        deletions += local_deletions
        d_diff += local_deletions

        # check if time to exit
        if check_stopping_criteria(G, logger):
            reduction_report(deletions, d_diff, updated, logger)
            return G, d_diff, deletions

        # remove subdivisions
        # NOTE: contracting an edge reduces dimension by 1
        if not updated:
            G, updated, local_deletions = remove_subdivisions(G, logger)
            deletions += local_deletions
            d_diff += local_deletions

        # check if time to exit
        if check_stopping_criteria(G, logger):
            reduction_report(deletions, d_diff, updated, logger)
            return G, d_diff, deletions

        # remove redundant vertices
        # NOTE: dimension does not change
        # NOTE: requires connectivity check
        if not updated:
            G, updated, local_deletions = remove_redundant_verts(G, logger)
            deletions += local_deletions

        # check if time to exit
        if check_stopping_criteria(G, logger):
            reduction_report(deletions, d_diff, updated, logger)
            return G, d_diff, deletions

        # remove duplicate pairs
        # NOTE: dimension does not change
        # NOTE: quadratic cost in number of vertices
        if not updated:
            G, updated, local_deletions = remove_duplicate_pairs(G, logger)
            deletions += local_deletions

    # report on the reduction and return
    reduction_report(deletions, d_diff, updated, logger)
    return G, d_diff, deletions


def reduction_report(
    deletions: int, d_diff: int, updated: bool, logger: Logger
) -> None:
    """
    Logs the results of the reduction.
    """
    if not updated:
        logger.debug("reduction stagnated")
    v = "vertices" if deletions != 1 else "vertex"
    logger.info(
        f"reduction removed {deletions} {v}"
        + f", reduced dimension by {d_diff}"
    )


def check_stopping_criteria(G: SimpleGraph, logger: Logger) -> bool:
    """
    reduction completes if G is
    * has less than 3 vertices
    * is disconnected
    * is complete
    * is a tree
    * is a cycle
    """
    stop = not G.is_connected()
    if stop:
        logger.debug("reduction stopped because graph is disconnected")
    if not stop:
        stop = G.num_verts < 3 or G.is_complete() or G.is_a_tree()
    if not stop:
        # more expensive check
        stop = G.is_a_cycle()
    if stop:
        logger.debug("reduction succeeded")
    return stop


def remove_pendants(
    G: SimpleGraph, logger: Logger
) -> tuple[SimpleGraph, bool, int]:
    """
    Removes all pendant vertices.
    """
    logger.debug("removing pendants")
    updated = False
    local_deletions = 0
    i = G.num_verts
    while i > 0 and G.num_verts > 2:
        i -= 1
        if G.vert_is_pendant(i) and G.num_verts > 2:
            G.remove_vert(i, still_connected=True)
            updated = True
            local_deletions += 1
    if local_deletions > 0:
        v = "pendants" if local_deletions != 1 else "pendant"
        logger.debug(f"removed {local_deletions} {v}")
    return G, updated, local_deletions


def remove_subdivisions(
    G: SimpleGraph, logger: Logger
) -> tuple[SimpleGraph, bool, int]:
    """
    Removes all subdivisions.
    """
    logger.debug("removing subdivisions")
    updated = False
    local_deletions = 0
    i = G.num_verts
    while i > 0 and G.num_verts > 2:
        i -= 1
        if G.vert_is_subdivided(i) and G.num_verts > 2:
            j, k = G.vert_neighbors(i)
            G.add_edge(j, k)  # important to add edge before removing vert
            G.remove_vert(i, still_connected=True)
            updated = True
            local_deletions += 1
    if local_deletions > 0:
        plural = "s" if local_deletions != 1 else ""
        logger.debug(f"removed {local_deletions} subdivision {plural}")
    return G, updated, local_deletions


def remove_redundant_verts(
    G: SimpleGraph, logger: Logger
) -> tuple[SimpleGraph, bool, int]:
    """
    Removes all vertices adjacent to every other vertex.

    If the graph becomes disconnected, the reduction is halted.
    """
    logger.debug("removing redundant vertices")
    updated = False
    local_deletions = 0
    i = G.num_verts
    while i > 0 and G.num_verts > 2:
        i -= 1
        if G.vert_is_redundant(i) and G.num_verts > 2:
            G.remove_vert(i, still_connected=None)
            updated = True
            local_deletions += 1
            # if G has become disconnected, stop reducing
            if not G.is_connected():
                v = "vertices" if local_deletions != 1 else "vertex"
                logger.debug(f"removed {local_deletions} redundant {v}")
                return G, updated, local_deletions
    if local_deletions > 0:
        v = "vertices" if local_deletions != 1 else "vertex"
        logger.debug(f"removed {local_deletions} redundant {v}")
    return G, updated, local_deletions


def remove_duplicate_pairs(
    G: SimpleGraph, logger: Logger
) -> tuple[SimpleGraph, bool, int]:
    """
    Removes all pairs of adjacent vertices with the same neighbors.
    """
    logger.debug("removing duplicate pairs")
    updated = False
    deletions = 0
    i = G.num_verts
    # triangular loop over vertices in reverse order
    while i > 0 and G.num_verts > 2:
        i -= 1
        j = i
        while j > 0 and G.num_verts > 2:
            j -= 1
            if G.verts_are_duplicate_pair(i, j):
                G.remove_vert(j, still_connected=True)
                updated = True
                deletions += 1
    if deletions > 0:
        v = "vertices" if deletions != 1 else "vertex"
        logger.debug(f"removed {deletions} duplicate {v}")
    return G, updated, deletions
