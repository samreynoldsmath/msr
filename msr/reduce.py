import logging
from .graph.simple_undirected_graph import simple_undirected_graph

def reduce(G: simple_undirected_graph) -> \
		tuple[simple_undirected_graph, int, int]:
	"""
	Attempts to reduce the number of vertices in the graph by
	* removing pendants
	* contracting subdivisions
	* removing redundant vertices (vertices adjacent to every other vertex)
	* removing duplicate pairs (adjacent vertices with the same neighbors)
	The reduction loop halts when either no	updates are made or the graph
	becomes disconnected.

	Returns
	* the reduced graph
	* the change in dimension
	* and the number of	vertices removed
	"""

	if not G.is_connected():
		msg = 'reduction loop assumes G is connected'
		logging.error(msg)
		raise Exception(msg)

	logging.info('performing reduction')

	updated = True # track whether any updates were made in the last iteration
	d_diff = 0 # track change in dimension
	deletions = 0 # track number of deletions

	# main reduction loop: continue until no updates are made
	while updated:

		# remove pendants
		# NOTE: this is a cheap operation
		# NOTE: deleting a pendant reduces dimension by 1
		G, updated, local_deletions = remove_pendants(G)
		deletions += local_deletions
		d_diff += local_deletions

		# remove subdivisions
		# NOTE: contracting an edge reduces dimension by 1
		if not updated:
			G, updated, local_deletions = remove_subdivisions(G)
			deletions += local_deletions
			d_diff += local_deletions

		# remove redundant vertices
		# NOTE: dimension does not change
		# NOTE: requires connectivity check
		# NOTE: premature termination if G becomes disconnected
		if not updated:
			G, updated, local_deletions = remove_redundant_verts(G)
			deletions += local_deletions
		if not G.is_connected():
			reduction_report(deletions, d_diff, updated, G.num_verts,
		      G.is_connected())
			return G, d_diff, deletions

		# remove duplicate pairs
		# NOTE: dimension does not change
		# NOTE: quadratic cost in number of vertices
		if not updated:
			G, updated, local_deletions = remove_duplicate_pairs(G)
			deletions += local_deletions

	# report on the reduction and return
	reduction_report(deletions, d_diff, updated, G.num_verts, G.is_connected())
	return G, d_diff, deletions

def reduction_report(deletions: int, d_diff: int,
		     updated: bool, n: int, is_connected: bool) -> None:
	if not is_connected:
		logging.debug('reduction halted: graph disconnected')
	elif not updated:
		logging.debug('reduction stagnated')
	elif n < 3:
		logging.debug('reduction completed')
	else:
		logging.warning('reduction stopped for reasons unknown')
	v = 'vertices' if deletions != 1 else 'vertex'
	logging.info(
		f'reduction removed {deletions} {v}' +
		f', reduced dimension by {d_diff}'
	)

def remove_pendants(G: simple_undirected_graph, verbose: bool=False) -> \
	tuple[simple_undirected_graph, bool, int]:
	"""
	Removes all pendant vertices.
	"""
	logging.debug('removing pendants')
	updated = False
	local_deletions = 0
	i = G.num_verts
	while i > 0 and G.num_verts > 2:
		i -= 1
		# to avoid index errors, apply only one test per iteration
		if G.vert_is_pendant(i) and G.num_verts > 2:
			G.remove_vert(i, still_connected=True)
			updated = True
			local_deletions += 1
	if verbose and local_deletions > 0:
		plural = 's' if local_deletions != 1 else ''
		logging.debug(f'removed {local_deletions} pendant {plural}')
	return G, updated, local_deletions

def remove_subdivisions(G: simple_undirected_graph, verbose: bool=False) -> \
	tuple[simple_undirected_graph, bool, int]:
	"""
	Removes all subdivisions.
	"""
	logging.debug('removing subdivisions')
	updated = False
	local_deletions = 0
	i = G.num_verts
	while i > 0 and G.num_verts > 2:
		i -= 1
		if G.vert_is_subdivided(i) and G.num_verts > 2:
			j, k = G.vert_neighbors(i)
			G.add_edge(j, k) # important to add edge before removing vert
			G.remove_vert(i, still_connected=True)
			updated = True
			local_deletions += 1
	if verbose and local_deletions > 0:
		plural = 's' if local_deletions != 1 else ''
		logging.debug(f'removed {local_deletions} subdivision {plural}')
	return G, updated, local_deletions

def remove_redundant_verts(G: simple_undirected_graph, verbose: bool=False) -> \
	tuple[simple_undirected_graph, bool, int]:
	"""
	Removes all vertices adjacent to every other vertex.

	If the graph becomes disconnected, the reduction is halted.
	"""
	logging.debug('removing redundant vertices')
	updated = False
	local_deletions = 0
	i = G.num_verts
	while i > 0 and G.num_verts > 2:
		i -= 1
		if G.vert_is_redundant(i) and G.num_verts > 2:
			G.remove_vert(i, still_connected=None)
			updated = True
			local_deletions += 1
			# if G has become disconnected, stop reducing
			if not G.is_connected():
				if verbose:
					v = 'vertices' if local_deletions != 1 else 'vertex'
					logging.debug(f'removed {local_deletions} redundant {v}')
				return G, updated, local_deletions
	if verbose and local_deletions > 0:
		v = 'vertices' if local_deletions != 1 else 'vertex'
		logging.debug(f'removed {local_deletions} redundant {v}')
	return G, updated, local_deletions

def remove_duplicate_pairs(G: simple_undirected_graph, verbose: bool=False) -> \
	tuple[simple_undirected_graph, bool, int]:
	"""
	Removes all pairs of adjacent vertices with the same neighbors.
	"""
	logging.debug('removing duplicate pairs')
	updated = False
	deletions = 0
	i = G.num_verts
	# triangular loop over vertices in reverse order
	while i > 0 and G.num_verts > 2:
		i -= 1
		j = i
		while j > 0 and G.num_verts > 2:
			j -= 1
			if G.verts_are_duplicate_pair(i, j):
				G.remove_vert(j, still_connected=True)
				updated = True
				deletions += 1
	if verbose and deletions > 0:
		v = 'vertices' if deletions != 1 else 'vertex'
		logging.debug(f'removed {deletions} duplicate {v}')
	return G, updated, deletions