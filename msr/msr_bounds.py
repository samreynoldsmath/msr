"""
Module for computing bounds on the minimum semidefinite rank of a graph.
"""

from copy import copy
from typing import Callable

from numpy import zeros

from .context_manager import GraphBoundsContextManager
from .graph import SimpleGraph
from .msr_lookup import load_msr_bounds, save_msr_bounds
from .msr_sdp import (
    msr_sdp_signed_cycle_search,
    msr_sdp_signed_exhaustive,
    msr_sdp_signed_simple,
    msr_sdp_upper_bound,
)
from .reduce import reduce
from .strategy_config import STRATEGY, BoundsStrategy


def build_strategy_dict() -> dict[
    str,
    Callable[
        [SimpleGraph, GraphBoundsContextManager], GraphBoundsContextManager
    ],
]:
    """
    Builds a dictionary of functions for computing bounds on dim(G). Each
    function takes a graph G and a context manager and returns a context manager
    with updated bounds and exit flag.
    """
    strategy_dict: dict[
        str,
        Callable[
            [SimpleGraph, GraphBoundsContextManager], GraphBoundsContextManager
        ],
    ] = {
        BoundsStrategy.BCD_LOWER_EXHAUSTIVE.value: _bcd_bounds_exhaustive,
        BoundsStrategy.BCD_LOWER.value: _bcd_max_indp_set,
        BoundsStrategy.BCD_UPPER.value: _bcd_upper_bound,
        BoundsStrategy.CLIQUE_UPPER.value: _upper_bound_from_cliques,
        BoundsStrategy.CUT_VERT.value: _bounds_from_cut_vert_induced_cover,
        BoundsStrategy.INDUCED_SUBGRAPH.value: _lower_bound_induced_subgraphs,
        BoundsStrategy.EDGE_ADDITION.value: _bounds_from_edge_addition,
        BoundsStrategy.EDGE_REMOVAL.value: _bounds_from_edge_removal,
        BoundsStrategy.SDP_SIGNED_CYCLE.value: _sdp_signed_cycle,
        BoundsStrategy.SDP_SIGNED_EXHAUSTIVE.value: _sdp_signed_exhaustive,
        BoundsStrategy.SDP_SIGNED_SIMPLE.value: _sdp_signed_simple,
        BoundsStrategy.SDP_UPPER.value: _sdp_upper,
    }
    return strategy_dict


def msr_bounds(G: SimpleGraph, **kwargs) -> tuple[int, int]:
    """
    Returns bounds on msr(G) using a recursive algorithm.

    Keyword arguments:
    - log_path:         path to log file (default: "msr/log")
    - log_filename:     name of log file (default: G.hash_id() + ".log"
    - log_level:        logging level (default: logging.ERROR)
    - max_depth:        maximum recursion depth (default: 10 * G.num_verts)
    - load_bounds:      load bounds from file (default: True)
    - save_bounds:      save bounds to file (default: True)
    """

    # configure context manager and start new log
    ctx = GraphBoundsContextManager(
        num_verts=G.num_verts, graph_id=G.hash_id(), **kwargs
    )
    ctx.start_new_log(graph_str=str(G))

    # find number of isolated vertices
    num_isolated_verts = G.num_isolated_verts()

    # find bounds on dim(G)
    ctx = _dim_bounds(G, ctx)

    # mod out isolated vertices
    d_lo = ctx.d_lo - num_isolated_verts
    d_hi = ctx.d_hi - num_isolated_verts

    # return bounds on msr(G)
    return d_lo, d_hi


