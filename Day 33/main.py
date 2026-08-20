import asyncio
import os
import threading
from typing import Any

import joblib
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException

from drift_detector import detect_drift
from retrain import train_model
from schemas import PredictionInput, PredictionResponse


MODEL_PATH = os.getenv("MODEL_PATH", "trained_model.pkl")
PIPELINE_PATH = os.getenv("PIPELINE_PATH", "pipeline.pkl")

MIN_F1_SCORE = 0.50


class ModelManager:
    """Manage thread-safe model and pipeline hot-swapping."""

    def __init__(self, model_path: str, pipeline_path: str):
        """Load the initial production model and pipeline."""

        self.lock = threading.Lock()
        self.model = joblib.load(model_path)
        self.pipeline = joblib.load(pipeline_path)
        self.model_version = "model_v1.pkl"

    def get_model_and_pipeline(self):
        """Return the current model and pipeline safely."""

        with self.lock:
            return self.model, self.pipeline, self.model_version

    def hot_swap(
        self,
        model_path: str,
        pipeline_path: str,
    ) -> None:
        """Atomically replace the model and pipeline in memory."""

        new_model = joblib.load(model_path)
        new_pipeline = joblib.load(pipeline_path)

        with self.lock:
            self.model = new_model
            self.pipeline = new_pipeline
            self.model_version = os.path.basename(model_path)


app = FastAPI(
    title="High Value Transaction Prediction API",
    version="4.0.0",
)


production_data: list[dict[str, Any]] = []
buffer_lock = asyncio.Lock()

model_manager = ModelManager(
    MODEL_PATH,
    PIPELINE_PATH,
)

retraining_lock = threading.Lock()
retraining_in_progress = False


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
        "status": "healthy",
        "model_version": model_manager.model_version,
    }


async def log_inference_payload(
    data: PredictionInput,
) -> None:
    """Store incoming production inference payload."""

    payload = {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
    }

    async with buffer_lock:
        production_data.append(payload)


def make_prediction(
    data: PredictionInput,
) -> float:
    """Generate a prediction using the current model."""

    model, pipeline, _ = (
        model_manager.get_model_and_pipeline()
    )

    input_data = {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
    }

    input_df = pd.DataFrame([input_data])

    transformed_data = pipeline.transform(
        input_df
    )

    prediction = model.predict(
        transformed_data
    )

    return float(prediction[0])


def run_retraining() -> None:
    """Run retraining and hot-swap validated artifacts."""

    global retraining_in_progress

    with retraining_lock:
        if retraining_in_progress:
            print(
                "Retraining already in progress."
            )
            return

        retraining_in_progress = True

    try:
        print(
            "Drift detected. "
            "Starting background retraining..."
        )

        result = train_model()

        f1_score = result["f1_score"]

        print(
            f"Retraining completed. "
            f"F1 Score: {f1_score}"
        )

        if f1_score < MIN_F1_SCORE:
            print(
                "New model failed validation. "
                "Production model unchanged."
            )
            return

        model_manager.hot_swap(
            result["model_path"],
            result["pipeline_path"],
        )

        print(
            "Model hot-swapped successfully: "
            f"{result['model_path']}"
        )

    except Exception as exc:
        print(
            f"Retraining failed: {exc}"
        )

    finally:
        with retraining_lock:
            retraining_in_progress = False


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
async def predict(
    data: PredictionInput,
):
    """Receive input and return prediction."""

    try:
        await log_inference_payload(data)

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
async def drift_metrics(
    background_tasks: BackgroundTasks,
):
    """Detect drift and trigger background retraining."""

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
            background_tasks.add_task(
                run_retraining
            )

            drift_result[
                "retraining_triggered"
            ] = True

            drift_result[
                "message"
            ] = (
                "Data drift detected. "
                "Background retraining triggered."
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