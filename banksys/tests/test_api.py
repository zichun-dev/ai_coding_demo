from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.backend.app import app
from src.core.models import DataLoader

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def client():
    import src.backend.app as app_module

    app_module.data_loader = DataLoader(data_dir=DATA_DIR)

    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    def test_health_check(self, client: TestClient):
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["app_name"] == "backsys"


class TestSummaryEndpoint:
    def test_get_summary(self, client: TestClient):
        response = client.get("/api/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 30000
        assert data["train_records"] == 22500
        assert data["test_records"] == 7500
        assert "age" in data["numeric_columns"]
        assert "job" in data["categorical_columns"]


class TestDataEndpoint:
    def test_get_data_default(self, client: TestClient):
        response = client.get("/api/data")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 22500
        assert data["limit"] == 100
        assert data["offset"] == 0
        assert len(data["data"]) == 100

    def test_get_data_with_pagination(self, client: TestClient):
        response = client.get("/api/data?limit=10&offset=5")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 22500
        assert data["limit"] == 10
        assert data["offset"] == 5
        assert len(data["data"]) == 10

    def test_get_test_data(self, client: TestClient):
        response = client.get("/api/data?dataset=test")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 7500
        assert len(data["data"]) == 100


class TestFilteredDataEndpoint:
    def test_filter_by_job(self, client: TestClient):
        response = client.get("/api/data/filtered?job=admin.")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        for record in data["data"]:
            assert record["job"] == "admin."

    def test_filter_by_age_range(self, client: TestClient):
        response = client.get("/api/data/filtered?min_age=30&max_age=40")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        for record in data["data"]:
            assert 30 <= record["age"] <= 40

    def test_filter_by_marital(self, client: TestClient):
        response = client.get("/api/data/filtered?marital=single")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        for record in data["data"]:
            assert record["marital"] == "single"

    def test_filter_by_subscribe(self, client: TestClient):
        response = client.get("/api/data/filtered?subscribe=yes")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        for record in data["data"]:
            assert record["subscribe"] == "yes"

    def test_filter_no_results(self, client: TestClient):
        response = client.get("/api/data/filtered?job=nonexistent_job")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["data"]) == 0


class TestUniqueValuesEndpoint:
    def test_get_unique_jobs(self, client: TestClient):
        response = client.get("/api/columns/job/unique")

        assert response.status_code == 200
        data = response.json()
        assert data["column"] == "job"
        assert "admin." in data["values"]
        assert "technician" in data["values"]

    def test_get_unique_marital(self, client: TestClient):
        response = client.get("/api/columns/marital/unique")

        assert response.status_code == 200
        data = response.json()
        assert data["column"] == "marital"
        assert "single" in data["values"]
        assert "married" in data["values"]

    def test_column_not_found(self, client: TestClient):
        response = client.get("/api/columns/nonexistent/unique")

        assert response.status_code == 404


class TestAggregatedEndpoint:
    def test_aggregate_count(self, client: TestClient):
        response = client.get("/api/aggregated?group_by=job&metric=count")

        assert response.status_code == 200
        data = response.json()
        assert data["group_by"] == "job"
        assert data["metric"] == "count"
        assert "admin." in data["data"]
        assert data["data"]["admin."] > 0

    def test_aggregate_mean_age(self, client: TestClient):
        response = client.get("/api/aggregated?group_by=job&metric=mean_age")

        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "mean_age"
        assert "admin." in data["data"]
        assert data["data"]["admin."] > 0

    def test_aggregate_subscribe_rate(self, client: TestClient):
        response = client.get("/api/aggregated?group_by=job&metric=subscribe_rate")

        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "subscribe_rate"
        assert "admin." in data["data"]

    def test_aggregate_column_not_found(self, client: TestClient):
        response = client.get("/api/aggregated?group_by=nonexistent")

        assert response.status_code == 404
