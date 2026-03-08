"""Unit tests for the FastAPI application layer."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from machineinnovatorsinc_solution.api.config import ApiConfig, load_api_config
from machineinnovatorsinc_solution.api.schemas import PredictionResult


def test_load_api_config_env_override():
    """Test that environment variables correctly override default config values."""
    os.environ["API_DEVICE"] = "cpu"
    os.environ["API_MAX_LENGTH"] = "50"

    try:
        cfg = load_api_config()
        assert cfg.device == "cpu"
        assert cfg.max_length == 50
    finally:
        del os.environ["API_DEVICE"]
        del os.environ["API_MAX_LENGTH"]


@pytest.fixture
def mock_predictor():
    """Provides a mocked SentimentPredictor that does not load ML dependencies."""
    mock = MagicMock()
    mock.model_repo_id = "mock-model/1.0"
    mock.predict.return_value = PredictionResult(
        label="positive",
        label_id=2,
        scores={"negative": 0.1, "neutral": 0.2, "positive": 0.7},
    )
    return mock


@pytest.fixture
def client(mock_predictor):
    """Provides a TestClient initialized with the mock predictor."""
    from machineinnovatorsinc_solution.api.app import create_app

    with patch("machineinnovatorsinc_solution.api.app.SentimentPredictor", return_value=mock_predictor):
        app = create_app()
        with TestClient(app) as client:
            yield client


def test_health_endpoint(client, mock_predictor):
    """Test that the health endpoint returns OK when the predictor is loaded."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "mock-model/1.0"}


def test_health_endpoint_no_model():
    """Test health endpoint fails gracefully (503) if predictor is None."""
    from contextlib import asynccontextmanager

    from machineinnovatorsinc_solution.api.app import create_app

    @asynccontextmanager
    async def dummy_lifespan(app):
        app.state.predictor = None
        yield

    with patch("machineinnovatorsinc_solution.api.app._make_lifespan", return_value=dummy_lifespan):
        app = create_app()
        with TestClient(app) as client:
            response = client.get("/api/v1/health")
            assert response.status_code == 503
            assert response.json()["detail"] == "Model is not loaded yet."


def test_predict_endpoint_valid(client, mock_predictor):
    """Test the predict endpoint with valid input."""
    response = client.post("/api/v1/predict", json={"text": "I love unit testing!"})

    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "positive"
    assert data["label_id"] == 2
    assert "scores" in data

    # Verify our mock was called correctly
    mock_predictor.predict.assert_called_once_with("I love unit testing!")


def test_predict_endpoint_invalid_schema(client):
    """Test validation errors for bad input payloads."""
    # Missing 'text'
    response = client.post("/api/v1/predict", json={"wrong_key": "x"})
    assert response.status_code == 422

    # Empty 'text' string (violates min_length=1)
    response = client.post("/api/v1/predict", json={"text": ""})
    assert response.status_code == 422


def test_metrics_endpoint_exposes_prediction_metrics(client):
    """Test Prometheus metrics are exposed after serving a prediction."""
    predict_response = client.post("/api/v1/predict", json={"text": "Monitoring test"})
    assert predict_response.status_code == 200

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "prediction_requests_total" in response.text
    assert 'predicted_label="positive"' in response.text
    assert "prediction_request_duration_seconds" in response.text
