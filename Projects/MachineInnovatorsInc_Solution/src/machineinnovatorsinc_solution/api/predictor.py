"""Sentiment predictor — loads the fine-tuned model and runs inference.

Designed to be instantiated **once** at application startup and kept alive
for the lifetime of the process (via FastAPI's lifespan context).

The predictor has no knowledge of HTTP concerns; it only deals with raw
text → :class:`~api.schemas.PredictionResult` conversions so it can be
tested independently of the web layer.

``torch`` and ``transformers`` are **lazy-imported** inside the methods
that need them so this module can be imported in lightweight environments
(e.g. for config validation or testing) without requiring ML deps.
"""

from __future__ import annotations

import logging
from typing import List

from .schemas import PredictionResult

logger = logging.getLogger(__name__)

# Canonical label mapping — matches the fine-tuning pipeline
ID2LABEL: dict[int, str] = {0: "negative", 1: "neutral", 2: "positive"}


class SentimentPredictor:
    """Wraps a HuggingFace sequence-classification model for inference.

    Parameters
    ----------
    model_repo_id : str
        HuggingFace Hub identifier **or** local directory path for the
        fine-tuned model.
    max_length : int
        Tokenizer truncation length.
    device : str
        ``"auto"``, ``"cpu"``, or ``"cuda"``.  ``"auto"`` picks CUDA when
        a GPU is available, otherwise falls back to CPU.

    Examples
    --------
    >>> predictor = SentimentPredictor("antoniop-dev/sentiment-model-finetuned")
    >>> result = predictor.predict("This is amazing!")
    >>> result.label
    'positive'
    """

    def __init__(
        self,
        model_repo_id: str,
        max_length: int = 96,
        device: str = "auto",
    ) -> None:
        import torch  # noqa: F401  (validates dependency at instantiation time)
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.model_repo_id = model_repo_id
        self.max_length = max_length
        self.device = self._resolve_device(device)

        logger.info("Loading tokenizer from '%s'", model_repo_id)
        self._tokenizer = AutoTokenizer.from_pretrained(
            model_repo_id,
            use_fast=True,
        )

        logger.info("Loading model from '%s' onto device '%s'", model_repo_id, self.device)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_repo_id)
        self._model.to(self.device)
        self._model.eval()

        logger.info("Predictor ready — label map: %s", ID2LABEL)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, text: str) -> PredictionResult:
        """Classify a single piece of text.

        Parameters
        ----------
        text : str
            Raw input text.

        Returns
        -------
        PredictionResult
            Predicted label, label id, and per-class softmax scores.
        """
        return self.predict_batch([text])[0]

    def predict_batch(self, texts: List[str]) -> List[PredictionResult]:
        """Classify a batch of texts in a single forward pass.

        Parameters
        ----------
        texts : List[str]
            List of raw input texts.

        Returns
        -------
        List[PredictionResult]
            One :class:`~api.schemas.PredictionResult` per input text,
            in the same order.
        """
        import torch
        import torch.nn.functional as F

        encoding = self._tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        # Move inputs to the same device as the model
        encoding = {k: v.to(self.device) for k, v in encoding.items()}

        with torch.no_grad():
            logits = self._model(**encoding).logits  # (batch, num_labels)

        probs = F.softmax(logits, dim=-1).cpu().tolist()  # list of lists
        pred_ids = logits.argmax(dim=-1).cpu().tolist()   # list of ints

        results = []
        for pred_id, prob_row in zip(pred_ids, probs):
            scores = {ID2LABEL[i]: round(p, 6) for i, p in enumerate(prob_row)}
            results.append(
                PredictionResult(
                    label=ID2LABEL[pred_id],
                    label_id=pred_id,
                    scores=scores,
                )
            )
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_device(device: str) -> str:
        """Resolve ``"auto"`` to the best available device string.

        Parameters
        ----------
        device : str
            ``"auto"``, ``"cpu"``, or ``"cuda"``.

        Returns
        -------
        str
            ``"cuda"`` or ``"cpu"``.
        """
        import torch

        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
