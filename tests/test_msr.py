import sys
import os
import json
import logging

TEST_PATH = os.path.dirname(__file__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import msr


def test_msr_4_vert() -> None:
    _msr_small_helper(4, TEST_PATH)


def test_msr_5_vert() -> None:
    _msr_small_helper(5, TEST_PATH)


def test_msr_6_vert() -> None:
    _msr_small_helper(6, TEST_PATH)


def _msr_small_helper(n: int, test_dir: str) -> None:
    json_filename = os.path.join(test_dir, f"soln/n{n}.json")
    data = json.load(open(json_filename, "r"))
    graphs = msr.graph.load_graphs_from_directory(num_verts=n)
    assert len(graphs) == len(data)
    for G in graphs:
        id = G.id()
        d_lo, d_hi = msr.msr_bounds(
            G,
            load_bounds=False,
            save_bounds=False,
            log_path=test_dir + "/log/",
            log_level=logging.INFO,
        )
        _assert_bounds_equal(id, d_lo, d_hi, data)


def _assert_bounds_equal(id: str, d_lo: int, d_hi: int, data: dict) -> None:
    name = "k" + id.split("k")[1]
    assert data[name] == d_lo
    assert data[name] == d_hi
