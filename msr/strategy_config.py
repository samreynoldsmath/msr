"""
Module for configuring the strategy for computing bounds on msr(G).
"""

import logging
from enum import Enum


# Enumeration of strategies for computing bounds on msr(G)
class BoundsStrategy(Enum):
    BCD_LOWER = "bcd-lower"
    BCD_LOWER_EXHAUSTIVE = "bcd-lower-exhaustive"
    BCD_UPPER = "bcd-upper"
    CUT_VERT = "cut-vert"
    CLIQUE_UPPER = "clique-upper"
    EDGE_ADDITION = "edge-add"
    EDGE_REMOVAL = "edge-rem"
    INDUCED_SUBGRAPH = "ind-subgraph"
    SDP_UPPER = "sdp-upper"
    SDP_SIGNED_EXHAUSTIVE = "sdp-signed-exhaustive"
    SDP_SIGNED_SIMPLE = "sdp-signed-simple"
    SDP_SIGNED_CYCLE = "sdp-signed-cycle"


# configure strategy
STRATEGY: list[BoundsStrategy] = [
    BoundsStrategy.CUT_VERT,
    BoundsStrategy.INDUCED_SUBGRAPH,
    BoundsStrategy.CLIQUE_UPPER,
    BoundsStrategy.SDP_UPPER,
    BoundsStrategy.EDGE_ADDITION,
    BoundsStrategy.BCD_LOWER_EXHAUSTIVE,
    BoundsStrategy.SDP_SIGNED_CYCLE,
    BoundsStrategy.BCD_UPPER,
]


def check_strategy(logger: logging.Logger) -> None:
    """Check that the strategy is valid."""
    if (
        BoundsStrategy.EDGE_ADDITION in STRATEGY
        and BoundsStrategy.EDGE_REMOVAL in STRATEGY
    ):
        msg = "cannot use edge addition and edge removal simultaneously"
        logger.error(msg)
        raise ValueError(msg)
