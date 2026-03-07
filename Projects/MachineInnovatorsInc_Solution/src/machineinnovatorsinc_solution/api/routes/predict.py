"""Prediction and health-check routes.

This module defines a single ``APIRouter`` that is registered on the
FastAPI application by :func:`~api.app.create_app`.  Keeping routes in a
dedicated module makes it straightforward to add more routers later
(e.g. ``routes/batch.py``) without touching the application factory.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from ..schemas import HealthResponse, PredictRequest, PredictionResult

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns ``200 OK`` when the model is loaded and ready to serve.",
)
async def health(request: Request) -> HealthResponse:
    """Return service health status.

    The predictor is stored in ``request.app.state.predictor``, set during
    the application lifespan in :func:`~api.app.create_app`.  If it is
    ``None``, the model hasn't finished loading and we return ``503``.
    """
    predictor = getattr(request.app.state, "predictor", None)
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded yet.",
        )
    return HealthResponse(status="ok", model=predictor.model_repo_id)


# ---------------------------------------------------------------------------
# Predict
# ---------------------------------------------------------------------------


@router.post(
    "/predict",
    response_model=PredictionResult,
    summary="Predict sentiment",
    description=(
        "Classify the sentiment of the provided text. "
        "Returns the predicted label, its integer id, and per-class softmax scores."
    ),
    status_code=status.HTTP_200_OK,
)
async def predict(request: Request, body: PredictRequest) -> PredictionResult:
    """Run sentiment classification on a single text input.

    Parameters
    ----------
    request : Request
        FastAPI request object used to access ``app.state.predictor``.
    body : PredictRequest
        JSON body containing the ``text`` field to classify.

    Returns
    -------
    PredictionResult
        Predicted label, label id, and per-class probabilities.

    Raises
    ------
    HTTPException (503)
        If the model predictor has not been initialised yet.
    HTTPException (500)
        If inference fails for any unexpected reason.
    """
    predictor = getattr(request.app.state, "predictor", None)
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded yet.",
        )

    logger.debug("Predicting for text (len=%d): %r", len(body.text), body.text[:80])

    try:
        result = predictor.predict(body.text)
    except Exception as exc:
        logger.exception("Inference failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {exc}",
        ) from exc

    logger.debug("Prediction → label=%r scores=%s", result.label, result.scores)
    return result
