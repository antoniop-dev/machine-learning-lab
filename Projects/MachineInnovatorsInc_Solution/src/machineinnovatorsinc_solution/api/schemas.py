"""Request / response Pydantic schemas for the inference API.

Kept separate from :mod:`predictor` so that schemas can be reused by tests,
client libraries, or OpenAPI documentation without importing ML dependencies.
"""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Input payload for the ``POST /predict`` endpoint.

    Attributes
    ----------
    text : str
        Raw text to classify.  Must be non-empty.
    """

    text: str = Field(..., min_length=1, description="Text to classify.")

    model_config = {"json_schema_extra": {"examples": [{"text": "I love this product!"}]}}


class PredictionResult(BaseModel):
    """Prediction response returned by ``POST /predict``.

    Attributes
    ----------
    label : str
        Human-readable predicted class label (e.g. ``"positive"``).
    label_id : int
        Integer class index corresponding to *label*.
    scores : Dict[str, float]
        Softmax probability for every class, keyed by label name.
    """

    label: str = Field(..., description="Predicted class label.")
    label_id: int = Field(..., description="Integer class index.")
    scores: Dict[str, float] = Field(..., description="Per-class softmax probabilities.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "label": "positive",
                    "label_id": 2,
                    "scores": {"negative": 0.03, "neutral": 0.07, "positive": 0.90},
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Response schema for the ``GET /health`` endpoint.

    Attributes
    ----------
    status : str
        Always ``"ok"`` when the service is healthy.
    model : str
        The model identifier that was loaded.
    """

    status: str = Field(default="ok")
    model: str = Field(..., description="Loaded model identifier.")
