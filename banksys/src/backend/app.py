"""FastAPI backend application."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.config import settings
from src.core.models import DataLoader, DataSummary


class HealthResponse(BaseModel):
    status: str
    version: str
    app_name: str


class FilterParams(BaseModel):
    dataset: str = "train"
    job: str | None = None
    marital: str | None = None
    education: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    subscribe: str | None = None


data_loader: DataLoader | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global data_loader
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_loader = DataLoader(data_dir=data_dir)
    yield
    data_loader = None


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="银行营销数据展示系统 API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        app_name=settings.app_name,
    )


@app.get("/api/summary", response_model=DataSummary)
async def get_summary() -> DataSummary:
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")
    return data_loader.get_summary()


@app.get("/api/data")
async def get_data(
    dataset: str = Query(default="train", description="Dataset to load: train or test"),
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")

    df = data_loader.train_df if dataset == "train" else data_loader.test_df
    total = len(df)
    df_slice = df.iloc[offset : offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": df_slice.to_dict(orient="records"),
    }


@app.get("/api/data/filtered")
async def get_filtered_data(
    dataset: str = Query(default="train"),
    job: str | None = Query(default=None),
    marital: str | None = Query(default=None),
    education: str | None = Query(default=None),
    min_age: int | None = Query(default=None, ge=0),
    max_age: int | None = Query(default=None, ge=0),
    subscribe: str | None = Query(default=None),
) -> dict[str, Any]:
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")

    df = data_loader.get_filtered_data(
        dataset=dataset,
        job=job,
        marital=marital,
        education=education,
        min_age=min_age,
        max_age=max_age,
        subscribe=subscribe,
    )

    return {
        "total": len(df),
        "data": df.to_dict(orient="records"),
    }


class UniqueValuesResponse(BaseModel):
    column: str
    values: list[str]


@app.get("/api/columns/{column}/unique", response_model=UniqueValuesResponse)
async def get_unique_values(column: str) -> UniqueValuesResponse:
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")

    try:
        values = data_loader.get_unique_values(column)
        return UniqueValuesResponse(column=column, values=values)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Column '{column}' not found")


@app.get("/api/aggregated")
async def get_aggregated_data(
    group_by: str = Query(default="job"),
    metric: str = Query(default="count"),
    dataset: str = Query(default="train"),
) -> dict[str, Any]:
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")

    try:
        result = data_loader.get_aggregated_data(
            group_by=group_by,
            metric=metric,
            dataset=dataset,
        )
        return {
            "group_by": group_by,
            "metric": metric,
            "dataset": dataset,
            "data": result,
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Column not found: {e}")


def run_server():
    import uvicorn

    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run(app, host=settings.host, port=port)


if __name__ == "__main__":
    run_server()
