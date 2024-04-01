"""
test_msr.py
===========

Test the MSR bounds on small graphs.
"""

import json
import logging
import os

import msr  # pylint: disable=import-error

TEST_PATH = os.path.dirname(__file__)


def test_msr_4_vert() -> None:
    """Test MSR bounds for all 4-vertex graphs."""
    _msr_small_helper(4, TEST_PATH)


def test_msr_5_vert() -> None:
    """Test MSR bounds for all 5-vertex graphs."""
    _msr_small_helper(5, TEST_PATH)


def test_msr_6_vert() -> None:
    """Test MSR bounds for all 6-vertex graphs."""
    _msr_small_helper(6, TEST_PATH)


def _msr_small_helper(n: int, test_dir: str) -> None:
    """Helper function for testing MSR bounds on small graphs."""
    json_filename = os.path.join(test_dir, f"soln/n{n}.json")
    with open(json_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        graphs = msr.graph.load_graphs_from_directory(num_verts=n)
        assert len(graphs) == len(data)
        for G in graphs:
            d_lo, d_hi = msr.msr_bounds(
                G,
                load_bounds=False,
                save_bounds=False,
                log_path=test_dir + "/log/",
                log_level=logging.INFO,
            )
            _assert_bounds_equal(G.hash_id(), d_lo, d_hi, data)


def _assert_bounds_equal(
    hash_id: str, d_lo: int, d_hi: int, data: dict
) -> None:
    """Assert that the MSR bounds match the expected values."""
    name = "k" + hash_id.split("k")[1]
    assert data[name] == d_lo
    assert data[name] == d_hi
