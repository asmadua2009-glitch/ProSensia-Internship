import asyncio
import threading
import time
from typing import Any

import pandas as pd
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from drift_detector import detect_drift
from retrain import train_model
from router import (
    get_ab_metrics,
    hot_swap_challenger,
    route_prediction,
    update_ab_split,
)
from schemas import PredictionInput, PredictionResponse
from security import settings, verify_api_key


# ============================================================
# RATE LIMITER
# ============================================================

limiter = Limiter(key_func=get_remote_address)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Automated End-to-End MLOps Pipeline",
    version="9.0.0",
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# ============================================================
# PROMETHEUS METRICS
# ============================================================

instrumentator = Instrumentator()

model_predictions_total = Counter(
    "model_predictions_total",
    "Total number of successful model predictions",
)

model_inference_latency_seconds = Histogram(
    "model_inference_latency_seconds",
    "Model inference latency in seconds",
)

model_inference_errors_total = Counter(
    "model_inference_errors_total",
    "Total number of model inference errors",
)

instrumentator.instrument(app).expose(
    app,
    endpoint="/metrics",
)


# ============================================================
# STRICT CORS CONFIGURATION
# ============================================================

allowed_origins = [
    origin.strip()
    for origin in settings.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Content-Type",
        "X-API-Key",
    ],
)


# ============================================================
# PRODUCTION DATA BUFFER
# ============================================================

production_data: list[dict[str, Any]] = []

buffer_lock = asyncio.Lock()

# Prevent multiple retraining jobs from running simultaneously.
retraining_lock = threading.Lock()

retraining_in_progress = False


# ============================================================
# AUTOMATED LIFECYCLE STATUS
# ============================================================

lifecycle_status: dict[str, Any] = {
    "drift_alert_triggered": False,
    "background_retraining": False,
    "retraining_completed": False,
    "model_hot_swapped": False,
    "ab_split_updated": False,
    "latest_model": "model_v1.pkl",
}


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Return API status message."""

    return {
        "message": (
            "Day 38 Observable Automated MLOps Pipeline is running."
        ),
        "version": "9.0.0",
    }


@app.get("/health")
async def health():
    """Return API health status."""

    return {
        "status": "healthy",
        "champion_model": "model_v1.pkl",
        "challenger_model": lifecycle_status[
            "latest_model"
        ],
        "retraining_in_progress": (
            retraining_in_progress
        ),
        "lifecycle": lifecycle_status.copy(),
    }


# ============================================================
# INFERENCE LOGGING
# ============================================================

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
    """Convert API input into router-compatible format."""

    return {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price_per_Unit": data.Price_per_Unit,
        "Gender": data.Gender,
        "Product_Category": data.Product_Category,
    }


# ============================================================
# BACKGROUND RETRAINING PIPELINE
# ============================================================

def run_retraining_pipeline() -> None:
    """
    Execute the automated MLOps lifecycle.

    Retrain the challenger model, hot-swap the
    new model, and update the A/B traffic split.
    """

    global retraining_in_progress

    if not retraining_lock.acquire(blocking=False):
        return

    try:
        retraining_in_progress = True

        lifecycle_status[
            "background_retraining"
        ] = True

        print(
            "Background retraining started."
        )

        # ----------------------------------------------------
        # STEP 1: RETRAIN MODEL
        # ----------------------------------------------------

        result = train_model()

        lifecycle_status[
            "retraining_completed"
        ] = True

        print(
            "Background retraining completed."
        )

        print(
            f"New model generated: "
            f"{result['model_path']}"
        )

        # ----------------------------------------------------
        # STEP 2: HOT-SWAP MODEL
        # ----------------------------------------------------

        swap_result = hot_swap_challenger()

        lifecycle_status[
            "model_hot_swapped"
        ] = True

        lifecycle_status[
            "latest_model"
        ] = swap_result["model"]

        print(
            "Model hot-swapped successfully."
        )

        # ----------------------------------------------------
        # STEP 3: UPDATE A/B TRAFFIC
        # ----------------------------------------------------

        split_result = update_ab_split(
            champion_ratio=0.50,
            challenger_ratio=0.50,
        )

        lifecycle_status[
            "ab_split_updated"
        ] = True

        print(
            "A/B traffic split updated."
        )

        print(
            f"New split: {split_result}"
        )

    except Exception as exc:

        lifecycle_status[
            "background_retraining"
        ] = False

        print(
            f"Background retraining failed: {exc}"
        )

    finally:

        retraining_in_progress = False

        lifecycle_status[
            "background_retraining"
        ] = False

        retraining_lock.release()


# ============================================================
# SECURE PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
)
@limiter.limit("10/minute")
async def predict(
    request: Request,
    data: PredictionInput,
    api_key: str = Depends(verify_api_key),
):
    """
    Run prediction using the current traffic routing.

    Requires a valid X-API-Key header and is limited
    to 10 requests per minute per client.
    """

    try:
        await log_inference_payload(data)

        router_payload = create_router_payload(
            data
        )

        # Start inference latency timer.
        start_time = time.perf_counter()

        result = await asyncio.to_thread(
            route_prediction,
            router_payload,
        )

        # Calculate model inference latency.
        inference_latency = (
            time.perf_counter() - start_time
        )

        # Record inference latency.
        model_inference_latency_seconds.observe(
            inference_latency
        )

        # Record successful prediction.
        model_predictions_total.inc()

        return PredictionResponse(
            prediction=result["prediction"]
        )

    except Exception as exc:

        # Record inference error.
        model_inference_errors_total.inc()

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc


# ============================================================
# DRIFT METRICS AND AUTOMATED RETRAINING
# ============================================================

@app.get("/metrics/drift")
async def drift_metrics(
    background_tasks: BackgroundTasks,
):
    """
    Detect statistical drift and automatically trigger
    background retraining without blocking the API.
    """

    try:

        async with buffer_lock:
            production_df = pd.DataFrame(
                production_data
            )

        if production_df.empty:

            return {
                "drift_detected": False,
                "drifted_features": [],
                "retraining_triggered": False,
                "message": (
                    "No production inference data "
                    "available yet."
                ),
                "lifecycle": lifecycle_status.copy(),
            }

        drift_result = await asyncio.to_thread(
            detect_drift,
            production_df,
        )

        if drift_result["drift_detected"]:

            lifecycle_status[
                "drift_alert_triggered"
            ] = True

            if not retraining_in_progress:

                background_tasks.add_task(
                    run_retraining_pipeline
                )

                drift_result[
                    "retraining_triggered"
                ] = True

                drift_result[
                    "message"
                ] = (
                    "Drift Alert Triggered -> "
                    "Background Retraining Started."
                )

            else:

                drift_result[
                    "retraining_triggered"
                ] = False

                drift_result[
                    "message"
                ] = (
                    "Drift detected. "
                    "Retraining already in progress."
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

        drift_result[
            "lifecycle"
        ] = lifecycle_status.copy()

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
# A/B DEPLOYMENT METRICS
# ============================================================

@app.get("/ab/metrics")
async def ab_metrics_endpoint():
    """
    Return A/B traffic metrics and automated lifecycle status.
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

        metrics[
            "automated_lifecycle"
        ] = lifecycle_status.copy()

        metrics[
            "retraining_in_progress"
        ] = retraining_in_progress

        return metrics

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "A/B metrics calculation failed: "
                f"{exc}"
            ),
        ) from exc