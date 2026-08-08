import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
# Load dataset
df = pd.read_csv("retail_sales_dataset.csv")

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# Create target
# Transactions above or equal to the median Total Amount
# are considered high-value transactions.
threshold = df["Total Amount"].median()

df["High_Value"] = (df["Total Amount"] >= threshold).astype(int)

print("High-value threshold:", threshold)
print("\nTarget distribution:")
print(df["High_Value"].value_counts())


# Features and target
X = df[
    [
        "Age",
        "Gender",
        "Product Category",
        "Quantity",
        "Price per Unit"
    ]
]

y = df["High_Value"]


# Feature types
categorical_features = [
    "Gender",
    "Product Category"
]

numeric_features = [
    "Age",
    "Quantity",
    "Price per Unit"
]


# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# Complete ML pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# Train model
pipeline.fit(X_train, y_train)


# Evaluate
y_pred = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", round(accuracy, 4))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# Save trained model
joblib.dump(
    pipeline,
    "high_value_transaction_model.pkl"
)

print("\nModel saved successfully!")
print("File: high_value_transaction_model.pkl")