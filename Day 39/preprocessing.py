import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERICAL_COLUMNS = [
    "Age",
    "Quantity",
    "Price per Unit",
]

CATEGORICAL_COLUMNS = [
    "Gender",
    "Product Category",
]


def create_preprocessing_pipeline():
    """Create the numerical and categorical preprocessing pipeline."""

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numerical", numerical_pipeline, NUMERICAL_COLUMNS),
            ("categorical", categorical_pipeline, CATEGORICAL_COLUMNS),
        ]
    )

    return preprocessor


def save_pipeline(pipeline, file_path="pipeline.pkl"):
    """Save the fitted preprocessing pipeline."""

    joblib.dump(pipeline, file_path)


def load_pipeline(file_path="pipeline.pkl"):
    """Load a serialized preprocessing pipeline."""

    return joblib.load(file_path)


def prepare_dataframe(data):
    """Convert raw input data into a Pandas DataFrame."""

    return pd.DataFrame([data])
