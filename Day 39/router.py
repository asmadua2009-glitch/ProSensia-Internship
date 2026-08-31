import threading
import time
from typing import Any

import joblib
import numpy as np
import pandas as pd

# ============================================================
# DAY 35 MODEL ROUTING CONFIGURATION
# ============================================================

ROUTING_MODE = "ab"

CHAMPION_TRAFFIC = 0.80
CHALLENGER_TRAFFIC = 0.20

# ============================================================
# MODEL PATHS
# ============================================================

CHAMPION_MODEL_PATH = "model_v1.pkl"
CHALLENGER_MODEL_PATH = "model_v2.pkl"

CHAMPION_PIPELINE_PATH = "pipeline.pkl"
CHALLENGER_PIPELINE_PATH = "pipeline_v2.pkl"

# ============================================================
# THREAD-SAFE MODEL REFERENCES
# ============================================================

model_lock = threading.Lock()

champion_model = joblib.load(CHAMPION_MODEL_PATH)
champion_pipeline = joblib.load(CHAMPION_PIPELINE_PATH)

challenger_model = joblib.load(CHALLENGER_MODEL_PATH)
challenger_pipeline = joblib.load(CHALLENGER_PIPELINE_PATH)

challenger_model_version = "model_v2.pkl"

# ============================================================
# METRICS STORAGE
# ============================================================

ab_metrics: dict[str, Any] = {
    "total_requests": 0,
    "champion_requests": 0,
    "challenger_requests": 0,
    "champion_latencies": [],
    "challenger_latencies": [],
    "champion_predictions": [],
    "challenger_predictions": [],
    "prediction_matches": 0,
}

# ============================================================
# HOT-SWAP FUNCTION
# ============================================================


def hot_swap_challenger() -> dict[str, str]:
    """Load the newly retrained challenger model and pipeline."""

    global challenger_model
    global challenger_pipeline
    global challenger_model_version

    new_model = joblib.load(CHALLENGER_MODEL_PATH)
    new_pipeline = joblib.load(CHALLENGER_PIPELINE_PATH)

    with model_lock:
        challenger_model = new_model
        challenger_pipeline = new_pipeline
        challenger_model_version = "model_v2.pkl"

    return {
        "status": "success",
        "model": challenger_model_version,
    }


# ============================================================
# A/B TRAFFIC UPDATE
# ============================================================


def update_ab_split(
    champion_ratio: float = 0.50,
    challenger_ratio: float = 0.50,
) -> dict[str, float]:
    """Update A/B traffic allocation safely."""

    global CHAMPION_TRAFFIC
    global CHALLENGER_TRAFFIC

    if champion_ratio + challenger_ratio != 1.0:
        raise ValueError("Traffic ratios must add up to 1.0.")

    with model_lock:
        CHAMPION_TRAFFIC = champion_ratio
        CHALLENGER_TRAFFIC = challenger_ratio

    return {
        "champion_traffic": CHAMPION_TRAFFIC,
        "challenger_traffic": CHALLENGER_TRAFFIC,
    }


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def prepare_input(payload: dict[str, Any]) -> pd.DataFrame:
    """Convert incoming request into a DataFrame."""

    data = {
        "Age": [payload["Age"]],
        "Quantity": [payload["Quantity"]],
        "Price per Unit": [payload["Price_per_Unit"]],
        "Gender": [payload["Gender"]],
        "Product Category": [payload["Product_Category"]],
    }

    return pd.DataFrame(data)


def predict_with_model(
    model: Any,
    pipeline: Any,
    data: pd.DataFrame,
) -> tuple[float, float]:
    """Run prediction and measure latency."""

    start_time = time.perf_counter()

    processed_data = pipeline.transform(data)
    prediction = model.predict(processed_data)[0]

    latency_ms = (time.perf_counter() - start_time) * 1000

    return float(prediction), float(latency_ms)


# ============================================================
# A/B ROUTING
# ============================================================


def route_prediction(payload: dict[str, Any]) -> dict[str, Any]:
    """Route traffic between champion and challenger."""

    data = prepare_input(payload)

    with model_lock:
        selected_model = np.random.choice(
            ["champion", "challenger"],
            p=[
                CHAMPION_TRAFFIC,
                CHALLENGER_TRAFFIC,
            ],
        )

        if selected_model == "champion":
            model = champion_model
            pipeline = champion_pipeline
        else:
            model = challenger_model
            pipeline = challenger_pipeline

    prediction, latency = predict_with_model(
        model,
        pipeline,
        data,
    )

    with model_lock:
        ab_metrics["total_requests"] += 1

        if selected_model == "champion":
            ab_metrics["champion_requests"] += 1
            ab_metrics["champion_latencies"].append(latency)
            ab_metrics["champion_predictions"].append(prediction)
        else:
            ab_metrics["challenger_requests"] += 1
            ab_metrics["challenger_latencies"].append(latency)
            ab_metrics["challenger_predictions"].append(prediction)

    return {
        "prediction": prediction,
        "served_by": selected_model,
        "routing_mode": ROUTING_MODE,
    }


# ============================================================
# METRICS
# ============================================================


def get_ab_metrics(
    drift_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return A/B deployment metrics."""

    with model_lock:
        total_requests = ab_metrics["total_requests"]
        champion_count = ab_metrics["champion_requests"]
        challenger_count = ab_metrics["challenger_requests"]

        champion_latencies = list(ab_metrics["champion_latencies"])
        challenger_latencies = list(ab_metrics["challenger_latencies"])

        champion_avg_latency = (
            float(np.mean(champion_latencies)) if champion_latencies else 0.0
        )

        challenger_avg_latency = (
            float(np.mean(challenger_latencies))
            if challenger_latencies
            else 0.0
        )

        champion_traffic = CHAMPION_TRAFFIC
        challenger_traffic = CHALLENGER_TRAFFIC

    champion_percentage = (
        champion_count / total_requests * 100 if total_requests > 0 else 0.0
    )

    challenger_percentage = (
        challenger_count / total_requests * 100 if total_requests > 0 else 0.0
    )

    return {
        "routing_mode": ROUTING_MODE,
        "traffic_configuration": {
            "champion_target": f"{champion_traffic * 100}%",
            "challenger_target": f"{challenger_traffic * 100}%",
        },
        "request_distribution": {
            "total_requests": total_requests,
            "champion_requests": champion_count,
            "challenger_requests": challenger_count,
            "champion_percentage": round(
                champion_percentage,
                2,
            ),
            "challenger_percentage": round(
                challenger_percentage,
                2,
            ),
        },
        "latency_comparison_ms": {
            "champion_average": round(
                champion_avg_latency,
                4,
            ),
            "challenger_average": round(
                challenger_avg_latency,
                4,
            ),
        },
        "model_versions": {
            "champion": "model_v1.pkl",
            "challenger": challenger_model_version,
        },
        "drift_statistics": (
            drift_data
            if drift_data is not None
            else {"message": "No drift statistics available yet."}
        ),
    }
