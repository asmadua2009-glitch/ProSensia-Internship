import pandas as pd
from sklearn.model_selection import train_test_split

from preprocessing import (
    NUMERICAL_COLUMNS,
    CATEGORICAL_COLUMNS,
    create_preprocessing_pipeline,
    save_pipeline,
)


DATASET_PATH = "retail_sales_dataset.csv"


def main():
    """Fit preprocessing pipeline on training data and save it."""

    df = pd.read_csv(DATASET_PATH)

    feature_columns = NUMERICAL_COLUMNS + CATEGORICAL_COLUMNS

    X = df[feature_columns]
    y = df["Total Amount"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline = create_preprocessing_pipeline()

    # IMPORTANT: fit ONLY on X_train
    pipeline.fit(X_train)

    save_pipeline(pipeline, "pipeline.pkl")

    print("Pipeline fitted successfully on X_train.")
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print("pipeline.pkl created successfully.")


if __name__ == "__main__":
    main()