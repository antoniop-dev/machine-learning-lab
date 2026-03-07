#!/usr/bin/env python3
"""Decide whether retraining should be triggered from evaluation metrics."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def _as_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _set_github_output(key: str, value: str) -> None:
    output_file = os.getenv("GITHUB_OUTPUT")
    if not output_file:
        return
    safe_value = value.replace("\n", " ").strip()
    with open(output_file, "a", encoding="utf-8") as fh:
        fh.write(f"{key}={safe_value}\n")


def _extract_split_metrics(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    metrics = payload.get("metrics")
    if isinstance(metrics, dict) and all(isinstance(v, dict) for v in metrics.values()):
        return metrics  # standalone evaluation output

    fallback: Dict[str, Dict[str, Any]] = {}
    for split in ("train", "validation", "test", "eval"):
        value = payload.get(split)
        if isinstance(value, dict):
            fallback[split] = value  # training metrics output
    if fallback:
        return fallback

    # Last-resort format: flat metric map at root level.
    return {"root": payload}


def _extract_metrics_for_split(split: str, values: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    accuracy_keys = [f"{split}_accuracy", "accuracy", "eval_accuracy", "test_accuracy", "validation_accuracy"]
    macro_f1_keys = [f"{split}_macro_f1", "macro_f1", "eval_macro_f1", "test_macro_f1", "validation_macro_f1"]

    accuracy = next((_as_float(values.get(key)) for key in accuracy_keys if key in values), None)
    macro_f1 = next((_as_float(values.get(key)) for key in macro_f1_keys if key in values), None)
    return accuracy, macro_f1


def _select_observed_metrics(
    split_metrics: Dict[str, Dict[str, Any]],
    prefer_split: str,
) -> Tuple[str, Optional[float], Optional[float]]:
    order = [prefer_split, "test", "validation", "eval", "train", "root"]
    order.extend(split_metrics.keys())

    seen = set()
    for split in order:
        if split in seen or split not in split_metrics:
            continue
        seen.add(split)
        accuracy, macro_f1 = _extract_metrics_for_split(split, split_metrics[split])
        if accuracy is not None or macro_f1 is not None:
            return split, accuracy, macro_f1

    return "unknown", None, None


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check whether retraining is needed from eval metrics.")
    parser.add_argument("--metrics-path", type=Path, required=True, help="Path to eval metrics JSON.")
    parser.add_argument("--min-accuracy", type=float, default=0.80, help="Minimum acceptable accuracy.")
    parser.add_argument("--min-macro-f1", type=float, default=0.78, help="Minimum acceptable macro F1.")
    parser.add_argument(
        "--prefer-split",
        type=str,
        default="test",
        help="Split to prefer when reading metrics (default: test).",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=None,
        help="Optional path where a decision summary JSON is written.",
    )
    return parser


def main() -> None:
    args = _build_argparser().parse_args()

    if not args.metrics_path.exists():
        raise FileNotFoundError(f"Metrics file not found: {args.metrics_path}")

    payload = json.loads(args.metrics_path.read_text(encoding="utf-8"))
    split_metrics = _extract_split_metrics(payload)
    split, accuracy, macro_f1 = _select_observed_metrics(split_metrics, prefer_split=args.prefer_split)

    reasons = []
    retrain_needed = False

    if accuracy is None:
        retrain_needed = True
        reasons.append("accuracy_not_found")
    elif accuracy < args.min_accuracy:
        retrain_needed = True
        reasons.append(f"accuracy_below_threshold({accuracy:.4f} < {args.min_accuracy:.4f})")

    if macro_f1 is None:
        retrain_needed = True
        reasons.append("macro_f1_not_found")
    elif macro_f1 < args.min_macro_f1:
        retrain_needed = True
        reasons.append(f"macro_f1_below_threshold({macro_f1:.4f} < {args.min_macro_f1:.4f})")

    if not reasons:
        reasons.append("metrics_meet_thresholds")

    decision = {
        "metrics_path": str(args.metrics_path.as_posix()),
        "evaluated_split": split,
        "observed_accuracy": accuracy,
        "observed_macro_f1": macro_f1,
        "thresholds": {
            "min_accuracy": args.min_accuracy,
            "min_macro_f1": args.min_macro_f1,
        },
        "retrain_needed": retrain_needed,
        "decision_reason": "; ".join(reasons),
    }

    if args.summary_path is not None:
        args.summary_path.parent.mkdir(parents=True, exist_ok=True)
        args.summary_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    print(json.dumps(decision, indent=2))

    _set_github_output("retrain_needed", str(retrain_needed).lower())
    _set_github_output("evaluated_split", split)
    _set_github_output("observed_accuracy", "" if accuracy is None else f"{accuracy:.6f}")
    _set_github_output("observed_macro_f1", "" if macro_f1 is None else f"{macro_f1:.6f}")
    _set_github_output("decision_reason", decision["decision_reason"])


if __name__ == "__main__":
    main()
