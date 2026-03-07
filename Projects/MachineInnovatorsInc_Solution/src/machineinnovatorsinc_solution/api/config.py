"""API configuration.

Reads settings from environment variables or a JSON config file.
All values have sensible defaults so the server can start with zero config.

Environment variable prefix: ``API_``

Examples
--------
Start with defaults::

    python scripts/serve.py

Override model via env var::

    API_MODEL_REPO_ID=my-org/my-model python scripts/serve.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ApiConfig(BaseModel):
    """Validated, immutable configuration for the inference API server.

    Attributes
    ----------
    model_repo_id : str
        HuggingFace Hub model identifier **or** a local directory path to load
        the fine-tuned model from.
    max_length : int
        Maximum tokenised sequence length passed to the tokenizer.
    device : str
        Compute device.  ``"auto"`` picks CUDA if available, else CPU.
    log_level : str
        Uvicorn/application log level (``"debug"``, ``"info"``, ``"warning"``
        or ``"error"``).
    """

    model_repo_id: str = Field(
        default="antoniop-dev/sentiment-model-finetuned",
        description="HuggingFace Hub model ID or local path.",
    )
    max_length: int = Field(
        default=96,
        gt=0,
        description="Tokenizer max sequence length.",
    )
    device: Literal["auto", "cpu", "cuda"] = Field(
        default="auto",
        description="Inference device. 'auto' selects CUDA when available.",
    )
    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info",
        description="Application log level.",
    )


def load_api_config(path: Optional[str] = None) -> ApiConfig:
    """Build a validated :class:`ApiConfig` from an optional JSON file and env vars.

    Resolution order (later wins):

    1. Built-in defaults on :class:`ApiConfig`.
    2. Values in the JSON file at *path*, scoped to an optional ``"api"`` key.
    3. Environment variables prefixed with ``API_`` (upper-cased field names).

    Parameters
    ----------
    path : Optional[str]
        Path to a JSON config file.  ``None`` silently skips file loading.

    Returns
    -------
    ApiConfig
        Fully validated, immutable configuration object.

    Raises
    ------
    FileNotFoundError
        If *path* is given but the file does not exist.
    ValueError
        If Pydantic validation fails.
    """
    cfg: dict = {}

    if path:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"API config file not found: {p}")
        raw = json.loads(p.read_text(encoding="utf-8"))
        # Support optional top-level "api" key
        cfg = raw.get("api", raw)

    # Environment variable overrides (prefix: API_)
    env_overrides = {
        field: os.environ[f"API_{field.upper()}"]
        for field in ApiConfig.model_fields
        if f"API_{field.upper()}" in os.environ
    }

    payload = {**cfg, **env_overrides}
    return ApiConfig.model_validate(payload)
