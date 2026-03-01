"""Reusable runner for script entrypoints."""

from __future__ import annotations

import importlib
import sys
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(entrypoint: str) -> None:
    """Run `package.module:function` after adding `src/` to sys.path."""
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root / "src"))

    print(f"[START {_utc_now()}] Running {entrypoint}", flush=True)
    try:
        module_name, func_name = entrypoint.split(":", maxsplit=1)
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        func()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        status = "DONE" if code == 0 else "FAILED"
        print(f"[{status} {_utc_now()}] Finished {entrypoint} (exit_code={code})", flush=True)
        raise
    except Exception as exc:
        print(f"[ERROR {_utc_now()}] {exc.__class__.__name__}: {exc}", flush=True)
        print(f"[FAILED {_utc_now()}] Finished {entrypoint} (exit_code=1)", flush=True)
        raise SystemExit(1) from None
    else:
        print(f"[DONE {_utc_now()}] Finished {entrypoint}", flush=True)
