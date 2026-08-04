# Day 13 – Neural Network Regularization with PyTorch

## Project Overview

This project extends the baseline Multi-Layer Perceptron (MLP) by implementing Neural Network Regularization techniques using **Batch Normalization** and **Dropout** in PyTorch.

The objective is to reduce overfitting, improve model generalization, and compare the performance of the baseline MLP with the Regularized MLP.
## Dataset
Global E-Commerce Sales Dataset
File:
- cleaned_global_ecommerce_sales.csv
## Technologies Used

- Python
- PyTorch
- Pandas
- NumPy
- Matplotlib
## Project Features

- Data preprocessing
- TensorDataset and DataLoader
- Baseline MLP Model
- Regularized MLP Model
- Batch Normalization
- Dropout (p = 0.3)
- Adam Optimizer
- Training and Validation Loops
- Model Comparison
- Training & Validation Loss Visualization
## Training Configuration

- Epochs: 30
- Batch Size: 64
- Optimizer: Adam
- Loss Function: CrossEntropyLoss
- Random Seed: 42
## Results

The Regularized MLP demonstrated improved generalization compared to the baseline model by reducing overfitting through Batch Normalization and Dropout.

The comparison plots show that the Regularized MLP achieves more stable validation performance than the baseline model.
## Repository Contents

- deep_learning_baseline.ipynb
- cleaned_global_ecommerce_sales.csv
- requirements.txt
- README.md
## Author
ASMA DUA
ProSensia AI/ML Internship – Day 13