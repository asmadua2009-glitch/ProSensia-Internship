# Day 28  OOD Boundary Interceptor for FastAPI ML Microservice
## Project Overview
Today I enhanced my FastAPI Machine Learning microservice by adding an Out-of-Distribution (OOD) Boundary Interceptor to protect the model from invalid and unexpected input data. The system calculates statistical boundaries from the training dataset and checks incoming requests before they reach the ML model.
## Statistical Boundary Checker
The OOD checker uses training-data statistics such as:
* Minimum and maximum values
* Mean
* Standard deviation
* Interquartile Range (IQR)
  For numerical features, IQR-based boundaries are used to identify values that fall outside the expected training-data distribution.
## OOD Boundary Interceptor
Before model inference, incoming feature values are checked against the defined statistical boundaries. If a value is outside the allowed boundary, the request is rejected and the model is not invoked.
For example, an extreme `Price_per_Unit` value of `99999` was rejected because it exceeded the calculated upper boundary of `705`.
The API returns a structured `400 Bad Request` response:

```json
{
  "detail": {
    "message": "Data Out of Bounds",
    "feature": "Price per Unit",
    "received_value": 99999,
    "allowed_lower_bound": -375,
    "allowed_upper_bound": 705
  }
}
```

## Why OOD Guardrails Matter

OOD guardrails are important for enterprise ML services because models can produce unreliable predictions when they receive data outside the distribution they were trained on. Detecting anomalous data before inference helps prevent incorrect predictions, unnecessary computation, and potential downstream failures.

## API Verification

A normal request was successfully processed:

```text
200 OK
```

An extreme outlier request was intercepted:

```text
400 Bad Request — Data Out of Bounds
```

The Docker logs confirmed both successful prediction handling and rejection of the out-of-bounds request.

## Docker Deployment

The FastAPI ML microservice was rebuilt and verified inside Docker.
Build:

```bash
docker build -t prosensia-ml-service:v3 .
```

Run:

```bash
docker run -d --name prosensia-ml-container -p 8000:8000 prosensia-ml-service:v3
```

The running container and application logs were verified using Docker.

## Technologies Used

* Python 3.11
* FastAPI
* Pydantic
* Pandas
* NumPy
* Scikit-learn
* Joblib
* Docker

## Key Learning

Day 28 helped me understand how statistical OOD detection can act as a safety layer around ML inference. Instead of allowing every request to reach the model, the API first checks whether the input is within the expected training-data boundaries, making the ML microservice more reliable and production-focused.
