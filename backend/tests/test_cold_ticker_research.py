import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.seed_data import seed_database
from app.services.research_engine import ResearchEngine
from app.models.schemas import PullResearchResponse

client = TestClient(app)

def setup_module():
    seed_database()
    ResearchEngine.clear_cache()

def test_cold_ticker_normalization_and_research():
    """
    Verifies that querying an unseeded NSE ticker (e.g., MARUTI without .NS):
    1. Automatically normalizes the ticker to MARUTI.NS.
    2. Dynamically resolves or synthesizes grounded financial fundamentals.
    3. Returns a valid, schema-compliant 200 OK research payload.
    4. Has non-empty quantitative metrics (Revenue, PAT, EBITDA, CFO).
    5. Caches the entity in SQLite for subsequent loads.
    """
    # 1. Query unseeded ticker without .NS suffix
    response = client.get("/api/pull/research/MARUTI")
    assert response.status_code == 200
    data = response.json()

    # 2. Check normalization
    assert data["ticker"] == "MARUTI.NS"
    assert "Maruti" in data["company_name"]
    assert data["sector"] == "Automotive"

    # 3. Check non-empty financial snapshot
    fin = data["financial_snapshot"]
    assert fin is not None
    assert fin["current_revenue_cr"] > 100000.0  # Maruti FY24/25 revenue is > ₹1.4 lakh Cr
    assert fin["pat_cr"] > 10000.0
    assert fin["ebitda_margin_pct"] > 5.0
    assert fin["roce_pct"] > 0
    assert fin["roe_pct"] > 0

    # 4. Check non-empty cash conversion
    cash = data["cash_quality"]
    assert cash is not None
    assert cash["cfo_cr"] > 0
    assert cash["cash_conversion_ratio"] > 0
    assert cash["working_capital_days"] is not None

    # 6. Verify Reg 33 filing grounding flag (Item 10)
    assert data.get("has_reg33_filing") is False
    assert data.get("xbrl_filing_grounded") is False

    # Check that Dixon (which has an indexed results filing) is marked grounded
    res_dixon = client.get("/api/pull/research/DIXON.NS")
    assert res_dixon.status_code == 200
    assert res_dixon.json().get("has_reg33_filing") is True
    assert res_dixon.json().get("xbrl_filing_grounded") is True
    # 5. Check business snapshot & moat
    biz = data["business_snapshot"]
    assert biz["summary"] is not None
    assert len(biz["segments"]) > 0
    assert biz["competitive_moat"] is not None

    # 6. Check bull & bear cases
    assert len(data["bull_case"]) > 0
    assert len(data["bear_case"]) > 0
    assert len(data["primary_sources_cited"]) > 0

    # 7. Check coverage assessment
    assert "coverage_assessment" in data
    assert data["coverage_assessment"]["coverage_pct"] >= 25.0

    # 8. Schema validation via Pydantic model
    # Should not raise ValidationError
    validated = PullResearchResponse(**data)
    assert validated.ticker == "MARUTI.NS"

def test_cold_ticker_infy_and_cache_speed():
    """
    Verifies unseeded large-cap INFY.NS query, schema compliance, and cache hit.
    """
    # First query resolves and caches
    res1 = client.get("/api/pull/research/INFY.NS")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["ticker"] == "INFY.NS"
    assert "Infosys" in data1["company_name"]
    assert data1["sector"] == "Information Technology"
    assert data1["financial_snapshot"]["current_revenue_cr"] > 100000.0

    # Second query hits memory / DB cache
    res2 = client.get("/api/pull/research/INFY.NS")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["ticker"] == "INFY.NS"
    assert data2.get("cache_hit") is True

def test_arbitrary_unseeded_ticker_generalization():
    """
    Verifies that finn can generalize to ANY arbitrary unseeded ticker (e.g. BHARATFORG or UNKNOWN.NS).
    Ensures coverage_line, available_documents, and missing_documents are populated without dead ends.
    """
    res = client.get("/api/pull/research/BHARATFORG")
    assert res.status_code == 200
    data = res.json()
    assert data["ticker"] == "BHARATFORG.NS"
    assert data["financial_snapshot"]["current_revenue_cr"] > 0
    assert data["financial_snapshot"]["pat_cr"] > 0
    assert len(data["business_snapshot"]["segments"]) > 0

    # Test BEL.NS
    res_bel = client.get("/api/pull/research/BEL.NS")
    assert res_bel.status_code == 200
    data_bel = res_bel.json()
    assert data_bel["ticker"] == "BEL.NS"
    assert "Bharat Electronics" in data_bel["company_name"]
    assert "transcripts" in data_bel["coverage_line"].lower()
    assert len(data_bel["available_documents"]) > 0
    assert len(data_bel["missing_documents"]) > 0

    # Test UNKNOWN.NS
    res_unk = client.get("/api/pull/research/UNKNOWN.NS")
    assert res_unk.status_code == 200
    data_unk = res_unk.json()
    assert data_unk["ticker"] == "UNKNOWN.NS"
    assert "transcripts" in data_unk["coverage_line"].lower()
    assert len(data_unk["available_documents"]) > 0
