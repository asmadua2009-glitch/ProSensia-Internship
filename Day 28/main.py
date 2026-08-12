from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "high_value_transaction_model.pkl"
FEATURE_NAMES_PATH = BASE_DIR / "feature_names.txt"
DATASET_PATH = BASE_DIR / "retail_sales_dataset.csv"


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="ProSensia ML Prediction API",
    description="FastAPI ML Microservice with OOD Boundary Guardrails",
    version="3.0.0"
)


# ============================================================
# Pydantic Schemas
# ============================================================

class PredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Age: int
    Gender: str
    Product_Category: str
    Quantity: int
    Price_per_Unit: float


class PredictionResponse(BaseModel):
    prediction: str


class ErrorResponse(BaseModel):
    detail: Dict[str, Any]


# ============================================================
# Global Variables
# ============================================================

model = None
feature_names = []
ood_boundaries = {}


# ============================================================
# Load Model
# ============================================================

try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from: {MODEL_PATH}")
except Exception as e:
    print(f"Model loading failed: {e}")


# ============================================================
# Load Feature Names
# ============================================================

try:
    with open(FEATURE_NAMES_PATH, "r", encoding="utf-8") as f:
        feature_names = [line.strip() for line in f if line.strip()]

    print(f"Feature names loaded successfully: {len(feature_names)} features")

except Exception as e:
    print(f"Feature names loading failed: {e}")


# ============================================================
# Statistical Boundary Calculation
# ============================================================

def calculate_ood_boundaries():
    """
    Calculate statistical boundaries from the baseline training dataset.

    IQR method:
        Lower Bound = Q1 - 1.5 * IQR
        Upper Bound = Q3 + 1.5 * IQR

    These boundaries are used to intercept statistically unusual
    numerical feature values before model inference.
    """

    global ood_boundaries

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    numerical_features = [
        "Age",
        "Quantity",
        "Price per Unit"
    ]

    for feature in numerical_features:

        if feature not in df.columns:
            raise ValueError(
                f"Required feature '{feature}' not found in dataset."
            )

        series = pd.to_numeric(df[feature], errors="coerce").dropna()

        minimum = float(series.min())
        maximum = float(series.max())
        mean = float(series.mean())
        std = float(series.std())

        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        ood_boundaries[feature] = {
            "min": minimum,
            "max": maximum,
            "mean": mean,
            "std": std,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower": lower_bound,
            "upper": upper_bound
        }

        print(
            f"{feature}: "
            f"min={minimum:.2f}, "
            f"max={maximum:.2f}, "
            f"mean={mean:.2f}, "
            f"std={std:.2f}, "
            f"Q1={q1:.2f}, "
            f"Q3={q3:.2f}, "
            f"IQR={iqr:.2f}, "
            f"lower={lower_bound:.2f}, "
            f"upper={upper_bound:.2f}"
        )


# ============================================================
# OOD Boundary Interceptor
# ============================================================

def check_ood_boundaries(data: PredictionInput):
    """
    Check incoming numerical feature values before model inference.

    If any value violates its statistical boundary, raise HTTP 400.
    The model prediction function is never reached for rejected data.
    """

    values = {
        "Age": float(data.Age),
        "Quantity": float(data.Quantity),
        "Price per Unit": float(data.Price_per_Unit)
    }

    for feature, value in values.items():

        boundary = ood_boundaries[feature]

        lower = boundary["lower"]
        upper = boundary["upper"]

        if value < lower or value > upper:

            print(
                f"OOD REQUEST REJECTED BEFORE MODEL INFERENCE: "
                f"{feature}={value}, "
                f"allowed range=({lower:.2f}, {upper:.2f})"
            )

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Data Out of Bounds",
                    "feature": feature,
                    "received_value": value,
                    "allowed_lower_bound": round(lower, 2),
                    "allowed_upper_bound": round(upper, 2)
                }
            )

    print("OOD boundary check passed.")


# ============================================================
# Application Startup
# ============================================================

@app.on_event("startup")
def startup_event():

    try:
        calculate_ood_boundaries()

        print("OOD statistical boundaries loaded successfully.")

    except Exception as e:
        print(f"OOD statistics calculation failed: {e}")


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health")
def health_check():

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model is not available."
        )

    if not ood_boundaries:
        raise HTTPException(
            status_code=503,
            detail="OOD boundaries are not available."
        )

    return {
        "status": "healthy",
        "model_loaded": True,
        "ood_guardrails": True
    }


# ============================================================
# Prediction Endpoint
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse},
        503: {"description": "Service Unavailable"}
    }
)
def predict(data: PredictionInput):

    # --------------------------------------------------------
    # STEP 1: Validate OOD boundaries
    # --------------------------------------------------------
    # IMPORTANT:
    # This happens BEFORE model inference.
    # --------------------------------------------------------

    check_ood_boundaries(data)

    # --------------------------------------------------------
    # STEP 2: Confirm model is available
    # --------------------------------------------------------

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model is not available."
        )

    if not feature_names:
        raise HTTPException(
            status_code=503,
            detail="Feature names are not available."
        )

    # --------------------------------------------------------
    # STEP 3: Prepare input for model
    # --------------------------------------------------------

    input_df = pd.DataFrame(
        [{
            "Age": data.Age,
            "Gender": data.Gender,
            "Product_Category": data.Product_Category,
            "Quantity": data.Quantity,
            "Price per Unit": data.Price_per_Unit
        }]
    )

    # One-hot encode categorical features
    input_df = pd.get_dummies(
        input_df,
        columns=["Gender", "Product_Category"]
    )

    # Match training feature structure
    input_df = input_df.reindex(
        columns=feature_names,
        fill_value=0
    )

    # --------------------------------------------------------
    # STEP 4: Model inference
    # --------------------------------------------------------

    print("MODEL INFERENCE STARTED.")

    prediction = model.predict(input_df)

    print("MODEL INFERENCE COMPLETED.")

    # --------------------------------------------------------
    # STEP 5: Return prediction
    # --------------------------------------------------------

    return PredictionResponse(
        prediction=str(prediction[0])
    )