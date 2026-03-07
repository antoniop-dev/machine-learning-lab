#!/usr/bin/env python
"""Launch the sentiment inference API server.

Usage
-----
    python scripts/serve.py [--host HOST] [--port PORT] [--reload] [--config CONFIG]

Defaults
--------
* host:   0.0.0.0
* port:   8000
* config: configs/api.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the src layout is importable when running directly from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import uvicorn


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Start the MachineInnovatorsInc sentiment API.")
    p.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    p.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    p.add_argument(
        "--reload",
        action="store_true",
        help="Enable hot-reload (development only; incompatible with --factory).",
    )
    p.add_argument(
        "--config",
        default="configs/api.json",
        help="Path to the API JSON config (default: configs/api.json).",
    )
    p.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Uvicorn log level (default: info).",
    )
    return p


def main() -> None:
    args = _build_argparser().parse_args()

    import os
    # Pass config path to the factory via env var so uvicorn's --factory mode
    # can pick it up without needing a custom import string.
    os.environ.setdefault("API_CONFIG_PATH", args.config)

    uvicorn.run(
        "machineinnovatorsinc_solution.api.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
