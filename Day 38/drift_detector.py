import os
from typing import Any

import pandas as pd
from scipy.stats import ks_2samp


BASELINE_DATASET_PATH = os.getenv(
    "BASELINE_DATASET_PATH",
    "retail_sales_dataset.csv",
)

KS_THRESHOLD = 0.05


def load_baseline_data() -> pd.DataFrame:
    """Load the original training dataset."""

    if not os.path.exists(BASELINE_DATASET_PATH):
        raise FileNotFoundError(
            f"Baseline dataset not found: {BASELINE_DATASET_PATH}"
        )

    return pd.read_csv(BASELINE_DATASET_PATH)


def detect_drift(production_df: pd.DataFrame) -> dict[str, Any]:
    """Compare production data with baseline using KS tests."""

    baseline_df = load_baseline_data()

    numeric_features = [
        "Age",
        "Quantity",
        "Price per Unit",
    ]

    drifted_features = []
    feature_metrics = {}

    for feature in numeric_features:
        if feature not in baseline_df.columns:
            continue

        if feature not in production_df.columns:
            continue

        baseline_values = pd.to_numeric(
            baseline_df[feature],
            errors="coerce",
        ).dropna()

        production_values = pd.to_numeric(
            production_df[feature],
            errors="coerce",
        ).dropna()

        if len(baseline_values) < 2 or len(production_values) < 2:
            continue

        ks_statistic, p_value = ks_2samp(
            baseline_values,
            production_values,
        )

        is_drifted = bool(p_value < KS_THRESHOLD)

        if is_drifted:
            drifted_features.append(feature)

        feature_metrics[feature] = {
            "ks_statistic": float(round(ks_statistic, 6)),
            "ks_p_value": float(round(p_value, 6)),
            "drift_detected": is_drifted,
        }

    return {
        "drift_detected": bool(len(drifted_features) > 0),
        "drifted_features": drifted_features,
        "ks_threshold": float(KS_THRESHOLD),
        "feature_metrics": feature_metrics,
        "production_samples": int(len(production_df)),
        "baseline_samples": int(len(baseline_df)),
    }