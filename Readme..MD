# Day 9 - SMOTE, Random Forest & Feature Importance
## Project Objective
The objective of this project was to handle class imbalance using SMOTE (Synthetic Minority Over-sampling Technique), retrain the Random Forest model on the balanced training data, evaluate model performance using the F1-score, and analyze Feature Importance to improve model interpretability.
## Dataset
Dataset: Global E-commerce Sales Dataset
Target Variable:
- Target (Binary Classification)
## Tasks Performed

- Analyzed class distribution using `value_counts()`
- Split the dataset into training and testing sets
- Applied SMOTE only on the training data
- Retrained the Random Forest Classifier
- Evaluated the model using the F1-score
- Extracted feature importance using `feature_importances_`
- Created a Top 10 Feature Importance horizontal bar chart
- Compared model performance before and after applying SMOTE
- Saved the final production model
## Results
### F1 Score Comparison

| Model | F1 Score |
|--------|----------|
| Before SMOTE | 0.7686 |
| After SMOTE | 0.7576 |
## Feature Importance
The Feature Importance analysis showed that Shipping Cost, Unit Price, Profit Margin, Revenue, and Profit were among the most influential features affecting the model's predictions.
## Business Interpretation
The Feature Importance chart helps identify which business factors have the greatest impact on predicting the target variable. Understanding these important features enables businesses to make better decisions, improve operational strategies, and increase confidence in machine learning predictions.
## Conclusion
SMOTE successfully balanced the training dataset by generating synthetic samples for the minority class. Although the F1-score slightly decreased after applying SMOTE, the model became more balanced and interpretable. This demonstrates that oversampling techniques should always be evaluated using performance metrics instead of assuming automatic improvement.
## Files Included

- random_forest_model.ipynb
- production_rf_model.pkl
- README..md
- requirement.txt