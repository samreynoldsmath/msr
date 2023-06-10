from numpy.linalg import svd
import cvxpy as cp
from .graph import graph

def msr(G: graph, tol: float=1e-4):

	EPSILON = 1.0

	# define the decision variable
	n = G.num_vert
	X = cp.Variable((n, n), symmetric=True)

	# define slack variable
	S = cp.Variable((n, n), symmetric=True)

	# impose psd condition on X
	constraints = [X >> 0]

	# impose sparsity constraints
	A = G.adjacency_matrix()
	for i in range(n):
		for j in range(i + 1, n):
			if A[i, j] == 0:
				# not an edge
				constraints.append(X[i, j] == 0)
				constraints.append(S[i, j] == 0)
			else:
				# is an edge
				constraints.append(X[i, j] - S[i, j] == EPSILON)
				constraints.append(S[i, j] >= 0)

	# set up and solve SDP
	prob = cp.Problem(cp.Minimize(cp.trace(X)), constraints)
	prob.solve()

	# find singular values of X
	_, s, _ = svd(X.value)

	# return approximate rank of X
	return sum(s > tol * s[0])