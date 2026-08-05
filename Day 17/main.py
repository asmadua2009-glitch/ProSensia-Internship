from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# Create FastAPI app
app = FastAPI(title="E-Commerce Order Prediction API")

# Load trained model
model = joblib.load("production_rf_model.pkl")

# Load feature names
with open("feature_names.txt", "r") as f:
    feature_names = [line.strip() for line in f]


# Pydantic Request Schema
class PredictionInput(BaseModel):
    Year: int
    Month: int
    Unit_Price: float


# Home Endpoint
@app.get("/")
def home():
    return {
        "message": "API is Running Successfully"
    }


# Prediction Endpoint
@app.post("/predict")
def predict(data: PredictionInput):

    # Convert input to dictionary
    input_data = data.model_dump()

    # Create dataframe with all training features
    input_df = pd.DataFrame(columns=feature_names)

    # Add one row with default value 0
    input_df.loc[0] = 0

    # Fill only the values received from API
    for key, value in input_data.items():
        if key in input_df.columns:
            input_df.at[0, key] = value

    try:
        prediction = model.predict(input_df)

        return {
            "prediction": int(prediction[0])
        }

    except Exception as e:
        return {
            "error": str(e)
        }