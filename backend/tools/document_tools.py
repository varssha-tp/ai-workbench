import fitz

from backend.services.file_service import file_store

MAX_CHARS = 20_000


def extract_text(file_id: str) -> str:
    meta = file_store.get(file_id)
    if meta is None:
        raise ValueError(f"Unknown file_id: {file_id}")
    if meta.file_type != "pdf":
        raise ValueError(f"'{meta.filename}' is not a PDF.")

    path = file_store.get_path(file_id)
    try:
        with fitz.open(path) as doc:
            text = "\n".join(page.get_text() for page in doc)
    except Exception as e:
        raise ValueError(
            f"Could not read '{meta.filename}' as a PDF — it may be corrupted or empty."
        ) from e

    return text[:MAX_CHARS]
