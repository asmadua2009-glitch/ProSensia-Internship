"""
DAY 23 - ASYNCHRONOUS FASTAPI MICROservice ARCHITECTURE

1. ASYNCIO EVENT LOOP AND NON-BLOCKING EXECUTION
------------------------------------------------
FastAPI uses Python's asyncio event loop to handle asynchronous requests.
An async endpoint can pause while waiting for non-CPU-bound operations,
allowing the event loop to serve other requests instead of remaining idle.

CPU-bound machine learning inference is different because model.predict()
may require significant CPU computation. Running such work directly inside
an async route can block the event loop and reduce concurrent request
handling.

For this reason, the prediction operation is delegated to a worker thread
using asyncio.to_thread(). The event loop remains available to process other
incoming requests while the prediction executes in the background thread.

2. THREADPOOL DELEGATION AND CPU USAGE
--------------------------------------
Assume:

    C = number of available CPU cores
    N = number of concurrent inference requests

If CPU-bound inference is executed directly inside the event loop, one
blocking operation can prevent the event loop from efficiently handling
other requests.

With thread delegation, inference tasks can execute on worker threads.
The practical CPU usage is bounded by the available CPU resources:

    Effective parallel CPU work <= min(N, C)

The exact performance depends on the machine, model complexity, Python
thread scheduling, and the amount of CPU work performed by the model.

Thread delegation does not create unlimited CPU capacity. Its purpose is
to prevent the FastAPI event loop from being blocked by synchronous
inference code and to improve responsiveness under concurrent traffic.

3. PYDANTIC VALIDATION
----------------------
Pydantic validates incoming JSON data before it reaches the machine
learning model.

For the prediction endpoint, the request contract requires:

    Age              -> int
    Gender           -> str
    Product_Category  -> str
    Quantity         -> int
    Price_per_Unit    -> float

Invalid or missing fields are rejected by FastAPI/Pydantic before the data
is converted into the model input DataFrame.

This protects the model pipeline from malformed JSON payloads and incorrect
data types.

4. LATENCY OPTIMIZATION
-----------------------
The prediction route is declared using async def and the CPU-bound
model.predict() operation is delegated using asyncio.to_thread().

This architecture prevents synchronous model inference from directly
blocking the FastAPI event loop.

Day 23 benchmark:

    Requests : 100
    Average  : 76.6 ms
    P95      : 129.61 ms
    Minimum  : 13.58 ms
    Maximum  : 168.5 ms

Required P95 threshold:

    P95 < 500 ms

Observed:

    129.61 ms < 500 ms

Therefore, the measured benchmark satisfies the Day 23 latency target."""
import os
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd


# Create FastAPI application
app = FastAPI(
    title="High Value Transaction Prediction API",
    version="1.1.0"
)


# Model and log paths
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "/app/model/high_value_transaction_model.pkl"
)

LOG_PATH = os.getenv(
    "LOG_PATH",
    "/app/logs/predictions.log"
)


# Load trained machine learning model
model = joblib.load(MODEL_PATH)


# Pydantic request model
class PredictionInput(BaseModel):
    Age: int
    Gender: str
    Product_Category: str
    Quantity: int
    Price_per_Unit: float


# Pydantic response models
class HealthResponse(BaseModel):
    status: str


class PredictionResponse(BaseModel):
    prediction: str


# Home endpoint
@app.get("/")
async def home():
    return {
        "message": "API is Running Successfully"
    }


# Health endpoint
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy"
    )


# Prediction endpoint
@app.post(
    "/predict",
    response_model=PredictionResponse
)
async def predict(data: PredictionInput):

    # Convert validated Pydantic data into a dictionary
    input_data = {
        "Age": data.Age,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit
    }

    # Convert input into a 2D Pandas DataFrame
    input_df = pd.DataFrame([input_data])

    try:
        # Run the heavy prediction task outside the event loop
        prediction = await asyncio.to_thread(
            model.predict,
            input_df
        )

        prediction_result = str(prediction[0])

        # Write prediction to persistent log file
        os.makedirs(
            os.path.dirname(LOG_PATH),
            exist_ok=True
        )

        with open(LOG_PATH, "a") as log_file:
            log_file.write(
                f"Input: {input_data} | "
                f"Prediction: {prediction_result}\n"
            )

        return PredictionResponse(
            prediction=prediction_result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )