"""Synthetic startup traffic generator for the prediction API.

This module is intended for demo environments where Grafana dashboards
should show non-empty, realistic-looking traffic shortly after startup.
It sends a one-shot burst of mixed sentiment requests to the running API.
"""

from __future__ import annotations

import argparse
import random
import time
from collections import Counter
from typing import Iterable

import httpx

POSITIVE_OPENERS = [
    "I really like",
    "I am impressed by",
    "I am happy with",
    "I trust",
    "I genuinely appreciate",
]

NEUTRAL_OPENERS = [
    "I find",
    "I think",
    "I noticed",
    "I would describe",
    "I see",
]

NEGATIVE_OPENERS = [
    "I dislike",
    "I am frustrated by",
    "I am disappointed with",
    "I do not trust",
    "I regret using",
]

SUBJECTS = [
    "the platform",
    "the service",
    "the application",
    "the dashboard",
    "the workflow",
    "the interface",
    "the deployment",
    "the overall experience",
]

POSITIVE_DESCRIPTORS = [
    "because it feels reliable and smooth",
    "because the results are excellent",
    "because everything works quickly",
    "because the experience is genuinely pleasant",
    "because it has been consistently helpful",
]

NEUTRAL_DESCRIPTORS = [
    "because it seems acceptable for everyday use",
    "because the overall experience feels fairly standard",
    "because the results are ordinary and predictable",
    "because it works about as expected",
    "because nothing stands out too much either way",
]

NEGATIVE_DESCRIPTORS = [
    "because it feels unreliable and clumsy",
    "because the results are disappointing",
    "because everything takes too long",
    "because the experience is genuinely frustrating",
    "because it has created unnecessary friction",
]

TIME_CONTEXTS = [
    "today",
    "this week",
    "during testing",
    "in production",
    "for our team",
]


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send one-shot synthetic prediction traffic to the running API."
    )
    parser.add_argument(
        "--base-url",
        default="http://backend:8000/api/v1",
        help="API base URL including version prefix (default: http://backend:8000/api/v1).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=250,
        help="Total number of prediction requests to send (default: 250).",
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=15.0,
        help="HTTP timeout for individual requests (default: 15).",
    )
    parser.add_argument(
        "--max-startup-wait-seconds",
        type=float,
        default=120.0,
        help="Maximum time to wait for the backend health endpoint (default: 120).",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=2.0,
        help="Polling interval while waiting for backend health (default: 2).",
    )
    parser.add_argument(
        "--sleep-between-requests-seconds",
        type=float,
        default=0.05,
        help="Small delay between requests to avoid an unrealistically sharp burst (default: 0.05).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic synthetic traffic generation (default: 42).",
    )
    return parser


def _allocate_label_counts(total_count: int) -> Counter[str]:
    """Allocate request counts across positive, neutral, and negative prompts."""
    if total_count <= 0:
        raise ValueError("count must be > 0")

    weights = {
        "positive": 0.45,
        "neutral": 0.25,
        "negative": 0.30,
    }
    allocated = Counter(
        {label: int(total_count * weight) for label, weight in weights.items()}
    )
    remainder = total_count - sum(allocated.values())

    for label in ("positive", "neutral", "negative"):
        if remainder == 0:
            break
        allocated[label] += 1
        remainder -= 1

    return allocated


def _build_phrase_bank(label: str) -> list[str]:
    """Create a reusable phrase bank for the given intended label."""
    if label == "positive":
        openers = POSITIVE_OPENERS
        descriptors = POSITIVE_DESCRIPTORS
    elif label == "neutral":
        openers = NEUTRAL_OPENERS
        descriptors = NEUTRAL_DESCRIPTORS
    elif label == "negative":
        openers = NEGATIVE_OPENERS
        descriptors = NEGATIVE_DESCRIPTORS
    else:
        raise ValueError(f"Unknown label: {label}")

    phrases = []
    for opener in openers:
        for subject in SUBJECTS:
            for descriptor in descriptors:
                for time_context in TIME_CONTEXTS:
                    phrases.append(f"{opener} {subject} {descriptor} {time_context}.")
    return phrases


def build_request_texts(total_count: int, seed: int = 42) -> list[tuple[str, str]]:
    """Build a deterministic set of synthetic request texts."""
    rng = random.Random(seed)
    allocations = _allocate_label_counts(total_count)

    requests: list[tuple[str, str]] = []
    for label, requested_count in allocations.items():
        bank = _build_phrase_bank(label)
        rng.shuffle(bank)
        for index in range(requested_count):
            requests.append((label, bank[index % len(bank)]))

    rng.shuffle(requests)
    return requests


def _wait_for_backend(
    client: httpx.Client,
    health_url: str,
    max_wait_seconds: float,
    poll_interval_seconds: float,
) -> None:
    """Block until the backend health endpoint responds with HTTP 200."""
    deadline = time.monotonic() + max_wait_seconds
    last_error: str | None = None

    while time.monotonic() < deadline:
        try:
            response = client.get(health_url)
            if response.status_code == 200:
                return
            last_error = f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            last_error = str(exc)
        time.sleep(poll_interval_seconds)

    raise RuntimeError(
        f"Backend did not become healthy within {max_wait_seconds:.1f}s"
        f" (last_error={last_error})"
    )


def _send_requests(
    client: httpx.Client,
    predict_url: str,
    requests: Iterable[tuple[str, str]],
    sleep_between_requests_seconds: float,
) -> Counter[str]:
    """Send synthetic traffic and count predicted labels."""
    observed = Counter()

    for intended_label, text in requests:
        response = client.post(predict_url, json={"text": text})
        response.raise_for_status()
        predicted_label = response.json()["label"]
        observed[predicted_label] += 1
        print(
            "seed_request intended_label=%s predicted_label=%s text=%r"
            % (intended_label, predicted_label, text[:96]),
            flush=True,
        )
        if sleep_between_requests_seconds > 0:
            time.sleep(sleep_between_requests_seconds)

    return observed


def main() -> None:
    args = _build_argparser().parse_args()

    predict_url = f"{args.base_url.rstrip('/')}/predict"
    health_url = f"{args.base_url.rstrip('/')}/health"
    synthetic_requests = build_request_texts(args.count, seed=args.seed)

    with httpx.Client(timeout=args.request_timeout_seconds) as client:
        print(f"Waiting for backend health at {health_url}", flush=True)
        _wait_for_backend(
            client,
            health_url=health_url,
            max_wait_seconds=args.max_startup_wait_seconds,
            poll_interval_seconds=args.poll_interval_seconds,
        )
        print(
            f"Backend is healthy. Sending {len(synthetic_requests)} synthetic prediction requests.",
            flush=True,
        )
        observed = _send_requests(
            client,
            predict_url=predict_url,
            requests=synthetic_requests,
            sleep_between_requests_seconds=args.sleep_between_requests_seconds,
        )

    print(
        "seed_summary total=%d positive=%d neutral=%d negative=%d"
        % (
            len(synthetic_requests),
            observed["positive"],
            observed["neutral"],
            observed["negative"],
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
