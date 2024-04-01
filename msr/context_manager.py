"""
Module for context manager for computing bounds on msr(G).
"""

from __future__ import annotations

import logging
from copy import copy

from .log_config import LOG_PATH, configure_logging
from .strategy_config import STRATEGY, check_strategy


class GraphBoundsContextManager:
    """
    Context manager for computing bounds on msr(G). Contains
    - current lower bound d_lo
    - current upper bound d_hi
    - logger object
    - current recursion depth
    - max recursion depth
    - flags to load and save bounds from file
    """

    d_lo: int
    d_hi: int
    logger: logging.Logger
    depth: int
    max_depth: int
    load_bounds_flag: bool
    save_bounds_flag: bool
    exit_flag: bool

    def __init__(self, num_verts: int, graph_id, **kwargs) -> None:
        self.d_lo = 0
        self.d_hi = num_verts
        self.depth = kwargs.get("depth", 0)
        self.max_depth = kwargs.get("max_depth", 10 * num_verts)
        self.load_bounds_flag = kwargs.get("load_bounds", True)
        self.save_bounds_flag = kwargs.get("save_bounds", True)
        self.exit_flag = False
        self.logger = kwargs.get(
            "logger",
            configure_logging(
                log_path=kwargs.get("log_path", LOG_PATH),
                filename=kwargs.get("log_filename", f"{graph_id}.log"),
                level=kwargs.get("log_level", logging.ERROR),
            ),
        )

    def child_context(self, num_verts: int) -> GraphBoundsContextManager:
        """Create a child context."""
        child_context = copy(self)
        child_context.depth += 1
        child_context.d_lo = 0
        child_context.d_hi = num_verts
        return child_context

    def save_condition(self, d_lo_file: int, d_hi_file: int) -> bool:
        """Check if bounds should be saved."""
        return self.save_bounds_flag and (
            (self.d_lo > d_lo_file and self.d_hi <= d_hi_file)
            or (self.d_lo >= d_lo_file and self.d_hi < d_hi_file)
        )

    def start_new_log(self, graph_str: str) -> None:
        """Start new log file."""
        msg = f"computing bounds on msr(G) with G = {graph_str}"
        msg += "\nUsing strategy: "
        for k, strategy in enumerate(STRATEGY):
            msg += f"\n{k}{strategy.value}.\t"
        self.logger.info(msg)
        check_strategy(self.logger)

    def update_lower_bound(self, d_lo_new: int) -> None:
        """Update lower bound if new bound is larger."""
        self.d_lo = max(self.d_lo, d_lo_new)

    def update_upper_bound(self, d_hi_new: int) -> None:
        """Update upper bound if new bound is smaller."""
        self.d_hi = min(self.d_hi, d_hi_new)

    def update_bounds(self, d_lo_new: int, d_hi_new: int) -> None:
        """Update lower and upper bounds."""
        self.update_lower_bound(d_lo_new)
        self.update_upper_bound(d_hi_new)

    def exit_msg(self, description: str) -> str:
        """Returns an exit message."""
        msg = f"EXIT({self.depth}): {description} "
        msg += f"(bounds: {self.d_lo}, {self.d_hi})"
        return msg

    def log_exit(self, description: str, level: int = logging.INFO) -> None:
        """Log an exit message."""
        msg = self.exit_msg(description)
        self.logger.log(level, msg)
        self.exit_flag = True

    def log_good_exit(self, description: str) -> None:
        """Log a good exit message."""
        self.log_exit(description, logging.INFO)

    def log_bad_exit(self, description: str) -> None:
        """Log a bad exit message."""
        self.log_exit(description, logging.WARNING)

    def check_bounds(self, action_name: str) -> bool:
        """Check if bounds potentially match."""
        self.exit_flag = self.exit_flag or (self.d_lo >= self.d_hi)
        if self.d_lo == self.d_hi:
            self.log_good_exit(f"bounds match after {action_name}")
        if self.d_lo > self.d_hi:
            self.log_bad_exit(f"invalid bounds after {action_name}")
        return self.exit_flag

    def check_depth(self, num_verts: int) -> bool:
        """Check if recursion depth limit is reached."""
        self.logger.info(f"DEPTH({self.depth}), num_verts = {num_verts}")
        self.exit_flag = self.depth > self.max_depth
        if self.exit_flag:
            msg = "recursion self.depth limit reached, returning loose bounds"
            self.logger.warning(msg)
        return self.exit_flag
