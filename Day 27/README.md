# Day 27 Async FastAPI & Pydantic Error Guardrails
## Project Overview
This project strengthens the containerized FastAPI machine learning microservice developed during Day 26.

The main focus of Day 27 is to improve API reliability by implementing strict Pydantic validation, graceful error handling, asynchronous request handling, and Docker-based testing.

## Objectives

* Implement strong input validation using Pydantic.
* Apply field constraints and value boundaries.
* Reject invalid or corrupted request data gracefully.
* Return appropriate HTTP status codes such as `422 Unprocessable Entity` and `400 Bad Request`.
* Refactor the prediction endpoint using `async def`.
* Prevent CPU-bound ML inference from blocking the FastAPI event loop.
* Test valid and invalid requests using Postman.
* Verify the complete application inside a Docker container.

## Validation Strategy

The API validates incoming prediction requests before they reach the machine learning model.

Pydantic is used to validate:

* Required fields.
* Data types.
* Numerical boundaries.
* Valid field values.
* Invalid or corrupted input.

Invalid input is rejected before model inference, helping protect the ML service from unexpected or malformed payloads.

### Example

A valid request contains values such as:

```json
{
  "Age": 25,
  "Gender": "Female",
  "Product_Category": "Clothing",
  "Quantity": 2,
  "Price_per_Unit": 100
}
```

Invalid values or incorrect data types are rejected with a `422 Unprocessable Entity` response.

Suspicious or application-level invalid input is handled with a `400 Bad Request` response.

## Pydantic Validation & Custom Validators

Pydantic provides structured request schemas that act as an API contract between the client and the machine learning service.

Field constraints and custom validation logic are used where required to detect:

* Missing values.
* Incorrect data types.
* Empty or corrupted values.
* Out-of-bound numerical values.
* Suspicious input patterns.

This prevents invalid data from reaching the prediction logic.

## Error Handling

The API is designed to fail gracefully instead of producing unhandled server errors for invalid user input.

The main response categories tested during Day 27 include:

### 200 — Successful Prediction

Returned when a valid request is processed successfully.

### 422 — Unprocessable Entity

Returned when request data fails Pydantic validation, such as an invalid data type or malformed field value.

### 400 — Bad Request

Returned when application-level validation identifies invalid or suspicious input.

The API was tested with valid requests, empty-string inputs, corrupted values, and suspicious inputs.

## Asynchronous API Architecture

The prediction endpoint uses `async def` to support asynchronous request handling.

FastAPI runs asynchronous endpoints through an ASGI event loop. This allows the application to handle other requests efficiently while waiting for operations that can be performed without blocking the event loop.

However, machine learning inference can be CPU-bound. A CPU-intensive prediction should not simply be placed directly inside an asynchronous endpoint because it can block the event loop.

For this reason, CPU-bound prediction work can be dispatched to a worker thread using an approach such as `asyncio.to_thread()`.

Conceptually:

```python
result = await asyncio.to_thread(run_prediction, data)
```

This keeps the main asynchronous event loop responsive while the prediction work is executed separately.

## CPU-Bound vs I/O-Bound Tasks

### I/O-Bound Tasks

I/O-bound operations spend much of their time waiting for external resources, such as:

* Network requests.
* File operations.
* Database operations.

Asynchronous programming is especially useful for these workloads because the event loop can handle other requests while waiting.

### CPU-Bound Tasks

CPU-bound operations spend most of their time performing computation.

Machine learning inference can be CPU-intensive depending on the model and workload. If executed directly inside the event loop, it can block other requests.

Therefore, CPU-bound inference should be handled carefully using an appropriate execution strategy such as a worker thread or process.

## Docker Configuration

The FastAPI application is containerized using Docker.

The Docker image uses:

```text
python:3.11-slim
```

The container includes:

* FastAPI application.
* Pydantic validation.
* Machine learning model.
* Feature names.
* Required Python dependencies.

The Docker image was rebuilt after the Day 27 changes:

```bash
docker build -t prosensia-ml-service:v2 .
```

The application was then started using:

```bash
docker run --rm -p 8000:8000 prosensia-ml-service:v2
```

The application successfully started inside the container and loaded the machine learning model.

## API Testing

The API was tested using Postman.

### Valid Request

Result:

```text
200 OK
```

### Invalid Data Type / Corrupted Input

Result:

```text
422 Unprocessable Entity
```

### Suspicious / Application-Level Invalid Input

Result:

```text
400 Bad Request
```

These tests confirmed that invalid inputs are intercepted gracefully without crashing the API server.

## API Endpoint

### POST `/predict`

Used to generate a machine learning prediction.

Example:

```text
http://127.0.0.1:8000/predict
```

### GET `/health`

Used to verify that the service is running correctly.

Example:

```text
http://127.0.0.1:8000/health
```

## Project Structure

```text
Day 27/
│
├── main.py
├── Dockerfile
├── requirements.txt
├── README.md
├── feature_names.txt
└── model/
    └── high_value_transaction_model.pkl
```

## Technologies Used

* Python 3.11
* FastAPI
* Pydantic
* Uvicorn
* Scikit-learn
* Pandas
* NumPy
* Joblib
* Docker
* Postman

## Key Learning Outcomes

Through this implementation, I learned how to:

1. Protect ML APIs using strict input validation.
2. Use Pydantic as a structured API contract.
3. Handle invalid requests with appropriate HTTP status codes.
4. Build asynchronous FastAPI endpoints.
5. Understand the difference between CPU-bound and I/O-bound workloads.
6. Prevent CPU-intensive inference from unnecessarily blocking the ASGI event loop.
7. Test API error boundaries using Postman.
8. Deploy and verify the ML service inside a Docker container.

## Conclusion

Day 27 focused on making the FastAPI machine learning microservice more reliable, predictable, and production-oriented.

By combining Pydantic validation, structured error handling, asynchronous request architecture, and Docker testing, the API can safely handle both valid and invalid client requests while protecting the underlying machine learning service from malformed input.
