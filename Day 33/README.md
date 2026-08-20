# Day 33 Automated Retraining Triggers and Dynamic Model Hot-Swapping
## Project Overview
This project extends the existing containerized FastAPI Machine Learning service by implementing an automated self-healing Machine Learning pipeline.
The system uses real-time Data Drift Monitoring to detect statistically significant changes between production inference data and the original baseline training dataset.
When significant data drift is detected, the `/metrics/drift` endpoint triggers an asynchronous background retraining process.
The retraining pipeline trains an updated model, evaluates its performance using the F1-score, saves a new versioned model artifact, and dynamically reloads the validated model into memory without restarting the FastAPI server or Docker container.

## Project Objective

The automated self-healing ML system:

* Detects production data drift using the Kolmogorov-Smirnov (KS) Test.
* Triggers automated model retraining when significant drift is detected.
* Runs the retraining process asynchronously using FastAPI BackgroundTasks.
* Loads fresh data for model retraining.
* Creates the `High_Value` classification target.
* Applies the Scikit-Learn preprocessing pipeline.
* Trains an updated Random Forest Classifier.
* Evaluates the newly trained model using the F1-score.
* Validates the new model before replacing the production model.
* Creates a new versioned model artifact.
* Dynamically reloads the validated model into memory.
* Uses thread-safe model access and replacement.
* Prevents duplicate retraining processes.
* Keeps the FastAPI service available during model updates.
* Runs successfully inside a Docker container.

## Project Structure
Day 33/

├── main.py
├── schemas.py
├── preprocessing.py
├── drift_detector.py
├── retrain.py
├── pipeline.pkl
├── trained_model.pkl
├── retail_sales_dataset.csv
├── requirements.txt
├── Dockerfile
└── README.md
## Automated Self-Healing Workflow
Prediction Requests
        ↓
FastAPI /predict Endpoint
        ↓
Production Payload Logged
        ↓
In-Memory Production Buffer
        ↓
GET /metrics/drift
        ↓
Load Baseline Training Dataset
        ↓
Kolmogorov-Smirnov Test
        ↓
Data Drift Detected?
        ↓
       Yes
        ↓
FastAPI BackgroundTasks
        ↓
Start retrain.py
        ↓
Load Fresh Dataset
        ↓
Create High_Value Target
        ↓
Train/Test Split
        ↓
Fit Preprocessing Pipeline
        ↓
Train Random Forest Classifier
        ↓
Evaluate F1-Score
        ↓
Model Validation
        ↓
Validation Passed?
        ↓
       Yes
        ↓
Save Versioned Model Artifact
        ↓
Thread-Safe Dynamic Hot-Swap
        ↓
New Model Loaded in Memory
        ↓
FastAPI Continues Without Restart
```

## Data Drift Detection

The project continues to use the Data Drift Monitoring system from Day 32.

The `drift_detector.py` module compares production inference data with the original baseline training dataset.

The monitored numerical features are:

* `Age`
* `Quantity`
* `Price per Unit`

The Kolmogorov-Smirnov (KS) Test is used to compare the feature distributions.

The KS significance threshold is:

```text
0.05
```

A feature is considered drifted when:

```text
p-value < 0.05
```

When one or more monitored features show statistically significant drift, the system flags:

```text
drift_detected: true
```

The drift result is then used to trigger the automated retraining pipeline.

## Automated Retraining Pipeline

The retraining logic is implemented inside:

```text
retrain.py
```

The retraining pipeline performs the following steps:

1. Loads the fresh dataset from `retail_sales_dataset.csv`.
2. Creates the `High_Value` target column.
3. Uses the `Total Amount` column to calculate the median transaction value.
4. Assigns `1` to transactions above the median.
5. Assigns `0` to transactions below or equal to the median.
6. Selects the required numerical and categorical features.
7. Splits the dataset into training and testing data.
8. Creates the preprocessing pipeline.
9. Fits the preprocessing pipeline on training data.
10. Transforms the training and testing datasets.
11. Trains a Random Forest Classifier.
12. Generates predictions on the test dataset.
13. Calculates the F1-score.
14. Saves the updated model as a versioned artifact.
15. Saves the updated preprocessing pipeline.

## Model Training Features

The retraining pipeline uses the following features:

### Numerical Features

* `Age`
* `Quantity`
* `Price per Unit`

### Categorical Features

* `Gender`
* `Product Category`

The preprocessing pipeline performs:

* Median imputation for numerical features.
* Standard scaling for numerical features.
* Most-frequent value imputation for categorical features.
* One-hot encoding for categorical features.

## Model Validation Using F1-Score

Every newly trained model is evaluated before replacing the current production model.

The validation metric used is:

```text
F1-Score
```

The minimum required F1-score is:

```text
0.50
```

The validation workflow is:

```text
New Model Trained
        ↓
