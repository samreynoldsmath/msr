import logging

import cvxpy as cp
from numpy import ndarray, sqrt, zeros
from numpy.linalg import norm, svd

from .graph.graph import graph


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
    return msr_sdp_signed(G, A, tol)


def msr_sdp_signed(G: graph, edge_signs: ndarray, tol: float = 1e-4) -> int:
    """
    Obtains an upper bound on $\text{msr}(G)$ by solving a semidefinite program
    with signed constraints on the entries of the generalized adjacency matrix.
    """

    logging.debug("beginning signed SDP relaxation")

    # define number of vertices
    n = G.num_verts
    if n < 1:
        msg = "G must have at least one vertex"
        logging.error(msg)
        raise ValueError(msg)

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
            if not G.is_edge(i, j):
                constraints.append(X[i, j] == 0)
                constraints.append(S[i, j] == 0)
            else:
                constraints.append(X[i, j] - S[i, j] == epsilon)
                constraints.append(edge_signs[i, j] * S[i, j] >= 0)

    # set up and solve SDP
    prob = cp.Problem(cp.Minimize(cp.trace(X)), constraints)
    prob.solve()

    # verify that ||X|| <= 1
    X_norm = norm(X.value, "fro")
    if X_norm > 1:
        logging.warning(f"||X|| = {X_norm} > 1, suboptimal solution likely")

    # find singular values of X
    sigma = svd(X.value, compute_uv=False)

    # return approximate rank of X
    return sum(sigma > tol * sigma[0])


def msr_sdp_signed_simple(G: graph, d_lo: int, tol=1e-4) -> int:
    """
    Flips sign of each edge in turn to find the minimum rank of a positive
    semidefinite generalized adjacency matrix.
    """
    logging.info("beginning simple search with SDP relaxation")
    n = G.num_verts
    d_hi = n
    edge_signs = G.adjacency_matrix()
    for ij in G.edges:
        i, j = ij.endpoints
        edge_signs[i, j] = -1
        edge_signs[j, i] = -1
        d = msr_sdp_signed(G, edge_signs, tol)
        if d <= d_lo:
            logging.info(f"simple search succeeded with edge {ij.endpoints}")
            return d
        d_hi = min(d_hi, d)
        edge_signs[i, j] = +1
        edge_signs[j, i] = +1
    logging.info("simple search exited without tight bound")
    return d_hi


def msr_sdp_signed_exhaustive(G: graph, d_lo: int, tol=1e-4) -> tuple[int, int]:
    """
    Searches over all possible edge signs to find the minimum rank of a
    positive semidefinite generalized adjacency matrix.
    """
    logging.info("beginning exhaustive search with SDP relaxation")
    n = G.num_verts
    e = G.num_edges()
    if e < 1:
        return 0, 0
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
        d = msr_sdp_signed(G, edge_signs, tol)
        d_hi = min(d_hi, d)
        if d_hi <= d_lo:
            logging.info(f"exhaustive search succeeded with iter {k}")
            return d_lo, d_hi
    logging.warning("exhaustive search failed")
    return d_hi, d_hi
