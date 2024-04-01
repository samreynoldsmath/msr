r"""
Module for computing an upper bound on msr(G) using a semidefinite program.

A relaxation of the objective function rank(A) to the trace
tr(A) and casts the problem as a semidefinite program. The sparsity constraints
$A_{ij} \neq 0$ for $ij \in E$ are nonconvex, and we instead use
$A_{ij} \geq \varepsilon$ for some fixed $\varepsilon > 0$. By introducing
slack variables, the feasible set can be shown to be a spectrahedron.

These constraints are a proper subset of the original sparsity constraints,
and for some graphs (e.g. the 4-cycle), the SDP returns an estimation of
$\text{msr}(G)$ that is strictly larger than the exact solution.

TODO: Further investigation is required to determine which types of graphs
have a minimum rank positive semidefinite generalized adjacency matrix with
nonnegative entries.
"""

from itertools import combinations
from logging import Logger

import cvxpy as cp
from numpy import ndarray, sign, sqrt, zeros
from numpy.linalg import norm, svd

from .graph.graph import SimpleGraph, UndirectedEdge


def msr_sdp_signed(
    edge_signs: ndarray,
    logger: Logger,
    tol: float = 1e-4,
) -> int:
    """
    Obtains an upper bound on $\text{msr}(G)$ by solving a semidefinite program
    with signed constraints on the entries of the generalized adjacency matrix.
    """

    # get number of vertices
    n = edge_signs.shape[0]

    # check that G has at least one vertex
    if n < 1:
        raise ValueError("G must have at least one vertex")

    # check that edge_signs is an n x n matrix
    if edge_signs.shape != (n, n):
        msg = "edge_signs must be an n x n matrix"
        logger.error(msg)
        raise ValueError(msg)

    # set minimum value of dot products of adjacent vertices
    epsilon = 0.01 / sqrt(n)

    # define the decision variable
    X = cp.Variable((n, n), symmetric=True)

    # define slack variable
    S = cp.Variable((n, n), symmetric=True)

    # impose psd condition on X
    constraints = [X >> 0]

    # impose sparsity constraints
    for i in range(n):
        for j in range(i + 1, n):
            if edge_signs[i, j] != 0:
                constraints.append(
                    edge_signs[i, j] * X[i, j] - S[i, j] == epsilon
                )
                constraints.append(S[i, j] >= 0)
            else:
                constraints.append(X[i, j] == 0)
                constraints.append(S[i, j] == 0)

    # set up and solve SDP
    prob = cp.Problem(cp.Minimize(cp.trace(X)), constraints)
    prob.solve(eps=1e-6)

    # round near-zero values to zero
    X.value[abs(X.value) < tol] = 0

    # verify that X is a generalized adjacency matrix
    if not _have_same_non_diagonal_sign_pattern(n, edge_signs, X.value):
        msg = "X is not a generalized adjacency matrix"
        msg += f" at edge ({i}, {j}), sign {edge_signs[i, j]}"
        msg += f" with value {X[i, j].value}"
        logger.error(msg)
        raise ValueError(msg)

    # verify that ||X|| <= 1
    X_norm = norm(X.value, "fro")
    if X_norm > 1:
        logger.warning(f"||X|| = {X_norm} > 1, suboptimal solution likely")

    # find singular values of X
    sigma = svd(X.value, compute_uv=False)

    # return approximate rank of X
    return sum(sigma > tol * sigma[0])


def _have_same_non_diagonal_sign_pattern(
    n: int, A: ndarray, B: ndarray
) -> bool:
    """
    Returns true if A and B have the same non-diagonal sign pattern. Assumes
    that A and B are n by n symmetric matrices with no near-zero entries.
    """
    for i in range(n):
        for j in range(i + 1, n):
            if sign(A[i, j]) != sign(B[i, j]):
                return False
    return True


def msr_sdp_upper_bound(
    G: SimpleGraph, logger: Logger, tol: float = 1e-4
) -> int:
    """
    Uses all positive edge signs to find an upper bound on msr(G).
    """

    logger.debug("beginning SDP relaxation to obtain upper bound")

    A = G.adjacency_matrix()
    return msr_sdp_signed(A, logger, tol)


