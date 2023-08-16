import matplotlib.pyplot as plt
from numpy import ndarray, zeros, sin, cos, pi
from numpy.random import random
import os
from .simple_undirected_graph import simple_undirected_graph

def draw_simple_undirected_graph(G: simple_undirected_graph,
				 embedding: str='circular', labels=False,
				 filename: str='') -> None:
	"""
	Draw a planar embedding of the vector graph G.
	"""

	# embed the graph
	x, y = embed(G, embedding)

	# draw the vertices
	for i in range(G.num_verts):
		plt.plot(x[i], y[i], 'ko')
		if labels:
			plt.text(x[i], y[i], i)

	# draw the edges
	for e in G.edges:
		i, j = e.endpoints
		plt.plot([x[i], x[j]], [y[i], y[j]], 'k-')

	# draw the graph
	plt.axis('off')
	plt.axis('equal')
	if len(filename) > 0:
		# create directory if none exists
		path = os.path.dirname(filename)
		if not os.path.exists(path):
			os.makedirs(path)
		plt.savefig(filename)
		plt.clf()
	else:
		plt.show()

def embed(G: simple_undirected_graph, embedding: str) -> \
	  tuple[ndarray, ndarray]:
	"""Embeds G in the plane using a specified embedding."""
	if embedding == 'circular':
		return circular_embedding(G)
	if embedding == 'random':
		return random_embedding(G)
	elif embedding == 'min_entropy':
		return rubber_electric_embedding(G)
	raise ValueError(f'Invalid embedding type "{embedding}"')

def circular_embedding(G: simple_undirected_graph) -> tuple[ndarray, ndarray]:
	"""
	Embeds G in the plane using a circular embedding.
	"""
	n = G.num_verts
	theta = 2 * pi / n
	x = zeros((n,))
	y = zeros((n,))
	for i in range(G.num_verts):
		x[i] = cos(i * theta)
		y[i] = sin(i * theta)
	return x, y

def random_embedding(G: simple_undirected_graph) -> tuple[ndarray, ndarray]:
	"""
	Embeds G in the plane using a random embedding.
	"""
	n = G.num_verts
	x = 2 * random((n,)) - 1
	y = 2 * random((n,)) - 1
	return x, y

def rubber_electric_embedding(G: simple_undirected_graph) -> \
	  tuple[ndarray, ndarray]:
	"""
	Returns an embedding of G in the plane that minimizes the entropy of the
	edge lengths, which are imagined to be rubber bands, and a repulsive force
	between vertices that is proportional to the inverse square of the distance,
	which is imagined to be an electric force.
	"""
	L = G.laplacian()

	tol = 1e-4
	max_iter = int(1e6)
	h = 0.005

	electric_constant = 3.0
	spring_constant = 1.0
	friction_constant = 0.02

	friction_growth_rate = 1 + 0.1 / (h * max_iter)

	x, y = random_embedding(G)

	n = G.num_verts

	dx = zeros((n,))
	dy = zeros((n,))

	ddx = zeros((n,))
	ddy = zeros((n,))

	for iter in range(max_iter):

		# update acceleration
		ddx, ddy = coulomb_repulsive_force(x, y)

		ddx *= electric_constant
		ddy *= electric_constant

		ddx -= spring_constant * L @ x
		ddy -= spring_constant * L @ y

		# update friction
		friction_constant *= friction_growth_rate

		ddx -= friction_constant * dx
		ddy -= friction_constant * dy

		# check for convergence
		if sum(ddx ** 2 + ddy ** 2) < tol:
			break

		# update position
		x += h * dx
		y += h * dy

		# update velocity
		dx += h * ddx
		dy += h * ddy

	# center the embedding at the origin
	x -= sum(x) / n
	y -= sum(y) / n

	return x, y

def coulomb_repulsive_force(x: ndarray, y: ndarray) -> tuple[ndarray, ndarray]:
	n = len(x)
	force_x = zeros((n, ))
	force_y = zeros((n, ))
	for i in range(n):
		for j in range(n):
			xx = x[i] - x[j]
			yy = y[i] - y[j]
			r3 = (xx ** 2 + yy ** 2) ** 1.5
			r3 = max(1, r3) # avoid division by zero
			force_x[i] += xx / r3
			force_y[i] += yy / r3
	return force_x, force_y