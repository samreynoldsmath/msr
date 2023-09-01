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
    graph_dir = f"../msr/graph/saved/n{n}/"

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
            print(f"{name}: {d_lo}, {d_hi}")

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
    fig_dir = f"figs/n{n}/"
    if len(names) > 0:
        print("saving figures...")
        for name in tqdm.tqdm(names):
            graph_file = graph_dir + name + ".json"
            image_file = fig_dir + name + ".png"
            msr.graph.draw_graph(
                G=msr.graph.load_graph(graph_file),
                embedding="min_entropy",
                filename=image_file,
                labels=True,
            )


if __name__ == "__main__":
    main(n=int(sys.argv[1]))
