"""Unit tests for dataset preprocessing and validation modules."""

import pytest
from datasets import Dataset

from machineinnovatorsinc_solution.data.preprocess import normalize_text, preprocess_dataset
from machineinnovatorsinc_solution.data.validate import (
    validate_non_empty_text,
    validate_schema,
    validate_splits,
)


def test_normalize_text():
    """Test text normalization rules."""
    assert normalize_text(None) == ""
    assert normalize_text("  hello   world  \n ") == "hello world"
    assert normalize_text(123) == "123"
    assert normalize_text("") == ""


def test_preprocess_dataset():
    """Test dataset text normalization and column canonicalization."""
    from datasets import DatasetDict

    dummy_ds = DatasetDict(
        {
            "train": Dataset.from_dict({"raw_text": ["  a   ", "b"], "target": [1, 0]}),
            "validation": Dataset.from_dict({"raw_text": ["c\nd"], "target": [2]}),
            "test": Dataset.from_dict({"raw_text": ["e"], "target": [1]}),
        }
    )

    processed = preprocess_dataset(
        dummy_ds, text_field="raw_text", label_field="target", batch_size=2
    )

    assert "train" in processed
    assert processed["train"].column_names == ["text", "labels"]
    assert processed["train"]["text"] == ["a", "b"]
    assert processed["train"]["labels"] == [1, 0]
    assert processed["validation"]["text"] == ["c d"]


def test_validate_splits():
    """Test checking for required dataset splits."""
    dummy_ds = {"train": [], "validation": []}

    # Should pass
    validate_splits(dummy_ds, ["train", "validation"])

    # Should fail due to missing "test"
    with pytest.raises(ValueError, match="Missing required splits: \\['test'\\]"):
        validate_splits(dummy_ds, ["train", "validation", "test"])


def test_validate_schema():
    """Test validating presence of text and label columns."""
    dummy_split = Dataset.from_dict({"text": ["a"], "labels": [1]})

    # Should pass
    validate_schema(dummy_split, text_field="text", label_field="labels", split_name="train")

    # Should fail due to missing columns
    with pytest.raises(ValueError, match="missing required columns \\['raw_text', 'target'\\]"):
        validate_schema(
            dummy_split, text_field="raw_text", label_field="target", split_name="train"
        )


def test_validate_non_empty_text():
    """Test identifying empty text records in a dataset split."""
    # Valid split
    valid_split = Dataset.from_dict({"text": ["hello", "world"]})
    validate_non_empty_text(
        valid_split, text_field="text", split_name="train", full_scan=True
    )

    # Invalid split with an empty string
    invalid_split = Dataset.from_dict({"text": ["hello", "   "]})
    with pytest.raises(ValueError, match="has 1 empty `text` values"):
        validate_non_empty_text(
            invalid_split, text_field="text", split_name="train", full_scan=True
        )

    # Empty dataset
    empty_split = Dataset.from_dict({"text": []})
    with pytest.raises(ValueError, match="is empty"):
        validate_non_empty_text(
            empty_split, text_field="text", split_name="train", full_scan=True
        )
