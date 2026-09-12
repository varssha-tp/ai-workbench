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


def test_execute_extracts_structured_data_from_pdf_into_a_real_table():
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Mentoring Session 1: 20-Jul-2026, duration 1 hour")
    page.insert_text((72, 100), "Mentoring Session 2: 27-Jul-2026, duration 1 hour")
    page.insert_text((72, 128), "Mentoring Session 3: 13-Aug-2026, duration 1 hour")
    pdf_bytes = doc.tobytes()
    doc.close()

    upload_response = client.post(
        "/upload",
        files=[("files", ("mentorship_form.pdf", pdf_bytes, "application/pdf"))],
    )
    file_id = upload_response.json()[0]["file_id"]

    response = client.post(
        "/execute",
        json={
            "goal": (
                "Extract each mentoring session from mentorship_form.pdf into a "
                "table with its date and duration."
            ),
            "file_ids": [file_id],
        },
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["table"] is not None
    assert len(body["table"]["rows"]) == 3
