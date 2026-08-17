from fastapi.testclient import TestClient

from main import app


def test_valid_prediction():
    payload = {
        "Age": 25,
        "Gender": "Female",
        "Product_Category": "Electronics",
        "Quantity": 2,
        "Price_per_Unit": 50.0
    }

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert isinstance(data["prediction"], str)


def test_invalid_input_returns_422():
    payload = {
        "Age": 150,
        "Gender": "Female",
        "Product_Category": "Electronics",
        "Quantity": 2,
        "Price_per_Unit": 50.0
    }

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_out_of_bounds_returns_400():
    payload = {
        "Age": 25,
        "Gender": "Female",
        "Product_Category": "Electronics",
        "Quantity": 2,
        "Price_per_Unit": 800.0
    }

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)

    assert response.status_code == 400


def test_malformed_request_does_not_crash():
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            content='{"Age": 25, "Gender": "Female"'
        )

    assert response.status_code != 500