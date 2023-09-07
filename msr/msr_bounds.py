import logging

from numpy import zeros

from .graph import graph
from .log_config import LOG_PATH, configure_logging
from .msr_lookup import load_msr_bounds, save_msr_bounds
from .msr_sdp import (
    msr_sdp_signed_cycle_search,
    msr_sdp_signed_exhaustive,
    msr_sdp_signed_simple,
    msr_sdp_upper_bound,
)
from .reduce import reduce
from .strategy_config import STRATEGY, check_strategy, msr_strategy


def msr_bounds(
    G: graph,
    log_path: str = LOG_PATH,
    log_level: int = logging.ERROR,
    log_print: bool = False,
    load_flag: bool = True,
    save_flag: bool = True,
) -> tuple[int, int]:
    """
    Returns bounds on msr(G) using a recursive algorithm.
    """

    # configure logging
    if log_print:
        filename = ""
    else:
        filename = G.id() + ".log"
    logger = configure_logging(
        log_path=log_path,
        filename=filename,
        level=log_level,
    )

    # log input
    logger.info("computing bounds on msr(G) with G = " + str(G))

    # log strategy
    msg = "Using strategy: "
    for k, strategy in enumerate(STRATEGY):
        msg += "\n%2d.\t" % k + strategy.value
    logger.info(msg)

    # check strategy
    check_strategy(logger)

    # check that G is nontrivial
    if G.num_verts < 1:
        msg = "G must have at least one vertex"
        logger.error(msg)
        raise ValueError(msg)

    # avoid corrupting G
    G = G.__copy__()

    # find number of isolated vertices
    num_isolated_verts = G.num_isolated_verts()

    # max recursion depth
    max_depth = 10 * G.num_verts

    # find bounds on dim(G)
    d_lo, d_hi = dim_bounds(
        G,
        max_depth,
        depth=0,
        logger=logger,
        load_flag=load_flag,
        save_flag=save_flag,
    )

    # mod out isolated vertices
    d_lo -= num_isolated_verts
    d_hi -= num_isolated_verts

    # log output
    logger.info(f"exited with result {(d_lo, d_hi)}")

    # return bounds on msr(G)
    return d_lo, d_hi


def dim_bounds(
    G: graph,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
    load_flag=True,
    save_flag=True,
) -> tuple[int, int]:
    """
    Returns bounds dim(G), where G is a simple undirected graph, and
    dim(G) = msr(G) + the number of isolated vertices. Equivalently, dim(G) is
    the minimum dimension of a faithful orthogonal representation of G such
    the zero vector is not assigned to any vertex.
    """

    # log recursion depth
    logger.info(f"DEPTH({depth}), num_verts = {G.num_verts}")
    if depth > max_depth:
        msg = "recursion depth limit reached, returning loose bounds"
        logger.warning(msg)
        return 0, G.num_verts

    # avoid corrupting G
    G = G.__copy__()

    # find bounds on dim(G) using simple methods
    d_lo, d_hi, exit_flag = dim_bounds_simple(G, max_depth, depth, logger)
    if exit_flag:
        logger.info(f"EXIT({depth}): simple methods triggered exit")
        return d_lo, d_hi
    if check_bounds(d_lo, d_hi, "simple methods", logger, depth):
        return d_lo, d_hi

    # reduce the graph and obtain bounds on the reduced graph
    G, d_lo, d_hi, exit_flag = reduce_and_bound_reduction(
        G, max_depth, depth, logger
    )
    if exit_flag:
        logger.info(f"EXIT({depth}): reduction triggered exit")
        return d_lo, d_hi
    if check_bounds(d_lo, d_hi, "reducing graph", logger, depth):
        return d_lo, d_hi

    # attempt to load bounds from file
    if load_flag:
        d_lo_file, d_hi_file = load_msr_bounds(G, logger)
        d_lo = max(d_lo, d_lo_file)
        d_hi = min(d_hi, d_hi_file)
        if check_bounds(d_lo, d_hi, "loading bounds from file", logger, depth):
            return d_lo, d_hi

    # advanced strategies
    for strategy in STRATEGY:
        d_lo_new, d_hi_new = run_strategy(
            strategy.value, G, d_lo, d_hi, max_depth, depth, logger
        )
        d_lo = max(d_lo, d_lo_new)
        d_hi = min(d_hi, d_hi_new)
        if check_bounds(d_lo, d_hi, strategy.value, logger, depth):
            if save_flag and d_lo >= d_lo_file and d_hi <= d_hi_file:
                save_msr_bounds(G, d_lo, d_hi, logger)
            return d_lo, d_hi

    # exit without tight bounds
    logger.info(
        f"EXIT({depth}): dim_bounds() exited without obtaining tight bounds"
    )
    if save_flag and d_lo >= d_lo_file and d_hi <= d_hi_file:
        save_msr_bounds(G, d_lo, d_hi, logger)
    return d_lo, d_hi


