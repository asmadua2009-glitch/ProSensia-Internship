# Day 23 - Asynchronous FastAPI Microservice

## Project Objective

The objective of Day 23 is to improve the existing FastAPI machine learning
microservice by implementing asynchronous request handling, strict Pydantic
API contracts, non-blocking model inference, and latency benchmarking.

The service is designed to remain responsive while processing machine
learning prediction requests and to meet the required P95 latency target
of less than 500 ms.

---

## Technology Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- Pandas
- Scikit-learn
- Joblib
- Docker
- Docker Compose

---

## API Endpoints

### GET /

Returns a basic API status message.

Response:

```json
{
  "message": "API is Running Successfully"
}

GET /health

The health endpoint verifies that the FastAPI service is running.

Response:

{
  "status": "healthy"
}

The response is validated using the HealthResponse Pydantic model.

POST /predict

The prediction endpoint accepts validated transaction data and returns the
machine learning prediction.

API Contract
Request Schema

The /predict endpoint requires the following fields:

Field	Type	Required
Age	integer	Yes
Gender	string	Yes
Product_Category	string	Yes
Quantity	integer	Yes
Price_per_Unit	float	Yes

Example request:

{
  "Age": 30,
  "Gender": "Male",
  "Product_Category": "Electronics",
  "Quantity": 2,
  "Price_per_Unit": 500
}
Response Schema
{
  "prediction": "1"
}

The response is validated using the PredictionResponse Pydantic model.

Pydantic Validation

Pydantic is used to validate every incoming prediction request before the
data reaches the machine learning model.

The PredictionInput schema defines the expected data types:

Age              -> int
Gender           -> str
Product_Category  -> str
Quantity         -> int
Price_per_Unit    -> float

Missing or invalid fields are rejected automatically by FastAPI and
Pydantic.

For example, sending only:

{
  "amount": 1000
}

results in validation errors because the required prediction fields are
missing.

This prevents malformed JSON payloads from reaching the model inference
pipeline.

Asynchronous Request Handling

The /, /health, and /predict endpoints use async def.

FastAPI uses Python's asyncio event loop to handle asynchronous requests.

The machine learning model prediction is a CPU-bound operation. Running
model.predict() directly inside an asynchronous route could block the
event loop.

To prevent this, the prediction operation is delegated using:

await asyncio.to_thread(
    model.predict,
    input_df
)

This allows the event loop to remain responsive while the synchronous
model inference executes in a worker thread.

CPU and Thread Delegation

Assume:

C = available CPU cores
N = concurrent inference requests

The practical amount of parallel CPU work is bounded by:

Effective parallel CPU work <= min(N, C)

Thread delegation does not create unlimited CPU capacity. Its purpose is to
prevent synchronous model inference from directly blocking the FastAPI
event loop and to improve responsiveness when multiple requests arrive.

Error Handling

The prediction endpoint uses HTTP exception handling.

If model inference fails, the API returns:

HTTP 500 Internal Server Error

with a descriptive error message.

Pydantic validation errors are automatically handled by FastAPI and return
appropriate HTTP validation responses.

Latency Optimization

The main latency optimization techniques used in Day 23 are:

Asynchronous FastAPI route handlers.
Pydantic validation before model inference.
Delegation of CPU-bound prediction using asyncio.to_thread().
Lightweight Pandas DataFrame construction.
Persistent prediction logging.

These techniques help prevent blocking operations from directly freezing
the FastAPI event loop.

Performance Benchmark

The /predict endpoint was benchmarked using 100 sequential prediction
requests.

Results
Metric	Result
Requests	100
Average Latency	76.6 ms
P95 Latency	129.61 ms
Minimum Latency	13.58 ms
Maximum Latency	168.5 ms
Required P95	< 500 ms
Result	PASS
Performance Conclusion

The measured P95 latency was:

129.61 ms

The required threshold is:

P95 < 500 ms

Therefore:

129.61 ms < 500 ms

The microservice successfully meets the Day 23 latency requirement under
the performed benchmark.

Docker Deployment

The FastAPI service is containerized using Docker and managed using
Docker Compose.

The FastAPI container exposes:

8000:8000

The Redis backend runs as a separate container.

Check the running services:

docker compose ps

Expected FastAPI status:

Up ... (healthy)
Running the Application

Build the Docker image:

docker compose build

Start the services:

docker compose up -d

Check the services:

docker compose ps
Testing
Health Check

Open:

http://localhost:8000/health

Expected response:

{
  "status": "healthy"
}
Prediction Test

Example request:

{
  "Age": 30,
  "Gender": "Male",
  "Product_Category": "Electronics",
  "Quantity": 2,
  "Price_per_Unit": 500
}

Expected response format:

{
  "prediction": "1"
}
Swagger Documentation

FastAPI interactive documentation is available at:

http://localhost:8000/docs
Project Files
Day 23/
│
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── benchmark_results.txt
├── model/
└── logs/
Conclusion

Day 23 upgrades the FastAPI machine learning service into a more
production-ready asynchronous microservice.

The project now provides:

Asynchronous FastAPI endpoints
Strict Pydantic request and response contracts
Non-blocking model inference using asyncio.to_thread()
HTTP error handling
Prediction logging
Docker containerization
Health monitoring
Latency benchmarking

The measured P95 latency of 129.61 ms is below the required 500 ms
threshold, satisfying the Day 23 performance target.

AUTHOR
ASMA DUA
