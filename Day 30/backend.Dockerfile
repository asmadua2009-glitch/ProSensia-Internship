FROM python:3.11-slim

WORKDIR /app

COPY backend_client.py .

RUN pip install --no-cache-dir requests==2.34.2

CMD ["python", "backend_client.py"]