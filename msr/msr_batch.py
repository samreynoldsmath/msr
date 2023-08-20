import multiprocessing
import tqdm
from .graph.simple_undirected_graph import simple_undirected_graph
from .graph.file_io import load_graphs_from_directory
from .msr_bounds import msr_bounds

def msr_batch_from_directory(path: str) -> list[tuple[int, int, str]]:
	"""
	Computes the MSR bounds for a batch of graphs in a directory with multiprocessing.

	Parameters
	----------
	directory : str
		The directory to load the graphs from.

	Returns
	-------
	list[tuple[int, int, str]]
		For each graph, the MSR bounds and the name/id of the graph.
	"""
	graphs = load_graphs_from_directory(path)
	return msr_batch(graphs)

def msr_batch(graphs: list[simple_undirected_graph]) -> \
	  list[tuple[int, int, str]]:
	"""
	Computes the MSR bounds for a batch of graphs with multiprocessing.

	Parameters
	----------
	graphs : list[simple_undirected_graph]
		The graphs to compute the MSR bounds for.

	Returns
	-------
	list[tuple[int, int, str]]
		For each graph, the MSR bounds and the name/id of the graph.
	"""
	with multiprocessing.Pool() as pool:
		return list(tqdm.tqdm(
			pool.imap_unordered(_msr_bounds_with_id, graphs),
			total=len(graphs)
			))

def _msr_bounds_with_id(graph: simple_undirected_graph) -> tuple[int, int, str]:
	d_lo, d_hi = msr_bounds(graph)
	return d_lo, d_hi, graph.name