from numpy.linalg import svd
from numpy import sqrt, set_printoptions
import cvxpy as cp
from .graph import graph

def msr(G: graph, tol: float=1e-4, debug=False):

	# define number of vertices
	n = G.num_vert

	# set minimum value of dot products of adjacent vertices
	epsilon = 0.01 / sqrt(n)

	# define the decision variable
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
				constraints.append(X[i, j] - S[i, j] == epsilon)
				constraints.append(S[i, j] >= 0)

	# set up and solve SDP
	prob = cp.Problem(cp.Minimize(cp.trace(X)), constraints)
	prob.solve()

	# find singular values of X
	_, sigma, _ = svd(X.value)

	if debug:
		set_printoptions(precision=2)
		print(sigma / sigma[0])

	# return approximate rank of X
	r = sum(sigma > tol * sigma[0])
	return r
