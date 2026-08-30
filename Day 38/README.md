# 🚀 Day 38 Prometheus & Grafana Observability for FastAPI ML Service

## 📌 Project Overview

This project upgrades the existing secured and containerized FastAPI Machine Learning microservice into an **Observable MLOps System** using **Prometheus and Grafana**.

The objective is to collect real-time API and model inference metrics, visualize service performance through Grafana dashboards, and monitor production indicators such as **P95/P99 latency, Requests Per Second (RPS), inference activity, and HTTP error rates**.

The system uses a multi-container Docker Compose architecture consisting of:

* FastAPI ML Service
* Prometheus
* Grafana

---

## 🎯 Objectives

The main objectives of Day 38 are:

* Integrate Prometheus metrics into the FastAPI ML microservice.
* Expose a `/metrics` endpoint for Prometheus scraping.
* Track model prediction activity using a custom Counter.
* Track model inference latency using a custom Histogram.
* Configure Prometheus for continuous metric collection.
* Build a Grafana dashboard for real-time observability.
* Monitor P95/P99 latency, RPS, prediction throughput, and HTTP errors.
* Verify the system under test traffic using 100 Postman requests.
* Run the complete observability stack using Docker Compose.

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │       Postman        │
                    │   Test Traffic       │
                    └──────────┬───────────┘
                               │
                               │ HTTP Requests
                               ▼
                    ┌──────────────────────┐
                    │   FastAPI ML Service │
                    │ prosensia-ml-service │
                    │      Port: 8000      │
                    └──────────┬───────────┘
                               │
                               │ /metrics
                               ▼
                    ┌──────────────────────┐
                    │      Prometheus      │
                    │      Port: 9090      │
                    └──────────┬───────────┘
                               │
                               │ PromQL
                               ▼
                    ┌──────────────────────┐
                    │       Grafana        │
                    │      Port: 3000      │
                    └──────────────────────┘
```

---

## 📁 Project Structure

```text
Day 38/
│
├── main.py
├── security.py
├── gunicorn_conf.py
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
│
├── grafana/
│   └── dashboards/
│       └── ml_service_observability.json
│
├── model/
│   └── model artifacts
│
└── README.md
```

---

## 📊 Prometheus Metrics

The FastAPI application is instrumented using:

```text
prometheus-fastapi-instrumentator
prometheus-client
```

The application exposes metrics through:

```text
/metrics
```

Prometheus continuously scrapes this endpoint to collect API and model performance metrics.

---

## 🔢 Custom Metrics

### 1. `model_predictions_total`

`model_predictions_total` is a **Counter** used to track the total number of successful model predictions/inferences.

A Counter is a metric that only increases over time, except when the application restarts.

Example PromQL:

```promql
rate(model_predictions_total[$__rate_interval])
```

This converts the cumulative prediction counter into a prediction rate and helps visualize **prediction throughput**.

---

### 2. `model_inference_latency_seconds`

`model_inference_latency_seconds` is a **Histogram** used to measure the distribution of model inference latency.

Histograms record observations into configurable buckets and maintain:

* Bucket counts
* Total observation count
* Sum of observed values

Histograms are useful for calculating latency quantiles such as **P95 and P99**.

---

## 📈 Grafana Dashboard

The Grafana dashboard provides real-time monitoring of the ML service.

The dashboard tracks:

### P95 Response Latency

The P95 latency is calculated using:

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[$__rate_interval])
  )
)
```

This calculates the latency value below which approximately 95% of observed requests fall.

### Prediction Throughput

```promql
rate(model_predictions_total[$__rate_interval])
```

This shows the rate of model predictions over time.

### Request Rate / RPS

```promql
rate(http_requests_total[$__rate_interval])
```

This monitors Requests Per Second (RPS).

### HTTP Error Rate

```promql
rate(http_requests_total{status=~"4..|5.."}[$__rate_interval])
```

This monitors HTTP 4xx and 5xx error activity.

---

## 📌 Counter vs Histogram

### Counter

A **Counter** represents a cumulative value that increases over time.

Example:

```text
model_predictions_total
```

It is useful for tracking:

* Total predictions
* Total requests
* Total errors

Counters are commonly converted into rates using PromQL `rate()`.

### Histogram

A **Histogram** measures the distribution of observed values across buckets.

Example:

```text
model_inference_latency_seconds
```

It is useful for measuring:

* Request latency
* Model inference latency
* P95 latency
* P99 latency

---

## 📐 P95 and P99 Latency

Tail latency represents the slower portion of requests received by the service.

### P95

P95 represents the latency value below which approximately 95% of requests are completed.

### P99

P99 represents the latency value below which approximately 99% of requests are completed.

Monitoring P95 and P99 is important because average latency can hide slow requests.

