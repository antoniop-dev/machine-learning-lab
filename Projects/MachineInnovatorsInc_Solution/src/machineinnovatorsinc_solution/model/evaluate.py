"""Evaluation utilities for the fine-tuned sentiment model.

This module serves two purposes:

1. **Library helpers** — :func:`build_compute_metrics` and
   :func:`evaluate_model` are called by the training pipeline
   (``model/train.py``) during fine-tuning.

2. **Standalone pipeline** — :func:`run_evaluation`, :func:`build_argparser`,
   and :func:`main` expose a self-contained evaluation entry-point that loads
   an already-saved model and evaluates it against the processed dataset,
   without requiring a training run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sklearn.metrics import accuracy_score, f1_score

from ..data.validate import validate_schema, validate_splits
from ..utils.common import now_iso, read_json_config, select_config_section, validate_required_keys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ID2LABEL = {0: "negative", 1: "neutral", 2: "positive"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}
NUM_LABELS = 3

REQUIRED_EVALUATION_CONFIG_KEYS = {
    "dataset_id_or_path",
    "model_id_or_path",
    "text_field",
    "label_field",
    "max_length",
    "per_device_eval_batch_size",
    "seed",
}

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class EvaluationConfig(BaseModel):
    """Validated, immutable configuration for the standalone evaluation pipeline.

    Attributes
    ----------
    dataset_id_or_path : str
        Directory or HuggingFace Hub ID containing the ``DatasetDict`` produced by the
        data-preprocessing pipeline.
    model_id_or_path : str
        Directory (or HuggingFace Hub ID) of the fine-tuned model to evaluate.
    output_dir : Path
        Where to write ``eval_metrics.json``.  Defaults to ``reports/``.
    text_field : str
        Column name for raw text in the dataset.
    label_field : str
        Column name for integer labels.
    max_length : int
        Maximum tokenised sequence length.
    per_device_eval_batch_size : int
        Batch size per accelerator device during evaluation.
    seed : int
        Random seed (used if subsampling splits).
    splits : List[str]
        Which dataset splits to evaluate.  Defaults to ``["validation", "test"]``.
    max_eval_samples : Optional[int]
        If set, subsample each split to this many rows before evaluation.
    fp16 : bool
        Whether to use 16-bit inference (speeds up GPU evaluation).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    dataset_id_or_path: str = "antoniop-dev/tweet-eval-sentiment-processed"
    model_id_or_path: str = "antoniop-dev/sentiment-model-finetuned"
    output_dir: Path = Path("reports")

    text_field: str = "text"
    label_field: str = "labels"
    max_length: int = Field(default=128, gt=0)

    per_device_eval_batch_size: int = Field(default=16, gt=0)
    seed: int = 42
    splits: List[str] = ["validation", "test"]
    max_eval_samples: Optional[int] = Field(default=None, ge=0)
    fp16: bool = False


def load_evaluation_config(
    path: Optional[str], *, cli_overrides: Dict[str, Any]
) -> EvaluationConfig:
    """Build a validated :class:`EvaluationConfig` from a JSON file and CLI overrides.

    Resolution order (later entries win):

    1. Built-in defaults defined on :class:`EvaluationConfig`.
    2. Values from the JSON config file at *path* (if provided).
    3. Non-``None`` values from *cli_overrides*.

    Parameters
    ----------
    path : Optional[str]
        Path to a JSON configuration file.  Pass ``None`` to use defaults /
        CLI overrides only.
    cli_overrides : Dict[str, Any]
        Mapping of field names to values supplied on the command line.
        ``None`` values are ignored.

    Returns
    -------
    EvaluationConfig
        Fully validated, immutable configuration object.

    Raises
    ------
    FileNotFoundError
        If the config file path is given but does not exist.
    ValueError
        If Pydantic validation fails.
    """
    cfg: Dict[str, Any] = {}
    if path:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
        raw_cfg = read_json_config(p)
        cfg = select_config_section(raw_cfg, expected_section="evaluation", source_path=p)
        validate_required_keys(
            cfg,
            required_keys=REQUIRED_EVALUATION_CONFIG_KEYS,
            source_path=p,
            expected_section="evaluation",
        )

    merged = {**cfg, **{k: v for k, v in cli_overrides.items() if v is not None}}

    defaults: Dict[str, Any] = {
        "dataset_id_or_path": "antoniop-dev/tweet-eval-sentiment-processed",
        "model_id_or_path": "antoniop-dev/sentiment-model-finetuned",
        "output_dir": "reports",
        "text_field": "text",
        "label_field": "labels",
        "max_length": 128,
        "per_device_eval_batch_size": 16,
        "seed": 42,
        "splits": ["validation", "test"],
        "max_eval_samples": None,
        "fp16": False,
    }
    payload = {**defaults, **merged}

    try:
        return EvaluationConfig.model_validate(payload)
    except ValidationError as exc:
        first = exc.errors()[0]
        loc = ".".join(str(part) for part in first.get("loc", []))
        msg = first.get("msg", "invalid value")
        raise ValueError(f"Invalid evaluation config at '{loc}': {msg}") from None


