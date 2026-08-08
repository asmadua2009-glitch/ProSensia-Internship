# High Value Transaction AI Microservice
## Project Overview
This project is a production-ready AI Microservice built using FastAPI and a trained Random Forest Machine Learning model.
The microservice predicts whether a retail transaction is a High Value Transaction or Not High Value Transaction based on customer and transaction information.
## Machine Learning Model
The model was trained using the retail sales dataset.
### Input Features
* Age
* Gender
* Product Category
* Quantity
* Price per Unit
### Target
* `1` = High Value Transaction
* `0` = Not High Value Transaction
The trained model is serialized using Joblib and saved as `high_value_transaction_model.pkl`.
## Project Structure
```text
Day 20/
├── main.py
├── train_model.py
├── high_value_transaction_model.pkl
├── retail_sales_dataset.csv
├── requirements.txt
└── README.md
```
## Technologies Used
* Python
* FastAPI
* Pydantic
* Uvicorn
* Pandas
* Scikit-learn
* Joblib
* Random Forest Classifier
## Installation
```bash
pip install -r requirements.txt
```
## Run the API
```bash
uvicorn main:app --reload
```
The API will be available at:

```text
http://127.0.0.1:8000
```
## API Documentation
Interactive Swagger UI:
```text
http://127.0.0.1:8000/docs
```
## API Endpoints

### GET /

Returns a message confirming that the microservice is running.

### GET /health

Checks the health status of the microservice.

### POST /predict

Predicts whether a transaction is a High Value Transaction.

Example request:

```json
{
  "Age": 30,
  "Gender": "Male",
  "Product_Category": "Beauty",
  "Quantity": 2,
  "Price_per_Unit": 100
}
```

Example response:

```json
{
  "prediction": 0,
  "result": "Not High Value Transaction"
}
```
## Input Validation
Pydantic validation is used to validate incoming requests.

| Field            | Allowed Values                  |
| ---------------- | ------------------------------- |
| Age              | 18–64                           |
| Gender           | Male / Female                   |
| Product Category | Beauty / Clothing / Electronics |
| Quantity         | 1–4                             |
| Price per Unit   | 25–500                          |

Invalid data types or missing required fields return `422 Unprocessable Content`.
## Out-of-Distribution Guardrails
Custom OOD validation prevents unsupported categorical values from reaching the Machine Learning model.
Invalid Gender and Product Category values return `400 Bad Request`.
## Error Handling
The API safely handles:
* Invalid data types
* Missing required fields
* Malformed JSON
* Values outside allowed ranges
* Unsupported categorical values
The API returns appropriate validation errors instead of crashing.
## Model Training
The model can be retrained by running:

```bash
python train_model.py
```
The trained model is saved as:
```text
high_value_transaction_model.pkl
```
## Testing
The API was tested using Swagger UI.
* Valid prediction request → `200`
* Incorrect data type → `422`
* Missing required field → `422`
* Malformed JSON → `422`
* Age outside allowed range → `422`
* Invalid Gender → `400`
* Invalid Product Category → `400`
## Conclusion
This project demonstrates a complete AI Microservice architecture using FastAPI, Pydantic validation, Machine Learning model serialization, OOD guardrails, error handling, and Swagger API documentation.
