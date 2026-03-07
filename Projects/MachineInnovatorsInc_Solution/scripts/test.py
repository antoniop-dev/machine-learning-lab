#!/usr/bin/env python
"""Run the project's unit test suite.

Usage
-----
    python scripts/test.py [pytest_args...]

Examples
--------
    python scripts/test.py
    python scripts/test.py tests/test_api.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the src layout is importable when running directly from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest


def main() -> None:
    # Pass all CLI args through to pytest, defaulting to "tests/" if none provided
    args = sys.argv[1:] if len(sys.argv) > 1 else ["tests/"]
    sys.exit(pytest.main(args))


if __name__ == "__main__":
    main()
