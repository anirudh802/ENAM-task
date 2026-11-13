import pytest
from datetime import datetime, timedelta
from app.services.filings_engine import FilingsEngine, SEBI_LODR_CATEGORIES

def test_sebi_17_categories_defined():
    assert len(SEBI_LODR_CATEGORIES) == 17
    assert "financial_results" in SEBI_LODR_CATEGORIES
    assert "management_change" in SEBI_LODR_CATEGORIES
    assert "mergers_acquisitions" in SEBI_LODR_CATEGORIES
    assert "capex_expansion" in SEBI_LODR_CATEGORIES
    assert "litigation_regulatory" in SEBI_LODR_CATEGORIES

def test_role_aware_kmp_classification():
    # 1. CFO resignation (KMP Tier 1 -> Score 9)
    res_cfo = FilingsEngine.classify_announcement(
        "Resignation of Chief Financial Officer Sanjay Upadhyay",
        "Mr. Sanjay Upadhyay has tendered resignation due to health reasons."
    )
    assert res_cfo["category"] == "management_change"
    assert res_cfo["materiality_score"] == 9
    assert res_cfo["severity"] == "CRITICAL"
    assert res_cfo["role_details"]["role_title"] == "CFO"

    # 2. Managing Director appointment (KMP Tier 1 -> Score 10)
    res_md = FilingsEngine.classify_announcement(
        "Appointment of Managing Director & CEO",
        "The Board has approved appointment of new MD & CEO for a term of 5 years."
    )
    assert res_md["category"] == "management_change"
    assert res_md["materiality_score"] == 10
    assert res_md["severity"] == "CRITICAL"

    # 3. Company Secretary resignation (Governance Tier 2 -> Score 7)
    res_cs = FilingsEngine.classify_announcement(
        "Resignation of Company Secretary & Compliance Officer",
        "Intimation regarding resignation of Company Secretary due to personal reasons."
    )
    assert res_cs["category"] == "management_change"
    assert res_cs["materiality_score"] == 7
    assert res_cs["severity"] == "HIGH"
    assert res_cs["role_details"]["role_tier"] == "GOVERNANCE_TIER_2"

def test_results_and_regulatory_classification():
    # Headline financial results
    res = FilingsEngine.classify_announcement(
        "Financial Results for Quarter Ended September 30, 2026",
        "Consolidated revenue up 120% YoY"
    )
    assert res["category"] == "financial_results"
    assert res["materiality_score"] == 10

    # Board meeting intimation to consider results (Score 6)
    res_int = FilingsEngine.classify_announcement(
        "Board Meeting Intimation to Consider Financial Results",
        "Meeting of Board of Directors scheduled on Nov 15, 2026"
    )
    assert res_int["category"] == "financial_results"
    assert res_int["materiality_score"] == 6

    # Tax demand / Regulatory litigation (Score 8)
    res_tax = FilingsEngine.classify_announcement(
        "Receipt of Order with Tax Demand under Section 73 of GST Act",
        "Deputy Commissioner of Commercial Taxes has levied demand of Rs 42 Crore."
    )
    assert res_tax["category"] == "litigation_regulatory"
    assert res_tax["materiality_score"] == 8

def test_cross_exchange_deduplication():
    now_dt = datetime.now()
    filings = [
        {
            "id": "bse-101",
            "isin": "INE806N01020",
            "ticker": "DIXON.BO",
            "category": "financial_results",
            "title": "Unaudited Financial Results for Quarter ended Sept 30 2026",
            "filing_time": now_dt.isoformat(),
            "materiality_score": 10
        },
        {
            "id": "nse-202",
            "isin": "INE806N01020",
            "ticker": "DIXON.NS",
            "category": "financial_results",
            "title": "Unaudited Financial Results for Quarter ended Sept 30 2026",
            "filing_time": (now_dt + timedelta(minutes=15)).isoformat(),
            "materiality_score": 10
        }
    ]

    deduped = FilingsEngine.deduplicate_filings(filings, window_hours=3)
    assert len(deduped) == 1
    assert "BSE" in deduped[0]["exchanges"]
    assert "NSE" in deduped[0]["exchanges"]
