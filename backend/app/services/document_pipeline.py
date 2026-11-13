"""
Document Pipeline & Parse Quality Engine (D-01, D-02, D-08, F-08)
Structured document ingestion, parse-quality scoring, section segmentation,
content hashing, and cold-ticker coverage reporting.
"""

import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple

class DocumentPipeline:
    @staticmethod
    def compute_sha256(content: str) -> str:
        """Computes SHA-256 hash for document auditability (F-08)."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def calculate_parse_quality_score(text: str) -> Tuple[float, List[str]]:
        """
        Computes a parse-quality score (0.0 to 1.0) for ingested PDF/text disclosures (D-01).
        Flags OCR corruption, garbled characters, or truncated extractions.
        """
        flags = []
        if not text or len(text.strip()) == 0:
            return 0.0, ["EMPTY_DOCUMENT"]

        raw_length = len(text)
        if raw_length < 200:
            flags.append("DOCUMENT_TOO_SHORT")

        # 1. Garbled character check (Unicode replacement \ufffd or excessive unprintable characters)
        garbled_count = len(re.findall(r"[\ufffd\x00-\x08\x0b\x0c\x0e-\x1f]", text))
        garbled_ratio = garbled_count / max(1, raw_length)
        if garbled_ratio > 0.02:
            flags.append("HIGH_GARBLED_CHAR_RATIO")

        # 2. Alphanumeric density check
        alphanumeric_count = len(re.findall(r"[a-zA-Z0-9]", text))
        alphanumeric_ratio = alphanumeric_count / max(1, raw_length)
        if alphanumeric_ratio < 0.60:
            flags.append("LOW_ALPHANUMERIC_DENSITY")

        # 3. Financial structure / numeric density check (filings and concalls must contain numbers)
        numeric_count = len(re.findall(r"\b\d+(?:\.\d+)?\b", text))
        if numeric_count < 5 and raw_length > 500:
            flags.append("SUSPICIOUSLY_LOW_NUMERIC_DENSITY")

        # 4. Sentence / line coherence check
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        avg_line_len = sum(len(l) for l in lines) / max(1, len(lines))
        if avg_line_len < 10 and len(lines) > 20:
            flags.append("FRAGMENTED_LINE_BREAKS")

        # Calculate final composite score
        score = 1.0
        if "EMPTY_DOCUMENT" in flags:
            return 0.0, flags
        if "HIGH_GARBLED_CHAR_RATIO" in flags:
            score -= 0.35
        if "LOW_ALPHANUMERIC_DENSITY" in flags:
            score -= 0.25
        if "SUSPICIOUSLY_LOW_NUMERIC_DENSITY" in flags:
            score -= 0.20
        if "DOCUMENT_TOO_SHORT" in flags:
            score -= 0.25
        if "FRAGMENTED_LINE_BREAKS" in flags:
            score -= 0.15

        final_score = max(0.0, min(1.0, round(score, 2)))
        return final_score, flags

    @staticmethod
    def get_ticker_coverage(ticker: str, conn) -> Dict[str, Any]:
        """
        Assesses research document coverage for cold or under-covered tickers (D-08).
        """
        cursor = conn.cursor()

        # Check Concalls
        cursor.execute("SELECT COUNT(*), MAX(fiscal_quarter) FROM concall_transcripts WHERE ticker = ?;", (ticker,))
        concall_count, latest_concall_qtr = cursor.fetchone()

        # Check Announcements
        cursor.execute("SELECT COUNT(*) FROM announcements WHERE ticker = ?;", (ticker,))
        ann_count = cursor.fetchone()[0]

        # Check Guidance History
        cursor.execute("SELECT COUNT(*) FROM guidance_history WHERE ticker = ?;", (ticker,))
        guidance_count = cursor.fetchone()[0]

        # Check Financials (eod or company master)
        cursor.execute("SELECT isin, name, sector FROM companies WHERE ticker = ?;", (ticker,))
        comp = cursor.fetchone()

        has_baseline = comp is not None
        coverage_pct = 0.0
        if has_baseline:
            coverage_pct += 25.0
        if concall_count > 0:
            coverage_pct += 35.0
        if ann_count >= 3:
            coverage_pct += 25.0
        elif ann_count > 0:
            coverage_pct += 15.0
        if guidance_count > 0:
            coverage_pct += 15.0

        status = "FULL_COVERAGE" if coverage_pct >= 85.0 else ("PARTIAL_COVERAGE" if coverage_pct >= 50.0 else "INSUFFICIENT_COVERAGE")

        return {
            "ticker": ticker,
            "isin": comp["isin"] if comp else None,
            "company_name": comp["name"] if comp else None,
            "coverage_pct": round(coverage_pct, 1),
            "status": status,
            "breakdown": {
                "concall_transcripts_available": concall_count,
                "latest_concall_quarter": latest_concall_qtr,
                "regulatory_announcements_count": ann_count,
                "guidance_track_records_count": guidance_count
            },
            "is_ready_for_deepdive": coverage_pct >= 50.0
        }
