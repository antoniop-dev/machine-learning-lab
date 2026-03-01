"""Preprocessing utilities for text datasets."""

from __future__ import annotations

from typing import Any


def normalize_text(value: Any) -> str:
    """Apply conservative normalization suitable for tweets.

    Rules:
    - cast to string
    - trim leading/trailing whitespace
    - collapse repeated whitespace into single spaces
    """
    if value is None:
        return ""
    return " ".join(str(value).split())


def preprocess_dataset(
    dataset_dict: Any,
    *,
    text_field: str,
    label_field: str,
    batch_size: int = 1000,
) -> Any:
    """Normalize text and canonicalize columns to `text` / `labels`."""
    from datasets import DatasetDict  # Local import keeps module lightweight.

    if batch_size <= 0:
        raise ValueError("`batch_size` must be > 0.")

    processed_splits = {}
    for split_name in ("train", "validation", "test"):
        split = dataset_dict[split_name]

        def _normalize_batch(batch: dict[str, list[Any]]) -> dict[str, list[str]]:
            return {text_field: [normalize_text(value) for value in batch[text_field]]}

        split = split.map(
            _normalize_batch,
            batched=True,
            batch_size=batch_size,
            desc=f"Normalize text for split '{split_name}'",
        )

        if text_field != "text":
            if "text" in split.column_names:
                split = split.remove_columns("text")
            split = split.rename_column(text_field, "text")

        if label_field != "labels":
            if "labels" in split.column_names:
                split = split.remove_columns("labels")
            split = split.rename_column(label_field, "labels")

        processed_splits[split_name] = split

    return DatasetDict(processed_splits)
