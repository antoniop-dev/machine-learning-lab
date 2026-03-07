"""Model fine-tuning utilities (single responsibility: train/save)."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..data.validate import validate_schema, validate_splits
from ..utils.common import now_iso, read_json_config, select_config_section, validate_required_keys
from .evaluate import build_compute_metrics, evaluate_model

ID2LABEL = {0: "negative", 1: "neutral", 2: "positive"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}
NUM_LABELS = 3

REQUIRED_TRAINING_CONFIG_KEYS = {
    "dataset_id_or_path",
    "model_id_or_path",
    "output_dir",
    "text_field",
    "label_field",
    "max_length",
    "num_train_epochs",
    "learning_rate",
    "weight_decay",
    "warmup_ratio",
    "per_device_train_batch_size",
    "per_device_eval_batch_size",
    "gradient_accumulation_steps",
    "save_total_limit",
    "logging_steps",
    "seed",
    "fp16",
}


class TrainingConfig(BaseModel):
    """Validated, immutable configuration for the fine-tuning pipeline.

    All fields are validated by Pydantic on construction.  Unknown keys
    are rejected (``extra="forbid"``) and the object is frozen after
    creation (``frozen=True``) to prevent accidental mutation during
    training.

    Attributes
    ----------
    dataset_id_or_path : Path
        Directory that contains the HuggingFace ``DatasetDict`` produced
        by the data-preprocessing pipeline.
    model_id_or_path : str
        HuggingFace Hub model identifier **or** a local directory path
        to load the base model from.
    output_dir : Path
        Destination directory for fine-tuned model artefacts (weights,
        tokenizer, metrics, metadata).
    text_field : str
        Name of the column in the dataset that contains the raw text.
    label_field : str
        Name of the column in the dataset that contains integer labels.
        Must be ``"labels"`` for compatibility with the HuggingFace
        ``Trainer``.
    max_length : int
        Maximum tokenised sequence length (tokens are truncated beyond
        this value).
    num_train_epochs : float
        Total number of training epochs.
    learning_rate : float
        Peak learning rate for the AdamW optimiser.
    weight_decay : float
        L2 regularisation coefficient applied to non-bias parameters.
    warmup_ratio : float
        Fraction of total training steps used for the linear learning-rate
        warm-up phase.
    per_device_train_batch_size : int
        Batch size per accelerator device during training.
    per_device_eval_batch_size : int
        Batch size per accelerator device during evaluation.
    gradient_accumulation_steps : int
        Number of forward passes to accumulate gradients over before an
        optimiser step (effective batch size multiplier).
    save_total_limit : int
        Maximum number of checkpoint directories to keep on disk.
    logging_steps : int
        Number of optimiser steps between consecutive console log lines.
    seed : int
        Global random seed for reproducibility.
    fp16 : bool
        Whether to use 16-bit mixed-precision training.
    max_train_samples : Optional[int]
        If set, randomly subsample the training split to this many rows.
    max_eval_samples : Optional[int]
        If set, randomly subsample the validation split to this many rows.
    max_test_samples : Optional[int]
        If set, randomly subsample the test split to this many rows.
    metric_for_best_model : str
        Name of the metric used to select the best checkpoint.
    greater_is_better : bool
        Whether a higher value of ``metric_for_best_model`` is better.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    dataset_id_or_path: Path = Path("data/processed/tweet_eval_sentiment")
    model_id_or_path: str = "artifacts/model/base"
    output_dir: Path = Path("artifacts/model/finetuned")

    text_field: str = "text"
    label_field: str = "labels"
    max_length: int = Field(default=128, gt=0)

    num_train_epochs: float = Field(default=2.0, gt=0)
    learning_rate: float = Field(default=2e-5, ge=0)
    weight_decay: float = Field(default=0.01, ge=0)
    warmup_ratio: float = Field(default=0.1, ge=0)
    per_device_train_batch_size: int = Field(default=8, gt=0)
    per_device_eval_batch_size: int = Field(default=8, gt=0)
    gradient_accumulation_steps: int = Field(default=1, gt=0)
    save_total_limit: int = Field(default=2, gt=0)
    logging_steps: int = Field(default=10, gt=0)
    seed: int = 42
    fp16: bool = False

    max_train_samples: Optional[int] = Field(default=None, ge=0)
    max_eval_samples: Optional[int] = Field(default=None, ge=0)
    max_test_samples: Optional[int] = Field(default=None, ge=0)

    metric_for_best_model: str = "macro_f1"
    greater_is_better: bool = True

    # HuggingFace Hub integration: when set, upload finetuned model after training
    hf_model_repo_id: Optional[str] = None


