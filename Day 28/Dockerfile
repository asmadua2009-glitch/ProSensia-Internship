FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY feature_names.txt .
COPY high_value_transaction_model.pkl .
COPY retail_sales_dataset.csv .

# Create directory for application logs
RUN mkdir -p /app/logs

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]