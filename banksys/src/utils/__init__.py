"""Utility functions for data processing."""

from pathlib import Path
from typing import Any

import pandas as pd


def ensure_path(path: str | Path) -> Path:
    return Path(path) if isinstance(path, str) else path


def format_number(value: float, decimal: int = 2) -> str:
    return f"{value:,.{decimal}f}"


def calculate_percentage(value: float, total: float) -> float:
    if total == 0:
        return 0.0
    return (value / total) * 100


def get_color_scale(values: list[float]) -> list[str]:
    if not values:
        return []

    min_val = min(values)
    max_val = max(values)

    if min_val == max_val:
        return ["#1f77b4"] * len(values)

    normalized = [(v - min_val) / (max_val - min_val) for v in values]

    colors = []
    for n in normalized:
        r = int(255 * (1 - n))
        g = int(255 * n)
        b = int(128)
        colors.append(f"rgb({r}, {g}, {b})")

    return colors


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator


def convert_df_to_dict(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df.to_dict(orient="records")


def get_column_type(df: pd.DataFrame, column: str) -> str:
    if column not in df.columns:
        return "unknown"

    dtype = str(df[column].dtype)
    if "int" in dtype or "float" in dtype:
        return "numeric"
    elif "object" in dtype or "category" in dtype:
        return "categorical"
    elif "datetime" in dtype:
        return "datetime"
    else:
        return "unknown"
