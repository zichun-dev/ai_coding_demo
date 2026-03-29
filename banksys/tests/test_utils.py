import pandas as pd

from src.utils import (
    calculate_percentage,
    convert_df_to_dict,
    ensure_path,
    format_number,
    get_color_scale,
    get_column_type,
    safe_divide,
)


class TestEnsurePath:
    def test_string_to_path(self):
        result = ensure_path("/some/path")
        from pathlib import Path

        assert isinstance(result, Path)
        assert result.as_posix() == "/some/path" or str(result) == "\\some\\path"

    def test_path_unchanged(self):
        from pathlib import Path

        path = Path("/some/path")
        result = ensure_path(path)
        assert result == path


class TestFormatNumber:
    def test_default_decimals(self):
        result = format_number(1234.5678)
        assert result == "1,234.57"

    def test_custom_decimals(self):
        result = format_number(1234.5678, decimal=4)
        assert result == "1,234.5678"

    def test_zero_decimals(self):
        result = format_number(1234.5678, decimal=0)
        assert result == "1,235"


class TestCalculatePercentage:
    def test_normal_calculation(self):
        result = calculate_percentage(25.0, 100.0)
        assert result == 25.0

    def test_zero_total(self):
        result = calculate_percentage(25.0, 0.0)
        assert result == 0.0

    def test_over_100_percent(self):
        result = calculate_percentage(150.0, 100.0)
        assert result == 150.0


class TestGetColorScale:
    def test_normal_values(self):
        values = [10, 20, 30, 40, 50]
        colors = get_color_scale(values)
        assert len(colors) == 5
        for color in colors:
            assert color.startswith("rgb(")

    def test_empty_values(self):
        colors = get_color_scale([])
        assert colors == []

    def test_single_value(self):
        colors = get_color_scale([42])
        assert len(colors) == 1

    def test_equal_values(self):
        colors = get_color_scale([10, 10, 10])
        assert len(colors) == 3


class TestSafeDivide:
    def test_normal_division(self):
        result = safe_divide(10.0, 2.0)
        assert result == 5.0

    def test_zero_denominator(self):
        result = safe_divide(10.0, 0.0)
        assert result == 0.0

    def test_custom_default(self):
        result = safe_divide(10.0, 0.0, default=-1.0)
        assert result == -1.0


class TestConvertDfToDict:
    def test_convert_dataframe(self):
        df = pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": ["x", "y", "z"],
            }
        )

        result = convert_df_to_dict(df)

        assert len(result) == 3
        assert result[0] == {"a": 1, "b": "x"}
        assert result[1] == {"a": 2, "b": "y"}
        assert result[2] == {"a": 3, "b": "z"}

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = convert_df_to_dict(df)
        assert result == []


class TestGetColumnType:
    def test_numeric_column(self):
        df = pd.DataFrame({"num": [1, 2, 3]})
        result = get_column_type(df, "num")
        assert result == "numeric"

    def test_categorical_column(self):
        df = pd.DataFrame({"cat": ["a", "b", "c"]})
        result = get_column_type(df, "cat")
        assert result == "categorical"

    def test_unknown_column(self):
        df = pd.DataFrame({"a": [1]})
        result = get_column_type(df, "nonexistent")
        assert result == "unknown"