def _require_training_dependencies() -> None:
    """Raise ``RuntimeError`` if heavy ML dependencies are not installed.

    Guards the training entry-point against environments where
    ``datasets``, ``torch``, or ``transformers`` are not available.
    This avoids confusing import-time errors with a single, clear
    message that points the user to the requirements file.

    Raises
    ------
    RuntimeError
        If any of the required packages cannot be imported.
    """
    try:
        import datasets  # noqa: F401
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Missing training dependencies. Install with: pip install -r requirements.txt"
        ) from exc


def _parse_json_path(path: Optional[str], expected_section: str) -> Dict[str, Any]:
    """Load and validate a JSON config file, optionally scoped to a section.

    Parameters
    ----------
    path : Optional[str]
        Path to the JSON configuration file.  If ``None`` or an empty
        string, an empty dictionary is returned so that the caller can
        fall back to its own defaults.
    expected_section : str
        The top-level key to look for inside the JSON file (e.g.
        ``"training"``).  If present the value of that key is used;
        otherwise the whole document is treated as the config.

    Returns
    -------
    Dict[str, Any]
        Parsed configuration dictionary, already validated for required
        keys.

    Raises
    ------
    FileNotFoundError
        If *path* is given but does not point to an existing file.
    """
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    raw_cfg = read_json_config(p)
    cfg = select_config_section(raw_cfg, expected_section=expected_section, source_path=p)
    validate_required_keys(
        cfg,
        required_keys=REQUIRED_TRAINING_CONFIG_KEYS,
        source_path=p,
        expected_section=expected_section,
    )
    return cfg


def load_training_config(path: Optional[str], *, cli_overrides: Dict[str, Any]) -> TrainingConfig:
    """Build a validated :class:`TrainingConfig` from a JSON file and CLI overrides.

    Resolution order (later entries win):

    1. Built-in defaults defined on :class:`TrainingConfig`.
    2. Values from the JSON config file at *path* (if provided).
    3. Non-``None`` values from *cli_overrides*.

    Parameters
    ----------
    path : Optional[str]
        Path to a JSON configuration file.  Pass ``None`` to use
        defaults / CLI overrides only.
    cli_overrides : Dict[str, Any]
        Mapping of field names to values supplied on the command line.
        ``None`` values are ignored so that absent CLI flags do not
        shadow file-based configuration.

    Returns
    -------
    TrainingConfig
        Fully validated, immutable configuration object.

    Raises
    ------
    FileNotFoundError
        Propagated from :func:`_parse_json_path` when the config file
        does not exist.
    ValueError
        If Pydantic validation fails (wraps the first validation error
        with a human-readable location hint).
    """
    cfg = _parse_json_path(path, expected_section="training")
    merged = {**cfg, **{k: v for k, v in cli_overrides.items() if v is not None}}

    defaults = {
        "dataset_id_or_path": "data/processed/tweet_eval_sentiment",
        "model_id_or_path": "artifacts/model/base",
        "output_dir": "artifacts/model/finetuned",
        "text_field": "text",
        "label_field": "labels",
        "max_length": 128,
        "num_train_epochs": 2.0,
        "learning_rate": 2e-5,
        "weight_decay": 0.01,
        "warmup_ratio": 0.1,
        "per_device_train_batch_size": 8,
        "per_device_eval_batch_size": 8,
        "gradient_accumulation_steps": 1,
        "save_total_limit": 2,
        "logging_steps": 10,
        "seed": 42,
        "fp16": False,
        "max_train_samples": None,
        "max_eval_samples": None,
        "max_test_samples": None,
        "metric_for_best_model": "macro_f1",
        "greater_is_better": True,
    }
    payload = {**defaults, **merged}

    try:
        return TrainingConfig.model_validate(payload)
    except ValidationError as exc:
        first = exc.errors()[0]
        loc = ".".join(str(part) for part in first.get("loc", []))
        msg = first.get("msg", "invalid value")
        raise ValueError(f"Invalid training config at '{loc}': {msg}") from None


