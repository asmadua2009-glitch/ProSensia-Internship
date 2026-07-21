# Day 12 PyTorch DataLoader & Adam Optimizer
## Project Objective
This project upgrades the Day 11 Deep Learning baseline model using PyTorch DataLoader, TensorDataset, and Adam Optimizer. The model is trained using mini-batches, validated after every epoch, and evaluated by comparing training and validation loss.
## Tasks Completed
- Loaded Day 11 feature and target tensors
- Created TensorDataset
- Split dataset into Training and Validation sets
- Created DataLoader with batch_size = 64
- Used shuffle=True for training
- Initialized MLP model
- Used Adam Optimizer (learning rate = 0.001)
- Used CrossEntropyLoss
- Implemented Mini-Batch Training
- Performed Validation using torch.no_grad()
- Trained model for 25 epochs
- Plotted Training and Validation Loss Curves
- Saved trained model
## Files Included
- deep_learning_baseline.ipynb
- cleaned_global_ecommerce_sales.csv
- mlp_model.pth
- README.md
- requirements.txt
## Conclusion
Using TensorDataset and DataLoader improved the training pipeline by processing data in mini-batches. The Adam optimizer provided stable convergence, while validation loss monitoring helped evaluate the model's performance during training.