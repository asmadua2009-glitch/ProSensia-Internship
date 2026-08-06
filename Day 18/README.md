# Day 18 - FastAPI OOD Guardrails & API Testing
## Project Overview
This project extends the FastAPI Machine Learning API by adding Out-of-Distribution (OOD) Guardrails. The API validates user inputs before making predictions to prevent unrealistic values from reaching the trained Random Forest model.
## Objectives
- Build a FastAPI prediction API
- Load the trained Random Forest model
- Validate incoming user inputs
- Reject Out-of-Distribution (OOD) data
- Return custom HTTP 400 Bad Request errors
- Predict using the trained ML model
## Files Included
- main.py
- production_rf_model.pkl
- feature_names.txt
- requirements.txt
- README.md
## API Endpoint
### Home

```
GET /
```
Returns:

```json
{
  "message": "API is Running Successfully"
}
```
### Prediction

```
POST /predict
```

Example Request

```json
{
  "Year": 2024,
  "Month": 8,
  "Unit_Price": 1500
}
```

Example Response

```json
{
  "prediction": 1
}
```
## Out-of-Distribution (OOD) Validation
The API validates input values before making predictions.
Validation Rules:
- Year: 2020 to 2025
- Month: 1 to 12
- Unit_Price: 0 to 100000
If any value is outside these ranges, the API returns:

```
HTTP 400 Bad Request
```

Example Error

```json
{
  "detail": "Data Out of Bounds: Year must be between 2020 and 2025."
}
```
## Technologies Used
- Python
- FastAPI
- Uvicorn
- Pandas
- Scikit-learn
- Joblib
- Pydantic
## How to Run

Create virtual environment

```bash
python -m venv venv
```

Activate environment

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run API

```bash
uvicorn main:app --reload
```

Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---
## Project Outcome
- FastAPI API successfully deployed
- OOD Guardrails implemented
- Custom HTTP 400 validation added
- ML prediction endpoint tested successfully
## Author
ASMA DUA