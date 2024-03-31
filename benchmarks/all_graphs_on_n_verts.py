import os
import sys

from tqdm import tqdm

current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

import msr

SAVE_FIGS = True
FIG_DIR = f"figs/"
QUIET = False


def main(n: int):
    """
    Benchmark the implementation of msr_bounds() by computing bounds on all
    connected graphs on n vertices (up to isomorphism). A report on how
    accurate the bounds are is generated.
    """

    # compute bounds on all graphs
    bounds_and_hash_ids = msr.msr_batch_from_directory(quiet=QUIET, num_verts=n)

    # find troublemakers
    not_tight = 0
    hash_ids = []
    for d_lo, d_hi, hash_id in bounds_and_hash_ids:
        if d_lo != d_hi:
            not_tight += 1
            hash_ids.append(hash_id)
            print(f"{hash_id}: {d_lo}, {d_hi}")

    # number of graphs in test set
    num_graphs = len(bounds_and_hash_ids)

    # final report
    if not_tight == 0:
        print("all bounds were tight")
    else:
        print(
            f"{not_tight} out of {num_graphs} graphs"
            + " had bounds that were not tight"
        )

    # save figures of troublemakers
    if SAVE_FIGS and len(hash_ids) > 0:
        print("saving figures...")
        for hash_id in tqdm(hash_ids):
            graph_file = msr.graph.SAVED_GRAPH_DIR + f"{hash_id}.graph"
            image_file = FIG_DIR + f"{hash_id}.png"
            msr.graph.draw_graph(
                G=msr.graph.load_graph(graph_file),
                embedding="min_entropy",
                filename=image_file,
                labels=True,
            )


if __name__ == "__main__":
    main(n=int(sys.argv[1]))
