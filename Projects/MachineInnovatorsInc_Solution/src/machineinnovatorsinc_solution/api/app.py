"""FastAPI application factory.

Usage
-----
Direct::

    uvicorn machineinnovatorsinc_solution.api.app:create_app --factory

Via the serve script::

    python scripts/serve.py
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from .config import ApiConfig, load_api_config
from .predictor import SentimentPredictor
from .routes.predict import router as predict_router

logger = logging.getLogger(__name__)


def _make_lifespan(cfg: ApiConfig):
    """Return an async lifespan context manager bound to *cfg*.

    Loads the :class:`~api.predictor.SentimentPredictor` on startup and
    stores it in ``app.state.predictor`` so route handlers can access it
    via ``request.app.state.predictor``.

    On shutdown the model reference is released so the GC can reclaim GPU
    memory if needed.

    Parameters
    ----------
    cfg : ApiConfig
        Validated API configuration.

    Returns
    -------
    Callable
        An ``asynccontextmanager`` suitable for FastAPI's ``lifespan`` argument.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        logger.info(
            "Loading model '%s' (device=%s, max_length=%d)",
            cfg.model_repo_id,
            cfg.device,
            cfg.max_length,
        )
        app.state.predictor = SentimentPredictor(
            model_repo_id=cfg.model_repo_id,
            max_length=cfg.max_length,
            device=cfg.device,
        )
        logger.info("Model loaded — ready to serve.")

        yield  # application runs here

        logger.info("Shutting down — releasing model.")
        app.state.predictor = None

    return lifespan


def create_app(config_path: str | None = "configs/api.json") -> FastAPI:
    """Build and return the configured FastAPI application.

    Parameters
    ----------
    config_path : str | None
        Path to the JSON config file.  Defaults to ``"configs/api.json"``.
        Pass ``None`` to rely entirely on environment variables / defaults.

    Returns
    -------
    FastAPI
        Fully configured application instance ready for ``uvicorn``.
    """
    cfg = load_api_config(config_path)

    logging.basicConfig(level=cfg.log_level.upper())

    app = FastAPI(
        title="MachineInnovatorsInc — Sentiment API",
        description=(
            "Real-time sentiment classification powered by a fine-tuned "
            "HuggingFace transformer model."
        ),
        version="0.1.0",
        lifespan=_make_lifespan(cfg),
    )

    app.include_router(predict_router, prefix="/api/v1")
    app.mount("/metrics", make_asgi_app())

    return app
