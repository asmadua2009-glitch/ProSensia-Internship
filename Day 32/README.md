# Day 32 Real-Time Data Drift Monitoring and Telemetry
# Project Overview
This project enhances the existing containerized FastAPI Machine Learning service by implementing real-time Data Drift Monitoring and Telemetry.

The system logs incoming prediction requests, stores production inference data in an in-memory buffer, and compares production data with the original training dataset.

The Kolmogorov-Smirnov (KS) Test is used to detect statistically significant changes in numerical feature distributions.

## Project Objective

The monitoring system:

- Logs incoming prediction requests.
- Stores production inference payloads in memory.
- Loads the original training dataset as the baseline.
- Compares production data with baseline data.
- Uses the Kolmogorov-Smirnov (KS) Test for drift detection.
- Identifies features with significant distribution changes.
- Exposes monitoring results through the `/metrics/drift` endpoint.
- Runs inside a Docker container.

## Project Structure

```text
Day 32/
│
├── main.py
├── schemas.py
├── preprocessing.py
├── drift_detector.py
├── pipeline.pkl
├── trained_model.pkl
├── retail_sales_dataset.csv
├── requirements.txt
├── Dockerfile
└── README.md
````

## How Drift Monitoring Works

```text
Prediction Request
        ↓
FastAPI /predict Endpoint
        ↓
Production Payload Logged
        ↓
In-Memory Production Buffer
        ↓
/metrics/drift Endpoint
        ↓
Load Baseline Training Dataset
        ↓
Compare Production vs Baseline Data
        ↓
Kolmogorov-Smirnov Test
        ↓
Calculate KS Statistic and p-value
        ↓
Detect Significant Drift
        ↓
Return Structured JSON Response
```

The original `retail_sales_dataset.csv` is used as the baseline dataset.

Production inference requests are stored in an in-memory buffer and compared with the baseline dataset when the `/metrics/drift` endpoint is called.

## Incoming Request Logging

Incoming prediction requests sent to `/predict` are processed asynchronously.

The production payload contains:

* Age
* Gender
* Product Category
* Quantity
* Price per Unit

The production inference payloads are stored in memory for drift analysis.

## Statistical Drift Detection

The project uses the Kolmogorov-Smirnov (KS) Test from SciPy.

The monitored numerical features are:

* `Age`
* `Quantity`
* `Price per Unit`

The KS significance threshold is:

```text
0.05
```

A feature is considered drifted when:

```text
p-value < 0.05
```

A p-value greater than or equal to `0.05` does not indicate statistically significant drift.

## Drift Monitoring Endpoint

The application provides:

```text
GET /metrics/drift
```

The endpoint returns:

* Drift status
* Drifted features
* KS threshold
* KS statistic
* KS p-value
* Per-feature drift status
* Production sample count
* Baseline sample count

Example:

```json
{
    "drift_detected": true,
    "drifted_features": [
        "Age",
        "Quantity",
        "Price per Unit"
    ],
    "ks_threshold": 0.05,
    "feature_metrics": {
        "Age": {
            "ks_statistic": 0.865392,
            "ks_p_value": 0.0,
            "drift_detected": true
        },
        "Quantity": {
            "ks_statistic": 0.717392,
            "ks_p_value": 0.0,
            "drift_detected": true
        },
        "Price per Unit": {
            "ks_statistic": 0.801,
            "ks_p_value": 0.0,
            "drift_detected": true
        }
    },
    "production_samples": 51,
    "baseline_samples": 1000
}
```

## Docker Setup

### Build the Docker Image

```powershell
docker build --no-cache -t prosensia-ml-service:v5 .
```

### Run the Docker Container

```powershell
docker run -d -p 8000:8000 --name day32_container prosensia-ml-service:v5
```

### Check the Container

```powershell
docker ps
```

## API Health Check

```powershell
curl.exe http://localhost:8000/health
```

Expected response:

```json
{
    "status": "healthy"
}
```

## Testing the Prediction Endpoint

```powershell
$body = '{"Age":30,"Gender":"Male","Product_Category":"Electronics","Quantity":2,"Price_per_Unit":500}'; Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -ContentType "application/json" -Body $body
```

## Simulating Production Data Drift

Approximately 50 intentionally shifted prediction requests can be sent using:

```powershell
1..50 | ForEach-Object {
    $body = @{
        Age = 60 + ($_ % 5)
        Gender = "Male"
        Product_Category = "Electronics"
        Quantity = 4
        Price_per_Unit = 500
    } | ConvertTo-Json

    Invoke-RestMethod `
        -Uri "http://localhost:8000/predict" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
}
```

## Testing the Drift Endpoint

```powershell
curl.exe http://localhost:8000/metrics/drift
```

The endpoint detects statistically significant changes between production and baseline data.

## Required Dependencies

```text
fastapi==0.115.6
uvicorn==0.34.0
scikit-learn==1.5.2
joblib==1.4.2
numpy==2.1.3
pandas==2.2.3
pydantic==2.9.2
scipy
```

Install dependencies with:

```powershell
pip install -r requirements.txt
```

## Project Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
docker build --no-cache -t prosensia-ml-service:v5 .
docker run -d -p 8000:8000 --name day32_container prosensia-ml-service:v5
```

## Verification Results

The drift monitoring system was tested with 50 intentionally shifted production prediction requests.

Detected drifted features:

* Age
* Quantity
* Price per Unit

The final verification showed:

```text
Drift Detected: True
KS Threshold: 0.05
Production Samples: 51
Baseline Samples: 1000
```

The KS p-values were below the `0.05` threshold, confirming statistically significant data drift.

```
```
