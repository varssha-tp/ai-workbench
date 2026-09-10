from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_upload_classifies_supported_types():
    response = client.post(
        "/upload",
        files=[
            ("files", ("sales.csv", b"product,jan,feb\nWidget,100,80\n", "text/csv")),
            ("files", ("report.pdf", b"%PDF-1.4 fake content", "application/pdf")),
            (
                "files",
                (
                    "January.xlsx",
                    b"fake xlsx bytes",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
            ),
        ],
    )
    assert response.status_code == 200

    body = response.json()
    types_by_name = {f["filename"]: f["file_type"] for f in body}
    assert types_by_name["sales.csv"] == "csv"
    assert types_by_name["report.pdf"] == "pdf"
    assert types_by_name["January.xlsx"] == "excel"

    listed = client.get("/files").json()
    listed_names = {f["filename"] for f in listed}
    assert {"sales.csv", "report.pdf", "January.xlsx"} <= listed_names


def test_upload_rejects_unsupported_extension():
    response = client.post(
        "/upload",
        files=[("files", ("notes.docx", b"whatever", "application/msword"))],
    )
    assert response.status_code == 400