# ---------------------------------------------------------------------------
# Training-time helpers (used by model/train.py)
# ---------------------------------------------------------------------------


def build_compute_metrics():
    """Create and return a ``compute_metrics`` callback for the HuggingFace ``Trainer``.

    The inner function converts raw logits into class predictions and
    computes two scalar metrics: *accuracy* and *macro-averaged F1*.

    Returns
    -------
    compute_metrics : callable
        A function with signature ``(eval_pred) -> Dict[str, float]``
        that the ``Trainer`` can call at the end of each evaluation step.

    Examples
    --------
    >>> compute_metrics = build_compute_metrics()
    >>> import numpy as np
    >>> logits = np.array([[2.0, 0.5, 0.1], [0.1, 0.2, 3.0]])
    >>> labels = np.array([0, 2])
    >>> compute_metrics((logits, labels))
    {'accuracy': 1.0, 'macro_f1': 1.0}
    """

    def compute_metrics(eval_pred: Any) -> Dict[str, float]:
        """Compute accuracy and macro-F1 from a ``(logits, labels)`` pair.

        Parameters
        ----------
        eval_pred : tuple
            A two-element tuple ``(logits, labels)`` where *logits* is a
            2-D array-like of shape ``(n_samples, n_classes)`` and *labels*
            is a 1-D array-like of ground-truth integer class indices.

        Returns
        -------
        Dict[str, float]
            Dictionary with keys ``"accuracy"`` and ``"macro_f1"``.
        """
        logits, labels = eval_pred
        pred_values = np.asarray(logits).argmax(axis=-1)
        label_values = np.asarray(labels)
        return {
            "accuracy": float(accuracy_score(label_values, pred_values)),
            "macro_f1": float(f1_score(label_values, pred_values, average="macro")),
        }

    return compute_metrics


def evaluate_model(
    trainer: Any,
    val_dataset: Any,
    test_dataset: Any,
) -> Dict[str, Any]:
    """Run the ``Trainer`` against the validation and test splits and return metrics.

    Called by the training pipeline after fine-tuning is complete.

    Parameters
    ----------
    trainer : transformers.Trainer
        A fully initialised HuggingFace ``Trainer`` instance whose model
        weights reflect the best checkpoint.
    val_dataset : datasets.Dataset
        Tokenised and format-set validation split.
    test_dataset : datasets.Dataset
        Tokenised and format-set test split.

    Returns
    -------
    Dict[str, Any]
        Dictionary with keys ``"validation"`` and ``"test"``, each containing
        the metrics returned by ``trainer.evaluate()``.
    """
    print("📊 Evaluating best model on validation/test", flush=True)
    validation_metrics = trainer.evaluate(val_dataset, metric_key_prefix="validation")
    test_metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")
    return {
        "validation": validation_metrics,
        "test": test_metrics,
    }


# ---------------------------------------------------------------------------
# Standalone evaluation pipeline
# ---------------------------------------------------------------------------


def _require_inference_dependencies() -> None:
    """Raise ``RuntimeError`` if inference dependencies are not installed.

    Raises
    ------
    RuntimeError
        If ``datasets``, ``torch``, or ``transformers`` cannot be imported.
    """
    try:
        import datasets  # noqa: F401
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Missing inference dependencies. Install with: pip install -r requirements.txt"
        ) from exc


