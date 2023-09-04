import json
import os

from .graph import graph


def load_graph(filename: str) -> graph:
    """Load a graph from a json file."""

    # load graph data from json file
    with open(filename, "r") as f:
        data = json.load(f)

    # create graph object
    G = graph(data["num_verts"])

    # add edges
    for i, j in data["edges"]:
        G.add_edge(i, j)

    return G


def files_in_directory(path: str) -> list[str]:
    """Returns all filenames in a directory."""
    filenames = []
    abspath = os.path.abspath(path)
    directory = os.fsencode(abspath)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        abs_filename = os.path.join(abspath, filename)
        filenames.append(abs_filename)
    return filenames


def load_graphs_from_directory(path: str) -> list[graph]:
    """Load all graphs from a directory."""
    filenames = files_in_directory(path)
    graphs = []
    for filename in filenames:
        if filename.endswith(".json"):
            graphs.append(load_graph(filename))
    return graphs


def save_graph(G: graph, filename: str) -> None:
    """Save a graph to a json file."""
    edges = []
    for e in G.edges:
        i, j = e.endpoints
        edges.append([i, j])
    data = {
        "num_verts": G.num_verts,
        "edges": edges,
    }
    _custom_json_dump(data, filename)


def _custom_json_dump(data, filename, indent=4):
    """Custom JSON dump function that expands the first level of lists."""

    def format_list(lst, level):
        if len(lst) > 0 and isinstance(lst[0], list):
            return ",\n".join(
                " " * level + json.dumps(sub_list) for sub_list in lst
            )
        else:
            return ", ".join(json.dumps(item) for item in lst)

    with open(filename, "w") as f:
        f.write("{\n")
        for key, value in data.items():
            if key == "edges":
                f.write(f'    "{key}": [\n')
                f.write(format_list(value, indent + 4))
                f.write("\n    ]\n")
            else:
                f.write(f'    "{key}": {json.dumps(value)},\n')
        f.write("}\n")
