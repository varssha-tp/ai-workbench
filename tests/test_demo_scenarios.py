"""Proves the three flagship demo scenarios (README / devpost script) actually
work end-to-end against the real model, using the real example files under
examples/ — not synthetic inline data. If these fail, the demo video will fail.
"""

import os

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")


def _upload(path: str, content_type: str) -> str:
    filename = os.path.basename(path)
    with open(path, "rb") as f:
        response = client.post("/upload", files=[("files", (filename, f, content_type))])
    assert response.status_code == 200, response.text
    return response.json()[0]["file_id"]


def test_demo_1_understand_pdf_summary_and_findings():
    file_id = _upload(
        os.path.join(EXAMPLES_DIR, "reports", "annual_report.pdf"), "application/pdf"
    )

    response = client.post(
        "/execute",
        json={
            "goal": "Give me a summary of this report and identify the three most important findings.",
            "file_ids": [file_id],
        },
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["summary"]
    assert len(body["findings"]) >= 1

    combined_text = (body["summary"] + " ".join(body["findings"])).lower()
    assert "revenue" in combined_text or "12%" in combined_text


def test_demo_2_analyse_compare_two_months_finds_decline():
    xlsx_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    jan_id = _upload(os.path.join(EXAMPLES_DIR, "sales", "January.xlsx"), xlsx_type)
    feb_id = _upload(os.path.join(EXAMPLES_DIR, "sales", "February.xlsx"), xlsx_type)

    response = client.post(
        "/execute",
        json={
            "goal": (
                "Compare January.xlsx and February.xlsx on the 'sales' column, "
                "matched by 'product', and find which products had sales decline "
                "by more than 20%. Show the result as a table."
            ),
            "file_ids": [jan_id, feb_id],
        },
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["table"] is not None
    products = {row["product"] for row in body["table"]["rows"]}
    assert "Keyboard C" in products
    assert "Laptop A" not in products
    assert "Monitor B" not in products


def test_demo_3_visualise_monthly_sales_trend():
    csv_id = _upload(
        os.path.join(EXAMPLES_DIR, "datasets", "monthly_sales.csv"), "text/csv"
    )

    response = client.post(
        "/execute",
        json={
            "goal": "Show me the monthly sales trend as a chart.",
            "file_ids": [csv_id],
        },
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["chart"] is not None
    assert body["chart"]["chart_type"] in ("line", "bar")
    assert len(body["chart"]["rows"]) == 6
