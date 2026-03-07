"""Unit tests for model evaluation and metrics logic."""

from math import isclose

import numpy as np

from machineinnovatorsinc_solution.model.evaluate import build_compute_metrics


def test_build_compute_metrics():
    """Test accuracy and macro-F1 calculations from dummy logits."""
    compute_metrics = build_compute_metrics()

    # Create dummy logits for 3 classes
    # Shape: (4 samples, 3 classes)
    logits = np.array([
        [1.0, 5.0, 0.1],  # Pred: class 1 (neutral)
        [0.2, 0.5, 3.0],  # Pred: class 2 (positive)
        [4.0, 0.1, 0.2],  # Pred: class 0 (negative)
        [0.1, 0.9, 0.8],  # Pred: class 1 (neutral)
    ])

    # True labels
    labels = np.array([1, 2, 0, 2])

    # Predictions:  [1, 2, 0, 1]
    # Ground truth: [1, 2, 0, 2]
    # Accuracy: 3 / 4 = 0.75

    eval_pred = (logits, labels)
    results = compute_metrics(eval_pred)

    assert "accuracy" in results
    assert "macro_f1" in results

    assert isclose(results["accuracy"], 0.75)
    # F1 for class 0 (neg): True Pos = 1, False Pos = 0, False Neg = 0 -> F1 = 1.0
    # F1 for class 1 (neu): True Pos = 1, False Pos = 1, False Neg = 0 -> F1 = 0.666...
    # F1 for class 2 (pos): True Pos = 1, False Pos = 0, False Neg = 1 -> F1 = 0.666...
    # Macro F1 = (1.0 + 0.666... + 0.666...) / 3 = 0.777...
    assert isclose(results["macro_f1"], 0.7777777777777778)
