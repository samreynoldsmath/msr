from .simple_undirected_graph import simple_undirected_graph
import json

def load(filename: str) -> simple_undirected_graph:
	with open(filename, 'r') as f:
		data = json.load(f)
	G = simple_undirected_graph(data['num_verts'])
	for i, j in data['edges']:
		G.add_edge(i, j)
	if 'msr' in data:
		G.known_msr = data['msr']
	return G

def save(G: simple_undirected_graph, filename: str) -> None:
	data = {
		'num_verts': G.num_verts,
		'edges': [[i ,j] for i, j in G.edges]
	}
	custom_json_dump(data, filename)

def custom_json_dump(data, filename, indent=4):
	"""
	Custom JSON dump function that only expands the first level of lists.
	"""

	def format_list(lst, level):
		if len(lst) > 0 and isinstance(lst[0], list):
			return ',\n'.join(' ' * level + json.dumps(sub_list) for sub_list in lst)
		else:
			return ', '.join(json.dumps(item) for item in lst)

	with open(filename, 'w') as f:
		f.write('{\n')
		for key, value in data.items():
			if key == 'edges':
				f.write(f'    "{key}": [\n')
				f.write(format_list(value, indent + 4))
				f.write('\n    ]\n')
			else:
				f.write(f'    "{key}": {json.dumps(value)},\n')
		f.write('}\n')