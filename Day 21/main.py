from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd

print("DAY 21 AI MICROSERVICE LOADED")

app = FastAPI(
    title="High Value Transaction Prediction API",
    description="AI Microservice for predicting high-value retail transactions.",
    version="1.0.0"
)

model = joblib.load("high_value_transaction_model.pkl")


class PredictionInput(BaseModel):
    Age: int = Field(..., ge=18, le=64)
    Gender: str
    Product_Category: str
    Quantity: int = Field(..., ge=1, le=4)
    Price_per_Unit: float = Field(..., ge=25, le=500)


class PredictionResponse(BaseModel):
    prediction: int
    result: str


@app.get("/")
def home():
    return {
        "message": "AI Microservice is Running Successfully"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "High Value Transaction Prediction API"
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(data: PredictionInput):
    allowed_genders = ["Male", "Female"]
    allowed_categories = ["Beauty", "Clothing", "Electronics"]

    if data.Gender not in allowed_genders:
        raise HTTPException(
            status_code=400,
            detail="Data Out of Bounds: Gender must be Male or Female."
        )

    if data.Product_Category not in allowed_categories:
        raise HTTPException(
            status_code=400,
            detail="Data Out of Bounds: Product Category is outside the training distribution."
        )

    input_data = {
        "Age": data.Age,
        "Gender": data.Gender,
        "Product Category": data.Product_Category,
        "Quantity": data.Quantity,
        "Price per Unit": data.Price_per_Unit
    }

    input_df = pd.DataFrame([input_data])

    prediction = model.predict(input_df)

    prediction_value = int(prediction[0])

    if prediction_value == 1:
        result = "High Value Transaction"
    else:
        result = "Not High Value Transaction"

    return PredictionResponse(
        prediction=prediction_value,
        result=result
    )