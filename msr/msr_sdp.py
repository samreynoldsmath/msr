import cvxpy as cp
from numpy import sqrt
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

    # define number of vertices
    n = G.num_verts
    if n < 1:
        raise ValueError("G must have at least one vertex")

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
                constraints.append(S[i, j] >= 0)

    # set up and solve SDP
    prob = cp.Problem(cp.Minimize(cp.trace(X)), constraints)
    prob.solve()

    # verify that ||X|| <= 1
    Xnorm = norm(X.value, "fro")
    if Xnorm > 1:
        raise Warning("||X|| > 1, suboptimal solution likely")

    # find singular values of X
    sigma = svd(X.value, compute_uv=False)

    # return approximate rank of X
    return sum(sigma > tol * sigma[0])
