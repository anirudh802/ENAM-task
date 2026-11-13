import pytest
from app.db.database import get_db
from app.services.citation_verifier import CitationVerifier

def test_verbatim_quote_locating():
    source_text = "Atul Lall (MD): In Q2, our consolidated revenues stood at Rs 11,534 Cr, representing a phenomenal 120% YoY growth."
    quote = "our consolidated revenues stood at Rs 11,534 Cr"

    found, offset, ratio = CitationVerifier.locate_quote(quote, source_text)
    assert found is True
    assert offset >= 0
    assert ratio >= 0.90

def test_near_verbatim_quote_locating():
    source_text = "We continue to see immense white space in tier 2 and tier 3 micro-markets for Zudio without cannibalization."
    # Minor difference in whitespace and punctuation
    quote = "see immense white space in tier 2 and tier 3 micro-markets for Zudio"

    found, offset, ratio = CitationVerifier.locate_quote(quote, source_text)
    assert found is True
    assert ratio >= 0.90

def test_hallucinated_quote_rejection():
    source_text = "Standalone Q2 revenue was Rs 4,035 Cr, up 39% YoY."
    hallucinated_quote = "Management plans to acquire an overseas fashion brand in Paris for 5,000 Cr."

    found, offset, ratio = CitationVerifier.locate_quote(hallucinated_quote, source_text)
    assert found is False
    assert ratio < 0.60

def test_claim_verification_against_primary_sources():
    with get_db() as conn:
        # 1. Real quote from Dixon Concall
        real_quote = "our consolidated revenues stood at Rs 11,534 Cr"
        res = CitationVerifier.verify_claim(real_quote, "DIXON.NS", conn)
        assert res["verified"] is True
        assert res["faithfulness"] == 1.0
        assert res["matched_doc_id"] == "concall-dixon-q2fy25"

        # 2. Fake quote claiming false guidance
        fake_quote = "We project EBITDA margins to exceed 25% in Q3 due to government grants."
        res_fake = CitationVerifier.verify_claim(fake_quote, "DIXON.NS", conn)
        assert res_fake["verified"] is False
        assert res_fake["faithfulness"] == 0.0

        # 3. Legitimate explicit non-disclosure claim
        non_disclosure = "Details of third-party contract manufacturers are not disclosed in provided sources."
        res_nd = CitationVerifier.verify_claim(non_disclosure, "DIXON.NS", conn)
        assert res_nd["verified"] is True
        assert res_nd["is_explicit_non_disclosure"] is True
        assert res_nd["faithfulness"] == 1.0
