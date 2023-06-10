"""
	Simple undirected graph
"""

from numpy import zeros

class graph:

	num_vert: 	int
	edges: 		list[list[int]]

	def __init__(self, num_vert: int, edges: list[list[int]]) -> None:
		self.set_num_vert(num_vert)
		self.edges = []
		self.add_edges(edges)

	def set_num_vert(self, num_vert: int) -> None:
		if type(num_vert) is not int:
			raise TypeError('Number of vertices must be an integer')
		if num_vert < 1:
			raise ValueError('Graph must have positive number of vertices')
		self.num_vert = num_vert

	def add_edges(self, edges: list[list[int]]) -> None:
		for edge in edges:
			self.add_edge(edge)

	def add_edge(self, edge: list[int]) -> None:
		if self.is_valid_edge(edge) and not self.is_edge(edge):
			self.edges.append(edge)

	def is_same_edge(self, edge1: list[int], edge2: list[int]):
		return (edge1[0] == edge2[0] and edge1[1] == edge2[1]) \
			or (edge1[1] == edge2[0] and edge1[0] == edge2[1])

	def is_edge(self, edge: list[int]) -> bool:
		k = self.get_edge_index(edge)
		return k > 0

	def get_edge_index(self, edge: list[int]) -> int:
		if self.is_valid_edge(edge):
			for k in range(len(self.edges)):
				if self.is_same_edge(self.edges[k], edge):
					return k
		return -1

	def is_valid_edge(self, edge: list[int]) -> bool:
		if len(edge) != 2:
			raise Exception('Edge must be a pair of distinct vertices')
		for i in range(2):
			if not isinstance(edge[i], int):
				raise TypeError('Endpoints must be integers')
			if edge[i] < 1 or edge[i] > self.num_vert:
				raise ValueError('Endpoints must be between 1 and num_vert')
		if edge[0] == edge[1]:
			raise Exception('Endpoints must be distinct')
		return True

	def remove_edge(self, edge: list[int]) -> None:
		k = self.get_edge_index(edge)
		if k > 0:
			del self.edges[k]

	def remove_edges(self, edges: list[list[int]]) -> None:
		for edge in edges:
			self.remove_edge(edge)

	def adjacency_matrix(self):
		A = zeros((self.num_vert, self.num_vert), dtype=int)
		for edge in self.edges:
			A[edge[0] - 1, edge[1] - 1] = 1
			A[edge[1] - 1, edge[0] - 1] = 1
		return A

	def __repr__(self) -> str:
		msg = f'Graph on {self.num_vert} vertices with edges\n'
		for edge in self.edges:
			msg += f'{edge}\n'
		return msg