"""Unit tests for the synthetic startup traffic generator."""

from collections import Counter

import pytest

from machineinnovatorsinc_solution.api.traffic_seed import (
    _allocate_label_counts,
    build_request_texts,
)


def test_allocate_label_counts_sums_to_requested_total():
    """Allocated label counts should sum to the requested total."""
    allocated = _allocate_label_counts(250)

    assert sum(allocated.values()) == 250
    assert allocated == Counter({"positive": 113, "negative": 75, "neutral": 62})


def test_allocate_label_counts_rejects_non_positive_values():
    """Count must be a positive integer."""
    with pytest.raises(ValueError, match="count must be > 0"):
        _allocate_label_counts(0)


def test_build_request_texts_is_deterministic():
    """Synthetic requests should be reproducible for a fixed seed."""
    first = build_request_texts(12, seed=7)
    second = build_request_texts(12, seed=7)

    assert first == second
    assert len(first) == 12
    assert {label for label, _ in first} == {"positive", "neutral", "negative"}


def test_build_request_texts_contains_requested_count():
    """Generated request list should match the requested total size."""
    generated = build_request_texts(25, seed=99)

    assert len(generated) == 25
    counts = Counter(label for label, _ in generated)
    assert counts["positive"] > 0
    assert counts["neutral"] > 0
    assert counts["negative"] > 0
