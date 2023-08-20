from numpy import ndarray, zeros

class undirected_edge:
	"""An undirected edge between two vertices."""

	endpoints: set[int]

	def __init__(self, i: int, j: int) -> None:
		self.set_endpoints(i, j)

	def __str__(self) -> str:
		return str(self.endpoints)

	def __eq__(self, other) -> bool:
		return self.endpoints == other.endpoints

	def __hash__(self) -> int:
		i, j = self.endpoints
		return hash((i, j))

	def set_endpoints(self, i: int, j: int) -> None:
		"""Sets the endpoints of the edge to the given vertices."""
		if not isinstance(i, int) or not isinstance(j, int):
			raise TypeError('Endpoints must be integers.')
		if i < 0 or j < 0:
			raise ValueError('Endpoints cannot be negative.')
		if i == j:
			raise ValueError('Loops are not allowed.')
		self.endpoints = {i, j}

class simple_undirected_graph:
	"""An simple undirected graph."""

	num_verts: int
	edges: set[undirected_edge]
	name: str
	_is_connected_flag: bool

	def __init__(self, num_verts: int) -> None:
		self.set_num_verts(num_verts)
		self.edges = set()
		self._is_connected_flag = None

	def __str__(self) -> str:
		s = f'Vertex count: {self.num_verts}'
		s += '\nNumber of edges: ' + str(self.num_edges())
		s += '\nEdges:'
		for e in self.edges:
			s += '\n' + str(e)
		return s

	def __copy__(self):
		G = simple_undirected_graph(self.num_verts)
		G.edges = self.edges.copy()
		return G

	def __hash__(self):
		n = self.num_verts
		n_choose_2 = n * (n - 1) // 2
		binary = '0' * n_choose_2
		for i in range(n- 1):
			for j in range(i + 1, n):
				if self.is_edge(i, j):
					ij = j - 1 + (i * (2 * n - 3 - i)) // 2
					binary = binary[:ij] + '1' + binary[ij + 1:]
		return int(binary, 2)

	### VERTICES ##############################################################

	def set_num_verts(self, num_verts: int) -> None:
		if num_verts < 1:
			raise ValueError('Must have a positive number of vertices')
		self.num_verts = num_verts

	def remove_vert(self, i: int, still_connected: bool=None) -> None:
		"""Removes the given vertex from the graph."""
		if self.num_verts < 2:
			raise ValueError('Cannot remove a vertex from a graph with fewer'
		    	+ ' than two vertices.')
		if i < 0 or i >= self.num_verts:
			raise ValueError('Vertex index out of bounds.')
		# remove edges incident to i
		for j in range(self.num_verts):
			if self.is_edge(i, j):
				self.remove_edge(i, j)
		# shift vertices after i down by one
		for j in range(i + 1, self.num_verts):
			for k in range(self.num_verts):
				if self.is_edge(j, k):
					self.remove_edge(j, k)
					self.add_edge(j - 1, k)
		self.num_verts -= 1
		self._is_connected_flag = still_connected

	def vert_neighbors(self, i: int) -> set[int]:
		"""Returns the set of neighbors of the given vertex."""
		if i < 0 or i >= self.num_verts:
			raise ValueError('Vertex index out of bounds.')
		return set([j for j in range(self.num_verts) if self.is_edge(i, j)])

	def vert_deg(self, i: int) -> int:
		"""Returns the degree of the given vertex."""
		return len(self.vert_neighbors(i))

	def num_isolated_verts(self) -> int:
		"""Returns the number of isolated vertices in the graph."""
		return len([i for i in range(self.num_verts) if self.vert_deg(i) == 0])

	def clique_containing_vert(self, i: int) -> bool:
		"""Returns a maximal clique containing the vertex i."""
		raise NotImplementedError()
		# N = self.vert_neighbors(i)
		# for j in N:
		# 	for k in N:
		# 		if j != k:
		# 			print(j, k, self.is_edge(j, k))
		# 			if not self.is_edge(j, k):
		# 				return False
		# return True

	def permute_verts(self, perm: list[int]) -> None:
		""""
		Returns a graph with vertices permuted according to the given list.
		"""
		if not set(perm) == set(range(self.num_verts)):
			raise ValueError('Permutation list must be a permutation of the'
				+ ' vertices.')
		H = simple_undirected_graph(self.num_verts)
		for e in self.edges:
			i, j = e.endpoints
			H.add_edge(perm[i], perm[j])
		return H

	### VERTEX TESTS ##########################################################

	def vert_is_pendant(self, i: int) -> bool:
		"""Returns True if the given vertex is a pendant vertex."""
		return self.vert_deg(i) == 1

	def vert_is_subdivided(self, i: int) -> bool:
		"""Returns True if the given vertex is subdivided."""
		if self.vert_deg(i) != 2:
			return False
		j, k = self.vert_neighbors(i)
		return not self.is_edge(j, k)

	def vert_is_redundant(self, i: int) -> bool:
		"""
		Returns True if the given vertex is adjacent to every other vertex.
		"""
		return self.vert_deg(i) == self.num_verts - 1

	def verts_are_duplicate_pair(self, i: int, j: int) -> bool:
		"""Returns True if i,j are adjacent and have the same neighbors."""
		if not self.is_edge(i, j):
			return False
		Ni = self.vert_neighbors(i)
		Ni.remove(j)
		Nj = self.vert_neighbors(j)
		Nj.remove(i)
		return Ni == Nj

	def vert_is_cut_vert(self, i: int) -> bool:
		"""Returns True if the given vertex is a cut vertex."""
		if self.num_verts < 3:
			return False
		if self.vert_deg(i) < 2:
			return False
		G = self.__copy__()
		G.remove_vert(i)
		return not G.is_connected()

	def get_a_cut_vert(self) -> int | None:
		"""
		Returns the index of a cut vertex in the graph, or None if there are
		no cut vertices.
		"""
		for i in range(self.num_verts):
			if self.vert_is_cut_vert(i):
				return i
		return None

	def get_cut_verts(self) -> set[int]:
		"""Returns the set of cut vertices in the graph."""
		# TODO: Tarjan's algorithm is more efficient
		return set(
			[i for i in range(self.num_verts) if self.vert_is_cut_vert(i)]
			)

	def maximal_independent_set(self) -> set[int]:
		"""
		DEPRECATED: networkx has a better implementation of this function.

		Returns a maximal independent set of vertices in the graph, using a
		greedy algorithm based on vertex degree.
		"""

		indep_set = set()
		candidates = set(range(self.num_verts))

		while len(candidates) > 0:

			# pick a candidate vertex of minimum degree
			i = min(candidates, key=self.vert_deg)

			# add i to the independent set
			indep_set.add(i)

			# remove i and its neighbors from the set of candidates
			candidates.remove(i)
			N = self.vert_neighbors(i)
			for j in N:
				candidates.discard(j)

		return indep_set

	### EDGES #################################################################

	def num_edges(self) -> int:
		return len(self.edges)

	def add_edge(self, i: int, j: int) -> None:
		if i > self.num_verts or j > self.num_verts:
			raise ValueError('Vertex index out of bounds.')
		self.edges.add(undirected_edge(i, j))
		self._is_connected_flag = None

	def remove_edge(self, i: int, j: int) -> None:
		self.edges.discard(undirected_edge(i, j))
		self._is_connected_flag = None

	def is_edge(self, i: int, j: int) -> bool:
		if i == j:
			return False
		return undirected_edge(i, j) in self.edges

	### COMPONENTS ############################################################

	def connected_components(self) -> list[object]:
		"""
		Returns a list of simple_undirected_graph objects, where each object is
		a connected component of the graph.
		"""
		component_vert_idx = self.connected_components_vert_idx()
		components = []
		for verts in component_vert_idx:
			num_verts = len(verts)
			verts_list = list(verts)
			H = simple_undirected_graph(num_verts)
			for i in range(num_verts):
				for j in range(i + 1, num_verts):
					if self.is_edge(verts_list[i], verts_list[j]):
						H.add_edge(i, j)
			H._is_connected_flag = True
			components.append(H)
		return components

	def connected_components_vert_idx(self) -> list[set[int]]:
		"""
		Returns a list of set of vertex indices, where each set of vertex
		indices is a connected component of the graph.
		"""
		component_index_list = []
		visited = set()
		for i in range(self.num_verts):
			if not (i in visited):
				this_component_idx_set = self.bfs(i)
				visited = visited.union(this_component_idx_set)
				component_index_list.append(this_component_idx_set)
		self._is_connected_flag = len(component_index_list) == 1
		return component_index_list

	def bfs(self, i: int) -> set[int]:
		"""
		Returns the set of vertices reachable from the given vertex by a
		breadth-first search.
		"""
		if i < 0 or i >= self.num_verts:
			raise ValueError('Vertex index out of bounds.')
		reachable = set([i,])
		frontier = set([i,])
		while len(frontier) > 0:
			new_frontier = set()
			for j in frontier:
				for k in self.vert_neighbors(j):
					if not k in reachable:
						reachable.add(k)
						new_frontier.add(k)
			frontier = new_frontier
		return reachable

	### INDUCED COVERS ########################################################

	def get_induced_cover_from_cut_vert(self) -> list[object]:
		"""
		Returns a list of induced subgraphs, where any two distinct subgraphs
		intersect at a single vertex (which is necessarily a cut vertex).
		"""
		cut_vert_idx = self.get_a_cut_vert()
		if cut_vert_idx is None:
			return [self,]

		# construct a proper induced cover
		H = self.__copy__()
		H.remove_vert(cut_vert_idx)
		component_vert_idx = H.connected_components_vert_idx()
		cover = []
		for verts in component_vert_idx:
			num_verts = len(verts)
			verts_list = list(verts)
			verts_list.append(cut_vert_idx)
			H = simple_undirected_graph(num_verts)
			for i in range(num_verts):
				for j in range(i + 1, num_verts):
					if self.is_edge(verts_list[i], verts_list[j]):
						H.add_edge(i, j)
			H._is_connected_flag = True
			cover.append(H)
		return cover

	### GRAPH TESTS ###########################################################

	def is_connected(self) -> bool:
		"""Returns True if the graph is connected."""
		if self.num_verts == 1:
			return True
		if self._is_connected_flag is None:
			self.connected_components_vert_idx()
		return self._is_connected_flag

	def is_empty(self) -> bool:
		"""Returns True if the graph has no edges."""
		return self.num_edges() == 0

	def is_complete(self) -> bool:
		"""Returns True if every vertex is adjacent to every other vertex."""
		return self.num_edges() == self.num_verts * (self.num_verts - 1) // 2

	def is_a_tree(self) -> bool:
		"""Returns True if the graph is connected and has no cycles."""
		if not self.is_connected():
			return False
		return self.num_edges() == self.num_verts - 1

	def is_k_regular(self, k: int) -> bool:
		"""Returns True if every vertex has degree k."""
		return all(self.vert_deg(i) == k for i in range(self.num_verts))

	def is_a_cycle(self) -> bool:
		"""Returns True if the graph is a cycle."""
		if not self.is_connected():
			return False
		return self.is_k_regular(2)

	### MATRIX REPRESENTATIONS ################################################

	def laplacian(self) -> ndarray:
		"""Returns the graph Laplacian matrix."""
		n = self.num_verts
		L = zeros((n, n))
		for e in self.edges:
			i, j = e.endpoints
			L[i, j] -= 1
			L[j, i] -= 1
			L[i, i] += 1
			L[j, j] += 1
		return L
