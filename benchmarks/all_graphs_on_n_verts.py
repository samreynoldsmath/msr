import os
import sys

import tqdm

current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

import msr


def main(n: int):
    """
    Benchmark the implementation of msr_bounds() by computing bounds on all
    connected graphs on n vertices (up to isomorphism). A report on how
    accurate the bounds are is generated. A rough estimate of efficiency is
    obtained with timing the execution with timeit.
    """

    # directory where graphs are saved
    graph_dir = f"../msr/graph/saved/n{n}"

    # compute bounds on all graphs
    bounds_and_names = msr.msr_batch_from_directory(path=graph_dir)

    # find troublemakers
    not_tight = 0
    names = []
    for b in bounds_and_names:
        d_lo, d_hi, name = b
        if d_lo != d_hi:
            not_tight += 1
            names.append(name)
            print(f"{name[len(graph_dir)+1:]}: \t{d_lo}, {d_hi}")

    # number of graphs in test set
    num_graphs = len(bounds_and_names)

    # final report
    if not_tight == 0:
        print("all bounds were tight")
    else:
        print(
            f"{not_tight} out of {num_graphs} graphs"
            + " had bounds that were not tight"
        )

    # save figures of troublemakers
    if len(names) > 0:
        print("saving figures...")
        for name in tqdm.tqdm(names):
            graph_file = name + ".json"
            image_file = f"figs/n{n}" + name[len(graph_dir) :] + ".png"
            msr.graph.draw_graph(
                G=msr.graph.load_graph(graph_file),
                embedding="min_entropy",
                filename=image_file,
                labels=True,
            )


def num_graphs_on_n_verts(n: int):
    """
    OEIS A001349: Number of connected graphs with n nodes.
    """
    if n > 20:
        raise ValueError("n must be <= 20")
    a = [
        1,
        1,
        1,
        2,
        6,
        21,
        112,
        853,
        11117,
        261080,
        11716571,
        1006700565,
        164059830476,
        50335907869219,
        29003487462848061,
        31397381142761241960,
        63969560113225176176277,
        245871831682084026519528568,
        1787331725248899088890200576580,
        24636021429399867655322650759681644,
    ]
    return a[n]


if __name__ == "__main__":
    main(n=int(sys.argv[1]))
