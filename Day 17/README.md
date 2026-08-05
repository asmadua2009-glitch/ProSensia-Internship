# AI & ML Internship Day 17
## Project Title
Machine Learning Model Deployment with FastAPI & Pydantic
## Project Overview
This project demonstrates the deployment of a trained Machine Learning model using FastAPI. The API validates incoming JSON requests with Pydantic, converts the validated data into a Pandas DataFrame, performs real-time predictions using a serialized Random Forest model, and returns the prediction as a JSON response.
## Features
* FastAPI REST API
* Pydantic request validation
* Real-time Machine Learning inference
* Random Forest model deployment
* Automatic 422 validation for invalid input
* Swagger UI for API testing
* Clean JSON prediction response
## Project Structure

```text
Day 17/
│── main.py
│── production_rf_model.pkl
│── feature_names.txt
│── requirements.txt
│── README.md
 ``` 
 ## Technologies Used
 * Python
* FastAPI
* Pydantic
* Pandas
* Scikit-learn
* Joblib
* Uvicorn
## Installation
Clone the repository:
```bash
git clone <>
```Move into the project folder:
```bash
cd Day17
```
Install the required packages:
```bash
pip install -r requirements.txt
```
## Run the API
Start the FastAPI server:
```bash
uvicorn main:app --reload
```
## Swagger Documentation
Open your browser and visit:

```text
http://127.0.0.1:8000/docs
```
## Sample Request
```json
{
  "Year": 2024,
  "Month": 8,
  "Unit_Price": 1500
}
```
## Sample Response

```json
{
  "prediction": 1
}
```
## Why Pydantic?

Pydantic validates incoming request data before it reaches the Machine Learning model. It ensures the correct data types are provided and automatically returns a **422 Unprocessable Entity** error if invalid input is submitted.
## Garbage In, Garbage Out (GIGO)

Machine Learning models are only as good as the data they receive. Incorrect, missing, or invalid input can lead to unreliable predictions. Pydantic helps prevent this by validating requests before inference, improving the reliability and stability of the API.
## Author

**ASMA DUA**
AI & ML Internship – ProSensia
