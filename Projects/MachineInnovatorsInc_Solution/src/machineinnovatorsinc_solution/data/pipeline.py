"""End-to-end data pipeline orchestrator.

Responsibilities:
- fetch raw data (via `fetch.py`)
- validate required structure/content (via `validate.py`)
- preprocess to canonical columns (via `preprocess.py`)
- persist raw + processed artifacts with metadata
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.common import now_iso
from ..utils.kaggle_upload import push_directory_to_kaggle
from .fetch import (
    DataConfig,
    dataset_slug,
    fetch_dataset,
    load_config,
    save_dataset_dict_with_split_logging,
    save_raw_dataset,
)
from .preprocess import preprocess_dataset
from .validate import validate_non_empty_text, validate_schema


def _extract_label_names(processed_ds: Any) -> Optional[list[str]]:
    try:
        feats = processed_ds["train"].features
        if "labels" in feats and hasattr(feats["labels"], "names"):
            return list(getattr(feats["labels"], "names"))
    except Exception:
        return None
    return None


def run_data_pipeline(cfg: DataConfig) -> Dict[str, Any]:
    """Run fetch -> validate -> preprocess and persist artifacts."""
    print("🔄 Stage 1/5: fetching raw dataset", flush=True)
    raw_ds = fetch_dataset(cfg)

    print("🔎 Stage 2/5: validating schema and text integrity", flush=True)
    for split_name in ("train", "validation", "test"):
        split = raw_ds[split_name]
        validate_schema(
            split,
            text_field=cfg.text_field,
            label_field=cfg.label_field,
            split_name=split_name,
        )
        validate_non_empty_text(
            split,
            text_field=cfg.text_field,
            split_name=split_name,
            sample_size=cfg.sample_size,
            seed=cfg.seed,
            full_scan=False,
        )

    print("💾 Stage 3/5: saving raw dataset", flush=True)
    raw_meta = save_raw_dataset(raw_ds, cfg)

    print("🧹 Stage 4/5: preprocessing dataset", flush=True)
    processed_ds = preprocess_dataset(
        raw_ds,
        text_field=cfg.text_field,
        label_field=cfg.label_field,
        batch_size=cfg.batch_size,
    )

    processed_dir = cfg.data_dir / "processed" / dataset_slug(cfg)
    processed_meta_path = processed_dir / "metadata.json"

    print("💾 Stage 5/5: saving processed dataset", flush=True)
    save_dataset_dict_with_split_logging(
        processed_ds,
        processed_dir,
        stage_label="processed",
    )

    processed_meta: Dict[str, Any] = {
        "created_utc": now_iso(),
        "raw_metadata_path": str((Path(raw_meta["raw_path"]) / "metadata.json").as_posix()),
        "raw_path": raw_meta["raw_path"],
        "processed_path": str(processed_dir.as_posix()),
        "splits": {
            "train": len(processed_ds["train"]),
            "validation": len(processed_ds["validation"]),
            "test": len(processed_ds["test"]),
        },
        "fields": {"text": "text", "label": "labels"},
        "label_names": _extract_label_names(processed_ds),
    }
    processed_meta_path.write_text(
        json.dumps(processed_meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if cfg.kaggle_dataset_slug:
        push_directory_to_kaggle(
            processed_dir,
            cfg.kaggle_dataset_slug,
            version_notes=f"processed {dataset_slug(cfg)}",
        )

    return {"raw": raw_meta, "processed": processed_meta}



def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run full data pipeline (fetch/validate/preprocess).")
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
    p.add_argument("--sample-size", type=int, default=None, help="Validation sample size per split")
    p.add_argument("--batch-size", type=int, default=None, help="Batch size used in text preprocessing")
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
        f"🚀 Starting data pipeline: dataset='{cfg.dataset_name}', subset='{subset}', "
        f"max_samples={cfg.max_samples}, sample_size={cfg.sample_size}, batch_size={cfg.batch_size}",
        flush=True,
    )
    meta = run_data_pipeline(cfg)
    print("\n✅ Data pipeline completed")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
