# Day 36 Multi-Worker Gunicorn Deployment & Microservice Memory Optimization

## Project Overview

This project upgrades an existing FastAPI Machine Learning microservice from a single-process Uvicorn deployment to a scalable multi-worker Gunicorn architecture.

The objective of this implementation is to improve concurrency, scalability, worker management, and production readiness while monitoring memory usage during concurrent ML inference requests.

The application uses Gunicorn as the production process manager and `uvicorn.workers.UvicornWorker` to serve the FastAPI application through multiple worker processes.

---

## Project Objectives

The main objectives of this project are:

* Upgrade the FastAPI ML microservice from single-process Uvicorn to Gunicorn.
* Configure multiple Uvicorn worker processes.
* Dynamically calculate workers based on available CPU cores.
* Apply the `2 × Cores + 1` worker formula.
* Configure appropriate timeouts for ML inference requests.
* Monitor memory usage across multiple worker processes.
* Reduce unnecessary ML model memory duplication where possible.
* Test the application using Locust with 100 concurrent virtual users.
* Monitor throughput, Requests Per Second (RPS), worker stability, and RAM usage.
* Verify graceful container shutdown using `docker stop`.

---

# Architecture

The production architecture is:

```text
                    ┌─────────────────────┐
                    │      Client         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Gunicorn       │
                    │   Master Process    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐    ┌────────────┐   ┌────────────┐
       │ Uvicorn    │    │ Uvicorn    │   │ Uvicorn    │
       │ Worker     │    │ Worker     │   │ Worker     │
       └─────┬──────┘    └─────┬──────┘   └─────┬──────┘
             │                 │                │
             └─────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI App      │
                    │      main:app       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ ML Models/Pipelines │
                    └─────────────────────┘
```

Gunicorn manages the master process and multiple worker processes. Each worker uses `uvicorn.workers.UvicornWorker` to handle FastAPI requests.

---

# Gunicorn Multi-Worker Configuration

The project includes a dedicated:

```text
gunicorn_conf.py
```

The configuration includes:

* Dynamic worker calculation.
* CPU core detection using Python multiprocessing.
* Worker formula:

```text
workers = multiprocessing.cpu_count() * 2 + 1
```

* Uvicorn worker class:

```text
worker_class = "uvicorn.workers.UvicornWorker"
```

* Long-running ML inference timeout.
* Graceful shutdown timeout.
* Keep-alive configuration.
* Application preloading to help reduce unnecessary memory duplication where supported.

The configured production server uses:

```text
gunicorn -c gunicorn_conf.py main:app
```

---

# Worker Calculation

The recommended worker formula used in this project is:

```text
2 × CPU Cores + 1
```

The Docker environment detected:

```text
8 CPU Cores
```

Therefore:

```text
2 × 8 + 1 = 17 Workers
```

The Gunicorn logs confirmed that multiple worker processes were successfully started.

---

# Why Multiple Workers?

A single-process server can become a bottleneck when many users send requests at the same time.

Gunicorn improves concurrency by creating multiple independent worker processes.

Benefits include:

* Handling multiple concurrent requests.
* Improved scalability.
* Better CPU utilization.
* Process isolation.
* Improved availability under concurrent traffic.
* Reduced blocking caused by a single application process.

Multiple processes are also useful in Python because the Global Interpreter Lock (GIL) limits parallel execution of Python bytecode inside a single process. A multi-process architecture allows work to be distributed across separate processes.

---

# Memory Optimization

Machine Learning applications can consume significant RAM because serialized model and pipeline files must be loaded into memory.

When multiple workers are created, loading a separate copy of the model inside every worker can increase total memory usage.

This project uses application preloading:

```python
preload_app = True
```

Preloading allows the application and ML resources to be loaded before worker processes are forked, which can help reduce unnecessary memory duplication through operating-system memory sharing mechanisms where supported.

Memory consumption was monitored during concurrent load testing using:

```bash
docker stats day36_container
```

During the 100-user Locust load test, the container remained within available memory limits.

Observed memory usage:

```text
781.9 MiB / 3.746 GiB
20.39% Memory Usage
```

This confirmed that the service remained stable during concurrent requests without exceeding the available container memory.

---

# Docker Configuration

The Dockerfile was updated to replace the single-process Uvicorn startup command.

Previous approach:

```text
uvicorn main:app
```

Production approach:

```text
gunicorn -c gunicorn_conf.py main:app
```

The Dockerfile includes the Gunicorn configuration file and all required application modules, ML models, pipelines, and supporting files.

The application is exposed on:

```text
Port 8000
```

---

# Project Structure

```text
Day 36/
│
├── main.py
├── router.py
├── schemas.py
├── preprocessing.py
├── drift_detector.py
├── retrain.py
│
├── gunicorn_conf.py
├── locustfile.py
│
├── Dockerfile
├── requirements.txt
│
├── model_v1.pkl
├── model_v2.pkl
├── pipeline.pkl
├── pipeline_v2.pkl
│
└── retail_sales_dataset.csv
```

---

# Requirements

The project uses the following main dependencies:

```text
fastapi
uvicorn
gunicorn
scikit-learn
joblib
numpy
pandas
pydantic
scipy
pytest
httpx
locust
```

