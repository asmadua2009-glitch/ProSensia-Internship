# Baseline Machine Learning Model using Logistic Regression

## Project Objective
The objective of this project is to build a baseline supervised Machine Learning classification model using Logistic Regression. The model predicts whether an order is delivered or not using the cleaned and one-hot encoded e-commerce dataset.

## Dataset
The project uses the **cleaned_global_ecommerce_sales.csv** dataset.

## Target Variable
The target variable is **Target**.

- 1 = Delivered
- 0 = Not Delivered(Returned, Processing, or Cancelled)

## Features (X) and Target (y)

- **X (Features):** All independent input variables used for prediction.
- **y (Target):** The dependent variable (Target) that the model predicts.

## Train-Test Split

The dataset was divided into:

- 80% Training Data
- 20% Testing Data

The training data was used to train the model, while the testing data was used to evaluate its performance on unseen data.

## Logistic Regression

Logistic Regression is a supervised Machine Learning classification algorithm used to predict binary outcomes.

## Model Accuracy 

Accuracy:

(1.0)

## Libraries Used

- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- jupyter

## How to Run

1. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
2. Open `baseline_model.ipynb`.
3. Run all cells from top to bottom.
4. View the model accuracy.