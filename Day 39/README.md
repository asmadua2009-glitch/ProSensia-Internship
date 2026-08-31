# ML-39  GitHub Actions CI/CD Pipeline & Automated Container Registry Builds

## Project Objective

The objective of this project is to automate the Machine Learning software delivery lifecycle using **GitHub Actions CI/CD**.

The pipeline automatically tests the FastAPI application, validates code quality, builds the production Docker image, and pushes the verified image to **GitHub Container Registry (GHCR)** whenever changes are pushed to GitHub.

---

## Key Features

* FastAPI Machine Learning microservice
* Automated API testing with pytest
* FastAPI TestClient integration testing
* API authentication and validation
* Out-of-bound input protection
* Automated drift detection
* Automated model retraining
* Champion/Challenger A/B model routing
* Prometheus monitoring
* Docker containerization
* GitHub Actions CI/CD
* GitHub Container Registry integration

---

## Automated Test Suite

The project includes a modular `test_pipeline.py` test suite using **pytest** and **FastAPI TestClient**.

The tests verify:

* Authentication failure returns **401 Unauthorized**
* Invalid input returns **422 Unprocessable Entity**
* Out-of-bound or invalid values return **400 Bad Request**
* Valid model inference returns **200 OK**

Run the tests locally:

```bash
pytest
```

Current test result:

```text
6 passed
```

---

## CI/CD Pipeline

The GitHub Actions workflow is located at:

```text
.github/workflows/main.yml
```

The pipeline performs the following steps:

1. Checkout the repository
2. Set up Python 3.11
3. Install project dependencies
4. Validate formatting with Black
5. Validate code quality with Flake8
6. Run the automated pytest test suite
7. Build the production Docker image
8. Tag the image as `prosensia-ml-service:latest`
9. Authenticate with GitHub Container Registry
10. Push the verified Docker image to GHCR

The Docker build depends on the successful completion of the testing and validation stage.

```text
Code Push
   ↓
GitHub Actions
   ↓
Install Dependencies
   ↓
Black Validation
   ↓
Flake8 Validation
   ↓
Pytest
   ↓
Docker Build
   ↓
GHCR
```

---

## Docker

The project includes production Docker configuration:

```text
Dockerfile
docker-compose.yml
```

The Docker image is tagged as:

```text
prosensia-ml-service:latest
```

The image is published to GitHub Container Registry after the CI validation stage succeeds.

---

## Container Registry

GitHub Container Registry (GHCR) is used to store the verified Docker image.

GitHub Actions authenticates securely using the repository's GitHub token and required package permissions.

The image uses the following tag:

```text
prosensia-ml-service:latest
```

Container image tagging provides a simple way to identify and deploy application versions within an MLOps workflow.

---

## Code Quality

The project uses **Black** for Python code formatting and **Flake8** for code-quality validation.

Black configuration is maintained in:

```text
pyproject.toml
```

The project uses a 79-character line length so that Black and Flake8 follow the same formatting standard.

Run Black:

```bash
black .
```

Check formatting:

```bash
black --check .
```

Run Flake8:

```bash
flake8 . --exclude=.venv,venv,__pycache__,.git
```

---

## Security

Sensitive configuration is managed through environment variables and repository secrets.

The project includes:

```text
.env.example
```

Sensitive values such as API keys should be stored securely and should not be committed to the public repository.

---

## Project Structure

```text
Day 39/
│
├── .github/
│   └── workflows/
│       └── main.yml
│
├── grafana/
│   ├── datasource.yml
│   └── dashboards/
│
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
│
├── main.py
├── router.py
├── schemas.py
├── security.py
├── drift_detector.py
├── retrain.py
├── preprocessing.py
├── gunicorn_conf.py
│
├── test_pipeline.py
│
├── model_v1.pkl
├── model_v2.pkl
├── pipeline.pkl
├── pipeline_v2.pkl
│
├── retail_sales_dataset.csv
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Technologies Used

* Python
* FastAPI
* Pydantic
* pytest
* FastAPI TestClient
* Black
* Flake8
* GitHub Actions
* Docker
* Docker Compose
* GitHub Container Registry
* Prometheus
* Grafana
* NumPy
* Pandas
* Scikit-learn
* Joblib

---

## Why CI/CD Matters in MLOps

CI/CD helps prevent bad code and broken changes from reaching production.

Automated testing verifies that important API functionality continues to work correctly. Code-quality checks identify formatting and quality problems before deployment.

The Docker build is also gated behind the test and validation stage. Therefore, if the tests fail, the production Docker image is not built or published.

This creates a reliable and repeatable software delivery process for Machine Learning applications.

---

## Integration Testing in MLOps

Integration testing is important because an ML service contains more than just a trained model.

The complete workflow includes:

```text
API Request
    ↓
Authentication
    ↓
Input Validation
    ↓
Preprocessing
    ↓
Model Inference
    ↓
API Response
```

Automated integration tests help verify that these components work together correctly.

---

## Day 39 Verification

The local project has successfully passed:

```text
Black          PASS
Flake8         PASS
Pytest         6 passed
```

The GitHub Actions pipeline is configured to perform these validations automatically before building and publishing the Docker image.

---

## Assignment

**ML-39 — GitHub Actions CI/CD Pipeline & Automated Container Registry Builds**

This project demonstrates a complete CI/CD workflow for an ML microservice, including automated testing, code-quality validation, Docker image building, and GitHub Container Registry publishing.
