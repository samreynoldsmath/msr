"""
test_graph.py
=============

Tests for the graph module.
"""

import msr  # pylint: disable=import-error


def test_hash():
    """Test that the hash function is correct."""
    n = 5
    n_choose_2 = n * (n - 1) // 2
    num_graphs = 2**n_choose_2
    for k in range(num_graphs):
        G = msr.graph.SimpleGraph(num_verts=n)
        G.build_from_hash(k)
        assert hash(G) == k
