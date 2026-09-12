import io

import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _upload_xlsx(filename, df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    response = client.post(
        "/upload",
        files=[
            (
                "files",
                (
                    filename,
                    buf.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
            )
        ],
    )
    return response.json()[0]["file_id"]


def test_execute_finds_product_with_large_decline():
    jan = pd.DataFrame(
        {
            "product": ["Laptop A", "Monitor B", "Keyboard C", "Mouse D"],
            "sales": [1000, 500, 500, 300],
        }
    )
    feb = pd.DataFrame(
        {
            "product": ["Laptop A", "Monitor B", "Keyboard C", "Mouse D"],
            "sales": [960, 460, 340, 282],
        }
    )
    file_id_jan = _upload_xlsx("January.xlsx", jan)
    file_id_feb = _upload_xlsx("February.xlsx", feb)

    response = client.post(
        "/execute",
        json={
            "goal": (
                "Compare January.xlsx and February.xlsx on the 'sales' column, "
                "matched by 'product', and find products whose sales dropped by "
                "more than 20%. Show the result as a table."
            ),
            "file_ids": [file_id_jan, file_id_feb],
        },
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["summary"]
    assert body["findings"]

    assert body["table"] is not None
    table_products = {row["product"] for row in body["table"]["rows"]}
    assert "Keyboard C" in table_products
    assert "Laptop A" not in table_products


def test_execute_corrupt_file_returns_clean_400_not_500():
    upload_response = client.post(
        "/upload",
        files=[
            (
                "files",
                (
                    "sales.xlsx",
                    b"this is not a real excel file, just garbage bytes",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
            )
        ],
    )
    file_id = upload_response.json()[0]["file_id"]

    response = client.post(
        "/execute",
        json={
            "goal": "Calculate the average of the 'sales' column in sales.xlsx",
            "file_ids": [file_id],
        },
    )
    assert response.status_code == 400, response.text
    assert "sales.xlsx" in response.json()["detail"]
