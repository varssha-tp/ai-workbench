from typing import Literal

from backend.services.result_service import result_store


def _get_result(result_id: str):
    df = result_store.get(result_id)
    if df is None:
        raise ValueError(f"Unknown result_id: {result_id}")
    return df


def generate_chart(
    result_id: str,
    chart_type: Literal["bar", "line", "pie"],
    x_field: str,
    y_field: str,
    title: str,
) -> dict:
    df = _get_result(result_id)
    for field in (x_field, y_field):
        if field not in df.columns:
            raise ValueError(
                f"Column '{field}' not found. Available columns: {list(df.columns)}"
            )

    return {
        "result_id": result_id,
        "chart_type": chart_type,
        "x_field": x_field,
        "y_field": y_field,
        "title": title,
    }


def create_table(result_id: str, title: str = "") -> dict:
    df = _get_result(result_id)
    return {
        "result_id": result_id,
        "title": title,
        "columns": list(df.columns),
    }