def _load_dataset_dict(dataset_id_or_path: Path) -> Any:
    """Load a HuggingFace ``DatasetDict`` from disk and validate its splits.

    Parameters
    ----------
    dataset_id_or_path : Path
        Directory previously written by
        ``datasets.DatasetDict.save_to_disk``.

    Returns
    -------
    datasets.DatasetDict
        Dataset dictionary guaranteed to contain ``"train"``,
        ``"validation"``, and ``"test"`` splits.

    Raises
    ------
    FileNotFoundError
        If *dataset_id_or_path* does not exist.
    ValueError
        If the directory exists but cannot be loaded as a
        ``DatasetDict`` (e.g. legacy split-by-split layout).
    """
    from datasets import load_from_disk

    if not dataset_id_or_path.exists():
        raise FileNotFoundError(
            f"Processed dataset directory not found: {dataset_id_or_path}. "
            "Run the data pipeline first."
        )

    try:
        ds = load_from_disk(str(dataset_id_or_path))
    except Exception as exc:
        raise ValueError(
            f"Unable to load dataset from {dataset_id_or_path}. "
            "This can happen with legacy split-by-split layout. "
            "Re-run `scripts/fetch_data.py` to re-save datasets in HF-native format."
        ) from exc

    validate_splits(ds, required_splits=["train", "validation", "test"])
    return ds


def _subsample_shuffle_select(split: Any, max_samples: Optional[int], seed: int) -> Any:
    """Optionally subsample a dataset split by shuffling and selecting rows.

    If *max_samples* is ``None`` or is greater than or equal to the
    number of rows in *split*, the original split is returned unchanged.
    Otherwise, the split is first shuffled with *seed* and then the
    first *max_samples* rows are selected.

    Parameters
    ----------
    split : datasets.Dataset
        A single HuggingFace ``Dataset`` split (train, validation, or
        test).
    max_samples : Optional[int]
        Maximum number of rows to retain.  ``None`` means no limit.
        ``0`` returns an empty dataset.
    seed : int
        Random seed used for the shuffle operation to ensure
        reproducibility.

    Returns
    -------
    datasets.Dataset
        Original or subsampled dataset split.
    """
    if max_samples is None:
        return split
    n = len(split)
    if max_samples >= n:
        return split
    if max_samples == 0:
        return split.select([])

    return split.shuffle(seed=seed).select(range(max_samples))