Calculate F1-Score
        ↓
F1-Score >= 0.50?
        ↓
      Yes ─────────→ Model Approved
      ↓
      No
      ↓
Production Model Remains Active
```

If the new model fails validation, it is not loaded into production memory.

The existing production model continues serving prediction requests.

## Model Versioning

The original production model is loaded from:

```text
trained_model.pkl
```

After successful retraining, a new versioned model artifact is created.

The model naming pattern is:

```text
model_v2_YYYYMMDD_HHMMSS.pkl
```

Example:

```text
model_v2_20260819_120000.pkl
```

The timestamped versioning approach allows newly trained model artifacts to be distinguished from the original production model.

The updated preprocessing pipeline is saved as:

```text
pipeline_v2.pkl
```

## Background Retraining with FastAPI BackgroundTasks

The `/metrics/drift` endpoint performs the KS-based drift detection.

When significant drift is detected, the system uses FastAPI `BackgroundTasks` to start:

```text
run_retraining()
```

The endpoint can return the drift monitoring response while the retraining process executes in the background.

The retraining workflow is:

```text
GET /metrics/drift
        ↓
KS Test Detects Drift
        ↓
drift_detected = true
        ↓
Background Task Added
        ↓
run_retraining()
        ↓
train_model()
        ↓
F1 Validation
        ↓
Dynamic Model Hot-Swap
```

The system also uses a retraining lock to prevent multiple retraining processes from running simultaneously.

## Dynamic Model Reloading and Hot-Swapping

Dynamic model reloading is managed by the `ModelManager` class.

The application initially loads:

```text
trained_model.pkl
```

and:

```text
pipeline.pkl
```

When a newly trained model passes validation:

1. The new model artifact is loaded.
2. The new preprocessing pipeline is loaded.
3. A thread-safe lock is acquired.
4. The in-memory model reference is replaced.
5. The in-memory pipeline reference is replaced.
6. The active model version is updated.
7. The lock is released.

This process allows the application to use the newly trained model without restarting the FastAPI server.

The Docker container also remains running.

## Thread-Safe Model Access

The `ModelManager` class uses:

```text
threading.Lock()
```

Prediction requests retrieve the current model and pipeline through a protected getter.

The hot-swap operation also uses the lock when replacing the model references.

This ensures that model replacement occurs safely while the application continues handling HTTP requests.

## API Endpoints

### Root Endpoint

```text
GET /
```

Response:

```json
{
    "message": "API is Running Successfully"
}
```

### Health Endpoint

```text
GET /health
```

The endpoint returns the application health status and the currently active model version.

Expected structure:

```json
{
    "status": "healthy",
    "model_version": "model_v1.pkl"
}
```

After successful hot-swapping, the model version changes to the new versioned model artifact.

### Prediction Endpoint

```text
POST /predict
```

The endpoint:

* Receives prediction input.
* Logs the production inference payload.
* Stores the payload in the in-memory production buffer.
* Retrieves the currently active model.
* Applies the currently active preprocessing pipeline.
* Generates a prediction.

Example request:

```powershell
$body = '{"Age":30,"Gender":"Male","Product_Category":"Electronics","Quantity":2,"Price_per_Unit":500}'

