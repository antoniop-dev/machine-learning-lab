"""Unit tests for the utils.common module."""

import json
from pathlib import Path

import pytest
from machineinnovatorsinc_solution.utils.common import (
    coerce_bool,
    read_json_config,
    select_config_section,
    validate_required_keys,
)


def test_coerce_bool():
    """Test boolean coercion handles various representations."""
    # True values
    assert coerce_bool(True) is True
    assert coerce_bool("true") is True
    assert coerce_bool("  TRUE  ") is True
    assert coerce_bool("yes") is True
    assert coerce_bool("1") is True
    assert coerce_bool("on") is True
    assert coerce_bool(1) is True

    # False values
    assert coerce_bool(False) is False
    assert coerce_bool("false") is False
    assert coerce_bool("NO") is False
    assert coerce_bool("0") is False
    assert coerce_bool("off") is False
    assert coerce_bool(0) is False
    assert coerce_bool("") is False


def test_read_json_config_valid(tmp_path: Path):
    """Test reading a valid JSON config file."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"key": "value", "num": 42}))

    data = read_json_config(config_file)
    assert data == {"key": "value", "num": 42}


def test_read_json_config_invalid_type(tmp_path: Path):
    """Test that a JSON list raises a ValueError (we expect a dict)."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(["not", "a", "dict"]))

    with pytest.raises(ValueError, match="must be a mapping"):
        read_json_config(config_file)


def test_select_config_section():
    """Test selecting a section from a raw config dictionary."""
    raw_cfg = {"api": {"port": 8000}, "other": "value"}
    source_path = Path("dummy.json")

    # Select existing section
    section = select_config_section(raw_cfg, expected_section="api", source_path=source_path)
    assert section == {"port": 8000}

    # Section missing -> returns raw config
    section_missing = select_config_section(
        raw_cfg, expected_section="missing", source_path=source_path
    )
    assert section_missing == raw_cfg


def test_validate_required_keys():
    """Test required keys validation."""
    cfg = {"a": 1, "b": 2}

    # Should pass silently
    validate_required_keys(
        cfg, required_keys=["a", "b"], source_path=Path("f.json"), expected_section="test"
    )

    # Missing keys should raise ValueError
    with pytest.raises(ValueError, match="missing required keys for 'test': \\['c', 'd'\\]"):
        validate_required_keys(
            cfg, required_keys=["a", "c", "d"], source_path=Path("f.json"), expected_section="test"
        )
