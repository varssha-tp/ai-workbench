from typing import Any

import fitz
import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent

from backend.agent.planner import _build_model
from backend.services.file_service import file_store
from backend.services.result_service import result_store
from backend.tools._common import to_records
from backend.tools.data_tools import PREVIEW_ROWS

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


class _ExtractedTable(BaseModel):
    rows: list[dict[str, Any]]


_EXTRACTION_SYSTEM_PROMPT = """\
You extract structured data from document text into a list of rows matching \
what the user asked for. Each row should be a flat object with consistent \
keys across all rows (the same fields, in the same order, for every row). \
Only extract information that is actually present in the text — never \
invent, estimate, or fill in data that isn't there. If nothing matching the \
request is present, return an empty list of rows.
"""

_extraction_agent = Agent(
    _build_model(),
    output_type=_ExtractedTable,
    system_prompt=_EXTRACTION_SYSTEM_PROMPT,
)


async def extract_structured_data(file_id: str, fields_description: str) -> dict:
    text = extract_text(file_id)
    result = await _extraction_agent.run(f"Extract: {fields_description}\n\nDocument text:\n{text}")
    rows = result.output.rows

    if not rows:
        raise ValueError(
            f"Could not find any data matching '{fields_description}' in this document."
        )

    df = pd.DataFrame(rows)
    result_id = result_store.save(df)
    return {
        "result_id": result_id,
        "row_count": len(df),
        "preview": to_records(df.head(PREVIEW_ROWS)),
    }
