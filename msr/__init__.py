"""MSR

This package contains tools for computing bounds on the minimum semidefinite
rank (MSR) of a graph, including combinatorial techniques and semidefinite
programming (SDP) techniques. The `graph` subpackage contains the representation
of simple undirected graphs.
"""

from . import graph
from .msr_batch import msr_batch, msr_batch_from_directory
from .msr_bounds import msr_bounds
from .msr_sdp import msr_sdp_upper_bound

__all__ = [
    "graph",
    "msr_batch",
    "msr_batch_from_directory",
    "msr_bounds",
    "msr_sdp_upper_bound",
]
