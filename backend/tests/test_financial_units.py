import pytest
from datetime import date
from app.core.financial_units import (
    date_to_fiscal_quarter,
    fiscal_quarter_to_date_range,
    crore_to_inr,
    lakh_to_inr,
    inr_to_crore,
    inr_to_lakh,
    bps_to_pct,
    pct_to_bps,
    calculate_growth_pct,
    calculate_margin_bps_delta,
)

def test_indian_fiscal_quarter_mapping():
    # Apr-Jun 2024 -> Q1FY25
    assert date_to_fiscal_quarter(date(2024, 4, 15)) == "Q1FY25"
    assert date_to_fiscal_quarter(date(2024, 6, 30)) == "Q1FY25"

    # Jul-Sep 2024 -> Q2FY25
    assert date_to_fiscal_quarter(date(2024, 8, 10)) == "Q2FY25"

    # Oct-Dec 2024 -> Q3FY25
    assert date_to_fiscal_quarter(date(2024, 11, 20)) == "Q3FY25"

    # Jan-Mar 2025 -> Q4FY25
    assert date_to_fiscal_quarter(date(2025, 2, 1)) == "Q4FY25"

    # Reverse date range mapping
    start, end = fiscal_quarter_to_date_range("Q2FY25")
    assert start == "2024-07-01"
    assert end == "2024-09-30"

def test_financial_unit_conversions():
    # Crore conversions
    assert crore_to_inr(1.5) == 15_000_000.0
    assert inr_to_crore(25_000_000.0) == 2.5

    # Lakh conversions
    assert lakh_to_inr(10.0) == 1_000_000.0
    assert inr_to_lakh(500_000.0) == 5.0

    # Basis points & percentages
    assert bps_to_pct(150.0) == 1.5
    assert pct_to_bps(1.5) == 150.0

    # Growth and margin delta calculations
    # 11534 Cr vs 5233 Cr = +120.41% YoY
    assert calculate_growth_pct(11534.0, 5233.0) == 120.41

    # Margin compressed from 4.0% to 3.64% = -36.0 bps
    assert calculate_margin_bps_delta(3.64, 4.0) == -36.0