def run_evaluation(cfg: EvaluationConfig) -> Dict[str, Any]:
    """Load a saved model and run evaluation on one or more dataset splits.

    This is the main function of the standalone evaluation pipeline.  It does
    **not** require a training run — any model previously saved with
    ``Trainer.save_model()`` (or compatible HuggingFace format) can be
    evaluated here.

    Steps:

    1. Load the processed ``DatasetDict`` from ``cfg.dataset_id_or_path``.
    2. Load the tokenizer and model from ``cfg.model_id_or_path``.
    3. Tokenize each requested split.
    4. Run inference and compute accuracy + macro-F1 for every split.
    5. Persist an ``eval_metrics.json`` to ``cfg.output_dir``.

    Parameters
    ----------
    cfg : EvaluationConfig
        Fully validated evaluation configuration.

    Returns
    -------
    Dict[str, Any]
        Dictionary with two top-level keys:

        ``"metrics"``
            Nested dict mapping split name → metrics dict.
        ``"eval_metrics_path"``
            Absolute POSIX path to the saved ``eval_metrics.json`` file.

    Raises
    ------
    RuntimeError
        If required dependencies are not installed.
    FileNotFoundError
        If ``cfg.dataset_id_or_path`` or a local model path does not exist.
    """
    _require_inference_dependencies()
    from datasets import load_from_disk, load_dataset
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        Trainer,
        TrainingArguments,
    )

    # --- Load dataset --------------------------------------------------------
    data_source_path = Path(cfg.dataset_id_or_path)
    data_local_only = data_source_path.exists()
    data_source_mode = "local" if data_local_only else "remote"

    print(f"📦 Loading processed dataset from '{cfg.dataset_id_or_path}' ({data_source_mode})", flush=True)
    try:
        if data_local_only:
            dataset_dict = load_from_disk(str(cfg.dataset_id_or_path))
        else:
            dataset_dict = load_dataset(cfg.dataset_id_or_path)
    except Exception as exc:
        raise ValueError(
            f"Unable to load dataset from {cfg.dataset_id_or_path}."
        ) from exc

    validate_splits(dataset_dict, required_splits=cfg.splits)

    for split_name in cfg.splits:
        validate_schema(
            dataset_dict[split_name],
            text_field=cfg.text_field,
            label_field=cfg.label_field,
            split_name=split_name,
        )

    # --- Load model & tokenizer ----------------------------------------------
    model_source_path = Path(cfg.model_id_or_path)
    model_source = str(model_source_path) if model_source_path.exists() else cfg.model_id_or_path
    local_only = model_source_path.exists()
    source_mode = "local" if local_only else "remote"

    print(f"🔤 Loading tokenizer/model from '{model_source}' ({source_mode})", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(
        model_source, use_fast=True, local_files_only=local_only
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        model_source, local_files_only=local_only
    )

    # --- Tokenize splits -----------------------------------------------------
    def tokenize_batch(batch: Dict[str, list]) -> Dict[str, Any]:
        """Tokenize a batch of raw text samples.

        Parameters
        ----------
        batch : Dict[str, list]
            Column-name → list-of-values mapping as produced by
            ``Dataset.map`` in batched mode.

        Returns
        -------
        Dict[str, Any]
            Tokeniser outputs (``input_ids``, ``attention_mask``, …).
        """
        return tokenizer(
            batch[cfg.text_field],
            truncation=True,
            max_length=cfg.max_length,
        )

    tokenized_splits: Dict[str, Any] = {}
    cols = ["input_ids", "attention_mask", "labels"]
    for split_name in cfg.splits:
        split = dataset_dict[split_name]
        if cfg.max_eval_samples is not None and cfg.max_eval_samples < len(split):
            split = split.shuffle(seed=cfg.seed).select(range(cfg.max_eval_samples))
        tokenized = split.map(
            tokenize_batch,
            batched=True,
            remove_columns=[cfg.text_field],
            desc=f"Tokenize {split_name}",
        )
        tokenized.set_format(type="torch", columns=cols)
        tokenized_splits[split_name] = tokenized

    # --- Run evaluation via a minimal Trainer --------------------------------
    output_dir = cfg.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_args = TrainingArguments(
        output_dir=str(output_dir),
        per_device_eval_batch_size=cfg.per_device_eval_batch_size,
        fp16=cfg.fp16,
        seed=cfg.seed,
        report_to=[],
        # Disable any training-specific behaviour
        no_cuda=False,
    )
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    trainer = Trainer(
        model=model,
        args=eval_args,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=build_compute_metrics(),
    )

    print("📊 Running evaluation", flush=True)
    all_metrics: Dict[str, Any] = {}
    for split_name, tokenized in tokenized_splits.items():
        print(f"  • {split_name} ({len(tokenized)} rows)", flush=True)
        split_metrics = trainer.evaluate(tokenized, metric_key_prefix=split_name)
        all_metrics[split_name] = split_metrics

    # --- Persist results -----------------------------------------------------
    eval_result: Dict[str, Any] = {
        "created_utc": now_iso(),
        "model_id_or_path": cfg.model_id_or_path,
        "dataset_id_or_path": cfg.dataset_id_or_path,
        "splits_evaluated": cfg.splits,
        "metrics": all_metrics,
    }
    metrics_path = output_dir / "eval_metrics.json"
    metrics_path.write_text(json.dumps(eval_result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"💾 Saved evaluation metrics to {metrics_path.as_posix()}", flush=True)

    return {"metrics": all_metrics, "eval_metrics_path": str(metrics_path.as_posix())}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser for the standalone evaluation script.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser whose ``parse_args()`` output can be passed
        directly to :func:`load_evaluation_config` via *cli_overrides*.
    """
    p = argparse.ArgumentParser(
        description="Evaluate a fine-tuned sentiment model against the processed dataset."
    )
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config (e.g. configs/evaluation.json). "
             "Supports optional top-level 'evaluation' key.",
    )
    p.add_argument(
        "--model-id-or-path",
        type=str,
        default=None,
        help="Model ID or local path to evaluate.",
    )
    p.add_argument(
        "--dataset-id-or-path",
        type=str,
        default=None,
        help="HF Dataset ID or local path to processed DatasetDict.",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Where to write eval_metrics.json (defaults to reports/).",
    )
    p.add_argument(
        "--splits",
        type=str,
        nargs="+",
        default=None,
        help="Dataset splits to evaluate (default: validation test).",
    )
    p.add_argument("--max-length", type=int, default=None, help="Tokenizer max length.")
    p.add_argument(
        "--eval-batch-size", type=int, default=None, help="Per-device evaluation batch size."
    )
    p.add_argument(
        "--max-eval-samples",
        type=int,
        default=None,
        help="Optional cap on rows evaluated per split.",
    )
    p.add_argument("--seed", type=int, default=None, help="Random seed.")
    p.add_argument("--fp16", action="store_true", default=None, help="Use FP16 inference.")
    return p


def main() -> None:
    """Entry point for running standalone evaluation from the command line.

    Parses CLI arguments, builds an :class:`EvaluationConfig`, runs
    :func:`run_evaluation`, and prints the resulting metrics JSON to stdout.

    Can be invoked via ``scripts/evaluate_model.py`` or directly as
    ``python -m machineinnovatorsinc_solution.model.evaluate``.
    """
    args = build_argparser().parse_args()
    overrides = {
        "model_id_or_path": args.model_id_or_path,
        "dataset_id_or_path": args.dataset_id_or_path,
        "output_dir": args.output_dir,
        "splits": args.splits,
        "max_length": args.max_length,
        "per_device_eval_batch_size": args.eval_batch_size,
        "max_eval_samples": args.max_eval_samples,
        "seed": args.seed,
        "fp16": True if args.fp16 else None,
    }

    cfg = load_evaluation_config(args.config, cli_overrides=overrides)
    print(
        f"🚀 Starting evaluation: model='{cfg.model_id_or_path}', "
        f"data='{cfg.dataset_id_or_path}', splits={cfg.splits}",
        flush=True,
    )
    result = run_evaluation(cfg)
    print("\n✅ Evaluation completed")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
