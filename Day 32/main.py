import asyncio
import os
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from drift_detector import detect_drift
from schemas import PredictionInput, PredictionResponse


MODEL_PATH = os.getenv("MODEL_PATH", "trained_model.pkl")
PIPELINE_PATH = os.getenv("PIPELINE_PATH", "pipeline.pkl")


app = FastAPI(
    title="High Value Transaction Prediction API",
    version="3.0.0",
)


# In-memory production inference buffer
production_data: list[dict[str, Any]] = []
buffer_lock = asyncio.Lock()


try:
    model = joblib.load(MODEL_PATH)
    pipeline = joblib.load(PIPELINE_PATH)
except Exception as exc:
    raise RuntimeError(
        f"Failed to load model or pipeline: {exc}"
    ) from exc


@app.get("/")
async def root():
    """Return API status message."""

    return {
        "message": "API is Running Successfully"
    }


@app.get("/health")
async def health():
    """Return API health status."""

    return {
        "status": "healthy"
    }


async def log_inference_payload(data: PredictionInput) -> None:
    """Store incoming production inference payload asynchronously."""

    payload = {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
    }

    async with buffer_lock:
        production_data.append(payload)


def make_prediction(data: PredictionInput):
    """Preprocess raw input and generate prediction."""

    input_data = {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
    }

    input_df = pd.DataFrame([input_data])

    transformed_data = pipeline.transform(input_df)

    prediction = model.predict(transformed_data)

    return float(prediction[0])


@app.post("/predict", response_model=PredictionResponse)
async def predict(data: PredictionInput):
    """Receive input, log it, and return prediction."""

    try:
        # Asynchronously store production request
        await log_inference_payload(data)

        # Run CPU-bound prediction in worker thread
        result = await asyncio.to_thread(
            make_prediction,
            data,
        )

        return PredictionResponse(
            prediction=result
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc


@app.get("/metrics/drift")
async def drift_metrics():
    """Return statistical data drift metrics."""

    try:
        async with buffer_lock:
            production_df = pd.DataFrame(production_data)

        if production_df.empty:
            return {
                "drift_detected": False,
                "drifted_features": [],
                "message": "No production inference data available yet.",
            }

        drift_result = await asyncio.to_thread(
            detect_drift,
            production_df,
        )

        return drift_result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Drift detection failed: {exc}",
        ) from exc