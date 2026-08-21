import time
from typing import Any

import joblib
import numpy as np
import pandas as pd


# ============================================================
# DAY 34 MODEL ROUTING CONFIGURATION
# ============================================================

# Available modes:
# "shadow" = Champion prediction returned to user,
#            Challenger runs silently for comparison.
#
# "ab"     = Traffic is split between Champion and Challenger.
ROUTING_MODE = "shadow"

# Used only when ROUTING_MODE = "ab"
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
# LOAD MODELS AND PIPELINES
# ============================================================

champion_model = joblib.load(CHAMPION_MODEL_PATH)
challenger_model = joblib.load(CHALLENGER_MODEL_PATH)

champion_pipeline = joblib.load(CHAMPION_PIPELINE_PATH)
challenger_pipeline = joblib.load(CHALLENGER_PIPELINE_PATH)


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
# HELPER FUNCTION
# ============================================================

def prepare_input(payload: dict[str, Any]) -> pd.DataFrame:
    """Convert incoming request data into a DataFrame."""

    data = {
        "Age": [payload["Age"]],
        "Quantity": [payload["Quantity"]],
        "Price per Unit": [payload["Price_per_Unit"]],
        "Gender": [payload["Gender"]],
        "Product Category": [
            payload["Product_Category"]
        ],
    }

    return pd.DataFrame(data)


def predict_with_model(
    model: Any,
    pipeline: Any,
    data: pd.DataFrame,
) -> tuple[float, float]:
    """Run prediction and measure execution latency."""

    start_time = time.perf_counter()

    processed_data = pipeline.transform(data)

    prediction = model.predict(processed_data)[0]

    latency_ms = (
        time.perf_counter() - start_time
    ) * 1000

    return float(prediction), float(latency_ms)


# ============================================================
# SHADOW / A-B ROUTING
# ============================================================

def route_prediction(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Route inference traffic using Shadow Deployment
    or A/B Traffic Splitting.
    """

    data = prepare_input(payload)

    # --------------------------------------------------------
    # SHADOW MODE
    # --------------------------------------------------------

    if ROUTING_MODE == "shadow":

        champion_prediction, champion_latency = (
            predict_with_model(
                champion_model,
                champion_pipeline,
                data,
            )
        )

        challenger_prediction, challenger_latency = (
            predict_with_model(
                challenger_model,
                challenger_pipeline,
                data,
            )
        )

        ab_metrics["total_requests"] += 1
        ab_metrics["champion_requests"] += 1

        ab_metrics["champion_latencies"].append(
            champion_latency
        )

        ab_metrics["challenger_latencies"].append(
            challenger_latency
        )

        ab_metrics["champion_predictions"].append(
            champion_prediction
        )

        ab_metrics["challenger_predictions"].append(
            challenger_prediction
        )

        if champion_prediction == challenger_prediction:
            ab_metrics["prediction_matches"] += 1

        return {
            "prediction": champion_prediction,
            "served_by": "champion",
            "routing_mode": "shadow",
        }

    # --------------------------------------------------------
    # A/B TRAFFIC SPLITTING MODE
    # --------------------------------------------------------

    if ROUTING_MODE == "ab":

        selected_model = np.random.choice(
            ["champion", "challenger"],
            p=[
                CHAMPION_TRAFFIC,
                CHALLENGER_TRAFFIC,
            ],
        )

        if selected_model == "champion":

            prediction, latency = predict_with_model(
                champion_model,
                champion_pipeline,
                data,
            )

            ab_metrics["champion_requests"] += 1

            ab_metrics["champion_latencies"].append(
                latency
            )

            ab_metrics["champion_predictions"].append(
                prediction
            )

        else:

            prediction, latency = predict_with_model(
                challenger_model,
                challenger_pipeline,
                data,
            )

            ab_metrics["challenger_requests"] += 1

            ab_metrics["challenger_latencies"].append(
                latency
            )

            ab_metrics["challenger_predictions"].append(
                prediction
            )

        ab_metrics["total_requests"] += 1

        return {
            "prediction": prediction,
            "served_by": selected_model,
            "routing_mode": "ab",
        }

    raise ValueError(
        "Invalid ROUTING_MODE. "
        "Use 'shadow' or 'ab'."
    )


# ============================================================
# METRICS CALCULATION
# ============================================================

def get_ab_metrics(
    drift_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Return comparative A/B and Shadow Deployment metrics.
    """

    champion_count = ab_metrics[
        "champion_requests"
    ]

    challenger_count = ab_metrics[
        "challenger_requests"
    ]

    total_requests = ab_metrics[
        "total_requests"
    ]

    champion_avg_latency = (
        float(
            np.mean(
                ab_metrics["champion_latencies"]
            )
        )
        if ab_metrics["champion_latencies"]
        else 0.0
    )

    challenger_avg_latency = (
        float(
            np.mean(
                ab_metrics["challenger_latencies"]
            )
        )
        if ab_metrics["challenger_latencies"]
        else 0.0
    )

    # In Shadow Mode both models process
    # the same requests, so prediction agreement
    # is used as a comparison metric.
    prediction_agreement = (
        (
            ab_metrics["prediction_matches"]
            / total_requests
        )
        if total_requests > 0
        else 0.0
    )

    return {
        "routing_mode": ROUTING_MODE,

        "traffic_configuration": {
            "champion_target": (
                f"{CHAMPION_TRAFFIC * 100}%"
            ),
            "challenger_target": (
                f"{CHALLENGER_TRAFFIC * 100}%"
            ),
        },

        "request_distribution": {
            "total_requests": total_requests,
            "champion_requests": champion_count,
            "challenger_requests": challenger_count,
            "champion_percentage": round(
                (
                    champion_count / total_requests
                    * 100
                )
                if total_requests > 0
                else 0.0,
                2,
            ),
            "challenger_percentage": round(
                (
                    challenger_count / total_requests
                    * 100
                )
                if total_requests > 0
                else 0.0,
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

        "performance_comparison": {
            "prediction_agreement": round(
                prediction_agreement,
                4,
            ),
            "prediction_agreement_percentage": round(
                prediction_agreement * 100,
                2,
            ),
        },

        "drift_statistics": (
            drift_data
            if drift_data is not None
            else {
                "message":
                    "No drift statistics available yet."
            }
        ),
    }