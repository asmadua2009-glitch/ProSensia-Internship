FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY router.py .
COPY schemas.py .
COPY preprocessing.py .
COPY drift_detector.py .
COPY retrain.py .

COPY pipeline.pkl .
COPY pipeline_v2.pkl .

COPY model_v1.pkl .
COPY model_v2.pkl .

COPY retail_sales_dataset.csv .

RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]