Gunicorn is used as the production process manager, while Uvicorn workers serve the FastAPI ASGI application.

---

# Build the Docker Image

Build the Docker image using:

```bash
docker build -t prosensia-ml-service:v8 .
```

---

# Run the Container

Run the application using:

```bash
docker run -d --name day36_container -p 8000:8000 prosensia-ml-service:v8
```

Check the running container:

```bash
docker ps
```

---

# Verify Gunicorn Workers

Check Gunicorn startup logs:

```bash
docker logs day36_container
```

The logs confirmed:

```text
Starting gunicorn
Using worker: uvicorn.workers.UvicornWorker
Booting worker with pid
Application startup complete
```

The Docker environment detected 8 CPU cores, resulting in 17 Gunicorn worker processes using the configured worker formula.

Worker processes can also be verified using:

```bash
docker top day36_container
```

This confirmed the Gunicorn master process and multiple worker processes running inside the container.

---

# API Testing

## Health Check

Test the health endpoint:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

The application successfully returned a healthy status.

---

## Prediction Test

Test the prediction endpoint:

```powershell
$body = @{
    Age = 30
    Gender = "Male"
    Product_Category = "Electronics"
    Quantity = 2
    Price_per_Unit = 500
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

The API successfully processed the request and returned a prediction.

---

# Locust Concurrency Testing

Locust was used to test the FastAPI application under concurrent load.

Start Locust using:

```bash
locust -f locustfile.py
```

Then open:

```text
http://localhost:8089
```

Load test configuration:

```text
Concurrent Users: 100
Spawn Rate: 10 Users per Second
Target Host: http://localhost:8000
```

The test successfully generated concurrent requests to the `/predict` endpoint.

Observed results included:

```text
100 Concurrent Users
0% Failures
Approximately 124.5 Requests Per Second
6,000+ Requests Successfully Processed
```

The application remained available during the test, and the Gunicorn workers did not crash.

---

# Docker Memory Monitoring

While the Locust load test was running, container resource usage was monitored using:

```bash
docker stats day36_container
```

Observed results:

```text
CPU Usage: 8.01%
Memory Usage: 781.9 MiB / 3.746 GiB
Memory Percentage: 20.39%
PIDs: 119
```

The container remained stable and within available memory limits while handling concurrent requests.

---

# Graceful Shutdown

Graceful shutdown was verified using:

```bash
docker stop day36_container
```

The container successfully stopped with:

```text
Exited (0)
```

Gunicorn logs confirmed that workers received termination signals and completed the application shutdown process:

```text
Application shutdown complete
Finished server process
Worker was sent SIGTERM
Shutting down: Master
```

This verified that the Gunicorn master process and worker processes shut down cleanly.

---

# Key Technical Learnings

## Gunicorn Process Management

Gunicorn uses a master-worker architecture. The master process manages worker processes, while individual workers handle incoming requests.

## Worker Count and CPU Cores

The worker count can be dynamically calculated using:

```text
2 × CPU Cores + 1
```

This provides a starting point for balancing concurrency and resource consumption. The actual number of workers should also consider available RAM and ML model size.

## Python GIL

The Python Global Interpreter Lock limits parallel execution of Python bytecode inside a single process. Multi-process deployments allow separate worker processes to execute independently and improve the ability to handle concurrent workloads.

## ML Model Memory Usage

Large ML models can consume significant memory. If every worker independently loads a complete model, memory usage can increase substantially.

Using application preloading before worker processes are forked can help reduce unnecessary duplication where copy-on-write memory sharing is supported.

## Concurrency Testing

Locust demonstrated that the multi-worker FastAPI application could handle 100 concurrent virtual users while maintaining:

* 0% request failures.
* Stable throughput.
* Approximately 124.5 RPS during the observed test.
* Stable worker processes.
* RAM usage within available container limits.

---

# Deployment Evidence

The following screenshots were captured during testing:

```text
day36_locust_100_users_success.png
day36_docker_stats_load_test.png
day36_multiple_gunicorn_workers.png
day36_graceful_shutdown.png
day36_graceful_shutdown_logs.png
```

These screenshots demonstrate:

* Successful concurrent Locust traffic.
* 100 concurrent users.
* Stable application performance.
* 0% failures.
* Multiple Gunicorn workers.
* RAM monitoring during load testing.
* Successful graceful container shutdown.

---

# Conclusion

This project successfully upgraded the existing FastAPI Machine Learning microservice from a single-process Uvicorn deployment to a production-oriented Multi-Worker Gunicorn architecture.

Gunicorn was configured with Uvicorn workers and dynamic worker allocation based on available CPU cores. The application successfully started with multiple worker processes and handled concurrent traffic during Locust load testing.

The service was tested with 100 concurrent virtual users and maintained 0% request failures with stable throughput. Docker resource monitoring confirmed that RAM consumption remained within the available memory limits during the load test.

The deployment also successfully demonstrated graceful shutdown using `docker stop`, with all worker processes receiving termination signals and the Gunicorn master shutting down cleanly.

This implementation demonstrates scalable FastAPI model serving, multi-process concurrency, ML deployment memory awareness, load testing, and production-oriented container deployment.