For example, an API may have a good average response time while a small percentage of requests experience significantly higher latency.

Monitoring tail latency helps identify performance degradation and potential **SLA breaches** before they become major production problems.

---

## 🐳 Docker Compose Stack

The complete observability environment is orchestrated using Docker Compose.

The stack contains three services:

```text
prosensia-ml-service
prometheus
grafana
```

The complete stack is launched using:

```bash
docker compose up -d
```

### Service Ports

| Service            | Port |
| ------------------ | ---: |
| FastAPI ML Service | 8000 |
| Prometheus         | 9090 |
| Grafana            | 3000 |

---

## 🔍 Prometheus Configuration

Prometheus is configured to continuously scrape the FastAPI application's:

```text
/metrics
```

endpoint.

The Prometheus configuration is stored in:

```text
prometheus.yml
```

The target points to the containerized ML service so that API and inference metrics can be collected continuously.

---

## 📊 Grafana Configuration

Grafana is connected to Prometheus as its data source.

Grafana is accessed through:

```text
http://localhost:3000
```

The dashboard provides visualization for:

* P95 response latency
* Prediction throughput
* Request rate / RPS
* 4xx/5xx error activity
* Model inference activity

---

## 🧪 Testing & Verification

The observability stack was tested using Postman and Docker Compose.

### 1. FastAPI Metrics Endpoint

The `/metrics` endpoint was verified to expose Prometheus metrics successfully.

### 2. Prometheus

Prometheus was verified to collect metrics from the FastAPI ML service.

### 3. Grafana

Grafana was verified to receive Prometheus data and display the monitoring metrics.

### 4. Postman Load Verification

100 requests were sent through Postman to generate test traffic.

Successful responses returned:

```text
HTTP 200 OK
```

The generated traffic was reflected in the Grafana metrics.

### 5. Docker Compose Verification

The following command was used:

```bash
docker compose ps
```

All three required containers were successfully running:

```text
grafana                Up
prometheus             Up
prosensia-ml-service   Up
```

---

## 📋 Production Observability Coverage

| Monitoring Requirement    | Implementation                       |
| ------------------------- | ------------------------------------ |
| P95 Latency               | `histogram_quantile()`               |
| P99 Latency               | Histogram-based quantile calculation |
| Request Rate              | `rate(http_requests_total[...])`     |
| Prediction Throughput     | `rate(model_predictions_total[...])` |
| 4xx/5xx Errors            | HTTP status filtering                |
| Model Prediction Activity | `model_predictions_total`            |
| API Metrics               | `/metrics` endpoint                  |
| Continuous Scraping       | Prometheus                           |
| Visualization             | Grafana                              |
| Container Orchestration   | Docker Compose                       |

---

## 🔐 Security & Existing ML Service

The existing secured FastAPI ML microservice remains part of the architecture.

The observability implementation does not replace the existing:

* Input validation
* Security controls
* ML inference pipeline
* Multi-worker Gunicorn configuration
* Containerized deployment

Instead, Prometheus and Grafana add a dedicated **observability layer** around the existing ML service.

---

## 📦 Dependencies

The project includes the required telemetry dependencies:

```text
prometheus-fastapi-instrumentator
prometheus-client
```

along with the existing FastAPI and Machine Learning dependencies.

---

## 🚀 How to Run

### Start the Complete Stack

```bash
docker compose up -d
```

### Check Running Containers

```bash
docker compose ps
```

### Access FastAPI

```text
http://localhost:8000
```

### Access Metrics

```text
http://localhost:8000/metrics
```

### Access Prometheus

```text
http://localhost:9090
```

### Access Grafana

```text
http://localhost:3000
```

---

## ✅ Final Deliverables

The Day 38 implementation includes:

* Updated `main.py`
* `docker-compose.yml`
* `prometheus.yml`
* Updated `requirements.txt`
* Grafana dashboard configuration
* Grafana dashboard screenshot
* Prometheus metrics instrumentation
* Custom prediction counter
* Model inference latency monitoring
* P95 latency visualization
* Prediction throughput monitoring
* RPS monitoring
* 4xx/5xx error monitoring
* 100-request Postman verification
* Docker Compose verification

---

## 🎯 Conclusion

Day 38 transforms the secured FastAPI Machine Learning microservice into an **Observable MLOps System**.

Prometheus provides continuous collection of operational and model inference metrics, while Grafana provides real-time visualization of service performance.

By monitoring **P95/P99 latency, RPS, prediction throughput, and HTTP errors**, the system provides better visibility into production behavior and helps detect performance degradation and potential SLA issues early.

This observability layer establishes a stronger foundation for reliable and production-ready ML microservice operations.
## Author 
ASMA DUAs