import logging
from itertools import combinations

import cvxpy as cp
from numpy import ndarray, sign, sqrt, zeros
from numpy.linalg import norm, svd

from .graph.graph import graph, undirected_edge


def msr_sdp_signed(edge_signs: ndarray, tol: float = 1e-4) -> int:
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
        logging.error(msg)
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
        logging.error(msg)
        raise ValueError(msg)

    # verify that ||X|| <= 1
    X_norm = norm(X.value, "fro")
    if X_norm > 1:
        logging.warning(f"||X|| = {X_norm} > 1, suboptimal solution likely")

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


def msr_sdp_upper_bound(G: graph, tol: float = 1e-4) -> int:
    """
    Obtains an approximation of $\text{msr}(G)$ using a relaxation of the
    objective function $\text{rank}(A)$ to the trace $\text{tr}(A)$ and casts
    the problem as a semidefinite program. The sparsity constraints
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

    logging.debug("beginning SDP relaxation to obtain upper bound")

    A = G.adjacency_matrix()
    return msr_sdp_signed(A, tol)


def msr_sdp_signed_simple(G: graph, d_lo: int, tol=1e-4) -> int:
    """
    Flips sign of each edge in turn to find the minimum rank of a positive
    semidefinite generalized adjacency matrix.
    """
    logging.info("beginning simple search with SDP relaxation")
    n = G.num_verts
    d_hi = n
    num_edges = G.num_edges()
    edge_signs = G.adjacency_matrix()
    for k, ij in enumerate(G.edges):
        i, j = ij.endpoints
        edge_signs[i, j] = -1
        edge_signs[j, i] = -1
        logging.debug(f"SDP signed simple {k} /  {num_edges}")
        d = msr_sdp_signed(edge_signs, tol)
        if d <= d_lo:
            logging.info(f"simple search succeeded")
            return d
        d_hi = min(d_hi, d)
        edge_signs[i, j] = +1
        edge_signs[j, i] = +1
    logging.info("simple search exited without tight bound")
    return d_hi


def msr_sdp_signed_cycle_search(G: graph, d_lo: int, tol=1e-4) -> int:
    """
    Flips sign of each edge in turn to find the minimum rank of a positive
    semidefinite generalized adjacency matrix.
    """
    logging.info("beginning search with signed-cycle SDP relaxation")

    # find edges that are part of an even cycle
    edge_list = _edges_in_induced_even_cycle(G)
    e = len(edge_list)

    # search over edges
    n = G.num_verts
    if e < 1:
        logging.info("no edges to search over")
        return n
    num_signs = 2**e
    logging.info(f"searching over {num_signs} possible edge signs")
    d_hi = n
    A = G.adjacency_matrix()
    for k in range(num_signs):
        edge_signs = A.copy()
        binary = bin(k)[2:].zfill(e)
        for ij, idx in zip(edge_list, range(e)):
            i, j = ij.endpoints
            edge_signs[i, j] = 1 - 2 * int(binary[idx])
            edge_signs[j, i] = edge_signs[i, j]
        logging.debug(f"SDP signed cycle {k} / {num_signs}")
        d = msr_sdp_signed(edge_signs, tol)
        d_hi = min(d_hi, d)
        if d_hi <= d_lo:
            logging.info(f"signed cycle search succeeded")
            return d_hi
    logging.info(f"signed cycle search exited without tight bound")
    return d_hi


def _edges_in_induced_even_cycle(G: graph) -> list[undirected_edge]:
    """Returns set of edges in an induced even cycle."""
    n = G.num_verts
    max_num_verts_induced_cycle = 2 * (n // 2)
    edges: set[undirected_edge] = set()

    # loop over induced subgraphs with even number of vertices >= 4
    for m in range(4, max_num_verts_induced_cycle + 1, 2):
        for vert_tuple in combinations(range(n), m):
            vert_set = set(vert_tuple)
            H = G.induced_subgraph(vert_set)
            if H.is_a_cycle():
                for ij in combinations(vert_set, 2):
                    i, j = ij
                    if G.is_edge(i, j):
                        edges.add(undirected_edge(i, j))

    return list(edges)


def msr_sdp_signed_exhaustive(G: graph, d_lo: int, tol=1e-4) -> int:
    """
    Searches over all possible edge signs to find the minimum rank of a
    positive semidefinite generalized adjacency matrix.
    """
    logging.info("beginning exhaustive search with SDP relaxation")
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
        logging.debug(f"SDP exhaustive {k} /  {num_signs}")
        d = msr_sdp_signed(edge_signs, tol)
        d_hi = min(d_hi, d)
        if d_hi <= d_lo:
            logging.info(f"exhaustive search succeeded")
            return d_hi
    logging.warning(f"exhaustive search failed")
    return d_hi
