import pandas as pd
import numpy as np
df = pd.read_csv("Day 1/train.csv")
print(df.head())
print(df.isnull().sum())
df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])
Q1 = df["Age"].quantile(0.25)
Q3 = df["Age"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df = df[(df["Age"] >= lower) & (df["Age"] <= upper)]
df.to_csv("cleaned_train.csv", index=False)
df["Age"] = df["Age"].fillna(df["Age"].mean())
df["Cabin"] = df["Cabin"].fillna("Unknown")
print("\nMissing Values After Cleaning:\n")
print(df.isnull().sum())
# Detect and remove outliers from Age column using IQR

Q1 = df["Age"].quantile(0.25)
Q3 = df["Age"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df = df[(df["Age"] >= lower) & (df["Age"] <= upper)]

print("\nDataset Shape After Removing Outliers:")
print(df.shape)
# Save cleaned dataset
df.to_csv("cleaned_train.csv", index=False)

print("Cleaned dataset saved successfully!")