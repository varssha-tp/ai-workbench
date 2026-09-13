import asyncio
import io

import pandas as pd
from fastapi.testclient import TestClient

from backend.agent.executor import run_plan
from backend.main import app
from backend.models import TaskPlan, ToolCall
from backend.services.file_service import file_store

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


def test_execute_summary_covers_substantive_content_not_just_metadata():
    """A document with several distinct reflective/opinion sections should get a
    summary and findings about that content, not just names/dates/labels that
    happen to be easy to extract. Reproduces a real bug: the original prompt +
    a 3000-char truncation cap produced a summary that was basically just the
    participant's name/school/company, with findings barely touching the
    document's actual substance."""
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Student Name: Jordan Lee, Admission No.: 2401234A")
    page.insert_text((72, 100), "Mentor: Sam Ong, Company: ExampleCo Pte Ltd")
    page.insert_textbox(
        fitz.Rect(72, 130, 525, 220),
        "Career journey: The sessions helped me think more seriously about my "
        "plans after graduation. I realized I should start building my "
        "knowledge and experience early so I have a stronger foundation.",
        fontsize=10,
    )
    page.insert_textbox(
        fitz.Rect(72, 230, 525, 320),
        "Industry insight: The AI industry is changing quickly and Singapore "
        "faces growing competition from other countries. Companies are also "
        "reconsidering whether to insource or outsource certain capabilities.",
        fontsize=10,
    )
    page.insert_textbox(
        fitz.Rect(72, 330, 525, 420),
        "Personal development: I learnt the importance of planning ahead, "
        "using my strengths to compensate for weaknesses, and staying open "
        "to opportunities even if my interests change over time.",
        fontsize=10,
    )
    pdf_bytes = doc.tobytes()
    doc.close()

    upload_response = client.post(
        "/upload", files=[("files", ("reflection_form.pdf", pdf_bytes, "application/pdf"))]
    )
    file_id = upload_response.json()[0]["file_id"]

    response = client.post(
        "/execute",
        json={
            "goal": "Summarise this and give me the important points.",
            "file_ids": [file_id],
        },
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert len(body["findings"]) >= 3

    combined = (body["summary"] + " ".join(body["findings"])).lower()
    # The summary/findings must engage with at least two of the three
    # substantive themes, not just restate the name/company header.
    themes_present = sum(
        theme in combined
        for theme in ("industry", "compet", "plan", "foundation", "strength", "opportunit")
    )
    assert themes_present >= 2, f"summary/findings too shallow: {combined}"


def test_run_plan_surfaces_uncalled_result_as_table_fallback():
    """A plan that computes something but never calls create_table/generate_chart
    should still show the result — the LLM doesn't reliably remember that extra
    step (verified empirically), so the executor covers it."""
    df = pd.DataFrame({"product": ["A", "B"], "sales": [100, 200]})
    meta = file_store.save("sales.csv", df.to_csv(index=False).encode())

    plan = TaskPlan(
        goal="Just calculate something, don't explicitly ask for a table",
        calls=[
            ToolCall(
                step="Sum sales",
                tool="analyse_dataset",
                args={"file_id": meta.file_id, "operation": "sum", "value_column": "sales"},
            )
        ],
    )

    result = asyncio.run(run_plan(plan))
    assert result.table is not None
    assert result.table.rows[0]["sales"] == 300
