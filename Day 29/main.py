import asyncio
from pathlib import Path
from typing import Dict, Any

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    description=(
        "Async FastAPI ML Microservice with "
        "Pydantic Validation, OOD Guardrails, "
        "and Load Testing Support"
    ),
    version="4.0.0"
)


# ============================================================
# Pydantic Schemas
# ============================================================

class PredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Age: int = Field(
        ...,
        ge=1,
        le=120
    )

    Gender: str = Field(
        ...,
        min_length=1,
        max_length=20
    )

    Product_Category: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    Quantity: int = Field(
        ...,
        ge=1,
        le=1000
    )

    Price_per_Unit: float = Field(
        ...,
        gt=0,
        le=100000
    )

    # --------------------------------------------------------
    # Gender validation
    # --------------------------------------------------------

    @field_validator("Gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Gender cannot be empty or whitespace."
            )

        if not all(
            char.isalpha() or char.isspace()
            for char in value
        ):
            raise ValueError(
                "Gender must contain alphabetic characters "
                "and spaces only."
            )

        return value

    # --------------------------------------------------------
    # Product Category validation
    # --------------------------------------------------------

    @field_validator("Product_Category")
    @classmethod
    def validate_product_category(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Product_Category cannot be empty."
            )

        allowed = set(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789 _-"
        )

        if not all(char in allowed for char in value):
            raise ValueError(
                "Product_Category contains invalid characters."
            )

        return value


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

    print(
        f"Model loaded successfully from: {MODEL_PATH}"
    )

except Exception as e:

    print(
        f"Model loading failed: {e}"
    )


# ============================================================
# Load Feature Names
# ============================================================

try:

    with open(
        FEATURE_NAMES_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        feature_names = [
            line.strip()
            for line in f
            if line.strip()
        ]

    print(
        f"Feature names loaded successfully: "
        f"{len(feature_names)} features"
    )

except Exception as e:

    print(
        f"Feature names loading failed: {e}"
    )


# ============================================================
# Statistical OOD Boundary Calculation
# ============================================================

def calculate_ood_boundaries():
    """
    Calculate statistical OOD boundaries using IQR.

    Lower Bound = Q1 - 1.5 * IQR
    Upper Bound = Q3 + 1.5 * IQR
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
                f"Required feature '{feature}' "
                f"not found in dataset."
            )

        series = pd.to_numeric(
            df[feature],
            errors="coerce"
        ).dropna()

        if series.empty:

            raise ValueError(
                f"No valid numerical values found "
                f"for '{feature}'."
            )

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
# OOD Boundary Check
# ============================================================

def check_ood_boundaries(data: PredictionInput):

    values = {
        "Age": float(data.Age),
        "Quantity": float(data.Quantity),
        "Price per Unit": float(data.Price_per_Unit)
    }

    for feature, value in values.items():

        boundary = ood_boundaries.get(feature)

        if boundary is None:

            raise HTTPException(
                status_code=503,
                detail=(
                    f"OOD boundary for {feature} "
                    f"is unavailable."
                )
            )

        lower = boundary["lower"]
        upper = boundary["upper"]

        if value < lower or value > upper:

            print(
                "OOD REQUEST REJECTED BEFORE "
                f"MODEL INFERENCE: {feature}={value}, "
                f"allowed range=({lower:.2f}, {upper:.2f})"
            )

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Data Out of Bounds",
                    "feature": feature,
                    "received_value": value,
                    "allowed_lower_bound": round(
                        lower,
                        2
                    ),
                    "allowed_upper_bound": round(
                        upper,
                        2
                    )
                }
            )

    print(
        "OOD boundary check passed."
    )


# ============================================================
# Model Input Preparation
# ============================================================

def prepare_model_input(
    data: PredictionInput
) -> pd.DataFrame:

    """
    Prepare raw input for the trained sklearn Pipeline.

    IMPORTANT:
    The saved model contains its own preprocessing/
    ColumnTransformer, so raw feature names must be passed.
    """

    input_df = pd.DataFrame(
        [{
            "Age": data.Age,
            "Gender": data.Gender,
            "Product Category": data.Product_Category,
            "Quantity": data.Quantity,
            "Price per Unit": data.Price_per_Unit
        }]
    )

    return input_df


# ============================================================
# CPU-Bound Model Inference
# ============================================================

def run_model_inference(
    input_df: pd.DataFrame
):
    """
    Run blocking ML inference.

    This function is executed inside asyncio.to_thread()
    so the FastAPI event loop is not blocked.
    """

    if model is None:

        raise RuntimeError(
            "ML model is not loaded."
        )

    print(
        "MODEL INFERENCE STARTED."
    )

    print(
        f"Model input columns: "
        f"{list(input_df.columns)}"
    )

    prediction = model.predict(input_df)

    print(
        "MODEL INFERENCE COMPLETED."
    )

    # --------------------------------------------------------
    # Convert prediction to string
    # --------------------------------------------------------

    prediction_value = prediction[0]

    return str(prediction_value)


# ============================================================
# Application Startup
# ============================================================

@app.on_event("startup")
def startup_event():

    print(
        "Starting ProSensia ML Prediction API..."
    )

    try:

        calculate_ood_boundaries()

        print(
            "OOD statistical boundaries "
            "loaded successfully."
        )

    except Exception as e:

        print(
            f"OOD statistics calculation failed: {e}"
        )


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

    if not feature_names:

        raise HTTPException(
            status_code=503,
            detail="Feature names are not available."
        )

    if not ood_boundaries:

        raise HTTPException(
            status_code=503,
            detail="OOD boundaries are not available."
        )

    return {
        "status": "healthy",
        "model_loaded": True,
        "ood_guardrails": True,
        "async_inference": True
    }


# ============================================================
# Async Prediction Endpoint
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {
            "model": ErrorResponse
        },
        503: {
            "description": "Service Unavailable"
        }
    }
)
async def predict(
    data: PredictionInput
):

    # --------------------------------------------------------
    # STEP 1: OOD validation
    # --------------------------------------------------------

    check_ood_boundaries(data)

    # --------------------------------------------------------
    # STEP 2: Service availability
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
    # STEP 3: Prepare raw model input
    # --------------------------------------------------------

    input_df = prepare_model_input(data)

    # --------------------------------------------------------
    # STEP 4: Async CPU-bound inference
    # --------------------------------------------------------

    prediction = await asyncio.to_thread(
        run_model_inference,
        input_df
    )

    # --------------------------------------------------------
    # STEP 5: Return prediction
    # --------------------------------------------------------

    return PredictionResponse(
        prediction=prediction
    )