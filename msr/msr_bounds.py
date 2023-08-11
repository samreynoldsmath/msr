import logging
from .graph.simple_undirected_graph import simple_undirected_graph
from .msr_sdp import msr_sdp_upper_bound
from .reduce import reduce

# configure logging
logging.basicConfig(
	filename='msr_bounds.log',
	filemode='w',
	encoding='utf-8',
	level=logging.DEBUG,
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
	dim(G) = n for G empty
	dim(G) = 1 for G complete
	"""

	n = G.num_verts
	if G.is_empty():
		logging.info('G is empty')
		return n, n
	if G.is_complete():
		logging.info('G is complete')
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

	"""
	TREES AND CYCLES
	----------------
	Proceed by assuming
	* G is connected
	* is not empty
	* is not complete
	dim(G) = n - 1 for G a tree
	dim(G) = n - 2 for G a cycle
	"""

	# special cases of trees and cycles
	if G.is_a_tree():
		logging.info('G is a tree')
		return n - 1, n - 1
	if G.is_a_cycle():
		logging.info('G is a cycle')
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
	G, d_lo, d_hi = reduce_and_bound_reduction(G, max_depth, depth)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'reducing graph'):
		return d_lo, d_hi

	"""
	INDUCED SUBGRAPH LOWER BOUND
	----------------------------
	Whenever H is an induced subgraph of G, dim(H) <= dim(G).
	"""

	# check all induced subgraphs to obtain a lower bound
	d_lo_subgraphs = lower_bound_induced_subgraphs(G, d_hi, max_depth,
						depth=depth + 1)
	d_lo = max(d_lo, d_lo_subgraphs)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking induced subgraphs'):
		return d_lo, d_hi

	"""
	EDGE ADDITION
	-------------
	Removing an edge can change the dimension by at most 1. Loop over all
	edges, adding each one and checking if the dimension bounds are improved.
	"""

	# check if adding an edge can improve the lower bound
	d_lo_edges, d_hi_edges = bounds_from_edge_addition(G, d_lo, d_hi,
						    max_depth, depth)
	d_lo = max(d_lo, d_lo_edges - 1)
	d_hi = min(d_hi, d_hi_edges + 1)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking edge addition'):
		return d_lo, d_hi

	"""
	EDGE REMOVAL
	------------
	Adding an edge can change the dimension by at most 1. Loop over all edges,
	removing each one and checking if the dimension bounds are improved.
	"""

	# TODO: recursion depth maxs out if both edge removal and addition are enabled

	logging.info('skipping edge removal')

	if depth < 0:

		# check if removing an edge can improve the lower bound
		d_lo_edges, d_hi_edges = bounds_from_edge_removal(G, d_lo, d_hi,
						    max_depth, depth)
		d_lo = max(d_lo, d_lo_edges - 1)
		d_hi = min(d_hi, d_hi_edges + 1)

		# check if bounds are tight
		if check_bounds(d_lo, d_hi, 'checking edge removal'):
			return d_lo, d_hi

	"""
	SDP UPPER BOUND
	---------------
	Use semidefinite progamming to obtain an upper bound. See the documentation
	in msr/msr_sdp.py for a summary. A derivation of the approach is given in
	doc/mth610-semidefprog-final-report-reynolds.pdf.
	"""
	d_hi_sdp = msr_sdp_upper_bound(G)
	d_hi = min(d_hi, d_hi_sdp)

	# check if bounds are tight
	if check_bounds(d_lo, d_hi, 'checking SDP upper bound'):
		return d_lo, d_hi

	### INDUCED COVER UPPER BOUND #############################################
	# TODO: find proper induced covers to obtain an upper bound
	# NOTE: it seems difficult to do this without a combinatorial explosion

	### BRIDGE-CORRECTION DECOMPOSITION #######################################
	# TODO: apply bridge-correction decomposition to refine bounds
	# NOTE: also a risk of combinatorial explosion

	# unable to find sharp bounds
	logging.info('dim_bounds() exited without obtaining sharp bounds')
	return d_lo, d_hi

def check_bounds(d_lo: int, d_hi: int, action_name: str='') -> bool:
	"""
	Checks that the bounds on the minimum dimension of the given graph are
	tight.
	"""
	bounds_match = d_lo == d_hi
	if bounds_match:
		logging.debug('bounds match after ' + action_name)
	if d_lo > d_hi:
		msg = 'lower bound exceeds upper bound after ' + action_name
		logging.error(msg)
		raise RuntimeError(msg)
	return bounds_match

def get_bounds_on_components(G: simple_undirected_graph, max_depth: int,
			     depth: int) -> tuple[int, int]:
	"""
	Computes bounds on the minimum dimension of each component of the given
	graph.
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
			       depth: int) -> \
	tuple[simple_undirected_graph, int, int]:
	"""
	Reduces the given graph and computes bounds on the reduced graph.

	Returns the reduced graph, the lower bound, and the upper bound.
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
	# in this case, we are dealing with a prereduced connected graph
	else:
		d_lo = 1
		d_hi = G.num_verts - 1

	return G, d_lo, d_hi

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

def bounds_from_edge_removal(G: simple_undirected_graph,
			     d_lo: int, d_hi: int,
				 max_depth: int, depth: int) -> tuple[int, int]:
	"""
	Computes bounds on the minimum dimension of the given graph by removing
	edges.
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
			if d_lo_edges >= d_hi and d_lo >= d_hi_edges:
				return d_lo_edges, d_hi_edges
	return d_lo_edges, d_hi_edges

def bounds_from_edge_addition(G: simple_undirected_graph,
			      d_lo: int, d_hi: int,
				  max_depth: int, depth: int) -> tuple[int, int]:
	"""
	Computes bounds on the minimum dimension of the given graph by adding
	edges.
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
				if d_lo_edges >= d_hi and d_lo >= d_hi_edges:
					return d_lo_edges, d_hi_edges
	return d_lo_edges, d_hi_edges