from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel


class BankData(BaseModel):
    id: int
    age: int
    job: str
    marital: str
    education: str
    default: str
    housing: str
    loan: str
    contact: str
    month: str
    day_of_week: str
    duration: int
    campaign: int
    pdays: int
    previous: int
    poutcome: str
    emp_var_rate: float
    cons_price_index: float
    cons_conf_index: float
    lending_rate3m: float
    nr_employed: float
    subscribe: str | None = None


class DataSummary(BaseModel):
    total_records: int
    train_records: int
    test_records: int
    columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    subscribe_distribution: dict[str, int] | None = None
    job_distribution: dict[str, int]
    age_stats: dict[str, float]
    marital_distribution: dict[str, int]
    education_distribution: dict[str, int]


class DataLoader:
    def __init__(self, data_dir: Path | None = None):
        from src.core.config import settings

        self.data_dir = data_dir or settings.data_dir
        self._train_df: pd.DataFrame | None = None
        self._test_df: pd.DataFrame | None = None

    @property
    def train_df(self) -> pd.DataFrame:
        if self._train_df is None:
            self._train_df = self._load_csv("train.csv")
        return self._train_df

    @property
    def test_df(self) -> pd.DataFrame:
        if self._test_df is None:
            self._test_df = self._load_csv("test.csv")
        return self._test_df

    def _load_csv(self, filename: str) -> pd.DataFrame:
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        return pd.read_csv(file_path)

    def get_summary(self) -> DataSummary:
        train_df = self.train_df
        test_df = self.test_df

        numeric_cols = train_df.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
        if "id" in numeric_cols:
            numeric_cols.remove("id")

        categorical_cols = train_df.select_dtypes(include=["object"]).columns.tolist()

        subscribe_dist = None
        if "subscribe" in train_df.columns:
            subscribe_dist = train_df["subscribe"].value_counts().to_dict()

        job_dist = (
            train_df["job"].value_counts().to_dict()
            if "job" in train_df.columns
            else {}
        )
        marital_dist = (
            train_df["marital"].value_counts().to_dict()
            if "marital" in train_df.columns
            else {}
        )
        education_dist = (
            train_df["education"].value_counts().to_dict()
            if "education" in train_df.columns
            else {}
        )

        age_stats = {}
        if "age" in train_df.columns:
            age_stats = {
                "mean": float(train_df["age"].mean()),
                "min": float(train_df["age"].min()),
                "max": float(train_df["age"].max()),
                "std": float(train_df["age"].std()),
            }

        return DataSummary(
            total_records=len(train_df) + len(test_df),
            train_records=len(train_df),
            test_records=len(test_df),
            columns=train_df.columns.tolist(),
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
            subscribe_distribution=subscribe_dist,
            job_distribution=job_dist,
            age_stats=age_stats,
            marital_distribution=marital_dist,
            education_distribution=education_dist,
        )

    def get_filtered_data(
        self,
        dataset: str = "train",
        job: str | None = None,
        marital: str | None = None,
        education: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        subscribe: str | None = None,
    ) -> pd.DataFrame:
        df = self.train_df if dataset == "train" else self.test_df

        if job:
            df = df[df["job"] == job]
        if marital:
            df = df[df["marital"] == marital]
        if education:
            df = df[df["education"] == education]
        if min_age is not None:
            df = df[df["age"] >= min_age]
        if max_age is not None:
            df = df[df["age"] <= max_age]
        if subscribe and "subscribe" in df.columns:
            df = df[df["subscribe"] == subscribe]

        return df

    def get_unique_values(self, column: str) -> list[str]:
        train_values = set(self.train_df[column].unique().tolist())
        test_values = set(self.test_df[column].unique().tolist())
        return sorted(train_values | test_values)

    def get_aggregated_data(
        self,
        group_by: str,
        metric: str = "count",
        dataset: str = "train",
    ) -> dict[str, Any]:
        df = self.train_df if dataset == "train" else self.test_df

        if metric == "count":
            result = df.groupby(group_by).size().to_dict()
        elif metric == "mean_age":
            result = df.groupby(group_by)["age"].mean().to_dict()
        elif metric == "subscribe_rate":
            if "subscribe" in df.columns:
                result = (
                    df.groupby(group_by)["subscribe"]
                    .apply(lambda x: (x == "yes").sum() / len(x) * 100)
                    .to_dict()
                )
            else:
                result = {}
        else:
            result = df.groupby(group_by).size().to_dict()

        return {str(k): v for k, v in result.items()}


data_loader = DataLoader()
