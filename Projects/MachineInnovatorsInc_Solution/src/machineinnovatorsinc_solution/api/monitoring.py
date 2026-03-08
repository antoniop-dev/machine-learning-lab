"""Prometheus metrics helpers for the inference API."""

from __future__ import annotations

from prometheus_client import Counter, Histogram

from .schemas import PredictionResult

PREDICTION_REQUESTS_TOTAL = Counter(
    "prediction_requests_total",
    "Total number of prediction requests handled by the API.",
    labelnames=("status", "predicted_label"),
)

PREDICTION_INPUT_CHARS = Histogram(
    "prediction_input_chars",
    "Input text length in characters for prediction requests.",
    buckets=(1, 25, 50, 100, 250, 500, 1000, 5000),
)

PREDICTION_REQUEST_DURATION_SECONDS = Histogram(
    "prediction_request_duration_seconds",
    "End-to-end latency for prediction requests.",
    labelnames=("status",),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


def record_prediction(result: PredictionResult, text_length: int, duration_seconds: float) -> None:
    """Record metrics for a successful prediction request."""
    PREDICTION_REQUESTS_TOTAL.labels(
        status="success",
        predicted_label=result.label,
    ).inc()
    PREDICTION_INPUT_CHARS.observe(text_length)
    PREDICTION_REQUEST_DURATION_SECONDS.labels(status="success").observe(duration_seconds)


def record_prediction_error(duration_seconds: float) -> None:
    """Record metrics for a failed prediction request."""
    PREDICTION_REQUESTS_TOTAL.labels(
        status="error",
        predicted_label="unknown",
    ).inc()
    PREDICTION_REQUEST_DURATION_SECONDS.labels(status="error").observe(duration_seconds)
