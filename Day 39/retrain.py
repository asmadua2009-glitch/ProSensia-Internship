import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from preprocessing import create_preprocessing_pipeline

DATASET_PATH = os.getenv(
    "DATASET_PATH",
    "retail_sales_dataset.csv",
)

MODEL_PATH = "model_v2.pkl"
PIPELINE_PATH = "pipeline_v2.pkl"


def load_fresh_data() -> pd.DataFrame:
    """Load fresh data for challenger model retraining."""

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    return pd.read_csv(DATASET_PATH)


def create_target(data: pd.DataFrame) -> pd.DataFrame:
    """Create the High_Value target column."""

    data = data.copy()

    if "Total Amount" not in data.columns:
        raise ValueError("Total Amount column is required for retraining.")

    median_value = data["Total Amount"].median()

    data["High_Value"] = (data["Total Amount"] > median_value).astype(int)

    return data


def train_model() -> dict:
    """Train, evaluate, and save the challenger model."""

    data = load_fresh_data()
    data = create_target(data)

    feature_columns = [
        "Age",
        "Quantity",
        "Price per Unit",
        "Gender",
        "Product Category",
    ]

    target_column = "High_Value"

    missing_columns = [
        column
        for column in feature_columns + [target_column]
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    x = data[feature_columns]
    y = data[target_column]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = create_preprocessing_pipeline()

    x_train_processed = pipeline.fit_transform(x_train)
    x_test_processed = pipeline.transform(x_test)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )

    model.fit(
        x_train_processed,
        y_train,
    )

    predictions = model.predict(x_test_processed)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    f1 = f1_score(
        y_test,
        predictions,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    joblib.dump(
        pipeline,
        PIPELINE_PATH,
    )

    return {
        "model_path": MODEL_PATH,
        "pipeline_path": PIPELINE_PATH,
        "accuracy": float(round(accuracy, 6)),
        "f1_score": float(round(f1, 6)),
    }


if __name__ == "__main__":
    result = train_model()

    print("Challenger model retraining completed successfully.")
    print(f"Model saved: {result['model_path']}")
    print(f"Pipeline saved: {result['pipeline_path']}")
    print(f"Accuracy: {result['accuracy']}")
    print(f"F1 Score: {result['f1_score']}")
