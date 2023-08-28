import os
import sys

current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

import msr


def main(n: int):
    path = f"../msr/graph/saved/n{n}"
    msr.graph.generate_and_save_all_graphs_on_n_vertices(n, path)


if __name__ == "__main__":
    n = int(sys.argv[1])
    main(n)