def fine_tune_model(cfg: TrainingConfig) -> Dict[str, Any]:
    """Run the full fine-tuning pipeline and return a summary of results.

    The pipeline executes the following steps in order:

    1. Load and validate the processed ``DatasetDict`` from disk.
    2. Optionally subsample each split according to *cfg*.
    3. Load the tokenizer and base model from *cfg.model_id_or_path*.
    4. Tokenize all three splits.
    5. Configure and run the HuggingFace ``Trainer``.
    6. Evaluate the best checkpoint on the validation and test splits
       (delegated to :func:`evaluate.evaluate_model`).
    7. Persist the fine-tuned model, tokenizer, metrics, training args,
       and metadata to *cfg.output_dir*.

    Parameters
    ----------
    cfg : TrainingConfig
        Fully validated training configuration.

    Returns
    -------
    Dict[str, Any]
        Dictionary with two keys:

        ``"metadata"``
            Provenance information (data paths, label mapping, split
            sizes, file locations …).
        ``"metrics"``
            Nested dictionary with sub-keys ``"train"``,
            ``"validation"``, and ``"test"``, each holding the
            corresponding metrics dictionary.

    Raises
    ------
    RuntimeError
        If required ML dependencies (``datasets``, ``torch``,
        ``transformers``) are not installed.
    FileNotFoundError
        If the processed dataset directory does not exist.
    ValueError
        If the dataset cannot be loaded or if ``cfg.label_field`` is
        not ``"labels"``.
    """
    _require_training_dependencies()
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        Trainer,
        TrainingArguments,
    )

    print(f"📦 Loading processed dataset from {cfg.dataset_id_or_path.as_posix()}", flush=True)
    dataset_dict = _load_dataset_dict(cfg.dataset_id_or_path)

    for split_name in ("train", "validation", "test"):
        validate_schema(
            dataset_dict[split_name],
            text_field=cfg.text_field,
            label_field=cfg.label_field,
            split_name=split_name,
        )

    # Enforce standardized schema from preprocessing pipeline
    if cfg.label_field != "labels":
        raise ValueError(
            "This pipeline expects processed data to contain label field 'labels'. "
            "Ensure preprocessing outputs 'labels' or update the pipeline accordingly."
        )

    train_split = _subsample_shuffle_select(dataset_dict["train"], cfg.max_train_samples, cfg.seed)
    val_split = _subsample_shuffle_select(dataset_dict["validation"], cfg.max_eval_samples, cfg.seed)
    test_split = _subsample_shuffle_select(dataset_dict["test"], cfg.max_test_samples, cfg.seed)

    id2label = dict(ID2LABEL)
    label2id = dict(LABEL2ID)

    model_source_path = Path(cfg.model_id_or_path)
    model_source = str(model_source_path) if model_source_path.exists() else cfg.model_id_or_path
    local_only = model_source_path.exists()
    source_mode = "local" if local_only else "remote"

    print(
        f"🔤 Loading tokenizer/model from '{model_source}' ({source_mode})",
        flush=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_source,
        use_fast=True,
        local_files_only=local_only,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        model_source,
        num_labels=NUM_LABELS,
        id2label=id2label,
        label2id=label2id,
        local_files_only=local_only,
    )

    def tokenize_batch(batch: Dict[str, list[Any]]) -> Dict[str, Any]:
        """Tokenize a batch of raw text samples.

        Parameters
        ----------
        batch : Dict[str, list[Any]]
            A dictionary of column-name → list-of-values as produced by
            the HuggingFace ``Dataset.map`` method in batched mode.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing the tokeniser outputs (``input_ids``,
            ``attention_mask``, and optionally ``token_type_ids``).
        """
        return tokenizer(
            batch[cfg.text_field],
            truncation=True,
            max_length=cfg.max_length,
        )

    print("🧠 Tokenizing train/validation/test splits", flush=True)
    train_tokenized = train_split.map(
        tokenize_batch,
        batched=True,
        remove_columns=[cfg.text_field],
        desc="Tokenize train",
    )
    val_tokenized = val_split.map(
        tokenize_batch,
        batched=True,
        remove_columns=[cfg.text_field],
        desc="Tokenize validation",
    )
    test_tokenized = test_split.map(
        tokenize_batch,
        batched=True,
        remove_columns=[cfg.text_field],
        desc="Tokenize test",
    )

    cols = ["input_ids", "attention_mask", "labels"]
    train_tokenized.set_format(type="torch", columns=cols)
    val_tokenized.set_format(type="torch", columns=cols)
    test_tokenized.set_format(type="torch", columns=cols)

    if cfg.output_dir.exists():
        print(f"♻ Overwriting existing training output at {cfg.output_dir.as_posix()}", flush=True)
        shutil.rmtree(cfg.output_dir)

    training_args = TrainingArguments(
        output_dir=str(cfg.output_dir),
        overwrite_output_dir=True,
        num_train_epochs=cfg.num_train_epochs,
        learning_rate=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
        warmup_ratio=cfg.warmup_ratio,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        per_device_eval_batch_size=cfg.per_device_eval_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=cfg.logging_steps,
        save_total_limit=cfg.save_total_limit,
        load_best_model_at_end=True,
        metric_for_best_model=cfg.metric_for_best_model,
        greater_is_better=cfg.greater_is_better,
        seed=cfg.seed,
        fp16=cfg.fp16,
        report_to=[],
        hub_model_id=cfg.hf_model_repo_id,
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=val_tokenized,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=build_compute_metrics(),
    )

    print("🏋 Starting fine-tuning", flush=True)
    train_result = trainer.train()

    eval_metrics = evaluate_model(trainer, val_tokenized, test_tokenized)

    print(f"💾 Saving fine-tuned model to {cfg.output_dir.as_posix()}", flush=True)
    trainer.save_model(str(cfg.output_dir))
    tokenizer.save_pretrained(str(cfg.output_dir))

    training_args_path = cfg.output_dir / "training_args.json"
    training_args_path.write_text(
        json.dumps(training_args.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    metrics: Dict[str, Any] = {
        "train": dict(train_result.metrics),
        "validation": eval_metrics["validation"],
        "test": eval_metrics["test"],
    }
    metrics_path = cfg.output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    metadata: Dict[str, Any] = {
        "created_utc": now_iso(),
        "dataset_id_or_path": str(cfg.dataset_id_or_path.as_posix()),
        "model_id_or_path": cfg.model_id_or_path,
        "output_dir": str(cfg.output_dir.as_posix()),
        "splits": {
            "train": len(train_tokenized),
            "validation": len(val_tokenized),
            "test": len(test_tokenized),
        },
        "fields": {"text": cfg.text_field, "label": "labels"},
        "label_names": [ID2LABEL[i] for i in range(NUM_LABELS)],
        "id2label": {str(k): v for k, v in id2label.items()},
        "label2id": label2id,
        "metrics_path": str(metrics_path.as_posix()),
        "training_args_path": str(training_args_path.as_posix()),
    }

    metadata_path = cfg.output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    if cfg.hf_model_repo_id:
        print(f"📤 Pushing fine-tuned model to HuggingFace Hub: {cfg.hf_model_repo_id}", flush=True)
        trainer.push_to_hub(commit_message="Auto-upload fine-tuned model")

    return {"metadata": metadata, "metrics": metrics}


def build_argparser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser for the training script.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser whose ``parse_args()`` output can be passed
        directly to :func:`load_training_config` via the
        *cli_overrides* mapping.
    """
    p = argparse.ArgumentParser(description="Fine-tune sentiment model with processed dataset.")
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config (e.g., configs/training.json). Supports optional top-level 'training' key.",
    )
    p.add_argument("--processed-data-dir", type=str, default=None, help="Path to processed dataset directory")
    p.add_argument("--model-id-or-path", type=str, default=None, help="Model id/path used for fine-tuning")
    p.add_argument("--output-dir", type=str, default=None, help="Where to save fine-tuned artifacts")
    p.add_argument("--max-length", type=int, default=None, help="Tokenizer max length")
    p.add_argument("--num-train-epochs", type=float, default=None, help="Training epochs")
    p.add_argument("--learning-rate", type=float, default=None, help="Optimizer learning rate")
    p.add_argument("--train-batch-size", type=int, default=None, help="Per-device train batch size")
    p.add_argument("--eval-batch-size", type=int, default=None, help="Per-device eval batch size")
    p.add_argument("--max-train-samples", type=int, default=None, help="Optional cap for train split")
    p.add_argument("--max-eval-samples", type=int, default=None, help="Optional cap for validation split")
    p.add_argument("--max-test-samples", type=int, default=None, help="Optional cap for test split")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    return p


def main() -> None:
    """Entry point for running fine-tuning from the command line.

    Parses CLI arguments, builds a :class:`TrainingConfig`, runs
    :func:`fine_tune_model`, and prints the resulting metrics JSON to
    stdout.

    This function is registered as the ``train`` console-script in
    ``pyproject.toml`` (or ``setup.cfg``) and can also be invoked
    directly via ``python -m machineinnovatorsinc_solution.model.train``.
    """
    args = build_argparser().parse_args()
    overrides = {
        "dataset_id_or_path": args.dataset_id_or_path,
        "model_id_or_path": args.model_id_or_path,
        "output_dir": args.output_dir,
        "max_length": args.max_length,
        "num_train_epochs": args.num_train_epochs,
        "learning_rate": args.learning_rate,
        "per_device_train_batch_size": args.train_batch_size,
        "per_device_eval_batch_size": args.eval_batch_size,
        "max_train_samples": args.max_train_samples,
        "max_eval_samples": args.max_eval_samples,
        "max_test_samples": args.max_test_samples,
        "seed": args.seed,
    }

    cfg = load_training_config(args.config, cli_overrides=overrides)
    print(
        f"🚀 Starting fine-tuning: model='{cfg.model_id_or_path}', data='{cfg.dataset_id_or_path.as_posix()}', "
        f"output='{cfg.output_dir.as_posix()}'",
        flush=True,
    )
    result = fine_tune_model(cfg)

    print("\n✅ Fine-tuning completed")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
