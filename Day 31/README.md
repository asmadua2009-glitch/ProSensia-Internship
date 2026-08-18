# Day 31 Modular Preprocessing Pipelines & Serialized ColumnTransformers

## Project Overview

This project upgrades the existing Machine Learning preprocessing system by implementing an automated, reusable, and serializable preprocessing pipeline using Scikit-Learn `Pipeline` and `ColumnTransformer`.

The objective is to combine numerical scaling, categorical encoding, and missing-value handling into a single preprocessing pipeline that can be reused consistently during model inference and deployment.

The complete application is integrated with FastAPI and Docker to support production-style Machine Learning inference.

---

## Project Objective

The main objectives of Day 31 are:

* Build a modular Scikit-Learn preprocessing pipeline.
* Use `ColumnTransformer` for numerical and categorical features.
* Apply `StandardScaler` to numerical features.
* Apply `OneHotEncoder` to categorical features.
* Handle missing values using `SimpleImputer`.
* Prevent data leakage by fitting preprocessing only on training data.
* Serialize the fitted preprocessing pipeline using Joblib.
* Integrate the serialized pipeline with FastAPI.
* Containerize the complete prediction service using Docker.
* Verify raw input to final prediction through Postman.

---

## Dataset

The project uses the Retail Sales Dataset.

### Dataset Features

The dataset contains the following columns:

* `Transaction ID`
* `Date`
* `Customer ID`
* `Gender`
* `Age`
* `Product Category`
* `Quantity`
* `Price per Unit`
* `Total Amount`

### Features Used for Prediction

#### Numerical Features

* `Age`
* `Quantity`
* `Price per Unit`

#### Categorical Features

* `Gender`
* `Product Category`

The target column is:

* `Total Amount`

---

## Preprocessing Pipeline

The preprocessing logic is implemented in the modular Python file:

```text
preprocessing.py
```

The pipeline uses:

### Numerical Pipeline

```text
SimpleImputer(strategy="median")
        ↓
StandardScaler()
```

### Categorical Pipeline

```text
SimpleImputer(strategy="most_frequent")
        ↓
OneHotEncoder(handle_unknown="ignore")
```

Both pipelines are combined using:

```text
ColumnTransformer
```

The final preprocessing object is serialized as:

```text
pipeline.pkl
```

---

## Data Leakage Prevention

To prevent data leakage, the dataset is first divided into training and testing partitions.

The preprocessing pipeline is fitted only on the training data:

```python
pipeline.fit(X_train)
```

The testing data is not used while fitting:

* Scalers are not fitted on the complete dataset.
* Encoders are not fitted on the complete dataset.
* Imputers are not fitted on the complete dataset.
* Test data remains unseen during preprocessing fitting.

The fitted pipeline is later reused to transform incoming prediction data.

This ensures consistent preprocessing between training and production inference.

---

## Pipeline Construction

The pipeline is created using:

```python
ColumnTransformer
```

The numerical features are processed with:

```python
SimpleImputer(strategy="median")
StandardScaler()
```

The categorical features are processed with:

```python
SimpleImputer(strategy="most_frequent")
OneHotEncoder(handle_unknown="ignore")
```

The fitted pipeline is saved using Joblib:

```python
joblib.dump(pipeline, "pipeline.pkl")
```

---

## Serialized Model Artifacts

The project contains two important serialized Machine Learning artifacts:

```text
pipeline.pkl
trained_model.pkl
```

### pipeline.pkl

Contains the fitted preprocessing pipeline.

It transforms raw input into the numerical feature representation expected by the trained model.

### trained_model.pkl

Contains the trained Random Forest classifier.

The trained model expects 8 transformed features.

---

## API Architecture

The complete prediction flow is:

```text
Raw JSON Request
       |
       v
Pydantic Validation
       |
       v
Pandas DataFrame
       |
       v
pipeline.pkl
       |
       v
Preprocessed Features
       |
       v
trained_model.pkl
       |
       v
Prediction
       |
       v
JSON Response
```

This architecture separates preprocessing from model inference and allows the same fitted preprocessing pipeline to be reused during deployment.

---

## FastAPI Application

The FastAPI application is implemented in:

```text
main.py
```

The API loads both serialized artifacts when the application starts:

```python
model = joblib.load(MODEL_PATH)
pipeline = joblib.load(PIPELINE_PATH)
```

The `/predict` endpoint:

1. Receives raw JSON.
2. Validates the request using Pydantic.
3. Converts the request into a Pandas DataFrame.
4. Passes the DataFrame through `pipeline.transform()`.
5. Sends the transformed data to the trained model.
6. Returns the final prediction as JSON.

---

