import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import msr


def test_msr_small():
    for n in [4, 5, 6]:
        helper(n)


def helper(n):
    test_dir = os.path.dirname(__file__)
    json_path = os.path.join(test_dir, f"../msr/soln/n{n}.json")
    graph_dir = os.path.join(test_dir, f"../msr/graph/saved/n{n}/")

    d = json.load(open(json_path, "r"))
    bounds_and_names = msr.msr_batch_from_directory(graph_dir, quiet=True)

    for d_lo, d_hi, name in bounds_and_names:
        assert d[name] == d_lo
        assert d[name] == d_hi
