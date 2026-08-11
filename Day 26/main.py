import os
import re
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------

np.random.seed(42)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = Path(
    os.getenv(
        "MODEL_PATH",
        BASE_DIR / "model" / "high_value_transaction_model.pkl"
    )
)

LOG_PATH = Path(
    os.getenv(
        "LOG_PATH",
        BASE_DIR / "logs" / "predictions.log"
    )
)


# ---------------------------------------------------------
# Global model
# Model is loaded ONCE during application startup
# ---------------------------------------------------------

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the trained ML model once when FastAPI starts.
    The model is not loaded for every prediction request.
    """

    global model

    try:
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded successfully from: {MODEL_PATH}")

    except Exception as exc:
        model = None
        print(f"Model loading failed: {exc}")

    yield

    # Release model when application shuts down
    model = None
    print("Model unloaded.")


# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title="High Value Transaction Prediction API",
    version="3.0.0",
    description="Production-ready ML prediction API for high-value transactions.",
    lifespan=lifespan
)


# ---------------------------------------------------------
# Pydantic Request Model
# ---------------------------------------------------------

class PredictionInput(BaseModel):
    """
    Request contract for the ML prediction endpoint.
    """

    model_config = ConfigDict(
        strict=True,
        extra="forbid"
    )

    Age: int = Field(
        ...,
        ge=1,
        le=120,
        description="Customer age between 1 and 120"
    )

    Gender: str = Field(
        ...,
        min_length=1,
        max_length=20,
        pattern=r"^[A-Za-z ]+$",
        description="Customer gender"
    )

    Product_Category: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9 _-]+$",
        description="Product category"
    )

    Quantity: int = Field(
        ...,
        ge=1,
        le=1000,
        description="Quantity between 1 and 1000"
    )

    Price_per_Unit: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Price per unit"
    )


# ---------------------------------------------------------
# Pydantic Response Models
# ---------------------------------------------------------

class HealthResponse(BaseModel):
    status: str


class PredictionResponse(BaseModel):
    prediction: str


class ErrorResponse(BaseModel):
    detail: str


# ---------------------------------------------------------
# Security Validation
# ---------------------------------------------------------

MALICIOUS_PATTERNS = [
    r"<\s*script",
    r"</\s*script",
    r"javascript\s*:",
    r"onerror\s*=",
    r"onload\s*=",
    r"union\s+select",
    r"select\s+.*\s+from",
    r"insert\s+into",
    r"delete\s+from",
    r"drop\s+table",
    r"--\s*$",
    r"/\*.*\*/",
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"system\s+prompt",
    r"reveal\s+.*prompt",
    r"show\s+.*instructions",
    r"bypass\s+.*security",
    r"jailbreak"
]


def contains_malicious_content(value: str) -> bool:
    """
    Check text fields for common malicious patterns.
    """

    if not isinstance(value, str):
        return False

    return any(
        re.search(pattern, value, re.IGNORECASE)
        for pattern in MALICIOUS_PATTERNS
    )


def security_check(data: PredictionInput) -> None:
    """
    Reject suspicious text input before ML inference.
    """

    text_values = (
        data.Gender,
        data.Product_Category
    )

    if any(
        contains_malicious_content(value)
        for value in text_values
    ):
        raise HTTPException(
            status_code=400,
            detail="Suspicious input detected. Request rejected."
        )


# ---------------------------------------------------------
# OOD Guardrails
# ---------------------------------------------------------

OOD_THRESHOLD = 3.0

OOD_STATS = {
    "Age": {
        "mean": 35.0,
        "std": 15.0
    },
    "Quantity": {
        "mean": 3.0,
        "std": 2.0
    },
    "Price_per_Unit": {
        "mean": 100.0,
        "std": 100.0
    }
}


def check_ood(data: PredictionInput) -> bool:
    """
    Detect statistically unusual numerical inputs
    using a Z-score threshold.
    """

    values = np.array(
        [
            data.Age,
            data.Quantity,
            data.Price_per_Unit
        ],
        dtype=float
    )

    means = np.array(
        [
            OOD_STATS["Age"]["mean"],
            OOD_STATS["Quantity"]["mean"],
            OOD_STATS["Price_per_Unit"]["mean"]
        ],
        dtype=float
    )

    stds = np.array(
        [
            OOD_STATS["Age"]["std"],
            OOD_STATS["Quantity"]["std"],
            OOD_STATS["Price_per_Unit"]["std"]
        ],
        dtype=float
    )

    z_scores = np.abs((values - means) / stds)

    return bool(np.any(z_scores > OOD_THRESHOLD))


# ---------------------------------------------------------
# Request Validation Error Handler
# ---------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Input validation failed.",
            "errors": exc.errors()
        }
    )


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/")
async def home():
    return {
        "message": "High Value Transaction Prediction API is running"
    }


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse
)
async def health():

    if model is None:
        return HealthResponse(
            status="model_unavailable"
        )

    return HealthResponse(
        status="healthy"
    )


# ---------------------------------------------------------
# Prediction Endpoint
# ---------------------------------------------------------

@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {
            "model": ErrorResponse
        },
        422: {
            "model": ErrorResponse
        },
        503: {
            "model": ErrorResponse
        }
    }
)
async def predict(data: PredictionInput):

    # Security validation
    security_check(data)

    # OOD validation
    if check_ood(data):
        raise HTTPException(
            status_code=400,
            detail="Data Out of Bounds: OOD input detected."
        )

    # Verify model availability
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Machine learning model is unavailable."
        )

    # -----------------------------------------------------
    # Build model input
    # -----------------------------------------------------

    input_df = pd.DataFrame(
        {
            "Age": [data.Age],
            "Gender": [data.Gender],
            "Product Category": [data.Product_Category],
            "Quantity": [data.Quantity],
            "Price per Unit": [data.Price_per_Unit]
        }
    )

    try:

        # -------------------------------------------------
        # ML inference
        # Model was already loaded during startup.
        # -------------------------------------------------

        prediction = await asyncio.to_thread(
            model.predict,
            input_df
        )

        prediction_result = str(prediction[0])

        # -------------------------------------------------
        # Prediction logging
        # -------------------------------------------------

        LOG_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with LOG_PATH.open(
            "a",
            encoding="utf-8"
        ) as log_file:

            log_file.write(
                f"Input: {input_df.to_dict(orient='records')[0]} | "
                f"Prediction: {prediction_result}\n"
            )

        return PredictionResponse(
            prediction=prediction_result
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Prediction could not be processed."
        )