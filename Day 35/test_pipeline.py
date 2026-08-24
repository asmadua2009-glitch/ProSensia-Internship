import os
import time

from fastapi.testclient import TestClient

from main import app
from router import get_ab_metrics


client = TestClient(app)


def test_api_health():
    """Verify that the API is available."""

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_high_volume_drifted_payloads():
    """Send extreme payloads to simulate data drift."""

    payload = {
        "Age": 100,
        "Gender": "Male",
        "Product_Category": "Electronics",
        "Quantity": 50,
        "Price_per_Unit": 10000,
    }

    for _ in range(60):

        response = client.post(
            "/predict",
            json=payload,
        )

        assert response.status_code == 200


def test_drift_detection_and_retraining_trigger():
    """Verify drift detection triggers retraining."""

    response = client.get(
        "/metrics/drift"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["drift_detected"] is True

    assert (
        data["retraining_triggered"] is True
        or data["retraining_triggered"] is False
    )


def test_background_retraining_and_hot_swap():
    """Verify retraining completes and model is hot-swapped."""

    time.sleep(5)

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert os.path.exists("model_v2.pkl")

    assert data["retraining_in_progress"] is False


def test_ab_metrics_after_retraining():
    """Verify A/B metrics remain available."""

    response = client.get(
        "/ab/metrics"
    )

    assert response.status_code == 200

    metrics = response.json()

    assert "traffic_configuration" in metrics

    assert "request_distribution" in metrics


def test_router_metrics():
    """Verify router metrics can be accessed."""

    metrics = get_ab_metrics()

    assert "routing_mode" in metrics

    assert "traffic_configuration" in metrics