def dim_bounds_simple(
    G: graph,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int, bool]:
    """
    Gets bounds on dim(G) by counting edges, degrees, and checking connectivity.
    Returns the bounds and a flag that indicates if the program is ready to
    exit.
    """

    # get number of vertices
    n = G.num_verts

    # special cases of empty and complete graphs
    if G.is_empty():
        logger.info(f"EXIT({depth}): G is empty on {n} vertices")
        return n, n, True
    if G.is_complete():
        logger.info(f"EXIT({depth}): G is complete on {n} vertices")
        return 1, 1, True

    # find bounds by summing bounds on components
    d_lo, d_hi = get_bounds_on_components(G, max_depth, depth, logger)

    # if G is disconnected, this is the best estimate
    if not G.is_connected():
        return d_lo, d_hi, True

    # special cases of trees and cycles
    if G.is_a_tree():
        logger.info(f"EXIT({depth}): G is a tree on {n} vertices")
        return n - 1, n - 1, True
    if G.is_a_cycle():
        logger.info(f"EXIT({depth}): G is a cycle on {n} vertices")
        return n - 2, n - 2, True

    # simple strategies failed
    return d_lo, d_hi, False


def run_strategy(
    strategy_name: str,
    G: graph,
    d_lo: int,
    d_hi: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int]:
    """Runs a strategy for computing bounds on dim(G)."""
    if strategy_name == msr_strategy.BCD_LOWER_EXHAUSTIVE.value:
        return bcd_bounds_exhaustive(
            G,
            d_lo,
            d_hi,
            max_depth,
            depth,
            logger,
        )
    if strategy_name == msr_strategy.BCD_LOWER.value:
        return bcd_bounds(
            G,
            d_lo,
            d_hi,
            max_depth,
            depth,
            logger,
        )
    if strategy_name == msr_strategy.BCD_UPPER.value:
        d_hi = bcd_upper_bound(
            G,
            d_lo,
            max_depth,
            depth,
            logger,
        )
        return d_lo, d_hi
    if strategy_name == msr_strategy.CLIQUE_UPPER.value:
        d_hi = upper_bound_from_cliques(
            G,
            d_lo,
            max_depth,
            depth,
            logger,
        )
        return d_lo, d_hi
    if strategy_name == msr_strategy.CUT_VERT.value:
        return bounds_from_cut_vert_induced_cover(
            G,
            max_depth,
            depth,
            logger,
        )
    if strategy_name == msr_strategy.INDUCED_SUBGRAPH.value:
        d_lo = lower_bound_induced_subgraphs(
            G,
            d_lo,
            d_hi,
            max_depth,
            depth,
            logger,
        )
        return d_lo, d_hi
    if strategy_name == msr_strategy.EDGE_ADDITION.value:
        return bounds_from_edge_addition(
            G,
            d_lo,
            d_hi,
            max_depth,
            depth,
            logger,
        )
    if strategy_name == msr_strategy.EDGE_REMOVAL.value:
        return bounds_from_edge_removal(
            G,
            d_lo,
            d_hi,
            max_depth,
            depth,
            logger,
        )
    if strategy_name == msr_strategy.SDP_UPPER.value:
        d_hi = msr_sdp_upper_bound(
            G,
            logger,
        )
        return d_lo, d_hi
    if strategy_name == msr_strategy.SDP_SIGNED_EXHAUSTIVE.value:
        d_hi = msr_sdp_signed_exhaustive(
            G,
            d_lo,
            logger,
        )
        return d_lo, d_hi
    if strategy_name == msr_strategy.SDP_SIGNED_SIMPLE.value:
        d_hi = msr_sdp_signed_simple(
            G,
            d_lo,
            logger,
        )
        return d_lo, d_hi
    if strategy_name == msr_strategy.SDP_SIGNED_CYCLE.value:
        d_hi = msr_sdp_signed_cycle_search(
            G,
            d_lo,
            logger,
        )
        return d_lo, d_hi
    msg = "unknown strategy: " + strategy_name
    logger.error(msg)
    raise ValueError(msg)