Invoke-RestMethod `
    -Uri "http://localhost:8000/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Drift Monitoring Endpoint

```text
GET /metrics/drift
```

The endpoint:

1. Reads the production inference buffer.
2. Loads the baseline dataset.
3. Performs KS statistical tests.
4. Detects statistically significant feature drift.
5. Returns drift metrics.
6. Triggers background retraining when drift is detected.

The response includes:

* Drift status.
* Drifted features.
* KS threshold.
* KS statistic.
* KS p-value.
* Per-feature drift status.
* Production sample count.
* Baseline sample count.
* Retraining trigger status.

## Simulating Production Data Drift

Approximately 50 intentionally shifted prediction requests can be sent to simulate production drift.

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

These shifted values are stored in the production inference buffer.

The `/metrics/drift` endpoint can then compare them with the baseline dataset.

## Testing the Drift and Retraining Pipeline

After sending the drifted prediction requests, call:

```powershell
curl.exe http://localhost:8000/metrics/drift
```

Expected workflow:

```text
Data Drift Detected
        ↓
Background Retraining Triggered
        ↓
Retraining Starts
        ↓
New Model Trained
        ↓
F1-Score Calculated
        ↓
Model Validation Passed
        ↓
New Model Loaded in Memory
        ↓
Hot-Swap Completed
        ↓
Container Continues Running
```

The `/metrics/drift` response includes:

```json
{
    "drift_detected": true,
    "retraining_triggered": true
}
```

Additional KS statistics and feature-level drift metrics are also returned.

## Docker Setup

### Build the Docker Image

```powershell
docker build --no-cache -t prosensia-ml-service:v6 .
```

### Run the Docker Container

```powershell
docker run -d -p 8000:8000 --name day33_container prosensia-ml-service:v6
```

### Check the Running Container

```powershell
docker ps
```

## API Health Check

```powershell
curl.exe http://localhost:8000/health
```

Expected response before retraining:

```json
{
    "status": "healthy",
    "model_version": "model_v1.pkl"
}
```

After successful retraining and hot-swapping, call the health endpoint again to verify that the active model version has changed.

## View Container Logs

The application logs can be checked using:

```powershell
docker logs day33_container
```

The expected verification should show messages similar to:

```text
Drift detected. Starting background retraining...

Retraining completed.

F1 Score: ...

Model hot-swapped successfully: model_v2_YYYYMMDD_HHMMSS.pkl
```

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

Install the dependencies using:

```powershell
pip install -r requirements.txt
```

## Project Setup

```powershell
python -m venv venv

.\venv\Scripts\activate

pip install -r requirements.txt

docker build --no-cache -t prosensia-ml-service:v6 .

docker run -d -p 8000:8000 --name day33_container prosensia-ml-service:v6
```

## Testing Methodology

The complete system is verified using the following methodology:

1. Start the Dockerized FastAPI application.
2. Verify the `/health` endpoint.
3. Send normal prediction requests.
4. Send approximately 50 intentionally shifted prediction requests.
5. Call `/metrics/drift`.
6. Confirm that statistical drift is detected.
7. Confirm that background retraining is triggered.
8. Check the container logs.
9. Verify that the retraining pipeline executes.
10. Verify that the F1-score validation is completed.
11. Confirm that the new model passes validation.
12. Confirm successful dynamic model hot-swapping.
13. Call `/health` again.
14. Verify that the active model version has changed.
15. Confirm that the Docker container was not restarted.

## Expected Verification Results

A successful Day 33 implementation should demonstrate:

```text
Drift Detected: True

Background Retraining: Triggered

Retraining: Completed

Model Validation: Passed

New Model Artifact: Created

Dynamic Hot-Swap: Successful

FastAPI Server Restart: Not Required

Docker Container Restart: Not Required
```

## Key Production Benefit

Data distributions can change after a Machine Learning model is deployed.

Automated drift monitoring allows the system to identify statistically significant changes in production data.

The automated retraining pipeline responds to detected drift by training and validating an updated model.

Dynamic hot-swapping allows the validated model to replace the existing in-memory model without interrupting active HTTP requests.

This creates a more reliable and production-oriented Machine Learning system capable of responding to real-world data drift while maintaining continuous service availability.