## Pydantic Schema

The request and response schemas are defined in:

```text
schemas.py
```

### Example Raw Request

```json
{
    "Age": 30,
    "Gender": "Male",
    "Product_Category": "Electronics",
    "Quantity": 2,
    "Price_per_Unit": 500
}
```

The API accepts the raw, unprocessed values and performs preprocessing automatically.

---

## API Endpoints

### GET /

Returns the API status message.

Example:

```json
{
    "message": "API is Running Successfully"
}
```

### GET /health

Returns the health status.

Example:

```json
{
    "status": "healthy"
}
```

### POST /predict

Accepts raw Machine Learning input and returns the prediction.

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

Example response:

```json
{
    "prediction": 0.0
}
```

---

## Docker Configuration

The application is containerized using Docker.

### Docker Image

The required Docker image name is:

```text
prosensia-ml-service:v4
```

### Build Command

```bash
docker build -t prosensia-ml-service:v4 .
```

### Run Command

```bash
docker run -d --name prosensia-day31 -p 8000:8000 prosensia-ml-service:v4
```

### Verify Container

```bash
docker ps
```

The Day 31 container was successfully verified as running with port mapping:

```text
0.0.0.0:8000->8000/tcp
```

---

## Docker Prediction Verification

The Dockerized FastAPI service was tested using a raw prediction request.

### Request

```json
{
    "Age": 30,
    "Gender": "Male",
    "Product_Category": "Electronics",
    "Quantity": 2,
    "Price_per_Unit": 500
}
```

### Response

```json
{
    "prediction": 0.0
}
```

### HTTP Status

```text
200 OK
```

The prediction request was successfully completed inside the Dockerized FastAPI service.

---

## Postman Testing

The `/predict` endpoint was tested using Postman.

### Endpoint

```text
POST http://localhost:8000/predict
```

### Request Body

```json
{
    "Age": 30,
    "Gender": "Male",
    "Product_Category": "Electronics",
    "Quantity": 2,
    "Price_per_Unit": 500
}
```

### Result

```text
200 OK
```

### Prediction Response

```json
{
    "prediction": 0.0
}
```

### Response Time

```text
36 ms
```

The measured Postman response time was below the required 500 ms target.

The Postman testing evidence is included in:

```text
postman_prediction_test.png
```

---

## Project Structure

```text
Day 31/
│
├── build_pipeline.py
├── preprocessing.py
├── main.py
├── schemas.py
├── Dockerfile
├── requirements.txt
├── README.md
│
├── retail_sales_dataset.csv
│
├── pipeline.pkl
├── trained_model.pkl
│
└── postman_prediction_test.png
```

---

## Technologies Used

* Python
* FastAPI
* Pydantic
* Pandas
* NumPy
* Scikit-Learn
* Joblib
* Docker
* Postman

---

## Dependencies

The project dependencies are defined in:

```text
requirements.txt
```

Required packages include:

```text
fastapi
uvicorn
scikit-learn
joblib
numpy
pandas
pydantic
```

---

## Production Workflow

The production prediction workflow is:

```text
Client
  |
  v
FastAPI
  |
  v
Pydantic Validation
  |
  v
Pandas DataFrame
  |
  v
Serialized pipeline.pkl
  |
  v
Numerical Scaling + Categorical Encoding
  |
  v
trained_model.pkl
  |
  v
Prediction
  |
  v
JSON Response
```

The preprocessing pipeline is serialized separately so that the exact fitted preprocessing logic can be reused without retraining during application startup or prediction.

---

## Verification Summary

The following Day 31 requirements were successfully verified:

* Modular preprocessing module created.
* Scikit-Learn Pipeline implemented.
* ColumnTransformer implemented.
* StandardScaler implemented.
* OneHotEncoder implemented.
* Missing-value imputation implemented.
* Training/testing split performed.
* Pipeline fitted only on `X_train`.
* `pipeline.pkl` successfully created.
* Trained model artifact available.
* FastAPI updated to load pipeline and model.
* Raw JSON prediction request supported.
* Local `/predict` endpoint verified.
* Docker image `prosensia-ml-service:v4` successfully built.
* Docker container successfully started.
* `docker ps` confirmed the container is running.
* Docker `/predict` endpoint returned `200 OK`.
* Postman returned `200 OK`.
* Postman response time was 36 ms.
* Prediction response was successfully returned as JSON.

---

## Day 31 Deliverables

The Day 31 submission includes:

* Modular preprocessing Python files
* Updated FastAPI application
* Pydantic schemas
* Serialized preprocessing pipeline
* Trained model artifact
* Dockerfile
* requirements.txt
* README.md
* Postman testing screenshot