def msr_sdp_signed_simple(
    G: SimpleGraph, d_lo: int, logger: Logger, tol=1e-4
) -> int:
    """
    Flips sign of each edge in turn to find the minimum rank of a positive
    semidefinite generalized adjacency matrix.
    """
    d_hi = msr_sdp_upper_bound(G, logger, tol)
    if d_hi <= d_lo:
        logger.info("simple search succeeded")
        return d_hi
    logger.info("beginning simple search with SDP relaxation")
    n = G.num_verts
    d_hi = n
    num_edges = G.num_edges()
    edge_signs = G.adjacency_matrix()
    for k, ij in enumerate(G.edges):
        i, j = ij.endpoints
        edge_signs[i, j] = -1
        edge_signs[j, i] = -1
        logger.debug(f"SDP signed simple {k} /  {num_edges}")
        d = msr_sdp_signed(edge_signs, tol)
        if d <= d_lo:
            logger.info(f"simple search succeeded with flip {k}")
            return d
        d_hi = min(d_hi, d)
        edge_signs[i, j] = +1
        edge_signs[j, i] = +1
    logger.info("simple search exited without tight bound")
    return d_hi


def msr_sdp_signed_cycle_search(
    G: SimpleGraph, d_lo: int, logger: Logger, tol=1e-4
) -> int:
    """
    Flips sign of each edge in turn to find the minimum rank of a positive
    semidefinite generalized adjacency matrix.
    """
    logger.info("beginning search with signed-cycle SDP relaxation")

    # find edges that are part of an even cycle
    edge_list = _edges_in_induced_even_cycle(G)
    e = len(edge_list)

    # search over edges
    n = G.num_verts
    if e < 1:
        logger.info("no edges to search over")
        return n
    num_signs = 2**e
    logger.info(f"searching over {num_signs} possible edge signs")
    d_hi = n
    A = G.adjacency_matrix()
    for k in range(num_signs):
        edge_signs = A.copy()
        binary = bin(k)[2:].zfill(e)
        for ij, idx in zip(edge_list, range(e)):
            i, j = ij.endpoints
            edge_signs[i, j] = 1 - 2 * int(binary[idx])
            edge_signs[j, i] = edge_signs[i, j]
        logger.debug(f"SDP signed cycle {k} / {num_signs}")
        d = msr_sdp_signed(edge_signs, tol)
        d_hi = min(d_hi, d)
        if d_hi <= d_lo:
            logger.info(f"signed cycle search succeeded with flip {k}")
            return d_hi
    logger.info("signed cycle search exited without tight bound")
    return d_hi


def _edges_in_induced_even_cycle(G: SimpleGraph) -> list[UndirectedEdge]:
    """Returns set of edges in an induced even cycle."""
    n = G.num_verts
    max_num_verts_induced_cycle = 2 * (n // 2)
    edges: set[UndirectedEdge] = set()

    # loop over induced subgraphs with even number of vertices >= 4
    for m in range(4, max_num_verts_induced_cycle + 1, 2):
        for vert_tuple in combinations(range(n), m):
            vert_set = set(vert_tuple)
            H = G.induced_subgraph(vert_set)
            if H.is_a_cycle():
                for ij in combinations(vert_set, 2):
                    i, j = ij
                    if G.is_edge(i, j):
                        edges.add(UndirectedEdge(i, j))

    return list(edges)


def msr_sdp_signed_exhaustive(
    G: SimpleGraph, d_lo: int, logger: Logger, tol=1e-4
) -> int:
    """
    Searches over all possible edge signs to find the minimum rank of a
    positive semidefinite generalized adjacency matrix.
    """
    logger.info("beginning exhaustive search with SDP relaxation")
    n = G.num_verts
    e = G.num_edges()
    if e < 1:
        return 0
    num_signs = 2**e
    d_hi = n
    edge_list = list(G.edges)
    for k in range(num_signs):
        edge_signs = zeros((n, n), dtype=int)
        binary = bin(k)[2:].zfill(e)
        for ij, idx in zip(edge_list, range(e)):
            i, j = ij.endpoints
            edge_signs[i, j] = 1 - 2 * int(binary[idx])
            edge_signs[j, i] = edge_signs[i, j]
        logger.debug(f"SDP exhaustive {k} /  {num_signs}")
        d = msr_sdp_signed(edge_signs, tol)
        d_hi = min(d_hi, d)
        if d_hi <= d_lo:
            logger.info(f"exhaustive search succeeded with flip {k}")
            return d_hi
    logger.info("exhaustive search failed")
    return d_hi
