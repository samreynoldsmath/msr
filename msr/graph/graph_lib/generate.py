import networkx as nx
import os
import tqdm
from ..simple_undirected_graph import simple_undirected_graph
from ..file_io import save_graph
from ..convert import convert_native_to_networkx, convert_networkx_to_native

# TODO: use multiprocessing?

def generate_all_graphs_on_n_vertices(n: int, path: str) -> \
	  list[simple_undirected_graph]:
	"""
	Generates all graphs on n vertices
	:param n: number of vertices
	:return: list of graphs
	"""
	nx_graphs: list[nx.Graph] = []
	n_choose_2 = n * (n - 1) // 2

	print(f'Generating all graphs on {n} vertices...')

	# hash each graph as an integer k, such that k written in binary represents
	# the edges of the graph, with zero being a non-edge, and one being an edge.
	for k in tqdm.tqdm(range(2 ** n_choose_2)):

		# convert k to binary, and pad with zeros to the left
		binary = bin(k)[2:].zfill(n_choose_2)

		# convert binary to a list of edges in a graph G
		G = simple_undirected_graph(num_verts=n)
		for i in range(n - 1):
			for j in range(i + 1, n):
				ij = j - 1 + (i * (2 * n - 3 - i)) // 2
				if binary[ij] == '1':
					G.add_edge(i, j)

		# determine if G is connected
		if G.is_connected():

			G_nx = convert_native_to_networkx(G)

			# test if G is isomorphic to a graph already in the list
			isomorphic = False
			for H_nx in nx_graphs:
				if nx.is_isomorphic(G_nx, H_nx):
					isomorphic = True
					break
			if not isomorphic:
				# TODO: relative path
				G_nx.filename = f'{path}/k{k}.json'
				nx_graphs.append(G_nx)

	# create directory if none exists
	if not os.path.exists(path):
		os.makedirs(path)

	# save all graphs
	print(f'Number of graphs on {n} vertices: {len(nx_graphs)}')
	for G_nx in tqdm.tqdm(nx_graphs):
		filename = G_nx.filename
		G = convert_networkx_to_native(G_nx)
		save_graph(G, filename)