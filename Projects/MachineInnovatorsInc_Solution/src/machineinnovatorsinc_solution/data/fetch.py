"""Data fetching utilities (single responsibility: retrieval + raw persistence)."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.common import (
    now_iso,
    read_json_config,
    select_config_section,
    validate_required_keys,
)
from .validate import validate_splits

REQUIRED_DATA_CONFIG_KEYS = {
    "dataset_name",
    "text_field",
    "label_field",
    "split_train",
    "split_val",
    "split_test",
    "data_dir",
    "seed",
    "sample_size",
    "batch_size",
}


@dataclass(frozen=True)
class DataConfig:
    dataset_name: str = "tweet_eval"
    dataset_subset: Optional[str] = "sentiment"
    text_field: str = "text"
    label_field: str = "label"

    # Output roots
    data_dir: Path = Path("data")

    # Dev knobs
    max_samples: Optional[int] = None
    seed: int = 42
    sample_size: int = 1024
    batch_size: int = 1000

    # Optional: allow overriding splits in case dataset changes
    split_train: str = "train"
    split_val: str = "validation"
    split_test: str = "test"

    # HuggingFace Hub integration: when set, upload processed dataset after pipeline
    hf_dataset_repo_id: Optional[str] = None


def _coerce_positive_int(value: Any, *, field_name: str) -> int:
    out = int(value)
    if out <= 0:
        raise ValueError(f"`{field_name}` must be > 0.")
    return out


def load_config(path: Optional[str], *, cli_overrides: Dict[str, Any]) -> DataConfig:
    cfg: Dict[str, Any] = {}
    if path:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
        raw_cfg = read_json_config(p)
        cfg = select_config_section(raw_cfg, expected_section="data", source_path=p)
        validate_required_keys(
            cfg,
            required_keys=REQUIRED_DATA_CONFIG_KEYS,
            source_path=p,
            expected_section="data",
        )

    # Merge JSON + CLI overrides (CLI wins)
    merged = {**cfg, **{k: v for k, v in cli_overrides.items() if v is not None}}

    # Paths
    data_dir = Path(merged.get("data_dir", "data"))

    dataset_subset = merged.get("dataset_subset", "sentiment")
    if dataset_subset in ("", None):
        dataset_subset = None

    max_samples = merged.get("max_samples", None)
    if max_samples is not None:
        max_samples = int(max_samples)
        if max_samples < 0:
            raise ValueError("`max_samples` must be >= 0.")

    return DataConfig(
        dataset_name=str(merged.get("dataset_name", "tweet_eval")),
        dataset_subset=dataset_subset,
        text_field=str(merged.get("text_field", "text")),
        label_field=str(merged.get("label_field", "label")),
        data_dir=data_dir,
        max_samples=max_samples,
        seed=int(merged.get("seed", 42)),
        sample_size=_coerce_positive_int(merged.get("sample_size", 1024), field_name="sample_size"),
        batch_size=_coerce_positive_int(merged.get("batch_size", 1000), field_name="batch_size"),
        split_train=str(merged.get("split_train", "train")),
        split_val=str(merged.get("split_val", "validation")),
        split_test=str(merged.get("split_test", "test")),
        hf_dataset_repo_id=merged.get("hf_dataset_repo_id", None) or None,
    )


def _require_datasets() -> None:
    try:
        import datasets  # noqa: F401
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency 'datasets'. Install with: pip install datasets"
        ) from e


def _stable_config_fingerprint(cfg: DataConfig) -> str:
    payload = {
        "dataset_name": cfg.dataset_name,
        "dataset_subset": cfg.dataset_subset,
        "text_field": cfg.text_field,
        "label_field": cfg.label_field,
        "max_samples": cfg.max_samples,
        "seed": cfg.seed,
        "sample_size": cfg.sample_size,
        "batch_size": cfg.batch_size,
        "split_train": cfg.split_train,
        "split_val": cfg.split_val,
        "split_test": cfg.split_test,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _maybe_subsample(ds_split: Any, max_samples: Optional[int], seed: int) -> Any:
    if max_samples is None:
        return ds_split
    if max_samples == 0:
        return ds_split.select([])
    n = len(ds_split)
    if max_samples >= n:
        return ds_split
    # deterministic shuffle + select
    return ds_split.shuffle(seed=seed).select(range(max_samples))


def save_dataset_dict_with_split_logging(
    dataset_dict: Any,
    output_dir: Path,
    *,
    stage_label: str,
) -> None:
    """Persist a DatasetDict in native HF format with explicit split logging."""
    if output_dir.exists():
        print(f"♻ Overwriting existing {stage_label} dataset at {output_dir.as_posix()}")
        shutil.rmtree(output_dir)
    _ensure_dir(output_dir.parent)

    split_names = list(dataset_dict.keys())
    for split_name in split_names:
        print(
            f"💾 Saving {stage_label} split '{split_name}' "
            f"({len(dataset_dict[split_name])} rows)"
        )
    dataset_dict.save_to_disk(str(output_dir))


def dataset_slug(cfg: DataConfig) -> str:
    suffix = f"_{cfg.dataset_subset}" if cfg.dataset_subset else ""
    return f"{cfg.dataset_name}{suffix}"


def fetch_dataset(cfg: DataConfig) -> Any:
    """Fetch dataset and normalize split keys to train/validation/test."""
    _require_datasets()
    from datasets import DatasetDict, load_dataset  # type: ignore

    subset = cfg.dataset_subset if cfg.dataset_subset is not None else "<none>"
    print(
        f"⬇ Fetching dataset from HF: name='{cfg.dataset_name}', subset='{subset}'",
        flush=True,
    )
    if cfg.dataset_subset:
        ds: DatasetDict = load_dataset(cfg.dataset_name, cfg.dataset_subset)
    else:
        ds = load_dataset(cfg.dataset_name)

    # Validate before split indexing to fail with a clear message.
    validate_splits(ds, required_splits=[cfg.split_train, cfg.split_val, cfg.split_test])

    train = _maybe_subsample(ds[cfg.split_train], cfg.max_samples, cfg.seed)
    val = _maybe_subsample(ds[cfg.split_val], cfg.max_samples, cfg.seed)
    test = _maybe_subsample(ds[cfg.split_test], cfg.max_samples, cfg.seed)
    return DatasetDict({"train": train, "validation": val, "test": test})


def save_raw_dataset(raw_ds: Any, cfg: DataConfig) -> Dict[str, Any]:
    """Persist fetched data into `data/raw` and write raw metadata."""
    slug = dataset_slug(cfg)
    raw_dir = cfg.data_dir / "raw" / slug
    meta_path = raw_dir / "metadata.json"

    _ensure_dir(raw_dir.parent)

    cfg_fp = _stable_config_fingerprint(cfg)

    save_dataset_dict_with_split_logging(raw_ds, raw_dir, stage_label="raw")

    meta: Dict[str, Any] = {
        "created_utc": now_iso(),
        "dataset": {"name": cfg.dataset_name, "subset": cfg.dataset_subset},
        "splits": {
            "train": len(raw_ds["train"]),
            "validation": len(raw_ds["validation"]),
            "test": len(raw_ds["test"]),
        },
        "config_fingerprint": cfg_fp,
        "raw_path": str(raw_dir.as_posix()),
    }

    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fetch dataset and persist raw artifacts.")
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config (e.g., configs/data.json). Supports optional top-level 'data' key.",
    )
    p.add_argument("--data-dir", type=str, default=None, help="Root data dir (default: data/)")
    p.add_argument("--dataset-name", type=str, default=None, help="HF dataset name (default: tweet_eval)")
    p.add_argument("--dataset-subset", type=str, default=None, help="HF subset/config name (default: sentiment)")
    p.add_argument("--max-samples", type=int, default=None, help="Dev mode: cap samples per split")
    p.add_argument("--seed", type=int, default=None, help="Seed used for subsampling")
    p.add_argument("--sample-size", type=int, default=None, help="Validation sample size used by pipeline")
    p.add_argument("--batch-size", type=int, default=None, help="Preprocess batch size used by pipeline")
    return p


def main() -> None:
    args = build_argparser().parse_args()

    overrides = {
        "data_dir": args.data_dir,
        "dataset_name": args.dataset_name,
        "dataset_subset": args.dataset_subset,
        "max_samples": args.max_samples,
        "seed": args.seed,
        "sample_size": args.sample_size,
        "batch_size": args.batch_size,
    }

    cfg = load_config(args.config, cli_overrides=overrides)
    subset = cfg.dataset_subset if cfg.dataset_subset is not None else "<none>"
    print(
        f"🚀 Starting raw fetch: dataset='{cfg.dataset_name}', subset='{subset}', "
        f"max_samples={cfg.max_samples}",
        flush=True,
    )

    raw_ds = fetch_dataset(cfg)
    meta = save_raw_dataset(raw_ds, cfg)
    print("\n✅ Raw data ready")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
