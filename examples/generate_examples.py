"""Regenerates the example files under examples/ used by the demo scenarios
and tests/test_demo_scenarios.py. Run with: python examples/generate_examples.py
"""

import os

import fitz
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))


def generate_annual_report_pdf():
    path = os.path.join(HERE, "reports", "annual_report.pdf")
    doc = fitz.open()

    page = doc.new_page()
    page.insert_text((72, 72), "Acme Robotics -- Annual Report 2025", fontsize=18)
    page.insert_text((72, 110), "Executive Summary", fontsize=13)
    page.insert_textbox(
        fitz.Rect(72, 130, 525, 260),
        "Acme Robotics delivered a solid year of growth in 2025, with total "
        "revenue increasing by 12% to $45.2 million, driven primarily by "
        "strong demand in the APAC region and the successful launch of two "
        "new product lines.",
        fontsize=11,
    )
    page.insert_text((72, 290), "Financial Highlights", fontsize=13)
    page.insert_textbox(
        fitz.Rect(72, 310, 525, 440),
        "Operating costs increased by 5% year-over-year, reflecting "
        "continued investment in headcount and cloud infrastructure to "
        "support scaling operations. Despite the increase in costs, "
        "operating margin improved slightly to 18.4%, up from 17.9% in the "
        "prior year.",
        fontsize=11,
    )

    page2 = doc.new_page()
    page2.insert_text((72, 72), "Regional Performance", fontsize=13)
    page2.insert_textbox(
        fitz.Rect(72, 92, 525, 230),
        "Singapore remained the company's largest market, contributing 38% "
        "of total revenue, followed by the broader APAC region at 29% and "
        "the Rest of World at 33%. Growth in Singapore was driven by "
        "enterprise contract renewals, while APAC ex-Singapore grew fastest "
        "at 21% year-over-year.",
        fontsize=11,
    )
    page2.insert_text((72, 260), "Outlook", fontsize=13)
    page2.insert_textbox(
        fitz.Rect(72, 280, 525, 420),
        "Looking ahead to 2026, management expects continued double-digit "
        "revenue growth, supported by an expanding product portfolio and "
        "deeper penetration into Southeast Asian markets. Key risks include "
        "supply chain volatility and increased competition in the robotics "
        "sensor market.",
        fontsize=11,
    )

    doc.save(path)
    doc.close()
    print(f"wrote {path}")


def generate_sales_files():
    products = [
        "Laptop A",
        "Monitor B",
        "Keyboard C",
        "Mouse D",
        "Headset E",
        "Webcam F",
        "Charger G",
        "Speaker H",
    ]
    january = [1000, 500, 500, 300, 220, 180, 150, 260]
    february = [960, 460, 340, 282, 235, 176, 158, 250]

    jan_path = os.path.join(HERE, "sales", "January.xlsx")
    feb_path = os.path.join(HERE, "sales", "February.xlsx")

    pd.DataFrame({"product": products, "sales": january}).to_excel(jan_path, index=False)
    pd.DataFrame({"product": products, "sales": february}).to_excel(feb_path, index=False)
    print(f"wrote {jan_path}")
    print(f"wrote {feb_path}")


def generate_monthly_sales_csv():
    path = os.path.join(HERE, "datasets", "monthly_sales.csv")
    df = pd.DataFrame(
        {
            "month": ["January", "February", "March", "April", "May", "June"],
            "sales": [12000, 12500, 15800, 16200, 16800, 17400],
        }
    )
    df.to_csv(path, index=False)
    print(f"wrote {path}")


if __name__ == "__main__":
    generate_annual_report_pdf()
    generate_sales_files()
    generate_monthly_sales_csv()
