# 🚀 Day 25  Production-Ready FastAPI Docker Deployment

## 📌 Project Overview

This project focuses on containerizing a production-ready FastAPI machine learning API using Docker.
The API provides an e-commerce prediction service and includes security-focused input validation, Out-of-Distribution (OOD) detection, structured API responses, and a lightweight multi-stage Docker build.
The application is packaged into a Docker image and deployed as a containerized FastAPI service.

## 🎯 Objectives

* Containerize the FastAPI ML application using Docker.
* Use a lightweight `python:3.11-slim` base image.
* Implement a multi-stage Docker build.
* Keep the production image optimized and secure.
* Install dependencies inside an isolated virtual environment.
* Run the application using a non-root user.
* Add input validation using Pydantic.
* Implement Out-of-Distribution (OOD) guardrails.
* Validate categorical string inputs using length and pattern constraints.
* Expose the API through Swagger UI.
* Verify the Dockerized API using real requests.

## 🏗️ Project Structure

```text
Day 25/
│
├── model/
│   └── trained model files
│
├── .dockerignore
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```

## 🛠️ Technologies Used

* Python 3.11
* FastAPI
* Uvicorn
* Pydantic
* Pandas
* Scikit-learn
* Joblib
* Docker
* Docker Desktop

---

## 🐳 Docker Implementation

The application uses a multi-stage Docker build.

### Builder Stage

The builder stage:

* Creates an isolated Python virtual environment.
* Installs all required Python dependencies.
* Keeps build-related operations separate from the production image.

### Production Stage

The production stage:

* Uses `python:3.11-slim`.
* Copies only the required virtual environment and application files.
* Creates a dedicated non-root application user.
* Runs the FastAPI application with Uvicorn.
  This approach helps create a smaller and more secure production container.

---

## 📦 Dependencies

The application uses the following packages:

```text
fastapi
uvicorn
pydantic
pandas
scikit-learn
joblib
```

---

## 🔐 API Security & Validation

The API includes multiple layers of input validation.

### 1. Pydantic Validation

Incoming request data is validated before reaching the prediction logic.
Examples include:

* Numeric type validation
* String length validation
* String pattern validation
* Required field validation

### 2. Out-of-Distribution Guardrails

The API detects inputs outside the expected data distribution.
For example, unrealistic values such as:

```json
{
  "Age": 120,
  "Gender": "Male",
  "Product_Category": "Electronics",
  "Quantity": 1000,
  "Price_per_Unit": 100
}
```

are rejected with:

```json
{
  "detail": "Data Out of Bounds: OOD input detected."
}
```

HTTP status:

```text
400 Bad Request
```

### 3. String Validation

Invalid or potentially unsafe string values are rejected.
For example:

```text
javascript:alert
```

is rejected because it does not match the allowed alphabetic pattern.
The API returns:

```text
422 Unprocessable Entity
```

---

## 🌐 Running the Application

Build the Docker image:

```powershell
docker build --no-cache -t prosensia-aiml-api:v1.0.0 .
```

Run the container:

```powershell
docker run -d --name prosensia-api -p 8000:8000 prosensia-aiml-api:v1.0.0
```

Check the running container:

```powershell
docker ps
```

View application logs:

```powershell
docker logs prosensia-api
```

---

## 📖 Swagger API Documentation

Once the container is running, open:

```text
http://localhost:8000/docs
```

## Swagger UI provides an interactive interface for testing the API endpoints.

## 🔌 API Endpoint

### POST `/predict`

The `/predict` endpoint accepts customer transaction information and returns a prediction.

### Example Request

```json
{
  "Age": 35,
  "Gender": "Male",
  "Product_Category": "Electronics",
  "Quantity": 2,
  "Price_per_Unit": 100
}
```

### Example Successful Response

```json
{
  "prediction": "0"
}
```

HTTP status:

```text
200 OK
```

---

## 🧪 API Testing Results

The Dockerized API was tested with valid, invalid, and out-of-distribution inputs.

| Test Case                 | Expected Result     | Status |
| ------------------------- | ------------------- | ------ |
| Valid prediction request  | Prediction returned | ✅ 200  |
| Out-of-distribution input | Request rejected    | ✅ 400  |
| Excessively long string   | Validation error    | ✅ 422  |
| Invalid string pattern    | Validation error    | ✅ 422  |
| Swagger documentation     | Successfully loaded | ✅ 200  |

---

## 📊 Container Verification

The running container was successfully verified with:

```text
docker ps
```

The application reported:

```text
Uvicorn running on http://0.0.0.0:8000
```

Swagger documentation was successfully accessed through:

```text
GET /docs → 200 OK
GET /openapi.json → 200 OK
```

Prediction testing also produced:

```text
POST /predict → 200 OK
```

Invalid/OOD requests correctly produced:

```text
POST /predict → 400 Bad Request
POST /predict → 422 Unprocessable Entity
```

---

## 🔒 Security Practices

This project follows several production-oriented practices:

* Multi-stage Docker build
* Lightweight Python base image
* Non-root application user
* Isolated Python virtual environment
* Pydantic request validation
* Input length restrictions
* Regex-based string validation
* Out-of-Distribution detection
* Docker `.dockerignore`
* Structured API responses
* Separation of builder and production stages

---

## 📈 Key Learning Outcomes

Through this project, I learned how to:

* Containerize a FastAPI machine learning application.
* Build optimized Docker images using multi-stage builds.
* Configure Uvicorn inside Docker.
* Manage Python dependencies in containers.
* Implement API-level input validation.
* Add OOD protection to an ML API.
* Test APIs through Swagger UI.
* Inspect Docker container logs.
* Apply production-oriented security practices.

---

## 🚀 Future Improvements

Possible future improvements include:

* Add automated unit and integration tests.
* Add Docker Compose configuration.
* Add CI/CD using GitHub Actions.
* Add structured application logging.
* Add API authentication and authorization.
* Add container health checks.
* Add monitoring and metrics.
* Deploy the container to a cloud platform.

---

## 👩‍💻 Author

**Asma Dua**
AI/ML Internship — ProSensia

### Day 25 Focus

**Production-Ready FastAPI Docker Deployment & API Security**
