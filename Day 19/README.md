# Day 19 FastAPI Prediction Endpoint & API Documentation
## Overview
Day 19 focuses on integrating a trained Machine Learning model with a FastAPI backend and creating a structured prediction endpoint.
## Project Objective
- Integrate the trained Random Forest model with FastAPI.
- Create a strict Pydantic response model.
- Finalize the `/predict` prediction endpoint.
- Implement OOD input guardrails.
- Return prediction and confidence score.
- Generate automatic Swagger/OpenAPI documentation.
- Test real-time predictions.
## Project Structure

Day 19/
├── main.py
├── production_rf_model.pkl
├── feature_names.txt
├── requirements.txt
└── README.md

## Technologies Used
Python
FastAPI
Uvicorn
Pydantic
Pandas
NumPy
Scikit-learn
Joblib
Swagger/OpenAPI
API Endpoint
```
## POST /predict
Input
{
  "Year": 2024,
  "Month": 8,
  "Unit_Price": 1500
}
Response Model
{
  "prediction": 1,
  "confidence_score": 0.53
}
The PredictionResponse Pydantic model ensures that the API returns a strictly structured response.

```
## OOD Guardrails
Year must be between 2020 and 2025.
Month must be between 1 and 12.
Unit_Price must be between 0 and 100000.
Invalid inputs return 400 Bad Request.
## API Documentation
FastAPI automatically generates Swagger/OpenAPI documentation.
Open:
http://127.0.0.1:8000/docs
Running the API
uvicorn main:app --reload
Testing
A valid request was successfully tested through Swagger.
Response:
{
  "prediction": 1,
  "confidence_score": 0.53
}
OOD tests were also successfully verified for invalid Year, Month, and Unit_Price values.


## Key Learning Outcomes
FastAPI backend integration
Pydantic response models
Machine Learning API deployment concepts
Input validation
OOD guardrails
Swagger/OpenAPI documentation
Real-time API testing
## Conclusion

The Day 19 Prediction Endpoint successfully connects the trained Machine Learning model with a FastAPI backend and provides validated, structured, and documented real-time predictions.