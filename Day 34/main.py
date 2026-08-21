import asyncio
import threading
from typing import Any

import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException

from drift_detector import detect_drift
from router import get_ab_metrics, route_prediction
from schemas import PredictionInput, PredictionResponse


app = FastAPI(
    title="High Value Transaction Prediction API",
    version="5.0.0",
)


# ============================================================
# PRODUCTION DATA BUFFER
# ============================================================

production_data: list[dict[str, Any]] = []
buffer_lock = asyncio.Lock()


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Return API status message."""

    return {
        "message": (
            "Day 34 API is running successfully. "
            "Shadow Deployment and A/B Routing are active."
        )
    }


@app.get("/health")
async def health():
    """Return API health status."""

    return {
        "status": "healthy",
        "champion_model": "model_v1.pkl",
        "challenger_model": "model_v2.pkl",
    }


async def log_inference_payload(
    data: PredictionInput,
) -> None:
    """Store incoming inference payload for drift detection."""

    payload = {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
    }

    async with buffer_lock:
        production_data.append(payload)


def create_router_payload(
    data: PredictionInput,
) -> dict[str, Any]:
    """Convert API input into router-compatible payload."""

    return {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price_per_Unit": data.Price_per_Unit,
        "Gender": data.Gender,
        "Product_Category": data.Product_Category,
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
)
async def predict(
    data: PredictionInput,
):
    """
    Run inference through the Day 34 model router.

    In Shadow Mode:
    Champion prediction is returned while Challenger
    prediction runs for comparison.

    In A/B Mode:
    Traffic is dynamically routed according to the
    configured traffic split.
    """

    try:
        await log_inference_payload(data)

        router_payload = create_router_payload(data)

        result = await asyncio.to_thread(
            route_prediction,
            router_payload,
        )

        return PredictionResponse(
            prediction=result["prediction"]
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc


# ============================================================
# DRIFT METRICS ENDPOINT
# ============================================================

@app.get("/metrics/drift")
async def drift_metrics(
    background_tasks: BackgroundTasks,
):
    """Detect production data drift."""

    try:
        async with buffer_lock:
            production_df = pd.DataFrame(
                production_data
            )

        if production_df.empty:
            return {
                "drift_detected": False,
                "drifted_features": [],
                "message": (
                    "No production inference data "
                    "available yet."
                ),
            }

        drift_result = await asyncio.to_thread(
            detect_drift,
            production_df,
        )

        if drift_result["drift_detected"]:
            drift_result[
                "retraining_triggered"
            ] = True

            drift_result[
                "message"
            ] = (
                "Data drift detected. "
                "Challenger model evaluation is active."
            )

        else:
            drift_result[
                "retraining_triggered"
            ] = False

            drift_result[
                "message"
            ] = (
                "No significant data drift detected."
            )

        return drift_result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Drift detection failed: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# A/B AND SHADOW DEPLOYMENT METRICS
# ============================================================

@app.get("/ab/metrics")
async def ab_metrics_endpoint():
    """
    Return Champion vs Challenger comparison metrics.

    Includes:
    - Request distribution
    - Average latency comparison
    - Prediction agreement
    - Drift statistics
    """

    try:
        async with buffer_lock:
            production_df = pd.DataFrame(
                production_data
            )

        drift_data = None

        if not production_df.empty:
            drift_data = await asyncio.to_thread(
                detect_drift,
                production_df,
            )

        metrics = get_ab_metrics(
            drift_data=drift_data,
        )

        return metrics

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "A/B metrics calculation failed: "
                f"{exc}"
            ),
        ) from exc