import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import msr


def test_hash():
    n = 5
    n_choose_2 = n * (n - 1) // 2
    num_graphs = 2**n_choose_2
    for k in range(num_graphs):
        G = msr.graph.SimpleGraph(num_verts=n)
        G.build_from_hash(k)
        assert hash(G) == k
