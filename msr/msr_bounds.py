import logging
from .graph.simple_undirected_graph import simple_undirected_graph
from .msr_sdp import msr_sdp_upper_bound
from .reduce import reduce

# configure logging
logging.basicConfig(
	filename='msr_bounds.log',
	filemode='w',
	encoding='utf-8',
	level=logging.WARNING,
	format='%(levelname)s [%(funcName)s %(lineno)s] %(message)s',
)

def msr_bounds(G: simple_undirected_graph) -> tuple[int, int]:
	"""
	Returns bounds on msr(G) using a recursive algorithm.
	"""

	# log input
	logging.info('computing bounds on msr(G) with G =\n' + str(G))

	# check that G is nontrivial
	if G.num_verts < 1:
		msg = 'G must have at least one vertex'
		logging.error(msg)
		raise ValueError(msg)

	# avoid corrupting G
	G = G.__copy__()

	# find number of isolated vertices
	num_isolated_verts = G.num_isolated_verts()

	# max recursion depth
	max_depth = 10 * G.num_verts

	# find bounds on dim(G)
	d_lo, d_hi = dim_bounds(G, max_depth)

	# mod out isolated vertices
	d_lo -= num_isolated_verts
	d_hi -= num_isolated_verts

	# log output
	logging.info(f'exited with result {(d_lo, d_hi)}')

	# return bounds on msr(G)
	return d_lo, d_hi

def dim_bounds(G: simple_undirected_graph, max_depth: int, depth: int=0) -> \
	tuple[int, int]:
	"""
	Returns bounds dim(G), where G is a simple undirected graph, and
	dim(G) = msr(G) + the number of isolated vertices. Equivalently, dim(G) is
	the minimum dimension of a faithful orthogonal representation of G such
	the zero vector is not assigned to any vertex.
	"""

	# log recursion depth
	logging.info('recursion depth: ' + str(depth))
	if depth > max_depth:
		msg = 'recursion depth limit reached'
		logging.error(msg)
		raise RecursionError(msg)

	# avoid corrupting G
	G = G.__copy__()

	"""
	EMPTY AND COMPLETE GRAPHS
	-------------------------
	dim(G) = n if G is empty
	dim(G) = 1 if G is complete
	"""

	n = G.num_verts
	if G.is_empty():
		logging.info(f'G is empty on {n} vertices')
		return n, n
	if G.is_complete():
		logging.info(f'G is complete on {n} vertices')
		return 1, 1

	"""
	DISCONNECTED GRAPHS
	-------------------
	dim(G) = sum(dim(H)) for H a component of G.

	If G is connected, we initialize the bounds to d_lo = 1 and d_hi = n - 1.
	"""

	# find bounds by summing bounds on components
	d_lo, d_hi = get_bounds_on_components(G, max_depth, depth)

	# if G is disconnected, this is the best estimate
	if not G.is_connected():
		return d_lo, d_hi

	# NOTE: no need to check if the bounds are equal here

	"""
	TREES AND CYCLES
	----------------
	Proceed by assuming
	* G is connected
	* is not empty
	* is not complete
	dim(G) = n - 1 if G is a tree
	dim(G) = n - 2 if G is a cycle
	"""

	# special cases of trees and cycles
	if G.is_a_tree():
		logging.info(f'G is a tree on {n} vertices')
		return n - 1, n - 1
	if G.is_a_cycle():
		logging.info(f'G is a cycle on {n} vertices')
		return n - 2, n - 2

	"""
	GRAPH REDUCTION
	---------------
	Reduce by eliminating
	* pendant vertices
	* subdivided edges
	* duplicate pairs (pairs of adjacent vertices with the same neighbors)
	* redundant vertices (vertices adjacent to all other vertices)
	The latter is the only reduction that can change the number of components.
	"""

	# reduce the graph and obtain bounds on the reduced graph
	G, d_lo, d_hi = reduce_and_bound_reduction(G, max_depth, depth)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'reducing graph'):
		return d_lo, d_hi

	"""
	CUT VERTICES
	------------
	A proper induced cover {G_1, ..., G_k} such that G_i and G_j intersect at a
	cut vertex v of G gives dim(G) = sum(dim(G_i))
	"""

	# check if G has a cut vertex and obtain bounds
	d_lo_cover, d_hi_cover = \
		  bounds_from_cut_vert_induced_cover(G, depth, max_depth)

	# update bounds
	d_lo = max(d_lo, d_lo_cover)
	d_hi = min(d_hi, d_hi_cover)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking for cut vertices'):
		return d_lo, d_hi

	"""
	INDUCED SUBGRAPHS (LOWER BOUND)
	-------------------------------
	Whenever H is an induced subgraph of G, dim(H) <= dim(G).
	"""

	# check all induced subgraphs to obtain a lower bound
	d_lo_subgraphs = lower_bound_induced_subgraphs(G, d_hi, max_depth,
						depth=depth + 1)

	# update lower bound
	d_lo = max(d_lo, d_lo_subgraphs)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking induced subgraphs'):
		return d_lo, d_hi

	"""
	CLIQUES AND PROPER INDUCED COVERS (UPPER BOUND)
	-----------------------------------------------
	Obtain a specific proper induced cover by identifying a clique.
	"""

	# obtain upper bound from cliques
	d_hi_clique = upper_bound_from_cliques(G, d_lo, depth, max_depth)

	# update upper bound
	d_hi = min(d_hi, d_hi_clique)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking clique upper bound'):
		return d_lo, d_hi

	"""
	EDGE ADDITION
	-------------
	Removing an edge can change the dimension by at most 1. Loop over all
	edges, adding each one and checking if the dimension bounds are improved.
	"""

	# check if adding an edge can improve the lower bound
	d_lo, d_hi = bounds_from_edge_addition(G, d_lo, d_hi, max_depth, depth)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking edge addition'):
		return d_lo, d_hi

	"""
	EDGE REMOVAL
	------------
	Adding an edge can change the dimension by at most 1. Loop over all edges,
	removing each one and checking if the dimension bounds are improved.
	"""

	# TODO: recursion depth maxes out if both edge removal and addition are
	# both enabled

	# NOTE: edge removal doesn't seem to be much use anyway, probably because
	# at this point most graphs will have a sharp lower bound, but removing an
	# edge typically does not decrease the dimension, so the upper bounds is
	# unlikely to be improved

	edge_removal_max_depth = 0

	if depth >= edge_removal_max_depth:
		logging.info('skipping edge removal')

	if depth < edge_removal_max_depth:

		# check if removing an edge can improve the lower bound
		d_lo, d_hi = bounds_from_edge_removal(G, d_lo, d_hi, max_depth, depth)

		# check if bounds are tight
		if check_bounds(d_lo, d_hi, 'checking edge removal'):
			return d_lo, d_hi

	"""
	SDP UPPER BOUND
	---------------
	Use semidefinite programming to obtain an upper bound. See the documentation
	in msr/msr_sdp.py for a summary. A derivation of the approach is given in
	doc/mth610-semidefprog-final-report-reynolds.pdf.
	"""

	logging.info('computing upper bound via	SDP')
	d_hi_sdp = msr_sdp_upper_bound(G)

	# report improvement on upper bound
	if d_hi_sdp < d_hi:
		logging.debug(f'SDP improved upper bound from {d_hi} to {d_hi_sdp}')
	else:
		logging.debug(f'upper bound not improved with SDP')

	# update upper bound
	d_hi = min(d_hi, d_hi_sdp)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking SDP upper bound'):
		return d_lo, d_hi

	"""
	TODO: INDUCED COVER UPPER BOUND
	-------------------------
	Search over proper induced covers to obtain an upper bound.
	NOTE: this is likely to lead to a combinatorial explosion.
	"""

	"""
	TODO: BCD LOWER BOUND
	---------------
	Find an independent set and apply bridge-correction decomposition to obtain
	a lower bound.
	"""

	"""
	EXIT WITHOUT TIGHT BOUNDS
	-------------------------
	"""
	logging.debug('dim_bounds() exited without obtaining tight bounds')
	return d_lo, d_hi

