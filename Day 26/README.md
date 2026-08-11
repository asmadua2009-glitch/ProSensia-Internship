# High Value Transaction Prediction API
A production-ready Machine Learning FastAPI microservice for predicting high-value transactions using a serialized Scikit-learn model and Docker.
## Technologies
- Python 3.11
- FastAPI
- Pydantic
- Uvicorn
- Pandas
- NumPy
- Scikit-learn
- Joblib
- Docker
## Project Structure
```text
Day 26/
├── model/
│   └── high_value_transaction_model.pkl
├── main.py
├── feature_names.txt
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
````
## API Input
The `/predict` endpoint accepts:
* Age
* Gender
* Product Category
* Quantity
* Price per Unit
## API Endpoints
### GET `/`
Checks whether the API is running.
### GET `/health`
Checks model availability.
Example response:
```json
{
  "status": "healthy"
}
```
### POST `/predict`
Example request:
```json
{  "Age": 35,
  "Gender": "Male",
  "Product_Category": "Electronics",
  "Quantity": 2,
  "Price_per_Unit": 100
}
```
Example response:
```json
{
  "prediction": "0"
}
```
## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```
## Docker Build

```bash
docker build -t prosensia-ml-service:v1 .
```
## Run Docker Container
```bash
docker run --name prosensia-ml-container -p 8000:8000 prosensia-ml-service:v1
```
## Test Docker API
Open:
```text
http://127.0.0.1:8000/docs
```
Use the `/predict` endpoint with:

```json
{
  "Age": 35,
  "Gender": "Male",
  "Product_Category": "Electronics",
  "Quantity": 2,
  "Price_per_Unit": 100
}
```
Expected response:

```json
{
  "prediction": "0"
}
```
## Model Loading
The trained model is loaded once during FastAPI application startup instead of being loaded for every prediction request. This improves inference efficiency and reduces unnecessary model-loading overhead.
## Validation and Security
The API includes:
* Pydantic input validation
* Extra-field rejection
* Input range validation
* Suspicious input detection
* Out-of-distribution (OOD) checks
* Controlled error responses
## Dockerization
Docker packages the FastAPI application, dependencies, and trained model into a consistent environment, helping solve the "works on my machine" problem.
## Testing
The API was successfully tested locally and inside Docker.
```text
POST /predict → 200 OK
Prediction → 0
```

```
```
