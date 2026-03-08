#!/usr/bin/env python
"""CLI wrapper for the synthetic startup traffic generator."""

from __future__ import annotations

from _runner import run


if __name__ == "__main__":
    run("machineinnovatorsinc_solution.api.traffic_seed:main")
