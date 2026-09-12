import io

import pandas as pd
import pytest

from backend.services.file_service import file_store
from backend.services.result_service import result_store
from backend.tools.data_tools import analyse_dataset, compare_datasets
from backend.tools.document_tools import extract_text
from backend.tools.output_tools import create_table, generate_chart


def _upload_csv(filename, df):
    content = df.to_csv(index=False).encode()
    return file_store.save(filename, content)


def _upload_xlsx(filename, df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return file_store.save(filename, buf.getvalue())


def test_analyse_dataset_average():
    df = pd.DataFrame({"product": ["A", "B", "C"], "sales": [100, 200, 300]})
    meta = _upload_csv("sales.csv", df)

    result = analyse_dataset(meta.file_id, operation="average", value_column="sales")
    assert result["row_count"] == 1
    assert result["preview"][0]["sales"] == 200


def test_analyse_dataset_top_n():
    df = pd.DataFrame({"product": ["A", "B", "C"], "sales": [100, 300, 200]})
    meta = _upload_csv("sales.csv", df)

    result = analyse_dataset(meta.file_id, operation="top_n", value_column="sales", top_n=1)
    assert result["row_count"] == 1
    assert result["preview"][0]["product"] == "B"


def test_analyse_dataset_filter_threshold():
    df = pd.DataFrame({"product": ["A", "B", "C"], "sales": [100, 300, 200]})
    meta = _upload_csv("sales.csv", df)

    result = analyse_dataset(
        meta.file_id, operation="filter_threshold", value_column="sales", threshold=150
    )
    assert result["row_count"] == 2


def test_analyse_dataset_unknown_column_raises():
    df = pd.DataFrame({"product": ["A"], "sales": [100]})
    meta = _upload_csv("sales.csv", df)

    with pytest.raises(ValueError):
        analyse_dataset(meta.file_id, operation="average", value_column="not_a_column")


def test_compare_datasets_computes_pct_change():
    jan = pd.DataFrame({"product": ["Keyboard C", "Mouse D"], "sales": [500, 100]})
    feb = pd.DataFrame({"product": ["Keyboard C", "Mouse D"], "sales": [340, 95]})
    meta_jan = _upload_xlsx("January.xlsx", jan)
    meta_feb = _upload_xlsx("February.xlsx", feb)

    result = compare_datasets(
        meta_jan.file_id, meta_feb.file_id, key_column="product", value_column="sales"
    )
    assert result["row_count"] == 2
    keyboard_row = next(r for r in result["preview"] if r["product"] == "Keyboard C")
    assert round(keyboard_row["pct_change"], 1) == -32.0


def test_compare_datasets_threshold_filters():
    jan = pd.DataFrame({"product": ["Keyboard C", "Mouse D"], "sales": [500, 100]})
    feb = pd.DataFrame({"product": ["Keyboard C", "Mouse D"], "sales": [340, 95]})
    meta_jan = _upload_xlsx("January.xlsx", jan)
    meta_feb = _upload_xlsx("February.xlsx", feb)

    result = compare_datasets(
        meta_jan.file_id,
        meta_feb.file_id,
        key_column="product",
        value_column="sales",
        threshold_pct=20,
    )
    assert result["row_count"] == 1
    assert result["preview"][0]["product"] == "Keyboard C"


def test_create_table_and_generate_chart():
    df = pd.DataFrame({"product": ["A", "B"], "sales": [100, 200]})
    result_id = result_store.save(df)

    table = create_table(result_id, title="Sales")
    assert table["columns"] == ["product", "sales"]

    chart = generate_chart(
        result_id, chart_type="bar", x_field="product", y_field="sales", title="Sales"
    )
    assert chart["chart_type"] == "bar"


def test_generate_chart_unknown_field_raises():
    df = pd.DataFrame({"product": ["A"], "sales": [100]})
    result_id = result_store.save(df)

    with pytest.raises(ValueError):
        generate_chart(
            result_id, chart_type="bar", x_field="product", y_field="not_a_field", title="x"
        )


def test_extract_text_reads_real_pdf():
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Revenue increased by 12%.")
    pdf_bytes = doc.tobytes()
    doc.close()

    meta = file_store.save("report.pdf", pdf_bytes)
    text = extract_text(meta.file_id)
    assert "Revenue increased by 12%" in text


def test_analyse_dataset_corrupt_excel_raises_value_error():
    meta = file_store.save("broken.xlsx", b"this is not a real xlsx file")

    with pytest.raises(ValueError):
        analyse_dataset(meta.file_id, operation="average", value_column="sales")


def test_compare_datasets_corrupt_csv_raises_value_error():
    good = _upload_csv("good.csv", pd.DataFrame({"product": ["A"], "sales": [1]}))
    bad = file_store.save("bad.csv", b"\x00\x01\x02not,valid,csv\x00\x00")

    with pytest.raises(ValueError):
        compare_datasets(
            good.file_id, bad.file_id, key_column="product", value_column="sales"
        )


def test_extract_text_corrupt_pdf_raises_value_error():
    meta = file_store.save("broken.pdf", b"this is not a real pdf file")

    with pytest.raises(ValueError):
        extract_text(meta.file_id)


def test_analyse_dataset_non_numeric_top_n_raises_clear_error():
    df = pd.DataFrame({"product": ["A", "B"], "sales": [100, 200]})
    meta = _upload_csv("sales.csv", df)

    with pytest.raises(ValueError, match="top_n"):
        analyse_dataset(meta.file_id, operation="top_n", value_column="sales", top_n="five")


def test_analyse_dataset_non_numeric_threshold_raises_clear_error():
    df = pd.DataFrame({"product": ["A", "B"], "sales": [100, 200]})
    meta = _upload_csv("sales.csv", df)

    with pytest.raises(ValueError, match="threshold"):
        analyse_dataset(
            meta.file_id,
            operation="filter_threshold",
            value_column="sales",
            threshold="a lot",
        )
