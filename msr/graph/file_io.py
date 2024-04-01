"""
Module for loading and saving graphs to disk.
"""

import json
import os

from .graph import SimpleGraph

SAVED_GRAPH_DIR = os.path.dirname(__file__) + "/saved/"


def files_in_directory(path: str, num_verts=0) -> list[str]:
    """Returns all filenames in a directory."""
    filenames = []
    abspath = os.path.abspath(path)
    directory = os.fsencode(abspath)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if num_verts > 0 and not filename.startswith(f"n{num_verts}"):
            continue
        if filename.endswith(".graph"):
            abs_filename = os.path.join(abspath, filename)
            filenames.append(abs_filename)
    return filenames


def load_graph(filename: str) -> SimpleGraph:
    """Load a graph from a json file."""

    # load graph data from json file
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # create graph object
    G = SimpleGraph(data["num_verts"])

    # add edges
    for i, j in data["edges"]:
        G.add_edge(i, j)

    return G


def load_graphs_from_directory(
    path: str = SAVED_GRAPH_DIR, num_verts=0
) -> list[SimpleGraph]:
    """Load all graphs from a directory."""
    filenames = files_in_directory(path, num_verts)
    graphs = []
    for filename in filenames:
        if filename.endswith(".graph"):
            graphs.append(load_graph(filename))
    return graphs


def save_graph(G: SimpleGraph, filename: str = "") -> None:
    """Save a graph to a json file."""
    if len(filename) == 0:
        filename = SAVED_GRAPH_DIR + f"{G.hash_id()}.graph"
    edges = []
    for e in G.edges:
        i, j = e.endpoints
        edges.append([i, j])
    data = {
        "num_verts": G.num_verts,
        "edges": edges,
    }
    _custom_json_dump(data, filename)


def save_graphs(graphs: list[SimpleGraph], path: str = SAVED_GRAPH_DIR) -> None:
    """Saves graphs to disk."""

    # create directory if none exists
    if not os.path.exists(path):
        os.makedirs(path)

    # save graphs
    for G in graphs:
        filename = path + f"{G.hash_id()}.graph"
        save_graph(G, filename)


def _custom_json_dump(data, filename, indent=4):
    """Custom JSON dump function that expands the first level of lists."""

    def format_list(lst, level):
        if len(lst) > 0 and isinstance(lst[0], list):
            return ",\n".join(
                " " * level + json.dumps(sub_list) for sub_list in lst
            )
        return ", ".join(json.dumps(item) for item in lst)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("{\n")
        for key, value in data.items():
            if key == "edges":
                f.write(f'    "{key}": [\n')
                f.write(format_list(value, indent + 4))
                f.write("\n    ]\n")
            else:
                f.write(f'    "{key}": {json.dumps(value)},\n')
        f.write("}\n")
