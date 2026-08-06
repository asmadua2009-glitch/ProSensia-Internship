from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
print("DAY 18 MAIN.PY LOADED")

# Create FastAPI app
app = FastAPI(title="E-Commerce Order Prediction API")

# Load trained model
model = joblib.load("production_rf_model.pkl")

# Load feature names
with open("feature_names.txt", "r") as f:
    feature_names = [line.strip() for line in f]


# -----------------------------
# Pydantic Request Schema
# -----------------------------
class PredictionInput(BaseModel):
    Year: int
    Month: int
    Unit_Price: float


# -----------------------------
# Home Endpoint
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "API is Running Successfully"
    }


# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/predict")
def predict(data: PredictionInput):

    # -----------------------------
    # Out-of-Distribution (OOD) Validation
    # Prevent unrealistic values from reaching the ML model
    # -----------------------------

    # Check Year
    if data.Year < 2020 or data.Year > 2025:
        raise HTTPException(
            status_code=400,
            detail="Data Out of Bounds: Year must be between 2020 and 2025."
        )

    # Check Month
    if data.Month < 1 or data.Month > 12:
        raise HTTPException(
            status_code=400,
            detail="Data Out of Bounds: Month must be between 1 and 12."
        )

    # Check Unit Price
    if data.Unit_Price < 0 or data.Unit_Price > 100000:
        raise HTTPException(
            status_code=400,
            detail="Data Out of Bounds: Unit_Price is outside the training distribution."
        )

    # Convert validated input into dictionary
    input_data = data.model_dump()

    # Create dataframe with all training features
    input_df = pd.DataFrame(columns=feature_names)

    # Fill default values
    input_df.loc[0] = 0

    # Fill API values
    for key, value in input_data.items():
        if key in input_df.columns:
            input_df.at[0, key] = value

    # Make prediction
    prediction = model.predict(input_df)

    # Return JSON response
    return {
        "prediction": int(prediction[0])
    }