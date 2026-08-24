
# Day 35  Automated End-to-End MLOps Pipeline

## Project Overview

This project implements an automated MLOps pipeline using FastAPI, Docker, data drift detection, automated retraining, model hot-swapping, and A/B traffic routing.

## Automated MLOps Workflow

Production Requests  
↓  
Inference Logging  
↓  
Data Drift Detection  
↓  
Drift Alert Triggered  
↓  
Background Model Retraining  
↓  
New Challenger Model Created  
↓  
Thread-Safe Model Hot Swap  
↓  
A/B Traffic Split Updated  

## API Endpoints

### Health Check

`GET /health`

### Prediction

`POST /predict`

### Drift Monitoring

`GET /metrics/drift`

### A/B Metrics

`GET /ab/metrics`

## Running the Project

```powershell
cd "C:\Users\cc\Desktop\ProSensia Internship\Day 35"
````

```powershell
..\venv\Scripts\Activate.ps1
```

```powershell
pip install -r requirements.txt
```

```powershell
python retrain.py
```

```powershell
uvicorn main:app --reload
```

## Testing

```powershell
pytest -v
```

Result:

```text
6 passed
```

## Docker Deployment

Build the image:

```powershell
docker build --no-cache -t day35-mlops .
```

Run the container:

```powershell
docker run -d -p 8000:8000 --name day35-container day35-mlops
```

Check the container:

```powershell
docker ps
```

Check logs:

```powershell
docker logs day35-container
```

## Project Structure

```text
Day 35/
├── main.py
├── router.py
├── retrain.py
├── drift_detector.py
├── preprocessing.py
├── schemas.py
├── test_pipeline.py
├── model_v1.pkl
├── model_v2.pkl
├── pipeline.pkl
├── pipeline_v2.pkl
├── retail_sales_dataset.csv
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

## Technologies Used

* Python
* FastAPI
* Scikit-learn
* Pandas
* NumPy
* SciPy
* Joblib
* Pydantic
* Pytest
* Docker

## Key Results

* Data drift detected successfully.
* Background retraining triggered automatically.
* Challenger model generated as `model_v2.pkl`.
* Thread-safe model hot-swapping implemented.
* A/B traffic split updated from 80/20 to 50/50.
* API and A/B metrics implemented.
* All automated tests passed.
* Docker container deployed successfully.

## Author

ASMA DUA 
ProSensia AI/ML Internship – Day 35
