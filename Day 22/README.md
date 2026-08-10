# Day 22 - Multi-Container FastAPI Application with Docker Compose
## Project Objective
The objective of Day 22 is to upgrade the existing Dockerized FastAPI application into a multi-container architecture using Docker Compose.
The application uses Docker Compose to manage multiple services, configure an isolated custom network, and use persistent volumes for model files and logs.
## Services
### FastAPI Service
The FastAPI service is the main application service.
It provides the following endpoints:
- `GET /`
- `GET /health`
- `POST /predict`
The `/predict` endpoint uses a Pydantic model to validate input and returns the machine learning prediction.
## Backend Service
Redis is used as the supporting backend service.
The backend runs in a separate container and is connected to the same custom Docker network as the FastAPI service.
## Docker Compose
Docker Compose is used to manage the multiple services required by the application.
The `docker-compose.yml` file includes:
- Multiple services
- FastAPI application
- Environment variables
- Service dependencies
- Custom bridge network
- Named volumes
- Port mappings
- Health checks
- CPU and memory resource limits
## Environment Variables
The FastAPI service uses the following environment variables:

```text
MODEL_PATH=/app/model/high_value_transaction_model.pkl
LOG_PATH=/app/logs/predictions.log
````

## Service Dependencies

The FastAPI service depends on the backend service.

```yaml
depends_on:
  backend:
    condition: service_healthy
```

## Custom Docker Network

A custom bridge network named `day22_network` is configured.

```yaml
networks:
  day22_network:
    driver: bridge
```

The services use this network for isolated communication instead of Docker's default bridge network.

## Volumes

Named volumes are used for persistent storage.

### Model Volume

```text
model_volume:/app/model:ro
```

The trained machine learning model is stored outside the container's writable layer.

### Logs Volume

```text
logs_volume:/app/logs
```

Prediction logs are stored persistently outside the container's writable layer.

### Backend Volume

```text
backend_data:/data
```

The backend service uses this volume for persistent data.

## Port Mapping

The FastAPI application uses port `8000`.

```yaml
ports:
  - "8000:8000"
```

The API is available at:

```text
http://localhost:8000
```

## Health Checks

The FastAPI service includes a health check for the `/health` endpoint.

The backend service also includes a health check.

## CPU and Memory Resource Limits

### FastAPI Service

```text
CPU: 0.50
Memory: 512 MB
```

### Backend Service

```text
CPU: 0.25
Memory: 256 MB
```

## Build and Run

Build the project:

```bash
docker compose build
```

Start the services:

```bash
docker compose up -d
```

Check the running containers:

```bash
docker compose ps
```

## Test the Application

Open:

```text
http://localhost:8000
```

Test the health endpoint:

```text
http://localhost:8000/health
```

Open the FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

Use:

```text
POST /predict
```

to test the prediction endpoint.

## Verify Prediction Logs

```bash
docker compose exec fastapi cat /app/logs/predictions.log
```

## Verify Docker Network

```bash
docker network ls
```

Inspect the custom network:

```bash
docker network inspect day22_network
```

## Verify Docker Volumes

```bash
docker volume ls
```

## Stop the Application

```bash
docker compose down
```

## Bind Mounts vs Named Volumes

A bind mount directly connects a specific location on the host machine to a location inside the container.

A named volume is managed by Docker and provides persistent storage independently of the container lifecycle.

## Benefits of Custom Docker Networks

Custom Docker networks provide isolated communication between application services and allow services to communicate through a dedicated network instead of Docker's default bridge network.

## Benefits of Multi-Container Applications

Multi-container applications provide:

* Service isolation
* Easier maintenance
* Independent service management
* Better organization
* Easier scaling
* Clear communication between services
* Persistent storage management

## Conclusion

Day 22 upgrades the existing Dockerized FastAPI application into a multi-container architecture using Docker Compose with custom networking, persistent volumes, service dependencies, health checks, and CPU and memory resource limits.
## AUTHOR:
ASMA DUA
