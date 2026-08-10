import os
import re
import asyncio

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict


app = FastAPI(
    title="Secure High Value Transaction Prediction API",
    version="2.0.0",
    description="Secure machine learning prediction API"
)


MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "model/high_value_transaction_model.pkl"
)

LOG_PATH = os.getenv(
    "LOG_PATH",
    "logs/predictions.log"
)


# Load the trained model safely
try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None


# Common patterns used in SQL, script and prompt injection attempts
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
    """Check text fields for common malicious patterns."""

    if not isinstance(value, str):
        return False

    for pattern in MALICIOUS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True

    return False


class PredictionInput(BaseModel):
    """
    Strict validation is applied before data reaches the ML model.
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
        description="Price per unit between 0 and 100000"
    )


class HealthResponse(BaseModel):
    status: str


class PredictionResponse(BaseModel):
    prediction: str


class ErrorResponse(BaseModel):
    detail: str


# Z-score is used to identify unusual numerical values.
# z = |value - mean| / standard deviation
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


def calculate_z_score(value: float, mean: float, std: float) -> float:

    if std <= 0:
        return 0.0

    return abs(value - mean) / std


def check_ood(data: PredictionInput) -> bool:
    """Check whether numerical input is statistically unusual."""

    values = {
        "Age": data.Age,
        "Quantity": data.Quantity,
        "Price_per_Unit": data.Price_per_Unit
    }

    for feature, value in values.items():

        stats = OOD_STATS[feature]

        z_score = calculate_z_score(
            value,
            stats["mean"],
            stats["std"]
        )

        print(
            f"{feature}: value={value}, "
            f"z-score={z_score:.2f}"
        )

        if z_score > OOD_THRESHOLD:
            return True

    return False


def security_check(data: PredictionInput) -> None:
    """Reject suspicious text before it reaches the ML model."""

    text_fields = {
        "Gender": data.Gender,
        "Product_Category": data.Product_Category
    }

    for field_name, value in text_fields.items():

        if contains_malicious_content(value):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Suspicious input detected in {field_name}. "
                    "Request rejected."
                )
            )


# Return a clean 422 response for invalid request data
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


@app.get("/")
async def home():

    return {
        "message": "Secure API is Running Successfully"
    }


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


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {
            "model": ErrorResponse
        },
        422: {
            "model": ErrorResponse
        }
    }
)
async def predict(data: PredictionInput):

    # Pydantic validation happens before this point.
    security_check(data)

    # Check for statistically unusual input
    if check_ood(data):

        raise HTTPException(
            status_code=400,
            detail="Data Out of Bounds: OOD input detected."
        )

    # Only validated data is converted into the model input
    input_data = {
        "Age": data.Age,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit
    }

    input_df = pd.DataFrame([input_data])

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="Machine learning model is unavailable."
        )

    try:

        # Run prediction in a worker thread so the event loop
        # remains responsive.
        prediction = await asyncio.to_thread(
            model.predict,
            input_df
        )

        prediction_result = str(prediction[0])

        # Save predictions in the log file
        log_directory = os.path.dirname(LOG_PATH)

        if log_directory:
            os.makedirs(
                log_directory,
                exist_ok=True
            )

        with open(
            LOG_PATH,
            "a",
            encoding="utf-8"
        ) as log_file:

            log_file.write(
                f"Input: {input_data} | "
                f"Prediction: {prediction_result}\n"
            )

        return PredictionResponse(
            prediction=prediction_result
        )

    except Exception:
        # Avoid exposing internal errors to the API user
        raise HTTPException(
            status_code=400,
            detail="Prediction could not be processed."
        )