import os
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd


# Create FastAPI application
app = FastAPI(
    title="High Value Transaction Prediction API",
    version="1.0.0"
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


# Pydantic request schema
class PredictionInput(BaseModel):
    Age: int
    Gender: str
    Product_Category: str
    Quantity: int
    Price_per_Unit: float


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "API is Running Successfully"
    }


# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# Prediction endpoint
@app.post("/predict")
def predict(data: PredictionInput):

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
        # Generate prediction
        prediction = model.predict(input_df)

        prediction_result = str(prediction[0])

        # Write prediction to persistent log file
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

        with open(LOG_PATH, "a") as log_file:
            log_file.write(
                f"Input: {input_data} | Prediction: {prediction_result}\n"
            )

        return {
            "prediction": prediction_result
        }

    except Exception as e:
        return {
            "error": str(e)
        }