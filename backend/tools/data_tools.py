from typing import Literal

import pandas as pd

from backend.services.file_service import file_store
from backend.services.result_service import result_store
from backend.tools._common import to_records

PREVIEW_ROWS = 5

AnalyseOperation = Literal["average", "sum_by_group", "top_n", "filter_threshold"]
Comparison = Literal["greater_than", "less_than"]


def _load_dataframe(file_id: str) -> pd.DataFrame:
    meta = file_store.get(file_id)
    if meta is None:
        raise ValueError(f"Unknown file_id: {file_id}")

    path = file_store.get_path(file_id)
    try:
        if meta.file_type == "csv":
            return pd.read_csv(path)
        if meta.file_type == "excel":
            return pd.read_excel(path)
    except Exception as e:
        raise ValueError(
            f"Could not read '{meta.filename}' as a {meta.file_type} file — "
            "it may be corrupted or empty."
        ) from e

    raise ValueError(
        f"'{meta.filename}' is a {meta.file_type} file, not a dataset. "
        "Use extract_text for documents."
    )


def _require_column(df: pd.DataFrame, column: str) -> None:
    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found. Available columns: {list(df.columns)}"
        )


def _require_numeric(value, name: str) -> None:
    if value is not None and not isinstance(value, (int, float)):
        raise ValueError(f"'{name}' must be a number, got: {value!r}")


def analyse_dataset(
    file_id: str,
    operation: AnalyseOperation,
    value_column: str,
    group_by_column: str | None = None,
    top_n: int | None = None,
    threshold: float | None = None,
    comparison: Comparison = "greater_than",
) -> dict:
    df = _load_dataframe(file_id)
    _require_column(df, value_column)
    _require_numeric(top_n, "top_n")
    _require_numeric(threshold, "threshold")

    if operation == "average":
        result_df = pd.DataFrame([{value_column: df[value_column].mean()}])
    elif operation == "sum_by_group":
        if not group_by_column:
            raise ValueError("sum_by_group requires group_by_column")
        _require_column(df, group_by_column)
        result_df = df.groupby(group_by_column, as_index=False)[value_column].sum()
    elif operation == "top_n":
        if not top_n:
            raise ValueError("top_n requires top_n")
        result_df = df.nlargest(top_n, value_column)
    elif operation == "filter_threshold":
        if threshold is None:
            raise ValueError("filter_threshold requires threshold")
        if comparison == "greater_than":
            result_df = df[df[value_column] > threshold]
        else:
            result_df = df[df[value_column] < threshold]
    else:
        raise ValueError(f"Unknown operation: {operation}")

    result_id = result_store.save(result_df)
    return {
        "result_id": result_id,
        "row_count": len(result_df),
        "preview": to_records(result_df.head(PREVIEW_ROWS)),
    }


def compare_datasets(
    file_id_a: str,
    file_id_b: str,
    key_column: str,
    value_column: str,
    threshold_pct: float | None = None,
) -> dict:
    df_a = _load_dataframe(file_id_a)
    df_b = _load_dataframe(file_id_b)
    _require_column(df_a, key_column)
    _require_column(df_a, value_column)
    _require_column(df_b, key_column)
    _require_column(df_b, value_column)
    _require_numeric(threshold_pct, "threshold_pct")

    merged = df_a[[key_column, value_column]].merge(
        df_b[[key_column, value_column]],
        on=key_column,
        suffixes=("_before", "_after"),
    )
    merged["pct_change"] = (
        (merged[f"{value_column}_after"] - merged[f"{value_column}_before"])
        / merged[f"{value_column}_before"]
        * 100
    )

    if threshold_pct is not None:
        merged = merged[merged["pct_change"].abs() >= threshold_pct]
    merged = merged.sort_values("pct_change")

    result_id = result_store.save(merged)
    return {
        "result_id": result_id,
        "row_count": len(merged),
        "preview": to_records(merged.head(PREVIEW_ROWS)),
    }
