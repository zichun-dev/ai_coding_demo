from pathlib import Path

import pandas as pd
import pytest

from src.core.config import Settings
from src.core.models import BankData, DataLoader, DataSummary


class TestSettings:
    def test_default_settings(self):
        settings = Settings()
        assert settings.app_name == "backsys"
        assert settings.app_version == "0.1.0"
        assert settings.port == 6100
        assert settings.host == "0.0.0.0"

    def test_custom_settings(self):
        settings = Settings(app_name="custom", port=8000)
        assert settings.app_name == "custom"
        assert settings.port == 8000


class TestDataLoader:
    @pytest.fixture
    def sample_data_dir(self, tmp_path: Path):
        train_data = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "age": [30, 40, 50],
                "job": ["admin", "technician", "blue-collar"],
                "marital": ["single", "married", "divorced"],
                "education": ["university.degree", "high.school", "basic.9y"],
                "default": ["no", "no", "no"],
                "housing": ["yes", "no", "yes"],
                "loan": ["no", "yes", "no"],
                "contact": ["cellular", "telephone", "cellular"],
                "month": ["may", "jun", "jul"],
                "day_of_week": ["mon", "tue", "wed"],
                "duration": [100, 200, 300],
                "campaign": [1, 2, 3],
                "pdays": [999, 999, 999],
                "previous": [0, 1, 2],
                "poutcome": ["nonexistent", "failure", "success"],
                "emp_var_rate": [1.1, 1.2, 1.3],
                "cons_price_index": [93.0, 94.0, 95.0],
                "cons_conf_index": [-40.0, -35.0, -30.0],
                "lending_rate3m": [4.0, 4.5, 5.0],
                "nr_employed": [5000.0, 5100.0, 5200.0],
                "subscribe": ["no", "yes", "no"],
            }
        )

        test_data = pd.DataFrame(
            {
                "id": [101, 102],
                "age": [25, 35],
                "job": ["student", "admin"],
                "marital": ["single", "married"],
                "education": ["high.school", "university.degree"],
                "default": ["no", "no"],
                "housing": ["no", "yes"],
                "loan": ["no", "no"],
                "contact": ["cellular", "cellular"],
                "month": ["aug", "sep"],
                "day_of_week": ["thu", "fri"],
                "duration": [150, 250],
                "campaign": [1, 1],
                "pdays": [999, 999],
                "previous": [0, 0],
                "poutcome": ["nonexistent", "nonexistent"],
                "emp_var_rate": [1.4, 1.5],
                "cons_price_index": [96.0, 97.0],
                "cons_conf_index": [-25.0, -20.0],
                "lending_rate3m": [5.5, 6.0],
                "nr_employed": [5300.0, 5400.0],
            }
        )

        train_data.to_csv(tmp_path / "train.csv", index=False)
        test_data.to_csv(tmp_path / "test.csv", index=False)

        return tmp_path

    def test_load_train_data(self, sample_data_dir: Path):
        loader = DataLoader(data_dir=sample_data_dir)
        df = loader.train_df

        assert len(df) == 3
        assert "subscribe" in df.columns
        assert list(df["age"]) == [30, 40, 50]

    def test_load_test_data(self, sample_data_dir: Path):
        loader = DataLoader(data_dir=sample_data_dir)
        df = loader.test_df

        assert len(df) == 2
        assert "subscribe" not in df.columns

    def test_get_summary(self, sample_data_dir: Path):
        loader = DataLoader(data_dir=sample_data_dir)
        summary = loader.get_summary()

        assert isinstance(summary, DataSummary)
        assert summary.total_records == 5
        assert summary.train_records == 3
        assert summary.test_records == 2
        assert len(summary.columns) == 22
        assert "age" in summary.numeric_columns
        assert "job" in summary.categorical_columns

    def test_get_filtered_data(self, sample_data_dir: Path):
        loader = DataLoader(data_dir=sample_data_dir)

        filtered = loader.get_filtered_data(job="admin")
        assert len(filtered) == 1
        assert filtered.iloc[0]["job"] == "admin"

        filtered = loader.get_filtered_data(min_age=35)
        assert len(filtered) == 2

        filtered = loader.get_filtered_data(max_age=35)
        assert len(filtered) == 1

    def test_get_unique_values(self, sample_data_dir: Path):
        loader = DataLoader(data_dir=sample_data_dir)

        jobs = loader.get_unique_values("job")
        assert "admin" in jobs
        assert "technician" in jobs
        assert "student" in jobs

    def test_get_aggregated_data(self, sample_data_dir: Path):
        loader = DataLoader(data_dir=sample_data_dir)

        result = loader.get_aggregated_data(group_by="job", metric="count")
        assert result["admin"] == 1
        assert result["technician"] == 1

        result = loader.get_aggregated_data(group_by="job", metric="mean_age")
        assert "admin" in result

    def test_file_not_found(self, tmp_path: Path):
        loader = DataLoader(data_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            _ = loader.train_df


class TestBankData:
    def test_bank_data_model(self):
        data = BankData(
            id=1,
            age=30,
            job="admin",
            marital="single",
            education="university.degree",
            default="no",
            housing="yes",
            loan="no",
            contact="cellular",
            month="may",
            day_of_week="mon",
            duration=100,
            campaign=1,
            pdays=999,
            previous=0,
            poutcome="nonexistent",
            emp_var_rate=1.1,
            cons_price_index=93.0,
            cons_conf_index=-40.0,
            lending_rate3m=4.0,
            nr_employed=5000.0,
            subscribe="no",
        )

        assert data.id == 1
        assert data.age == 30
        assert data.job == "admin"
        assert data.subscribe == "no"

    def test_bank_data_without_subscribe(self):
        data = BankData(
            id=1,
            age=30,
            job="admin",
            marital="single",
            education="university.degree",
            default="no",
            housing="yes",
            loan="no",
            contact="cellular",
            month="may",
            day_of_week="mon",
            duration=100,
            campaign=1,
            pdays=999,
            previous=0,
            poutcome="nonexistent",
            emp_var_rate=1.1,
            cons_price_index=93.0,
            cons_conf_index=-40.0,
            lending_rate3m=4.0,
            nr_employed=5000.0,
        )

        assert data.subscribe is None
