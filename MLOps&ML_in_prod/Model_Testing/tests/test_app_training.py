from fastapi.testclient import TestClient
from src.app_train import app

client = TestClient(app)

def test_root_endpoint():
    data = {
        "X": [1, 2, 3, 4, 5],
        "y": [2, 4, 6, 8, 10]
    }

    response = client.post("/training", json=data)

    assert response.status_code == 200, response.json()
    assert type(response.json()["mse"]) == float