def check_bounds(
    d_lo: int,
    d_hi: int,
    action_name: str,
    logger: logging.Logger,
    depth: int,
) -> bool:
    """
    Checks that the bounds on dim(G) are tight.
    """
    exit_flag = d_lo >= d_hi
    if d_lo == d_hi:
        logger.info(f"EXIT({depth}): bounds match after " + action_name)
    if d_lo > d_hi:
        msg = (
            f"EXIT({depth}): lower bound exceeds upper bound after "
            + action_name
        )
        logger.warning(msg)
    return exit_flag


def get_bounds_on_components(
    G: graph,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int]:
    """
    Computes bounds on dim(G) by summing bounds on components of G.
    """

    # find components of G
    components = G.connected_components()

    # log if G is disconnected
    if G.is_connected():
        logger.info("G is connected")
    else:
        num_components = len(components)
        logger.info(f"G is disconnected with {num_components} components")

    # add bounds for each component when G is disconnected
    if not G.is_connected():
        d_lo = 0
        d_hi = 0
        for H in components:
            H_d_lo, H_d_hi = dim_bounds(H, max_depth, depth + 1, logger)
            d_lo += H_d_lo
            d_hi += H_d_hi
        return d_lo, d_hi
    else:
        return 1, G.num_verts - 1


def reduce_and_bound_reduction(
    G: graph,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[graph, int, int, bool]:
    """
    Performs the reduction G |-> H and returns H and bounds on dim(H).

    If the reduction is trivial (i.e. no vertices removed), we return the
    original graph and bound dim(G) with (2, n - 2).

    If the reduction is nontrivial, we get bounds on the reduced graph using
    simple methods. (This includes using advanced methods on the components of
    the reduced graph, if it is disconnected.) If this fails to get tight
    bounds, we will attempt advanced strategies after returning to dim_bounds().
    """

    # reduce the graph
    G, d_diff, deletions = reduce(G, logger)

    # get bounds on the reduced graph
    if deletions == 0:
        return G, 2, G.num_verts - 2, False
    elif deletions > 0:
        logger.info("checking bounds of reduced graph")
        d_lo, d_hi, exit_flag = dim_bounds_simple(
            G, max_depth, depth + 1, logger
        )
        d_lo += d_diff
        d_hi += d_diff
        return G, d_lo, d_hi, exit_flag
    else:
        msg = f"reduction failed: deletions = {deletions} < 0"
        logger.error(msg)
        raise ValueError(msg)


def lower_bound_induced_subgraphs(
    G: graph,
    d_lo: int,
    d_hi: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> int:
    """
    Returns the maximum lower bound of the dimension of any induced subgraph.
    """
    logger.info("checking induced subgraphs")
    d_lo = 0
    n = G.num_verts
    for i in range(n):
        logger.debug(f"induced subgraph {i}")
        H = G.__copy__()
        H.remove_vert(i)
        d_lo_H = dim_bounds(H, max_depth, depth + 1, logger)[0]
        d_lo = max(d_lo, d_lo_H)
        if d_lo >= d_hi:
            return d_lo
    return d_lo


def bounds_from_cut_vert_induced_cover(
    G: graph,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int]:
    """
    Checks if G has a cut vertex. If so, generate a proper induced cover
    {G_1, G_2} such that G_1 and G_2 intersect at exactly one vertex. Then it
    holds that dim(G) = dim(G_1) + dim(G_2).
    """

    logger.info("checking bounds from cut vertex")

    # find a cut vertex and associated induced cover of G
    cover = G.get_induced_cover_from_cut_vert()

    # determine if G has a cut vertex, if so return its index
    if len(cover) < 2:
        logger.info("no cut vertices found")
        return 0, G.num_verts

    # in the event that a cut vertex is found
    logger.info(f"cut vertex found, induced cover with size {len(cover)}")

    # determine dim(G_i) for each G_i in the cover, sum bounds
    d_lo_cover = 0
    d_hi_cover = 0
    for Gi in cover:
        d_lo_i, d_hi_i = dim_bounds(Gi, max_depth, depth + 1, logger)
        d_lo_cover += d_lo_i
        d_hi_cover += d_hi_i
    return d_lo_cover, d_hi_cover


def upper_bound_from_cliques(
    G: graph,
    d_lo: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> int:
    """
    Returns an upper bound on dim(G) by locating a vertex i that is part of a
    clique and obtaining a proper induced cover {K, H}, where K is the clique
    consisting of i and its neighborhood and H is the induced subgraph G - i.
    Assumes that G is connected and has already undergone reduction.
    """
    logger.info("checking bounds from cliques")
    d_hi_cliques = G.num_verts
    for i in range(G.num_verts):
        N = G.vert_neighbors(i)
        if all(G.is_edge(j, k) for j in N for k in N if j != k):
            H = G.__copy__()
            H.remove_vert(i)
            d_hi_H = dim_bounds(H, max_depth, depth + 1, logger)[1]
            d_hi_cliques = min(d_hi_cliques, d_hi_H + 1)
            if d_lo >= d_hi_cliques:
                return d_hi_cliques
    return d_hi_cliques


def bounds_from_edge_addition(
    G: graph,
    d_lo: int,
    d_hi: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int]:
    """
    Computes bounds on dim(G) by adding edges.

    NOTE: Recursion depth maxes out if both edge removal and addition are both
    enabled.
    """

    logger.info("checking bounds from edge addition")

    # avoid corrupting G
    G = G.__copy__()

    # sort vertices in descending order by degree
    perm = list(range(G.num_verts))
    perm.sort(key=lambda i: G.vert_deg(i), reverse=True)
    G.permute_verts(perm)

    # add edges
    d_lo_edges = 0
    d_hi_edges = G.num_verts
    for i in range(G.num_verts):
        for j in range(i + 1, G.num_verts):
            if not G.is_edge(i, j):
                H = G.__copy__()
                H.add_edge(i, j)
                d_lo_H, d_hi_H = dim_bounds(H, max_depth, depth + 1, logger)
                d_lo_edges = max(d_lo_edges, d_lo_H)
                d_hi_edges = min(d_hi_edges, d_hi_H)
                d_lo = max(d_lo, d_lo_edges - 1)
                d_hi = min(d_hi, d_hi_edges + 1)
                if d_lo >= d_hi:
                    return d_lo, d_hi
    return d_lo, d_hi


def bounds_from_edge_removal(
    G: graph,
    d_lo: int,
    d_hi: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int]:
    """
    Computes bounds on dim(G) by removing edges.

    NOTE: Recursion depth maxes out if both edge removal and addition are both
    enabled.
    """

    logger.info("checking bounds from edge removal")

    # avoid corrupting G
    G = G.__copy__()

    # sort vertices in ascending order by degree
    perm = list(range(G.num_verts))
    perm.sort(key=lambda i: G.vert_deg(i))
    G.permute_verts(perm)

    # remove edges
    d_lo_edges = 0
    d_hi_edges = G.num_verts
    for e in G.edges:
        H = G.__copy__()
        i, j = e.endpoints
        H.remove_edge(i, j)
        if H.is_connected():
            d_lo_H, d_hi_H = dim_bounds(H, max_depth, depth + 1, logger)
            d_lo_edges = max(d_lo_edges, d_lo_H)
            d_hi_edges = min(d_hi_edges, d_hi_H)
            d_lo = max(d_lo, d_lo_edges - 1)
            d_hi = min(d_hi, d_hi_edges + 1)
            if d_lo >= d_hi:
                return d_lo, d_hi
    return d_lo, d_hi


def bcd_bounds(
    G: graph,
    d_lo: int,
    d_hi: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int]:
    """
    Computes a lower bound on dim(G) by finding an independent set and applying
    bridge-correction decomposition.
    """

    logger.info("computing lower bound via BCD")

    # find a maximum independent set
    R = G.maximum_independent_set()
    m = len(R)

    # compute correction number
    xi = _correction_number(G, R, d_hi, max_depth, depth, logger)

    # compute lower bound
    d_lo = xi + m

    # if dim(G) - |R| <= 1, then dim(G) = |R| + xi
    if d_hi - m <= 1:
        logger.debug("d_hi - m <= 1, tight bounds found")
        d_hi = d_lo

    return d_lo, d_hi


def bcd_bounds_exhaustive(
    G: graph,
    d_lo: int,
    d_hi: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> tuple[int, int]:
    """
    Computes a lower bound on dim(G) by applying bridge-correction decomposition
    to every independent set.
    """

    logger.info("starting exhaustive BCD search")

    # obtain all independent sets
    R_list = G.independent_sets()

    # sort list of independent sets by size in descending order
    R_list.sort(key=lambda R: len(R), reverse=True)

    # find a maximum independent set
    for R in R_list:
        # size of independent set
        m = len(R)

        # compute correction number
        xi = _correction_number(G, R, d_hi, max_depth, depth, logger)

        # compute lower bound
        d_lo_R = xi + m

        # if dim(G) - |R| <= 1, then dim(G) = |R| + xi
        if d_hi - m <= 1:
            logger.debug("d_hi - m <= 1, tight bounds found")
            d_hi = d_lo_R
            return d_lo_R, d_hi

        # update lower bound
        d_lo = max(d_lo, d_lo_R)
        if d_lo >= d_hi:
            logger.debug("d_lo >= d_hi, tight bounds found")
            return d_lo, d_hi

    return d_lo, d_hi


def _correction_number(
    G: graph,
    R: set[int],
    d_hi: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
) -> int:
    """
    Computes the correction number of G with respect to an independent set R.
    """

    # sizes
    m = len(R)
    n = G.num_verts
    b = n - m

    # if G is empty, stop (but this should never happen)
    if b < 1:
        logger.warning("correction number aborted, G is empty")
        return 0

    # sort R in descending order to avoid index issues
    R_list: list[int] = list(R)
    R_list.sort(reverse=True)

    # target graph
    H_T = G.__copy__()
    for i in R_list:
        H_T.remove_vert(i)

    # complement of independent set
    V_minus_R = [i for i in range(n) if i not in R_list]

    # bridge matrix
    B = zeros((m, b), dtype=int)
    for i in range(m):
        for j in range(b):
            if G.is_edge(R_list[i], V_minus_R[j]):
                B[i, j] = 1

    # bridge generalized adjacency matrix
    BtB = B.T @ B

    # bridge graphs
    H_B = graph(b)
    H_BO = graph(b)
    for i in range(b):
        for j in range(i + 1, b):
            if BtB[i, j] == 1:
                H_B.add_edge(i, j)
            if BtB[i, j] > 1:
                H_BO.add_edge(i, j)

    # correction graphs
    H_C = graph(b)
    H_CO = H_BO.__copy__()
    for i in range(b):
        for j in range(i + 1, b):
            if H_T.is_edge(i, j) and H_B.is_edge(i, j):
                H_CO.add_edge(i, j)
            elif H_T.is_edge(i, j) != H_B.is_edge(i, j):  # XOR
                H_C.add_edge(i, j)

    # compute number of correction graphs
    num_opt_edges = H_CO.num_edges()

    # if there are no optional edges, return the correction number
    if num_opt_edges == 0:
        logger.debug("no optional edges in correction graph")
        num_isolated_verts = H_C.num_isolated_verts()
        d_lo_H_C = dim_bounds(H_C, max_depth, depth + 1, logger)[0]
        xi = d_lo_H_C - num_isolated_verts
        logger.info(f"correction number is {xi}")
        return xi

    # enumerate all correction graphs and compute correction number
    num_correction_graphs = 2**num_opt_edges
    # TODO: check that is not too large?
    logger.info(
        f"computing bounds for {num_correction_graphs} correction graphs"
    )
    xi = d_hi - m
    opt_edges = list(H_CO.edges)
    for k in range(num_correction_graphs):
        logger.debug(f"computing correction graph {k}")
        H_Ck = H_C.__copy__()
        binary = bin(k)[2:].zfill(num_opt_edges)
        for ij in range(num_opt_edges):
            if binary[ij] == "1":
                p, q = opt_edges[ij].endpoints
                H_Ck.add_edge(p, q)
        d_lo_k = dim_bounds(H_Ck, max_depth, depth + 1, logger)[0]
        xi = min(xi, d_lo_k - H_Ck.num_isolated_verts())  # yes, this is a min
        if xi == 0:
            break

    logger.info(f"correction number is {xi}")
    return xi


def bcd_upper_bound(
    G: graph,
    d_lo: int,
    max_depth: int,
    depth: int,
    logger: logging.Logger,
    n_max: int = 6,
) -> int:
    """
    !!! UNSTABLE
    Obtains an upper bound on dim(G) by treating it as a target graph of a
    larger graph. The independent set is taken to be a singleton whose
    neighborhood forms a clique in the target graph.
    """
    logger.info("computing upper bound via BCD")
    n = G.num_verts

    # TODO: this fails for n too large... why?
    if n > n_max:
        logger.debug(f"n > {n_max}, returning n")
        return n

    if n_max > 6:
        logger.warning("n_max > 6, may be unstable")

    d_hi_bcd = n
    for i in range(G.num_verts):
        N = G.vert_neighbors(i)

        # clique discovery
        # TODO: this is suboptimal
        clique = set([i])
        for j in N:
            if all([G.is_edge(j, k) for k in clique]):
                clique.add(j)

        # apply BCD
        if len(clique) > 2:
            H = G.__copy__()
            H.set_num_verts(n + 1)
            for p in clique:
                H.add_edge(p, n)
                for q in clique:
                    if p != q:
                        H.remove_edge(p, q)
            d_hi_H = dim_bounds(H, max_depth, depth + 1, logger)[1]
            d_hi_bcd = min(d_hi_bcd, d_hi_H - 1)
            if d_hi_bcd <= d_lo:
                return d_hi_bcd

    return d_hi_bcd
