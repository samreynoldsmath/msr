import matplotlib.pyplot as plt
from numpy import sin, cos, pi
from .simple_undirected_graph import simple_undirected_graph

def draw_simple_undirected_graph(G: simple_undirected_graph) -> None:
	"""
	Draw a planar embedding of the vector graph G.
	"""
	x, y = circular_embedding(G)
	for i in range(G.num_verts):
		plt.plot(x[i], y[i], 'ko')
		plt.text(x[i], y[i], i)
	for e in G.edges:
		i, j = e.endpoints
		plt.plot([x[i], x[j]], [y[i], y[j]], 'k-')
	plt.axis('off')
	plt.axis('equal')
	plt.show()

def circular_embedding(G: simple_undirected_graph) -> \
	tuple[list[float], list[float]]:
	"""
	Embeds G in the plane using a circular embedding.
	"""
	theta = 2 * pi / G.num_verts
	x = []
	y = []
	for i in range(G.num_verts):
		x.append(cos(i * theta))
		y.append(sin(i * theta))
	return x, y