import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import msr


def test_msr_small() -> None:
    test_dir = os.path.dirname(__file__)
    for n in [4, 5, 6]:
        _msr_small_helper(n, test_dir)


def _msr_small_helper(n: int, test_dir: str) -> None:
    json_filename = os.path.join(test_dir, f"soln/n{n}.json")
    data = json.load(open(json_filename, "r"))
    graphs = msr.graph.load_graphs_from_directory(num_verts=n)
    assert len(graphs) == len(data)
    for G in graphs:
        id = G.id()
        d_lo, d_hi = msr.msr_bounds(G, load_flag=False, save_flag=False)
        _assert_bounds_equal(id, d_lo, d_hi, data)


def _assert_bounds_equal(id: str, d_lo: int, d_hi: int, data: dict) -> None:
    name = "k" + id.split("k")[1]
    assert data[name] == d_lo
    assert data[name] == d_hi
