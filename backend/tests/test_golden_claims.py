"""
Golden Set of Hand-Checked Claims & Citation Faithfulness Gate (X-01)
Phase 1 Exit Gate Test.
Verifies that primary-source claims achieve 100% citation faithfulness
and that any hallucinated or modified quotes fail verification.
"""

import pytest
from app.db.database import get_db
from app.services.citation_verifier import CitationVerifier
from app.services.research_engine import ResearchEngine

GOLDEN_CLAIMS = [
    {
        "ticker": "DIXON.NS",
        "company": "Dixon Technologies",
        "quote": "our consolidated revenues stood at Rs 11,534 Cr, representing a phenomenal 120% YoY growth",
        "doc_type": "CONCALL_TRANSCRIPT",
        "expected_verified": True
    },
    {
        "ticker": "DIXON.NS",
        "company": "Dixon Technologies",
        "quote": "Our smartphone monthly run rate has crossed 3.8 million units",
        "doc_type": "CONCALL_TRANSCRIPT",
        "expected_verified": True
    },
    {
        "ticker": "TRENT.NS",
        "company": "Trent Ltd",
        "quote": "Standalone Q2 revenue was Rs 4,035 Cr, up 39% YoY",
        "doc_type": "CONCALL_TRANSCRIPT",
        "expected_verified": True
    },
    {
        "ticker": "TRENT.NS",
        "company": "Trent Ltd",
        "quote": "We will open between 50 to 60 Zudio stores in Q3 ahead of the festive and winter season",
        "doc_type": "CONCALL_TRANSCRIPT",
        "expected_verified": True
    },
    {
        "ticker": "HDFCBANK.NS",
        "company": "HDFC Bank",
        "quote": "core Net Interest Margin stabilizing at 3.46%",
        "doc_type": "CONCALL_TRANSCRIPT",
        "expected_verified": True
    },
    {
        "ticker": "RELIANCE.NS",
        "company": "Reliance Industries",
        "quote": "Our pan-India 5G capex cycle has peaked, and telecom cash flows are now strongly converting to free cash flow",
        "doc_type": "CONCALL_TRANSCRIPT",
        "expected_verified": True
    }
]

HALLUCINATED_CLAIMS = [
    {
        "ticker": "DIXON.NS",
        "company": "Dixon Technologies",
        "quote": "Dixon plans to acquire Apple assembly plants in Vietnam for 10,000 Crore.",
        "expected_verified": False
    },
    {
        "ticker": "TRENT.NS",
        "company": "Trent Ltd",
        "quote": "Trent is shutting down 200 Zudio stores due to severe margin erosion.",
        "expected_verified": False
    },
    {
        "ticker": "HDFCBANK.NS",
        "company": "HDFC Bank",
        "quote": "Gross NPA surged to 12.5% following major corporate defaults in real estate.",
        "expected_verified": False
    }
]

def test_golden_set_claims_100pct_faithfulness():
    """Validates that all hand-checked golden claims achieve 100% verification."""
    with get_db() as conn:
        for claim in GOLDEN_CLAIMS:
            res = CitationVerifier.verify_claim(claim["quote"], claim["ticker"], conn)
            assert res["verified"] is True, f"Failed to verify golden claim for {claim['company']}: {claim['quote']}"
            assert res["faithfulness"] == 1.0
            assert res.get("matched_doc_id") is not None

def test_failure_injection_rejects_hallucinations():
    """Validates that hallucinated or fabricated claims are strictly rejected."""
    with get_db() as conn:
        for claim in HALLUCINATED_CLAIMS:
            res = CitationVerifier.verify_claim(claim["quote"], claim["ticker"], conn)
            assert res["verified"] is False, f"Hallucinated claim was falsely verified: {claim['quote']}"
            assert res["faithfulness"] == 0.0

def test_research_engine_golden_deepdive_and_caching():
    """
    End-to-end Phase 1 verification:
    - Verifies citation faithfulness score >= 0.90
    - Checks Bank/NBFC vs Industrial template selection
    - Checks SEBI disclaimer and versioning metadata
    - Validates cache invalidation and cache hits
    """
    ResearchEngine.clear_cache()

    # 1. Industrial Equity Test (DIXON)
    dixon_research = ResearchEngine.get_company_research("DIXON")
    assert dixon_research["ticker"] == "DIXON.NS"
    assert dixon_research["template_type"] == "INDUSTRIAL_EQUITY"
    assert dixon_research["citation_faithfulness_score"] >= 0.90
    assert dixon_research["verification_status"] == "PASSED"
    assert "SEBI (Research Analysts) Regulations, 2014" in dixon_research["sebi_research_disclaimer"]
    assert dixon_research["model_version"] == "gemini-2.5-pro"
    assert dixon_research["prompt_version"] == "2026-11-13.v2"
    assert dixon_research["cache_hit"] is False

    # Second call hits cache (D-11)
    dixon_cached = ResearchEngine.get_company_research("DIXON")
    assert dixon_cached["cache_hit"] is True

    # 2. Bank/NBFC Template Test (HDFCBANK - D-12)
    hdfc_research = ResearchEngine.get_company_research("HDFCBANK")
    assert hdfc_research["ticker"] == "HDFCBANK.NS"
    assert hdfc_research["template_type"] == "BFSI_BANK_NBFC"
    assert hdfc_research["financial_snapshot"]["nim_bps"] > 0
    assert "gross_npa_pct" in hdfc_research["financial_snapshot"]
    assert "liquidity_coverage_ratio_pct" in hdfc_research["cash_quality"]

    # 3. Trent Test
    trent_research = ResearchEngine.get_company_research("TRENT")
    assert trent_research["ticker"] == "TRENT.NS"
    assert len(trent_research["narrative_vs_numbers"]) > 0