def _dim_bounds(
    G: SimpleGraph, parent_ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Returns bounds dim(G), where G is a simple undirected graph, and
    dim(G) = msr(G) + the number of isolated vertices. Equivalently, dim(G) is
    the minimum dimension of a faithful orthogonal representation of G such
    the zero vector is not assigned to any vertex.
    """

    # create child context
    ctx = parent_ctx.child_context(num_verts=G.num_verts)

    # check recursion depth
    if ctx.check_depth(num_verts=G.num_verts):
        return ctx

    # avoid corrupting G
    G = copy(G)

    # find bounds on dim(G) using simple methods
    ctx = _dim_bounds_simple(G, ctx)
    if ctx.check_bounds("simple methods"):
        return ctx

    # reduce the graph and obtain bounds on the reduced graph
    G, ctx = _reduce_and_bound_reduction(G, ctx)
    if ctx.check_bounds("reducing graph"):
        return ctx

    # attempt to load bounds from file
    if ctx.load_bounds_flag:
        d_lo_file, d_hi_file = load_msr_bounds(G, ctx.logger)
        ctx.update_bounds(d_lo_file, d_hi_file)
        if ctx.check_bounds("loading bounds from file"):
            return ctx
    else:
        d_lo_file = 0
        d_hi_file = G.num_verts

    # advanced strategies
    strategy_dict = build_strategy_dict()
    for strategy in STRATEGY:
        ctx = strategy_dict[strategy.value](G, ctx)
        if ctx.check_bounds(strategy.value):
            if ctx.save_condition(d_lo_file, d_hi_file):
                save_msr_bounds(G, ctx.d_lo, ctx.d_hi, ctx.logger)
            return ctx

    # exit without tight bounds
    ctx.log_good_exit("out of strategies")
    if ctx.save_condition(d_lo_file, d_hi_file):
        save_msr_bounds(G, ctx.d_lo, ctx.d_hi, ctx.logger)
    return ctx


def _dim_bounds_simple(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Gets bounds on dim(G) by counting edges, degrees, and checking connectivity.
    Returns the bounds and a flag that indicates if the program is ready to
    exit.
    """

    # get number of vertices
    n = G.num_verts

    # special case: empty graph
    if G.is_empty():
        ctx.update_bounds(n, n)
        ctx.log_good_exit("G is empty on {n} vertices")
        return ctx

    # special case: complete graph
    if G.is_complete():
        ctx.update_bounds(1, 1)
        ctx.log_good_exit("G is complete on {n} vertices")
        return ctx

    # find bounds by summing bounds on components
    ctx = _get_bounds_on_components(G, ctx)

    # if G is disconnected, this is the best estimate
    if not G.is_connected():
        return ctx

    # special case: tree
    if G.is_a_tree():
        ctx.update_bounds(n - 1, n - 1)
        ctx.log_good_exit("G is a tree on {n} vertices")
        return ctx

    # special case: cycle
    if G.is_a_cycle():
        ctx.update_bounds(n - 2, n - 2)
        ctx.log_good_exit("G is a cycle on {n} vertices")
        return ctx

    # simple strategies failed
    return ctx


def _get_bounds_on_components(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Computes bounds on dim(G) by summing bounds on components of G.
    """

    # find components of G
    components = G.connected_components()

    # log if G is disconnected
    if G.is_connected():
        ctx.logger.info("G is connected")
        ctx.update_bounds(1, G.num_verts - 1)
        return ctx

    # otherwise, G is disconnected
    ctx.logger.info(f"G is disconnected with {len(components)} components")
    d_lo = 0
    d_hi = 0
    for H in components:
        comp_ctx = _dim_bounds(H, ctx)
        d_lo += comp_ctx.d_lo
        d_hi += comp_ctx.d_hi
    ctx.update_bounds(d_lo, d_hi)
    ctx.log_good_exit("graph is disconnected")
    return ctx


def _reduce_and_bound_reduction(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> tuple[SimpleGraph, GraphBoundsContextManager]:
    """
    Performs the reduction G |-> H and returns H and bounds on dim(H).

    If the reduction is trivial (i.e. no vertices removed), we return the
    original graph and bound dim(G) with (2, n - 2).

    If the reduction is nontrivial, we get bounds on the reduced graph using
    simple methods. (This includes using advanced methods on the components of
    the reduced graph, if it is disconnected.) If this fails to get tight
    bounds, we will attempt advanced strategies after returning to
    _dim_bounds().
    """

    # reduce the graph
    G, d_diff, deletions = reduce(G, ctx.logger)

    # reduction changed nothing
    if deletions == 0:
        ctx.logger.debug("reduction is trivial")
        return G, ctx

    # get bounds on the reduced graph
    if deletions > 0:
        ctx.logger.info("checking bounds of reduced graph")
        ctx = _dim_bounds_simple(G, ctx)
        ctx.d_lo += d_diff
        ctx.d_hi += d_diff
        return G, ctx

    # something went wrong
    msg = f"reduction failed: deletions = {deletions} < 0"
    ctx.log_bad_exit(msg)
    raise ValueError(msg)


def _lower_bound_induced_subgraphs(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Returns the maximum lower bound of the dimension of any induced subgraph.
    """
    ctx.logger.info("checking induced subgraphs")
    d_lo = 0
    n = G.num_verts
    for i in range(n):
        ctx.logger.debug(f"induced subgraph {i}")
        H = copy(G)
        H.remove_vert(i)
        subgraph_ctx = _dim_bounds(H, ctx)
        d_lo = max(d_lo, subgraph_ctx.d_lo)
        if d_lo >= ctx.d_hi:
            ctx.update_lower_bound(d_lo)
            return ctx
    ctx.update_lower_bound(d_lo)
    return ctx


def _bounds_from_cut_vert_induced_cover(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Checks if G has a cut vertex. If so, generate a proper induced cover
    {G_1, G_2} such that G_1 and G_2 intersect at exactly one vertex. Then it
    holds that dim(G) = dim(G_1) + dim(G_2).
    """

    ctx.logger.info("checking bounds from cut vertex")

    # find a cut vertex and associated induced cover of G
    cover = G.get_induced_cover_from_cut_vert()

    # determine if G has a cut vertex, if so return its index
    if len(cover) < 2:
        ctx.logger.info("no cut vertices found")
        return ctx

    # in the event that a cut vertex is found
    ctx.logger.info(f"cut vertex found, induced cover with size {len(cover)}")

    # determine dim(G_i) for each G_i in the cover, sum bounds
    d_lo_cover = 0
    d_hi_cover = 0
    for G_i in cover:
        subgraph_ctx = _dim_bounds(G_i, ctx)
        d_lo_cover += subgraph_ctx.d_lo
        d_hi_cover += subgraph_ctx.d_hi
    ctx.update_bounds(d_lo_cover, d_hi_cover)
    return ctx


def _upper_bound_from_cliques(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Returns an upper bound on dim(G) by locating a vertex i that is part of a
    clique and obtaining a proper induced cover {K, H}, where K is the clique
    consisting of i and its neighborhood and H is the induced subgraph G - i.
    Assumes that G is connected and has already undergone reduction.
    """
    ctx.logger.info("checking bounds from cliques")
    d_hi_cliques = G.num_verts
    for i in range(G.num_verts):
        neighborhood = G.vert_neighbors(i)
        if all(
            G.is_edge(j, k)
            for j in neighborhood
            for k in neighborhood
            if j != k
        ):
            H = copy(G)
            H.remove_vert(i)
            subgraph_ctx = _dim_bounds(H, ctx)
            d_hi_cliques = min(d_hi_cliques, subgraph_ctx.d_hi + 1)
            if ctx.d_lo >= d_hi_cliques:
                ctx.update_upper_bound(d_hi_cliques)
                return ctx
    ctx.update_upper_bound(d_hi_cliques)
    return ctx


def _bounds_from_edge_addition(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Computes bounds on dim(G) by adding edges.

    NOTE: Recursion depth maxes out if both edge removal and addition are both
    enabled.
    """

    ctx.logger.info("checking bounds from edge addition")

    # avoid corrupting G
    G = copy(G)

    # sort vertices in descending order by degree
    perm = list(range(G.num_verts))
    perm.sort(key=G.vert_deg, reverse=True)
    G.permute_verts(perm)

    # add edges
    d_lo = ctx.d_lo
    d_hi = ctx.d_hi
    d_lo_edges = 0
    d_hi_edges = G.num_verts
    for i in range(G.num_verts):
        for j in range(i + 1, G.num_verts):
            if not G.is_edge(i, j):
                H = copy(G)
                H.add_edge(i, j)
                new_edge_ctx = _dim_bounds(H, ctx)
                d_lo_edges = max(d_lo_edges, new_edge_ctx.d_lo)
                d_hi_edges = min(d_hi_edges, new_edge_ctx.d_hi)
                d_lo = max(d_lo, d_lo_edges - 1)
                d_hi = min(d_hi, d_hi_edges + 1)
                if d_lo >= d_hi:
                    ctx.update_bounds(d_lo, d_hi)
                    return ctx
    ctx.update_bounds(d_lo, d_hi)
    return ctx


def _bounds_from_edge_removal(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Computes bounds on dim(G) by removing edges.

    NOTE: Recursion depth maxes out if both edge removal and addition are both
    enabled.
    """

    ctx.logger.info("checking bounds from edge removal")

    # avoid corrupting G
    G = copy(G)

    # sort vertices in ascending order by degree
    perm = list(range(G.num_verts))
    perm.sort(key=G.vert_deg)
    G.permute_verts(perm)

    # remove edges
    d_lo = ctx.d_lo
    d_hi = ctx.d_hi
    d_lo_edges = 0
    d_hi_edges = G.num_verts
    for e in G.edges:
        H = copy(G)
        i, j = e.endpoints
        H.remove_edge(i, j)
        if H.is_connected():
            new_edge_ctx = _dim_bounds(H, ctx)
            d_lo_edges = max(d_lo_edges, new_edge_ctx.d_lo)
            d_hi_edges = min(d_hi_edges, new_edge_ctx.d_hi)
            d_lo = max(d_lo, d_lo_edges - 1)
            d_hi = min(d_hi, d_hi_edges + 1)
            if d_lo >= d_hi:
                ctx.update_bounds(d_lo, d_hi)
                return ctx
    ctx.update_bounds(d_lo, d_hi)
    return ctx


def _bcd_max_indp_set(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Computes a lower bound on dim(G) by finding a maximum independent set and
    applying bridge-correction decomposition.
    """

    ctx.logger.info("starting BCD search")

    # find a maximum independent set
    max_indp_set = G.maximum_independent_set()

    return _bcd_bounds(G, max_indp_set, ctx)


def _bcd_bounds_exhaustive(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Computes a lower bound on dim(G) by applying bridge-correction decomposition
    to every independent set.
    """

    ctx.logger.info("starting exhaustive BCD search")

    # obtain all independent sets
    max_indp_set_list = G.independent_sets()

    # sort list of independent sets by size in descending order
    max_indp_set_list.sort(key=len, reverse=True)

    # find a maximum independent set
    for max_indp_set in max_indp_set_list:
        # apply BCD
        ctx = _bcd_bounds(G, max_indp_set, ctx)

        # update lower bound
        if ctx.check_bounds("exhaustive BCD search"):
            return ctx

    # if no tight bounds found, return the best lower bound
    return ctx


def _bcd_bounds(
    G: SimpleGraph, max_indp_set: set[int], ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Computes a lower bound on dim(G) by finding an independent set and applying
    bridge-correction decomposition.
    """

    m = len(max_indp_set)

    # compute correction number
    xi = _correction_number(G, max_indp_set, ctx)

    # compute lower bound
    d_lo = xi + m
    ctx.update_lower_bound(d_lo)

    # if dim(G) - |R| <= 1, then dim(G) = |R| + xi
    if ctx.d_hi - m <= 1:
        ctx.logger.debug("d_hi - m <= 1, tight bounds found")
        ctx.update_upper_bound(d_lo)
    return ctx


def _correction_number(
    G: SimpleGraph, max_indp_set: set[int], ctx: GraphBoundsContextManager
) -> int:
    """
    Computes the correction number of G with respect to an independent set R.
    """

    # sizes
    m = len(max_indp_set)
    n = G.num_verts
    b = n - m

    # if G is empty, stop (but this should never happen)
    if b < 1:
        ctx.logger.warning("correction number aborted, G is empty")
        return 0

    # sort R in descending order to avoid index issues
    max_indp_set_list: list[int] = list(max_indp_set)
    max_indp_set_list.sort(reverse=True)

    # target graph
    H_T = copy(G)
    for i in max_indp_set_list:
        H_T.remove_vert(i)

    # complement of independent set
    remaining_verts = [i for i in range(n) if i not in max_indp_set_list]

    # bridge matrix
    bridge_mat = zeros((m, b), dtype=int)
    for i in range(m):
        for j in range(b):
            if G.is_edge(max_indp_set_list[i], remaining_verts[j]):
                bridge_mat[i, j] = 1

    # bridge generalized adjacency matrix
    gen_adj_mat = bridge_mat.T @ bridge_mat

    # bridge graphs
    H_B = SimpleGraph(b)
    H_BO = SimpleGraph(b)
    for i in range(b):
        for j in range(i + 1, b):
            if gen_adj_mat[i, j] == 1:
                H_B.add_edge(i, j)
            if gen_adj_mat[i, j] > 1:
                H_BO.add_edge(i, j)

    # correction graphs
    H_C = SimpleGraph(b)
    H_CO = copy(H_BO)
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
        ctx.logger.debug("no optional edges in correction graph")
        num_isolated_verts = H_C.num_isolated_verts()
        correction_ctx = _dim_bounds(H_C, ctx)
        xi = correction_ctx.d_lo - num_isolated_verts
        ctx.logger.info(f"correction number is {xi}")
        return xi

    # enumerate all correction graphs and compute correction number
    num_correction_graphs = 2**num_opt_edges
    # TODO: check that is not too large?
    ctx.logger.info(
        f"computing bounds for {num_correction_graphs} correction graphs"
    )
    xi = ctx.d_hi - m
    opt_edges = list(H_CO.edges)
    for k in range(num_correction_graphs):
        ctx.logger.debug(f"computing correction graph {k}")
        H_Ck = copy(H_C)
        binary = bin(k)[2:].zfill(num_opt_edges)
        for ij in range(num_opt_edges):
            if binary[ij] == "1":
                p, q = opt_edges[ij].endpoints
                H_Ck.add_edge(p, q)
        correction_ctx = _dim_bounds(H_Ck, ctx)
        xi = min(xi, correction_ctx.d_lo - H_Ck.num_isolated_verts())
        if xi == 0:
            break

    ctx.logger.info(f"correction number is {xi}")
    return xi


def _bcd_upper_bound(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    !!! UNSTABLE
    Obtains an upper bound on dim(G) by treating it as a target graph of a
    larger graph. The independent set is taken to be a singleton whose
    neighborhood forms a clique in the target graph.
    """
    ctx.logger.info("computing upper bound via BCD")

    n = G.num_verts
    n_max = 6  # TODO: this fails for n too large... why?

    if n > n_max:
        ctx.logger.info(f"n > {n_max}, returning n")
        return ctx

    if n_max > 6:
        ctx.logger.warning("n_max > 6, may be unstable")

    d_hi_bcd = n
    for i in range(G.num_verts):
        neighborhood = G.vert_neighbors(i)

        # clique discovery
        # TODO: this is suboptimal
        clique = set([i])
        for j in neighborhood:
            if all(G.is_edge(j, k) for k in clique):
                clique.add(j)

        # apply BCD
        if len(clique) > 2:
            H = copy(G)
            H.set_num_verts(n + 1)
            for p in clique:
                H.add_edge(p, n)
                for q in clique:
                    if p != q:
                        H.remove_edge(p, q)
            new_graph_ctx = _dim_bounds(H, ctx)
            d_hi_bcd = min(d_hi_bcd, new_graph_ctx.d_hi - 1)
            if d_hi_bcd <= ctx.d_lo:
                ctx.update_upper_bound(d_hi_bcd)
                return ctx

    ctx.update_upper_bound(d_hi_bcd)
    return ctx


def _sdp_upper(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """Wrapper for msr_sdp_upper_bound()"""
    d_hi = msr_sdp_upper_bound(G, ctx.logger)
    ctx.update_upper_bound(d_hi)
    return ctx


def _sdp_signed_cycle(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Wrapper for msr_sdp_signed_cycle_search()
    """
    d_hi = msr_sdp_signed_cycle_search(G, ctx.d_lo, ctx.logger)
    ctx.update_upper_bound(d_hi)
    return ctx


def _sdp_signed_exhaustive(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Wrapper for msr_sdp_signed_exhaustive()
    """
    d_hi = msr_sdp_signed_exhaustive(G, ctx.d_lo, ctx.logger)
    ctx.update_upper_bound(d_hi)
    return ctx


def _sdp_signed_simple(
    G: SimpleGraph, ctx: GraphBoundsContextManager
) -> GraphBoundsContextManager:
    """
    Wrapper for msr_sdp_signed_simple()
    """
    d_hi = msr_sdp_signed_simple(G, ctx.d_lo, ctx.logger)
    ctx.update_upper_bound(d_hi)
    return ctx
