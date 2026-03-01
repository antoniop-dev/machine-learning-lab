"""Small shared helpers used by multiple modules."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable


def read_json_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config at {path} must be a mapping (dict-like).")
    return data


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "y", "on"}:
            return True
        if lowered in {"0", "false", "no", "n", "off"}:
            return False
    return bool(value)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def select_config_section(
    raw_cfg: Dict[str, Any],
    *,
    expected_section: str,
    source_path: Path,
) -> Dict[str, Any]:
    """Return expected config section if present, otherwise return root config."""
    if expected_section in raw_cfg:
        section = raw_cfg[expected_section]
        if not isinstance(section, dict):
            raise ValueError(
                f"Config at {source_path} has '{expected_section}' but it is not an object."
            )
        return section
    return raw_cfg


def validate_required_keys(
    cfg: Dict[str, Any],
    *,
    required_keys: Iterable[str],
    source_path: Path,
    expected_section: str,
) -> None:
    missing = sorted(key for key in required_keys if key not in cfg)
    if missing:
        raise ValueError(
            f"Config at {source_path} is missing required keys for '{expected_section}': {missing}"
        )
