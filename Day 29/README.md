# 🚀 Day 29  FastAPI ML Microservice Load Testing with Locust

## 📌 Project Overview

This project extends the ProSensia Machine Learning microservice by adding **high-concurrency load testing using Locust**.

The FastAPI service provides a `/predict` endpoint for ML inference and includes:

* Pydantic input validation
* Statistical Out-of-Distribution (OOD) guardrails
* Asynchronous CPU-bound inference using `asyncio.to_thread()`
* Model loading during application startup
* Docker containerization
* Locust-based performance and load testing

---

## 🏗️ Project Architecture

```text
Client / Locust
      │
      ▼
FastAPI Microservice
      │
      ├── Pydantic Validation
      │
      ├── OOD Guardrails
      │
      ├── Input Preparation
      │
      └── Async Inference
              │
              ▼
        Scikit-learn ML Model
              │
              ▼
        Prediction Response
```

---

## 📂 Project Files

```text
Day 29/
│
├── main.py
├── locustfile.py
├── Dockerfile
├── requirements.txt
├── feature_names.txt
├── high_value_transaction_model.pkl
├── retail_sales_dataset.csv
└── README.md
```

---

## 🔹 FastAPI Prediction API

The `/predict` endpoint accepts the following input:

```json
{
  "Age": 25,
  "Gender": "Female",
  "Product_Category": "Electronics",
  "Quantity": 2,
  "Price_per_Unit": 500
}
```

The API validates the request before sending it to the ML model.

### Validation includes:

* `Age`: 1–120
* `Quantity`: 1–1000
* `Price_per_Unit`: greater than 0 and up to 100000
* `Gender`: alphabetic characters and spaces only
* `Product_Category`: alphanumeric characters, spaces, `_` and `-`
* Extra/unexpected fields are rejected

---

## 🛡️ OOD Guardrails

The API uses the **Interquartile Range (IQR)** method to calculate statistical boundaries.

```text
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

The numerical features checked are:

* Age
* Quantity
* Price per Unit

Requests outside the calculated statistical boundaries are rejected before model inference.

This prevents unusual or out-of-distribution values from reaching the ML model.

---

## ⚡ Asynchronous Inference

The FastAPI `/predict` endpoint is asynchronous.

CPU-bound model inference is delegated using:

```python
await asyncio.to_thread(...)
```

This prevents blocking the FastAPI event loop while the machine-learning model performs inference.

---

## ❤️ Health Check

The service provides:

```text
GET /health
```

Successful response:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "ood_guardrails": true,
  "async_inference": true
}
```

This confirms that:

* The ML model is loaded
* OOD guardrails are available
* Async inference is enabled

---

# 🐳 Docker Containerization

The FastAPI application is containerized using Docker.

### Build image

```powershell
docker build -t prosensia-ml-service:v4 .
```

### Run container

```powershell
docker run --name prosensia-ml-container -p 8000:8000 prosensia-ml-service:v4
```

The API runs on:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 📊 Locust Load Testing

Locust was used to simulate multiple concurrent users sending requests to the `/predict` endpoint.

### Start Locust

```powershell
locust -f locustfile.py --host http://127.0.0.1:8000
```

Then open:

```text
http://localhost:8089
```

---

## 🧪 Load Test Results

A successful Locust test was performed with:

* **Concurrent users:** 20
* **Endpoint:** `POST /predict`
* **Requests:** 55
* **Failures:** 0
* **Failure rate:** 0%
* **Current RPS:** 5.75
* **Average response time:** 178.88 ms
* **Median response time:** 100 ms
* **95th percentile:** 470 ms
* **99th percentile:** 520 ms
* **Minimum response time:** 26 ms
* **Maximum response time:** 519 ms

### Result

```text
POST /predict
Requests: 55
Failures: 0
Failure Rate: 0%
Average: 178.88 ms
Median: 100 ms
95th percentile: 470 ms
99th percentile: 520 ms
RPS: 5.75
```

The load test successfully completed without request failures, demonstrating that the containerized FastAPI ML service handled the simulated concurrent workload successfully.

---

# 📈 Performance Analysis

The Locust test demonstrates that the API can process concurrent prediction requests while maintaining a **0% failure rate** during the tested workload.

The asynchronous inference design helps prevent CPU-bound ML inference from directly blocking the FastAPI event loop.

The response-time percentiles also provide useful information for identifying performance bottlenecks under increasing concurrency.

---

# 🔍 Key Learning Outcomes

### 1. Load Testing

Locust makes it possible to simulate multiple users and measure API performance under concurrent traffic.

### 2. API Reliability

The test verifies whether the `/predict` endpoint remains stable under repeated requests.

### 3. Latency Monitoring

Average, median, 95th percentile, and 99th percentile response times provide a better understanding of API performance than average latency alone.

### 4. Async ML Inference

Using `asyncio.to_thread()` allows blocking model inference to run outside the main FastAPI event loop.

### 5. Production-Oriented Architecture

Combining:

```text
FastAPI
+
Pydantic Validation
+
OOD Guardrails
+
Async Inference
+
Docker
+
Locust
```

creates a more robust and production-oriented ML microservice.

---

# ✅ Day 29 Deliverables

* [x] FastAPI ML microservice
* [x] `/predict` endpoint
* [x] `/health` endpoint
* [x] Pydantic validation
* [x] OOD guardrails
* [x] Async inference
* [x] Docker containerization
* [x] Locust load testing
* [x] Concurrent-user testing
* [x] Performance analysis
* [x] 0% failure rate in final load test

---

## 🎯 Conclusion

Day 29 focused on evaluating the FastAPI ML microservice under concurrent load. Locust was used to benchmark the `/predict` endpoint, while the asynchronous inference architecture helped maintain responsive API behavior.

The final test with **20 concurrent users and 55 requests achieved a 0% failure rate**, with an average response time of **178.88 ms** and a 95th-percentile response time of **470 ms**.

This completes the Day 29 objective of integrating **load testing and performance evaluation** into the containerized ML inference service.
