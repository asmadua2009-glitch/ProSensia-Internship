# Day 21 AI Microservice with Docker
This project containerizes a FastAPI-based Machine Learning application that predicts whether a retail transaction is a high-value transaction. The trained Random Forest model is served through FastAPI and packaged inside a Docker container for a portable and consistent deployment environment.
## Project Features
* FastAPI-based AI Microservice
* Random Forest Machine Learning model
* Pydantic input validation
* `/predict` prediction endpoint
* `/health` health-check endpoint
* Swagger API documentation
* Out-of-Distribution (OOD) validation
* Docker containerization
* Non-root user for improved security
* Multi-stage Docker build
## API Endpoints
### GET /
Checks whether the AI Microservice is running.
### GET /health
Returns the health status of the service.
### POST /predict
Accepts transaction details and returns the prediction.
Example Request:

```json
{
  "Age": 30,
  "Gender": "Male",
  "Product_Category": "Beauty",
  "Quantity": 2,
  "Price_per_Unit": 100
}
```

Example Response:

```json
{
  "prediction": 0,
  "result": "Not High Value Transaction"
}
```
## Validation
The API uses Pydantic to validate incoming requests. Incorrect data types and missing required fields return HTTP 422 responses. Custom OOD guardrails return HTTP 400 responses when values fall outside the expected training distribution.
## Docker Setup
Build the Docker image:
```bash
docker build -t high-value-transaction-api .
```
Run the container:

```bash
docker run -d -p 8000:8000 --name high-value-transaction-container high-value-transaction-api
```

Check the running container:

```bash
docker ps
```
## API Documentation

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```
## Project Structure
```text
Day 21/
├── Dockerfile
├── main.py
├── requirements.txt
├── high_value_transaction_model.pkl
└── README.md
```
## Testing
The Dockerized API was tested with valid and invalid inputs. Valid requests returned HTTP 200, incorrect data types returned HTTP 422, missing required fields returned HTTP 422, and out-of-distribution values returned HTTP 400.
## Technologies Used
Python, FastAPI, Pydantic, Pandas, Scikit-learn, Joblib, Uvicorn and Docker.
This project demonstrates how a Machine Learning model can be packaged as a FastAPI microservice and deployed in a portable Docker container.







