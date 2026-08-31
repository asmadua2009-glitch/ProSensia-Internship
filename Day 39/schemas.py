from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """Raw input data received by the prediction API."""

    Age: int = Field(..., ge=18, le=100)
    Gender: str
    Product_Category: str
    Quantity: int = Field(..., ge=1)
    Price_per_Unit: float = Field(..., gt=0)


class PredictionResponse(BaseModel):
    """Prediction API response."""

    prediction: float
