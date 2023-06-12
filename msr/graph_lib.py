from .graph import graph
from .vert6 import six_verts

def empty(num_vert: int) -> graph:
	return graph(num_vert, [])

def complete(num_vert: int) -> graph:
	edges = []
	for i in range(1, num_vert + 1):
		for j in range(i + 1, num_vert + 1):
			edges.append([i, j])
	return graph(num_vert, edges)

def path(num_vert: int) -> graph:
	edges = []
	for i in range(1, num_vert):
		edges.append([i, i + 1])
	return graph(num_vert, edges)

def cycle(num_vert: int) -> graph:
	G = path(num_vert)
	G.add_edge([1, num_vert])
	return G

def wheel(num_vert: int) -> graph:
	G = cycle(num_vert - 1)
	G.set_num_vert(num_vert)
	for i in range(1, num_vert):
		G.add_edge([i, num_vert])
	return G

def star(num_vert: int) -> graph:
	G = graph(num_vert, [])
	for i in range(1, num_vert):
		G.add_edge([i, num_vert])
	return G

def house() -> graph:
	G = cycle(num_vert=5)
	G.add_edge([2, 5])
	return G

def triforce() -> graph:
	G, _ = six_verts(idx=42)
	return G
