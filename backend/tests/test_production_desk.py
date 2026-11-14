import os
import json
import sqlite3
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, get_db_path
from app.services.exchange_ingestion import exchange_ingestion
from app.services.llm_cache_service import llm_cache
from app.services.outbox_service import outbox_service
from app.worker import FinnWorker

client = TestClient(app)

def test_bse_deduplication_hash():
    """Verifies that cross-exchange announcements generate deterministic SHA-256 hashes."""
    isin = "INE806N01020"
    category = "results"
    title1 = "Financial Results for the Quarter Ended September 30, 2026"
    title2 = "financial results for the quarter ended september 30, 2026 "
    date = "2026-11-13T18:45:00"

    hash1 = exchange_ingestion.compute_filing_hash(isin, category, title1, date)
    hash2 = exchange_ingestion.compute_filing_hash(isin, category, title2, date)

    assert hash1 == hash2
    assert len(hash1) == 64

def test_xbrl_deterministic_financial_parsing():
    """Verifies parsing of structured Ind-AS XBRL tags with zero OCR error."""
    sample_xbrl = """<?xml version="1.0" encoding="UTF-8"?>
    <xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:in-bse-fin="http://www.bseindia.com/xbrl/fin/2020-03-31/in-bse-fin">
        <in-bse-fin:RevenueFromOperations unitRef="INR_Crores">11534.00</in-bse-fin:RevenueFromOperations>
        <in-bse-fin:OperatingProfit unitRef="INR_Crores">420.00</in-bse-fin:OperatingProfit>
        <in-bse-fin:ProfitBeforeTax unitRef="INR_Crores">290.00</in-bse-fin:ProfitBeforeTax>
        <in-bse-fin:ProfitLossForPeriod unitRef="INR_Crores">215.00</in-bse-fin:ProfitLossForPeriod>
    </xbrli:xbrl>
    """
    res = exchange_ingestion.parse_xbrl_financials(sample_xbrl, "INE806N01020")
    assert res["status"] == "VERIFIED_XBRL"
    metrics = res["metrics"]
    assert metrics["revenue_cr"] == 11534.0
    assert metrics["ebitda_cr"] == 420.0
    assert metrics["pbt_cr"] == 290.0
    assert metrics["pat_cr"] == 215.0
    assert metrics["ebitda_margin_pct"] == 3.64

def test_pdf_quarantine_fallback():
    """Verifies that degraded scanned PDFs (<0.60 quality) are safely quarantined."""
    quarantined = exchange_ingestion.evaluate_pdf_quarantine(0.42, "https://bseindia.com/filings/scanned_doc.pdf")
    assert quarantined["quarantined"] is True
    assert quarantined["status"] == "EXTRACTION_QUARANTINED"
    assert "0.42" in quarantined["reason"]

    clean = exchange_ingestion.evaluate_pdf_quarantine(0.92, "https://bseindia.com/filings/clean_doc.pdf")
    assert clean["quarantined"] is False
    assert clean["status"] == "READY_FOR_EXTRACTION"

def test_bhavcopy_delivery_percentage_signal():
    """Verifies delivery % extraction and institutional accumulation classification."""
    bhavcopy_csv = """SYMBOL,SERIES,CLOSE_PRICE,TTL_TRD_QNTY,DELIV_PER
DIXON,EQ,14850.00,1680000,74.50
TATAMOTORS,EQ,785.40,24500000,14.20
RELIANCE,EQ,1280.00,4200000,48.00
"""
    records = exchange_ingestion.parse_bhavcopy_csv(bhavcopy_csv, tracked_tickers=["DIXON.NS", "TATAMOTORS.NS"])
    assert len(records) == 2

    dixon = next(r for r in records if r["symbol"] == "DIXON")
    assert dixon["deliv_per"] == 74.5
    assert dixon["accumulation_signal"] == "INSTITUTIONAL_ACCUMULATION"

    tata = next(r for r in records if r["symbol"] == "TATAMOTORS")
    assert tata["deliv_per"] == 14.2
    assert tata["accumulation_signal"] == "SPECULATIVE_INTRADAY_CHURN"

def test_content_addressed_llm_cache():
    """Verifies content-addressed caching by doc_sha256 to guarantee zero re-inference cost."""
    sample_context = "Audited Notes to Accounts: Dixon Mobile Plant 12 Capacity Expansion."
    doc_sha = llm_cache.compute_sha256(sample_context)

    # First write to cache
    test_output = {"moat": "PLI Scale", "trajectory": "Expanding", "confidence": "HIGH"}
    llm_cache.set(doc_sha, test_output)

    # Second read retrieves cached data without external call
    cached = llm_cache.get(doc_sha)
    assert cached is not None
    assert cached["moat"] == "PLI Scale"
    assert cached["confidence"] == "HIGH"

def test_transactional_notification_outbox():
    """Verifies outbox queueing, state transitions, and stats."""
    user_id = "user-enam-01"
    anomaly_id = "anom-dixon-vol-01"
    payload = {"headline": "Test Surge", "ticker": "DIXON.NS"}

    outbox_id = outbox_service.enqueue(user_id, anomaly_id, payload)
    assert outbox_id.startswith("outbox-")

    pending = outbox_service.get_pending()
    matching = [p for p in pending if p["id"] == outbox_id]
    assert len(matching) == 1

    # Mark sent
    outbox_service.mark_sent(outbox_id)
    stats = outbox_service.get_outbox_stats()
    assert stats["sent_notifications"] >= 1

def test_http_etag_304_caching():
    """Verifies HTTP ETag generation and 304 Not Modified response."""
    # First request receives 200 and an ETag header
    res1 = client.get("/api/push/digest?hours=24")
    assert res1.status_code == 200
    etag = res1.headers.get("etag")
    assert etag is not None

    # Second request with matching If-None-Match receives 304 Not Modified
    res2 = client.get("/api/push/digest?hours=24", headers={"If-None-Match": etag})
    assert res2.status_code == 304
    assert res2.text == ""

def test_operational_readiness_health():
    """Verifies rich operational readiness subsystem diagnostics."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "database_vitals" in data
    assert data["database_vitals"]["wal_mode"] is True
    assert data["database_vitals"]["latency_ms"] < 20.0
    assert "ingestion" in data
    assert "outbox" in data
    assert "llm_gateway" in data
    assert data["llm_gateway"]["circuit_breaker"] == "CLOSED"

def test_online_hot_backup_vacuum_into(tmp_path):
    """Verifies that online hot backups via VACUUM INTO produce clean, openable SQLite databases."""
    worker = FinnWorker()
    backup_file = worker.online_hot_backup(backup_dir=str(tmp_path))
    assert os.path.exists(backup_file)

    # Open backed-up database and verify table counts
    conn = sqlite3.connect(backup_file)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM companies;")
    count = c.fetchone()[0]
    conn.close()
    assert count >= 8
