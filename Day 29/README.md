# Day 29 Locust Load Testing & FastAPI Performance Evaluation

## Objective

Evaluate the FastAPI Machine Learning microservice under concurrent load using Locust, measure API performance, analyze latency, and identify potential inference bottlenecks.

## Technology Stack

- FastAPI
- Python 3.11
- Docker
- Locust 2.46.3
- Pydantic
- Scikit-learn
- Pandas
- NumPy
- Joblib

## Load Testing

Locust was used to simulate concurrent users sending POST requests to:

```text
/predict
````

### Test Configuration

* Concurrent Users: **50**
* Request Type: **POST**
* Endpoint: **/predict**
* Ramp-up: **1 user/second**
* Wait Time: **1–3 seconds**

### Request Payload

```json
{
    "Age": 25,
    "Gender": "Female",
    "Product_Category": "Electronics",
    "Quantity": 2,
    "Price_per_Unit": 100.0
}
```

## Performance Results

| Metric                |     Result |
| --------------------- | ---------: |
| Total Requests        |      1,916 |
| Failed Requests       |          0 |
| Failure Rate          |         0% |
| Requests/Second       |       10.5 |
| Average Response Time | 1550.64 ms |
| Median Response Time  |    1500 ms |
| 95th Percentile       |    2800 ms |
| 99th Percentile       |    3100 ms |
| Minimum Response Time |      26 ms |
| Maximum Response Time |  13,727 ms |
| Average Response Size |   18 bytes |

## Performance Analysis

The API successfully handled **1,916 requests with 0% failures** under 50 concurrent users.

The average response time was **1550.64 ms**, while the 95th percentile was **2800 ms**. The maximum response time of **13,727 ms** indicates occasional latency spikes under high concurrency.

The results confirm that the API remained stable during the load test, while ML inference latency is the primary area for further optimization.

## Inference Optimization

The ML model is loaded once during application startup to avoid repeated model-loading overhead.

Asynchronous inference is used to prevent CPU-bound model prediction from blocking the main asynchronous event loop.

## Conclusion

The Day 29 load test successfully validated the stability and performance of the containerized FastAPI ML microservice.

**50 concurrent users → 1,916 requests → 0 failures → 10.5 RPS → 0% failure rate**
## AUTHOR
ASMA DUA
