"""Model retrieval utilities (single responsibility: load tokenizer/model from HF)."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.common import (
    coerce_bool,
    now_iso,
    read_json_config,
    select_config_section,
    validate_required_keys,
)

REQUIRED_MODEL_CONFIG_KEYS = {
    "model_id",
    "num_labels",
    "id2label",
    "label2id",
    "padding",
    "truncation",
    "max_length",
    "use_fast_tokenizer",
    "artifacts_dir",
}


def _coerce_id2label(value: Any) -> Dict[int, str]:
    if not isinstance(value, dict):
        raise ValueError("`id2label` must be a JSON object.")
    out: Dict[int, str] = {}
    for key, label in value.items():
        out[int(key)] = str(label)
    return out


def _coerce_label2id(value: Any) -> Dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError("`label2id` must be a JSON object.")
    out: Dict[str, int] = {}
    for label, idx in value.items():
        out[str(label)] = int(idx)
    return out


def _ensure_transformers() -> None:
    try:
        import transformers  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency 'transformers'. Install with: pip install transformers torch"
        ) from exc


@dataclass(frozen=True)
class ModelConfig:
    model_id: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    num_labels: int = 3
    id2label: Dict[int, str] = field(
        default_factory=lambda: {
            0: "negative",
            1: "neutral",
            2: "positive",
        }
    )
    label2id: Dict[str, int] = field(
        default_factory=lambda: {
            "negative": 0,
            "neutral": 1,
            "positive": 2,
        }
    )
    padding: str = "max_length"
    truncation: bool = True
    max_length: int = 128
    use_fast_tokenizer: bool = True
    revision: Optional[str] = None
    cache_dir: Optional[Path] = None
    artifacts_dir: Path = Path("artifacts/model/base")
    force: bool = False


def load_model_config(path: Optional[str], *, cli_overrides: Dict[str, Any]) -> ModelConfig:
    cfg: Dict[str, Any] = {}
    if path:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
        raw_cfg = read_json_config(p)
        cfg = select_config_section(raw_cfg, expected_section="model", source_path=p)
        validate_required_keys(
            cfg,
            required_keys=REQUIRED_MODEL_CONFIG_KEYS,
            source_path=p,
            expected_section="model",
        )

    merged = {**cfg, **{k: v for k, v in cli_overrides.items() if v is not None}}

    num_labels = int(merged.get("num_labels", 3))
    if num_labels <= 0:
        raise ValueError("`num_labels` must be > 0.")

    id2label_raw = merged.get("id2label", {0: "negative", 1: "neutral", 2: "positive"})
    id2label = _coerce_id2label(id2label_raw)

    label2id_raw = merged.get("label2id", None)
    if label2id_raw is None:
        label2id = {label: idx for idx, label in id2label.items()}
    else:
        label2id = _coerce_label2id(label2id_raw)

    if len(id2label) != num_labels:
        raise ValueError(
            f"`id2label` size ({len(id2label)}) does not match `num_labels` ({num_labels})."
        )
    if len(label2id) != num_labels:
        raise ValueError(
            f"`label2id` size ({len(label2id)}) does not match `num_labels` ({num_labels})."
        )

    expected_label2id = {label: idx for idx, label in id2label.items()}
    if label2id != expected_label2id:
        raise ValueError(
            "`label2id` must be the inverse mapping of `id2label`."
        )

    max_length = int(merged.get("max_length", 128))
    if max_length <= 0:
        raise ValueError("`max_length` must be > 0.")

    cache_dir = merged.get("cache_dir", None)
    artifacts_dir = Path(merged.get("artifacts_dir", "artifacts/model/base"))

    return ModelConfig(
        model_id=str(merged.get("model_id", "cardiffnlp/twitter-roberta-base-sentiment-latest")),
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
        padding=str(merged.get("padding", "max_length")),
        truncation=coerce_bool(merged.get("truncation", True)),
        max_length=max_length,
        use_fast_tokenizer=coerce_bool(merged.get("use_fast_tokenizer", True)),
        revision=merged.get("revision", None),
        cache_dir=Path(cache_dir) if cache_dir else None,
        artifacts_dir=artifacts_dir,
        force=coerce_bool(merged.get("force", False)),
    )


def _normalize_id2label(mapping: Dict[Any, Any]) -> Dict[int, str]:
    return {int(k): str(v) for k, v in mapping.items()}


def _validate_model_config(model: Any, cfg: ModelConfig) -> None:
    if int(model.config.num_labels) != cfg.num_labels:
        raise ValueError(
            f"Loaded model num_labels={model.config.num_labels}, expected {cfg.num_labels}."
        )

    loaded_id2label = _normalize_id2label(dict(model.config.id2label))
    loaded_label2id = {str(k): int(v) for k, v in dict(model.config.label2id).items()}

    if loaded_id2label != cfg.id2label:
        raise ValueError(
            f"Loaded id2label mapping does not match config.\n"
            f"loaded={loaded_id2label}\nexpected={cfg.id2label}"
        )

    if loaded_label2id != cfg.label2id:
        raise ValueError(
            f"Loaded label2id mapping does not match config.\n"
            f"loaded={loaded_label2id}\nexpected={cfg.label2id}"
        )


def _validate_tokenizer(tokenizer: Any) -> None:
    missing: list[str] = []
    if tokenizer.pad_token_id is None:
        missing.append("pad_token_id")
    if tokenizer.cls_token_id is None:
        missing.append("cls_token_id")
    if tokenizer.sep_token_id is None:
        missing.append("sep_token_id")

    if missing:
        raise ValueError(f"Tokenizer is missing required special tokens: {missing}")


def retrieve_model_assets(cfg: ModelConfig) -> Dict[str, Any]:
    """Retrieve tokenizer + model from Hugging Face and persist local artifacts + metadata."""
    _ensure_transformers()
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    pretrained_kwargs: Dict[str, Any] = {}
    if cfg.revision:
        pretrained_kwargs["revision"] = cfg.revision
    if cfg.cache_dir:
        pretrained_kwargs["cache_dir"] = str(cfg.cache_dir)

    print(f"⬇ Retrieving tokenizer for model '{cfg.model_id}'", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(
        cfg.model_id,
        use_fast=cfg.use_fast_tokenizer,
        **pretrained_kwargs,
    )

    print(f"⬇ Retrieving model weights for '{cfg.model_id}'", flush=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg.model_id,
        num_labels=cfg.num_labels,
        id2label=cfg.id2label,
        label2id=cfg.label2id,
        **pretrained_kwargs,
    )

    _validate_model_config(model, cfg)
    _validate_tokenizer(tokenizer)

    if cfg.force and cfg.artifacts_dir.exists():
        shutil.rmtree(cfg.artifacts_dir)
    cfg.artifacts_dir.mkdir(parents=True, exist_ok=True)

    print(f"💾 Saving pretrained model/tokenizer to {cfg.artifacts_dir.as_posix()}", flush=True)
    model.save_pretrained(str(cfg.artifacts_dir))
    tokenizer.save_pretrained(str(cfg.artifacts_dir))

    model_safetensors = cfg.artifacts_dir / "model.safetensors"
    model_bin = cfg.artifacts_dir / "pytorch_model.bin"
    tokenizer_json = cfg.artifacts_dir / "tokenizer.json"
    tokenizer_config_json = cfg.artifacts_dir / "tokenizer_config.json"
    config_json = cfg.artifacts_dir / "config.json"

    print(f"📝 Writing retrieval metadata to {cfg.artifacts_dir.as_posix()}", flush=True)
    metadata: Dict[str, Any] = {
        "created_utc": now_iso(),
        "model_id": cfg.model_id,
        "revision": cfg.revision,
        "num_labels": cfg.num_labels,
        "id2label": {str(k): v for k, v in cfg.id2label.items()},
        "label2id": cfg.label2id,
        "tokenizer": {
            "name_or_path": str(getattr(tokenizer, "name_or_path", cfg.model_id)),
            "is_fast": bool(getattr(tokenizer, "is_fast", False)),
            "padding": cfg.padding,
            "truncation": cfg.truncation,
            "max_length": cfg.max_length,
            "special_tokens_map": dict(tokenizer.special_tokens_map),
            "pad_token_id": tokenizer.pad_token_id,
            "cls_token_id": tokenizer.cls_token_id,
            "sep_token_id": tokenizer.sep_token_id,
        },
        "artifacts_dir": str(cfg.artifacts_dir.as_posix()),
        "saved_artifacts": {
            "model_safetensors": str(model_safetensors.as_posix()) if model_safetensors.exists() else None,
            "model_bin": str(model_bin.as_posix()) if model_bin.exists() else None,
            "config": str(config_json.as_posix()) if config_json.exists() else None,
            "tokenizer_json": str(tokenizer_json.as_posix()) if tokenizer_json.exists() else None,
            "tokenizer_config": str(tokenizer_config_json.as_posix()) if tokenizer_config_json.exists() else None,
        },
        "cache_dir": str(cfg.cache_dir.as_posix()) if cfg.cache_dir else None,
    }

    metadata_path = cfg.artifacts_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return metadata


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Retrieve base model/tokenizer from Hugging Face.")
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config (e.g., configs/model.json). Supports optional top-level 'model' key.",
    )
    p.add_argument("--model-id", type=str, default=None, help="HF model id")
    p.add_argument("--num-labels", type=int, default=None, help="Number of output labels")
    p.add_argument("--max-length", type=int, default=None, help="Tokenizer max_length")
    p.add_argument("--padding", type=str, default=None, help="Tokenizer padding mode")
    p.add_argument("--truncation", type=str, default=None, help="Tokenizer truncation (true/false)")
    p.add_argument("--use-fast-tokenizer", type=str, default=None, help="Use fast tokenizer (true/false)")
    p.add_argument("--revision", type=str, default=None, help="HF revision/tag/commit")
    p.add_argument("--cache-dir", type=str, default=None, help="Transformers cache directory")
    p.add_argument("--artifacts-dir", type=str, default=None, help="Output metadata directory")
    p.add_argument("--force", action="store_true", help="Overwrite existing retrieval metadata directory")
    return p


def main() -> None:
    args = build_argparser().parse_args()
    overrides = {
        "model_id": args.model_id,
        "num_labels": args.num_labels,
        "max_length": args.max_length,
        "padding": args.padding,
        "truncation": args.truncation,
        "use_fast_tokenizer": args.use_fast_tokenizer,
        "revision": args.revision,
        "cache_dir": args.cache_dir,
        "artifacts_dir": args.artifacts_dir,
        "force": True if args.force else None,
    }
    cfg = load_model_config(args.config, cli_overrides=overrides)
    print(
        f"🚀 Starting model retrieval: model_id='{cfg.model_id}', revision='{cfg.revision}', "
        f"artifacts_dir='{cfg.artifacts_dir.as_posix()}'",
        flush=True,
    )
    meta = retrieve_model_assets(cfg)
    print("\n✅ Model retrieval completed")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
