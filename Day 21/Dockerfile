# ============================================================
# DOCKER ARCHITECTURE & SECURITY NOTES
# ============================================================
# Docker containers share the host operating system kernel,
# while Virtual Machines require a hypervisor and a separate
# guest operating system. This reduces virtualization overhead.
# Linux namespaces isolate process IDs (PID), networking (NET),
# and inter-process communication (IPC) between containers.
# Docker layer caching keeps unchanged dependency layers reusable,
# so modifying application code does not require reinstalling
# unchanged dependencies, reducing rebuild time.
# ============================================================
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --default-timeout=300 --retries=10 --no-cache-dir --prefix=/install -r requirements.txt
# Stage 2: Production image
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY main.py .
COPY high_value_transaction_model.pkl .
# Create a dedicated non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]