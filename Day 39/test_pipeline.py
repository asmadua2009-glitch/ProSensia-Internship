from fastapi.testclient import TestClient

from main import app
from security import settings

client = TestClient(app)


def get_valid_api_key() -> str:
    return settings.API_KEYS.split(",")[0].strip()


def valid_payload() -> dict:
    return {
        "Age": 30,
        "Gender": "Male",
        "Product_Category": "Electronics",
        "Quantity": 2,
        "Price_per_Unit": 100.0,
    }


def test_predict_missing_api_key():
    response = client.post(
        "/predict",
        json=valid_payload(),
    )

    assert response.status_code == 401


def test_predict_invalid_api_key():
    response = client.post(
        "/predict",
        json=valid_payload(),
        headers={"X-API-Key": "invalid-key"},
    )

    assert response.status_code == 401


def test_predict_invalid_input():
    payload = valid_payload()
    payload["Age"] = "invalid"

    response = client.post(
        "/predict",
        json=payload,
        headers={"X-API-Key": get_valid_api_key()},
    )

    assert response.status_code == 422


def test_predict_out_of_bound_input():
    payload = valid_payload()
    payload["Age"] = 17

    response = client.post(
        "/predict",
        json=payload,
        headers={"X-API-Key": get_valid_api_key()},
    )

    assert response.status_code == 422


def test_predict_negative_price():
    payload = valid_payload()
    payload["Price_per_Unit"] = -10

    response = client.post(
        "/predict",
        json=payload,
        headers={"X-API-Key": get_valid_api_key()},
    )

    assert response.status_code == 422


def test_predict_valid_inference():
    response = client.post(
        "/predict",
        json=valid_payload(),
        headers={"X-API-Key": get_valid_api_key()},
    )

    assert response.status_code == 200
    assert "prediction" in response.json()
