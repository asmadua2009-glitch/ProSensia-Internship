# Day 34 Shadow Deployment and A/B Traffic Splitting

## Project Overview

This project extends the existing containerized FastAPI Machine Learning microservice by implementing Shadow Deployment and A/B Traffic Splitting for safe model evaluation.

The system uses two machine learning models:

* **model_v1.pkl** – Champion Model
* **model_v2.pkl** – Challenger Model

Instead of directly replacing the production model, the Challenger model is evaluated alongside the Champion model. This approach allows the new model to be tested safely before receiving full production traffic.

## Project Objective

The objective of Day 34 is to implement dynamic model routing inside the FastAPI Machine Learning microservice.

The system supports:

* Shadow Deployment
* A/B Traffic Splitting
* Dynamic model routing
* Champion and Challenger model comparison
* Prediction logging
* Latency tracking
* Request distribution monitoring
* Drift statistics
* Comparative performance metrics
* Dockerized deployment

## Champion and Challenger Models

### Champion Model

The Champion model is the current stable production model:

```text
model_v1.pkl
```

It represents the validated model currently trusted for production inference.

### Challenger Model

The Challenger model is the newly retrained model:

```text
model_v2.pkl
```

The Challenger model is evaluated against the Champion model before it can safely replace it.

## Project Structure

```text
Day 34/
├── main.py
├── router.py
├── schemas.py
├── preprocessing.py
├── drift_detector.py
├── retrain.py
├── model_v1.pkl
├── model_v2.pkl
├── pipeline.pkl
├── pipeline_v2.pkl
├── retail_sales_dataset.csv
├── requirements.txt
├── Dockerfile
└── README.md
```

## Routing Strategy

The routing logic is implemented inside:

```text
router.py
```

The routing mode is configurable using:

```python
ROUTING_MODE = "shadow"
```

The application also supports:

```python
ROUTING_MODE = "ab"
```

For A/B testing, the configured traffic split is:

```python
CHAMPION_TRAFFIC = 0.80
CHALLENGER_TRAFFIC = 0.20
```

This represents:

* 80% traffic → Champion Model
* 20% traffic → Challenger Model

## Shadow Deployment

Shadow Deployment allows the Challenger model to receive the same inference request as the Champion model without exposing the Challenger prediction to the user.

The workflow is:

```text
Incoming Request
        ↓
Champion Model ───────→ Prediction Returned to User
        ↓
Challenger Model ─────→ Prediction Logged for Evaluation
```

In Shadow Mode:

* The Champion prediction is returned to the user.
* The Challenger prediction is executed silently.
* Both model latencies are measured.
* Predictions are compared.
* The production model remains unaffected.

This allows safe evaluation of the Challenger model using production-style traffic.

## A/B Traffic Splitting

A/B testing distributes requests between two models.

The routing algorithm uses random traffic selection with configurable probabilities.

Example configuration:

```text
Champion:   80%
Challenger: 20%
```

The workflow is:

```text
Incoming Request
        ↓
Dynamic Router
        ↓
 ┌─────────────────────┐
 │ 80% → Champion      │
 │ 20% → Challenger    │
 └─────────────────────┘
        ↓
Selected Model Prediction
        ↓
Response Returned
```

Unlike Shadow Deployment, only the selected model processes the request for the user response.

## Shadow Deployment vs A/B Testing

### Shadow Deployment

Advantages:

* The Champion model continues serving users.
* The Challenger can be evaluated safely.
* Both model predictions can be compared on the same input.

Trade-off:

* Both models execute for each request, increasing compute overhead.

### A/B Traffic Splitting

Advantages:

* Real user traffic is distributed between models.
* Request distribution can be controlled.
* Latency and request behavior can be compared.

Trade-off:

* Some users may receive predictions from the Challenger model.

## Prediction Flow

The `/predict` endpoint performs the following steps:

```text
POST /predict
        ↓
Validate Request with Pydantic
        ↓
Log Production Payload
        ↓
Send Request to router.py
        ↓
Shadow Mode or A/B Mode
        ↓
Model Prediction
        ↓
Return Prediction Response
```

## Comparative Metrics

The application provides the following endpoint:

```text
GET /ab/metrics
```

The endpoint displays:

* Routing mode
* Traffic configuration
* Total requests
* Champion request count
* Challenger request count
* Request distribution percentages
* Champion average latency
* Challenger average latency
* Prediction agreement
* Drift statistics

Example response structure:

```json
{
    "routing_mode": "shadow",
    "traffic_configuration": {
        "champion_target": "80.0%",
        "challenger_target": "20.0%"
    },
    "request_distribution": {
        "total_requests": 50,
        "champion_requests": 50,
        "challenger_requests": 0
    },
    "latency_comparison_ms": {
        "champion_average": 1.25,
        "challenger_average": 1.10
    },
    "performance_comparison": {
        "prediction_agreement_percentage": 100.0
    }
}
```

In Shadow Mode, the Champion serves all user-facing responses while the Challenger predictions are evaluated silently.

## Data Drift Monitoring

The project continues using the existing Data Drift Monitoring implementation.

The monitored numerical features are:

* Age
* Quantity
* Price per Unit

The Kolmogorov-Smirnov (KS) Test compares production inference data against the baseline dataset.

A feature is considered drifted when:

```text
p-value < 0.05
```

The drift statistics are also included in the `/ab/metrics` endpoint when production data is available.

The existing drift endpoint is:

```text
GET /metrics/drift
```  

## API Endpoints

### Root Endpoint

```text
GET /
```

Returns the API status.

### Health Endpoint

```text
GET /health
```

Returns:

```json
{
    "status": "healthy",
    "champion_model": "model_v1.pkl",
    "challenger_model": "model_v2.pkl"
}
```

### Prediction Endpoint

```text
POST /predict
```

Example request:

```json
{
    "Age": 30,
    "Gender": "Male",
    "Product_Category": "Electronics",
    "Quantity": 2,
    "Price_per_Unit": 500
}
```

### Drift Monitoring Endpoint

```text
GET /metrics/drift
```

Detects drift between production inference data and the baseline dataset.

### A/B Metrics Endpoint

```text
GET /ab/metrics
```

Displays comparative metrics for the Champion and Challenger models.

## Testing with 50 Requests

Send approximately 50 POST requests to:

```text
POST /predict
```

After sending the requests, open:

```text
http://localhost:8000/ab/metrics
```

Verify:

* Total request count
* Request distribution
* Champion latency
* Challenger latency
* Prediction agreement
* Drift statistics

For A/B mode with an 80/20 split, the exact result may not always be exactly 40/10 because routing is probabilistic, but the distribution should generally approach the configured ratio as the number of requests increases.

## Docker Setup

### Build the Docker Image

```powershell
docker build --no-cache -t prosensia-ml-service:v7 .
```

### Run the Docker Container

```powershell
docker run -d -p 8000:8000 --name day34_container prosensia-ml-service:v7
```

### Check Container Stability

```powershell
docker ps
```

The container should remain running while processing inference requests.

## Requirements

The project uses:

```text
fastapi==0.115.6
uvicorn==0.34.0
scikit-learn==1.5.2
joblib==1.4.2
numpy==2.1.3
pandas==2.2.3
pydantic==2.9.2
scipy==1.14.1
```

Install dependencies using:

```powershell
pip install -r requirements.txt
```

## Project Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Then build and run:

```powershell
docker build --no-cache -t prosensia-ml-service:v7 .
docker run -d -p 8000:8000 --name day34_container prosensia-ml-service:v7
```

## Observations and Conclusion

Shadow Deployment provides a safe way to evaluate a newly retrained Challenger model because the Champion model continues serving production users.

The Challenger receives the same requests and its predictions and latency can be compared without affecting users.

A/B Traffic Splitting provides controlled exposure to the Challenger model by routing a configurable percentage of traffic to it.

The main trade-off is that Shadow Deployment increases computational overhead because both models process the same request, while A/B testing reduces duplicate computation but exposes some production traffic to the Challenger.

This implementation demonstrates why production Machine Learning models should not be replaced immediately. Validating a new model through Shadow Deployment or controlled A/B testing reduces deployment risk and provides real performance evidence before a full production rollout.
## AUTHOR,
ASMA DUA.