###############################################################################

def check_bounds(d_lo: int, d_hi: int, action_name: str='last action') -> bool:
	"""
	Checks that the bounds on dim(G) are tight.
	"""
	bounds_match = d_lo == d_hi
	if bounds_match:
		logging.info('bounds match after ' + action_name)
	if d_lo > d_hi:
		msg = 'lower bound exceeds upper bound after ' + action_name
		logging.error(msg)
		raise RuntimeError(msg)
	return bounds_match

def get_bounds_on_components(G: simple_undirected_graph, max_depth: int,
			     depth: int) -> tuple[int, int]:
	"""
	Computes bounds on dim(G) by summing bounds on components of G.
	"""

	# find components of G
	components = G.connected_components()

	# log if G is disconnected
	if G.is_connected():
		logging.info('G is connected')
	else:
		num_components = len(components)
		logging.info(f'G is disconnected with {num_components} components')

	# add bounds for each component when G is disconnected
	if not G.is_connected():
		d_lo = 0
		d_hi = 0
		for H in components:
			H_d_lo, H_d_hi = dim_bounds(H, max_depth, depth=depth + 1)
			d_lo += H_d_lo
			d_hi += H_d_hi
		return d_lo, d_hi
	else:
		return 1, G.num_verts - 1

def reduce_and_bound_reduction(G: simple_undirected_graph, max_depth: int,
			       depth: int) -> tuple[simple_undirected_graph, int, int]:
	"""
	Performs the reduction G |-> H and returns H and bounds on dim(H).
	"""
	G, d_diff, deletions = reduce(G)

	# if G was disconnected by the reduction, return bounds for each component
	if not G.is_connected():
		d_lo, d_hi = dim_bounds(G, max_depth, depth=depth + 1)
		d_lo += d_diff
		d_hi += d_diff
		return G, d_lo, d_hi

	# if reduction was nontrivial and G is still connected,
	# compute bounds on the reduced graph
	if deletions > 0:
		logging.debug('checking bounds of reduced graph')
		d_lo, d_hi = dim_bounds(G, max_depth, depth=depth + 1)
		d_lo += d_diff
		d_hi += d_diff
		return G, d_lo, d_hi

	# otherwise, we are dealing with a connected pre-reduced connected graph
	# TODO: prove that G connected and dim(G) = n - 1 implies G is a tree
	d_lo = 2 # G is not complete
	d_hi = G.num_verts - 2 # G is not a tree and has at least 4 vertices
	return G, d_lo, d_hi

