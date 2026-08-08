from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
print("DAY 19 MAIN.PY LOADED")
# Create FastAPI app
app = FastAPI(
    title="E-Commerce Order Prediction API",
    description="Production ML API for real-time order status prediction",
    version="1.0.0"
)
# Load trained model
model = joblib.load("production_rf_model.pkl")
# Load feature names
with open("feature_names.txt", "r") as f:
    feature_names = [line.strip() for line in f.readlines()]
# Input Schema
class PredictionInput(BaseModel):
    Year: int
    Month: int
    Unit_Price: float
# Output Schema
class PredictionResponse(BaseModel):
    prediction: int
    confidence_score: float
# Health Check
@app.get("/")
def home():
    return {
        "message": "E-Commerce Order Prediction API is running"
    }
# Prediction Endpoint
@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(data: PredictionInput):
    # OOD Guardrails
    if data.Year < 2020 or data.Year > 2025:
        raise HTTPException(
            status_code=400,
            detail="Year must be between 2020 and 2025."
        )
    if data.Month < 1 or data.Month > 12:
        raise HTTPException(
            status_code=400,
            detail="Month must be between 1 and 12."
        )
    if data.Unit_Price < 0 or data.Unit_Price > 100000:
        raise HTTPException(
            status_code=400,
            detail="Unit_Price must be between 0 and 100000."
        )
    # Create input DataFrame
    input_data = pd.DataFrame(
        0,
        index=[0],
        columns=feature_names
    )
     # Fill available input features
    if "Year" in input_data.columns:
        input_data["Year"] = data.Year

    if "Month" in input_data.columns:
        input_data["Month"] = data.Month

    if "Unit_Price" in input_data.columns:
        input_data["Unit_Price"] = data.Unit_Price
    # Model Prediction
    prediction = model.predict(input_data)
    # Confidence Score
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_data)
        confidence_score = float(probabilities.max())
    else:
        confidence_score = 1.0
    # Strict Response Model
    return PredictionResponse(
        prediction=int(prediction[0]),
        confidence_score=round(confidence_score, 4)
    )