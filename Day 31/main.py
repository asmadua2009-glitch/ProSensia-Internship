import asyncio
import os

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from schemas import PredictionInput, PredictionResponse


MODEL_PATH = os.getenv("MODEL_PATH", "trained_model.pkl")
PIPELINE_PATH = os.getenv("PIPELINE_PATH", "pipeline.pkl")


app = FastAPI(
    title="High Value Transaction Prediction API",
    version="2.0.0",
)


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

    return {"message": "API is Running Successfully"}


@app.get("/health")
async def health():
    """Return API health status."""

    return {"status": "healthy"}


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
    """Receive raw input and return prediction."""

    try:
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