def bounds_from_cut_vert_induced_cover(G: simple_undirected_graph,
				  depth: int, max_depth: int) -> tuple[int, int]:
	"""
	Checks if G has a cut vertex. If so, generate a proper induced cover
	{G_1, G_2} such that G_1 and G_2 intersect at exactly one vertex. Then it
	holds that dim(G) = dim(G_1) + dim(G_2).
	"""

	# find a cut vertex and associated induced cover of G
	cover = G.get_induced_cover_from_cut_vert()

	# determine if G has a cut vertex, if so return its index
	if len(cover) < 2:
		logging.debug('no cut vertices found')
		return 0, G.num_verts

	# in the event that a cut vertex is found
	logging.debug(f'cut vertex found, induced cover with size {len(cover)}')

	# determine dim(G_i) for each G_i in the cover, sum bounds
	d_lo_cover = 0
	d_hi_cover = 0
	for Gi in cover:
		d_lo_i, d_hi_i = dim_bounds(Gi, max_depth, depth=depth + 1)
		d_lo_cover += d_lo_i
		d_hi_cover += d_hi_i
	return d_lo_cover, d_hi_cover

def lower_bound_induced_subgraphs(G: simple_undirected_graph,
		  d_hi: int, max_depth: int, depth: int) -> int:
	"""
	Returns the maximum lower bound of the dimension of any induced subgraph.
	"""
	d_lo = 0
	n = G.num_verts
	for i in range(n):
		logging.debug(f'checking induced subgraph {i}')
		H = G.__copy__()
		H.remove_vert(i)
		d_lo_H = dim_bounds(H, max_depth, depth=depth + 1)[0]
		d_lo = max(d_lo, d_lo_H)
		if d_lo >= d_hi:
			return d_lo
	return d_lo

def upper_bound_from_cliques(G: simple_undirected_graph, d_lo: int,
			      depth: int, max_depth: int) -> int:
	"""
	Returns an upper bound on dim(G) by locating a vertex i that is part of a
	clique and obtaining a proper induced cover {K, H}, where K is the clique
	consisting of i and its neighborhood and H is the induced subgraph G - i.
	Assumes that G is connected and has already undergone reduction.
	"""
	d_hi_cliques = G.num_verts
	for i in range(G.num_verts):
		N = G.vert_neighbors(i)
		if all(G.is_edge(j, k) for j in N for k in N if j != k):
			H = G.__copy__()
			H.remove_vert(i)
			d_hi_H = dim_bounds(H, max_depth, depth=depth + 1)[1]
			d_hi_cliques = min(d_hi_cliques, d_hi_H + 1)
			if d_lo >= d_hi_cliques:
				return d_hi_cliques
	return d_hi_cliques

def bounds_from_edge_addition(G: simple_undirected_graph,
			      d_lo: int, d_hi: int,
				  max_depth: int, depth: int) -> tuple[int, int]:
	"""
	Computes bounds on dim(G) by adding edges.
	"""
	logging.info('checking bounds from edge addition')
	d_lo_edges = 0
	d_hi_edges = G.num_verts
	for i in range(G.num_verts):
		for j in range(i + 1, G.num_verts):
			if not G.is_edge(i, j):
				H = G.__copy__()
				H.add_edge(i, j)
				d_lo_H, d_hi_H = dim_bounds(H, max_depth, depth=depth + 1)
				d_lo_edges = max(d_lo_edges, d_lo_H)
				d_hi_edges = min(d_hi_edges, d_hi_H)
				d_lo = max(d_lo, d_lo_edges - 1)
				d_hi = min(d_hi, d_hi_edges + 1)
				if d_lo >= d_hi:
					return d_lo, d_hi
	return d_lo, d_hi

# likely to become deprecated
def bounds_from_edge_removal(G: simple_undirected_graph,
			     d_lo: int, d_hi: int,
				 max_depth: int, depth: int) -> tuple[int, int]:
	"""
	Computes bounds on dim(G) by removing edges.
	"""
	logging.info('checking bounds from edge removal')
	d_lo_edges = 0
	d_hi_edges = G.num_verts
	for e in G.edges:
		H = G.__copy__()
		i, j = e.endpoints
		H.remove_edge(i, j)
		if H.is_connected():
			d_lo_H, d_hi_H = dim_bounds(H, max_depth, depth=depth + 1)
			d_lo_edges = max(d_lo_edges, d_lo_H)
			d_hi_edges = min(d_hi_edges, d_hi_H)
			d_lo = max(d_lo, d_lo_edges - 1)
			d_hi = min(d_hi, d_hi_edges + 1)
			if d_lo >= d_hi:
				return d_lo, d_hi
	return d_lo, d_hi