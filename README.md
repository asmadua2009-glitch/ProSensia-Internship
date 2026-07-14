# Day 7 – Random Forest Classifier
## Project Overview
This project focuses on building a Random Forest Classifier using Scikit-learn and comparing its performance with the previously developed Logistic Regression baseline model. The model was evaluated using multiple classification metrics to better understand its prediction performance.
## Dataset
Dataset Used: cleaned_global_ecommerce_sales.csv
The dataset contains e-commerce order information including customer details, product details, shipping information, payment methods, and order status. The target variable was created from the Order_Status column.
## Technologies Used
- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Joblib
- Jupyter Notebook
## Steps Performed
1. Loaded the cleaned dataset.
2. Created the target variable.
3. Selected features and target.
4. Applied One-Hot Encoding to categorical columns.
5. Split the data into training and testing sets.
6. Built a Random Forest Classifier with:
   - n_estimators = 100
   - random_state = 42
7. Trained the model using the training dataset.
8. Generated predictions on the testing dataset.
9. Evaluated the model using:
   - Accuracy 1.0
   - Precision 1.0 
   - Recall    1.0
   - F1-Score   1.0
   - Classification Report
   - Confusion Matrix
10. Compared the Random Forest model with the Logistic Regression baseline model.
11. Saved the trained model using Joblib (.pkl).

## Results
The Random Forest Classifier successfully classified the test data and was evaluated using Accuracy, Precision, Recall, F1-Score, Classification Report, and Confusion Matrix. The model demonstrated strong classification performance and provided a reliable comparison with the baseline Logistic Regression model.
## Files Included

- random_forest_model.ipynb
- random_forest_model.pkl
- requirements.txt
- README.md
## How to Run

1. Clone or download the repository.
2. Install the required libraries:
pip install -r requirements.txt
3. Open the Jupyter Notebook:
random_forest_model.ipynb
4. Run all cells from top to bottom.

5. The notebook will:
   - Train the Random Forest model
   - Generate predictions
   - Display the Confusion Matrix
   - Print the Classification Report
   - Show Accuracy, Precision, Recall, and F1-Score
   - Save the trained model as `random_forest_model.pkl`
## Author
Asma Dua
AI/ML Internship ProSensia