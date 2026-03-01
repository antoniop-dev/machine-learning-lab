"""Validation utilities for dataset integrity checks."""

from __future__ import annotations

import random
from typing import Any, Sequence


def _column_names(split: Any) -> list[str]:
    names = getattr(split, "column_names", None)
    if names is not None:
        return list(names)

    features = getattr(split, "features", None)
    if features is not None:
        try:
            return list(features.keys())
        except Exception as exc:  # pragma: no cover
            raise TypeError("Unable to infer split columns from dataset features.") from exc

    raise TypeError("Dataset split must expose `column_names` or `features`.")


def validate_splits(dataset_dict: Any, required_splits: Sequence[str]) -> None:
    """Ensure all required splits exist in a DatasetDict-like object."""
    if not hasattr(dataset_dict, "keys"):
        raise TypeError("Expected a DatasetDict-like object exposing `.keys()`.")

    available = set(dataset_dict.keys())
    missing = [split for split in required_splits if split not in available]
    if missing:
        raise ValueError(
            f"Missing required splits: {missing}. Available splits: {sorted(available)}"
        )


def validate_schema(
    split: Any,
    *,
    text_field: str,
    label_field: str,
    split_name: str,
) -> None:
    """Validate that text/label columns exist in a split."""
    cols = _column_names(split)
    missing: list[str] = []
    if text_field not in cols:
        missing.append(text_field)
    if label_field not in cols:
        missing.append(label_field)

    if missing:
        raise ValueError(
            f"Split '{split_name}' is missing required columns {missing}. "
            f"Available columns: {cols}"
        )


def _is_empty_text(value: Any) -> bool:
    return value is None or not str(value).strip()


def validate_non_empty_text(
    split: Any,
    *,
    text_field: str,
    split_name: str,
    sample_size: int = 1024,
    seed: int = 42,
    full_scan: bool = False,
) -> None:
    """Validate that text field is non-empty after trimming.

    By default this performs a sample-based check for speed. Set `full_scan=True`
    to validate all rows.
    """
    if len(split) == 0:
        raise ValueError(f"Split '{split_name}' is empty.")

    if sample_size <= 0:
        raise ValueError("`sample_size` must be > 0.")

    n_rows = len(split)
    if full_scan or sample_size >= n_rows:
        indices = list(range(n_rows))
        mode = "full_scan"
    else:
        rng = random.Random(seed)
        indices = sorted(rng.sample(range(n_rows), k=sample_size))
        mode = "sampled"

    empty_indices: list[int] = []
    for idx in indices:
        value = split[idx][text_field]
        if _is_empty_text(value):
            empty_indices.append(idx)

    if empty_indices:
        sample = empty_indices[:10]
        raise ValueError(
            f"Split '{split_name}' has {len(empty_indices)} empty `{text_field}` values "
            f"detected in {mode} ({len(indices)} rows checked). "
            f"Example indices: {sample}"
        )
