# Day 37  Securing a FastAPI ML Microservice

## Project Overview

This project strengthens an existing FastAPI Machine Learning microservice by implementing API Key Authentication, Rate Limiting, and strict CORS policies.

The existing MLOps functionality is preserved, including data drift detection, background model retraining, model hot-swapping, and A/B deployment monitoring.

## Features

- API Key Authentication using `X-API-Key`
- 401 Unauthorized for missing or invalid API keys
- Environment variables using `pydantic-settings`
- Rate limiting using SlowAPI
- `/predict` limited to 10 requests per minute per client
- 429 Too Many Requests when the limit is exceeded
- Strict CORS policy with explicitly allowed origins
- No hardcoded API keys or secrets
- Secure Docker environment variable handling

## API Key Authentication

Protected endpoints require:

```text
X-API-Key: your-secret-api-key
````

The authentication logic is implemented in:

```text
security.py
```

API keys are stored in environment variables and are not hardcoded inside Python files.

Missing or invalid API keys return:

```text
401 Unauthorized
```

Example:

```json
{
  "detail": "Invalid or missing API key"
}
```

## Environment Variables

Example `.env`:

```env
API_KEYS=your-secret-api-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

The actual `.env` file is ignored by Git.

The project includes `.env.example` to document the required environment variables.

## Rate Limiting

The `/predict` endpoint is limited to:

```text
10 requests per minute per client
```

When the limit is exceeded:

```text
429 Too Many Requests
```

Example:

```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

Rate limiting helps protect CPU/GPU-intensive ML inference endpoints from excessive traffic and resource abuse.

## CORS Policy

Only explicitly verified origins are allowed.

Example:

```text
http://localhost:3000
http://localhost:5173
```

The application does not use:

```python
allow_origins=["*"]
```

Allowed headers include:

```text
Content-Type
X-API-Key
```

## Existing MLOps Features

* Statistical data drift detection
* Production inference monitoring
* Background model retraining
* Model hot-swapping
* Champion and Challenger models
* A/B traffic splitting
* A/B deployment metrics

## Project Structure

```text
Day 37/
│
├── main.py
├── security.py
├── router.py
├── schemas.py
├── preprocessing.py
├── drift_detector.py
├── retrain.py
├── gunicorn_conf.py
├── locustfile.py
│
├── Dockerfile
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── model_v1.pkl
├── model_v2.pkl
├── pipeline.pkl
├── pipeline_v2.pkl
│
└── retail_sales_dataset.csv
```

## Installation

```bash
pip install -r requirements.txt
```

## Run Locally

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate
```

Run the application:

```powershell
python -m uvicorn main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Testing

### Missing API Key

Send a request to:

```text
POST /predict
```

without the `X-API-Key` header.

Expected:

```text
401 Unauthorized
```

### Valid API Key

Send:

```text
X-API-Key: your-secret-api-key
```

Request body:

```json
{
  "Age": 30,
  "Gender": "Male",
  "Product_Category": "Electronics",
  "Quantity": 2,
  "Price_per_Unit": 500
}
```

Expected:

```text
200 OK
```

### Rate Limit Test

Send 15 rapid requests with a valid API key.

Expected after exceeding 10 requests:

```text
429 Too Many Requests
```

## Docker Deployment

Build the image:

```bash
docker build -t prosensia-ml-service:v9 .
```

Run the container securely:

```bash
docker run --env-file .env -p 8000:8000 --name day37-container prosensia-ml-service:v9
```

Check running containers:

```bash
docker ps
```

Check logs:

```bash
docker logs day37-container
```

## Docker Verification

The following tests were successfully completed:

| Test                   | Result                |
| ---------------------- | --------------------- |
| Missing API Key        | 401 Unauthorized      |
| Valid API Key          | 200 OK                |
| 15 Rapid Requests      | 429 Too Many Requests |
| Docker Valid API Key   | 200 OK                |
| Docker Missing API Key | 401 Unauthorized      |
| Docker Rate Limit      | 429 Too Many Requests |

## Security Best Practices

* API keys are not hardcoded in Python files.
* API keys are not stored in the Dockerfile.
* Secrets are loaded using environment variables.
* `.env` is included in `.gitignore`.
* `.env.example` documents required variables.
* Protected endpoints require `X-API-Key`.
* Invalid API keys return 401.
* Heavy inference endpoints are rate limited.
* Only explicitly allowed CORS origins are permitted.
* `allow_origins=["*"]` is not used.
* Authentication logic is kept modular in `security.py`.

## Conclusion

This project secures a FastAPI ML microservice using API Key Authentication, Rate Limiting, and strict CORS policies.

The `/predict` endpoint requires a valid API key, unauthorized requests return `401 Unauthorized`, and excessive requests return `429 Too Many Requests`.

All security features were successfully tested locally and inside Docker while preserving the existing MLOps pipeline.

```
```
## Author
ASMA DUA
