import pytest
from app.db.database import get_db
from app.services.document_pipeline import DocumentPipeline

def test_parse_quality_score_high_quality():
    clean_filing = """
    Unaudited Consolidated Financial Results for Quarter ended September 30, 2026.
    Revenue from operations stood at Rs 11,534.00 Crore compared to Rs 5,233.00 Crore in the previous year.
    EBITDA for the quarter was Rs 420.00 Crore, yielding a margin of 3.64%.
    Profit before tax stood at Rs 482.00 Crore and Net Profit (PAT) was Rs 412.00 Crore.
    The Board of Directors approved these results at their meeting held on November 5, 2026.
    """
    score, flags = DocumentPipeline.calculate_parse_quality_score(clean_filing)
    assert score >= 0.85
    assert len(flags) == 0

def test_parse_quality_score_garbled_ocr():
    garbled_text = "Th\ufffd\ufffd \ufffdqu\ufffdrter r\ufffdesults \x00\x01\x02 \ufffd\ufffd\ufffd"
    score, flags = DocumentPipeline.calculate_parse_quality_score(garbled_text)
    assert score < 0.60
    assert "HIGH_GARBLED_CHAR_RATIO" in flags or "DOCUMENT_TOO_SHORT" in flags

def test_parse_quality_score_empty():
    score, flags = DocumentPipeline.calculate_parse_quality_score("")
    assert score == 0.0
    assert "EMPTY_DOCUMENT" in flags

def test_cold_ticker_coverage_assessment():
    with get_db() as conn:
        # DIXON is fully seeded with concall, announcements, and guidance
        dixon_cov = DocumentPipeline.get_ticker_coverage("DIXON.NS", conn)
        assert dixon_cov["coverage_pct"] >= 80.0
        assert dixon_cov["status"] == "FULL_COVERAGE"
        assert dixon_cov["is_ready_for_deepdive"] is True

        # Unseeded cold ticker
        cold_cov = DocumentPipeline.get_ticker_coverage("RANDOM_TICKER.NS", conn)
        assert cold_cov["coverage_pct"] == 0.0
        assert cold_cov["status"] == "INSUFFICIENT_COVERAGE"
        assert cold_cov["is_ready_for_deepdive"] is False
