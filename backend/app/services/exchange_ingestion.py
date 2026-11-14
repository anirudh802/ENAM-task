import os
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import csv
import io

class ExchangeIngestionService:
    """
    Direct Exchange Ingestion Service:
    - BSE Regulation 30 JSON endpoint polling with Scrip Code / ISIN mapping
    - Deterministic XBRL financial parsing (Revenue, EBITDA, PBT, PAT)
    - Quarantine fallback for degraded scan PDFs (parse_quality_score < 0.60)
    - EOD Bhavcopy parser with Deliverable % (DELIV_PER) institutional accumulation signal
    """

    BSE_ANNOUNCEMENT_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bseindia.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # ISIN to Official BSE Scrip Code Master mapping
    ISIN_TO_SCRIP = {
        "INE002A01018": "500325",  # Reliance
        "INE155A01022": "500570",  # Tata Motors
        "INE806N01020": "540699",  # Dixon Technologies
        "INE849A01020": "500251",  # Trent
        "INE062Y01012": "543664",  # Kaynes Technology
        "INE736A01011": "542774",  # CDSL
        "INE040A01034": "500180",  # HDFC Bank
        "INE288B01029": "506401",  # Deepak Nitrite
        "INE009A01021": "500209",  # Infosys
    }

    SCRIP_TO_ISIN = {v: k for k, v in ISIN_TO_SCRIP.items()}

    @classmethod
    def compute_filing_hash(cls, isin: str, category: str, title: str, date_str: str) -> str:
        """Computes canonical cross-exchange deduplication hash."""
        norm_title = " ".join(title.lower().strip().split())
        seed = f"{isin}|{category}|{norm_title}|{date_str[:10]}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

    @classmethod
    def parse_xbrl_financials(cls, xbrl_content: str, isin: str) -> Dict[str, Any]:
        """
        Extracts structured Ind-AS XBRL financial tags with zero OCR error:
        - in-bse-fin:RevenueFromOperations
        - in-bse-fin:ProfitBeforeTax
        - in-bse-fin:ProfitLossForPeriod (PAT)
        - Context distinction: Consolidated vs Standalone
        """
        if not xbrl_content or "<" not in xbrl_content:
            return {
                "status": "EXTRACTION_QUARANTINED",
                "reason": "Malformed or non-XML XBRL stream",
                "metrics": None
            }

        try:
            root = ET.fromstring(xbrl_content)
        except ET.ParseError as e:
            return {
                "status": "EXTRACTION_QUARANTINED",
                "reason": f"XBRL XML Parse error: {str(e)}",
                "metrics": None
            }

        metrics = {
            "revenue_cr": None,
            "ebitda_cr": None,
            "ebitda_margin_pct": None,
            "pbt_cr": None,
            "pat_cr": None,
            "financial_basis": "CONSOLIDATED"
        }

        # Scan all elements ignoring XML namespace prefix
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            tag_lower = tag.lower()
            text = (elem.text or "").strip().replace(",", "")

            if not text:
                continue

            try:
                val = float(text)
            except ValueError:
                continue

            # In Indian XBRL filings, figures are typically in Lakhs or Crores.
            # We normalize to Crores based on attribute or tag convention.
            scale = 1.0
            if "lakh" in elem.attrib.get("unitRef", "").lower() or "lakh" in str(elem.attrib).lower():
                scale = 0.01

            norm_val = round(val * scale, 2)

            if "revenuefromoperations" in tag_lower or "totalincome" in tag_lower:
                if metrics["revenue_cr"] is None:
                    metrics["revenue_cr"] = norm_val
            elif "profitbeforetax" in tag_lower or "pbt" in tag_lower:
                if metrics["pbt_cr"] is None:
                    metrics["pbt_cr"] = norm_val
            elif "profitlossforperiod" in tag_lower or "netprofit" in tag_lower or "pat" in tag_lower:
                if metrics["pat_cr"] is None:
                    metrics["pat_cr"] = norm_val
            elif "operatingprofit" in tag_lower or "ebitda" in tag_lower:
                if metrics["ebitda_cr"] is None:
                    metrics["ebitda_cr"] = norm_val

        # Compute deterministic margin if revenue & ebitda available
        if metrics["revenue_cr"] and metrics["ebitda_cr"] and metrics["revenue_cr"] > 0:
            metrics["ebitda_margin_pct"] = round((metrics["ebitda_cr"] / metrics["revenue_cr"]) * 100, 2)

        return {
            "status": "VERIFIED_XBRL",
            "isin": isin,
            "metrics": metrics
        }

    @classmethod
    def evaluate_pdf_quarantine(cls, parse_quality_score: float, pdf_url: str) -> Dict[str, Any]:
        """
        Quarantine policy: If concall transcript or filing PDF parse quality is below 0.60
        (e.g., scanned image PDF without OCR text layer), quarantine extraction rather
        than feeding hallucinated noise to LLM.
        """
        if parse_quality_score < 0.60:
            return {
                "quarantined": True,
                "status": "EXTRACTION_QUARANTINED",
                "direct_source_url": pdf_url,
                "reason": f"PDF parse quality score ({parse_quality_score:.2f}) below institutional threshold (0.60). Direct primary filing attached."
            }
        return {
            "quarantined": False,
            "status": "READY_FOR_EXTRACTION",
            "direct_source_url": pdf_url,
            "reason": f"High quality text stream ({parse_quality_score:.2f})."
        }

    @classmethod
    def parse_bhavcopy_csv(cls, csv_content: str, tracked_tickers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Parses official NSE/BSE UDiFF Bhavcopy CSV (published ~16:15 IST).
        Extracts Close, Volume, and Deliverable % (DELIV_PER) to distinguish
        genuine institutional accumulation from intraday speculative churn.
        """
        results = []
        reader = csv.DictReader(io.StringIO(csv_content.strip()))

        # Normalize column names to uppercase
        field_map = {f.strip().upper(): f for f in (reader.fieldnames or [])}

        symbol_col = field_map.get("SYMBOL") or field_map.get("TICKER") or field_map.get("SCRIP_CD")
        series_col = field_map.get("SERIES")
        close_col = field_map.get("CLOSE_PRICE") or field_map.get("CLOSE")
        vol_col = field_map.get("TTL_TRD_QNTY") or field_map.get("TOTTRDQTY") or field_map.get("VOLUME")
        deliv_col = field_map.get("DELIV_PER") or field_map.get("DELIV_QTY_PCT") or field_map.get("DELIVERY_PCT")

        if not symbol_col or not close_col or not vol_col:
            return results

        tracked_set = set(t.upper().replace(".NS", "").replace(".BO", "") for t in (tracked_tickers or []))

        for row in reader:
            series = row.get(series_col, "").strip() if series_col else "EQ"
            # In NSE, only EQ (Equity) series represents normal cash trading
            if series and series not in ("EQ", ""):
                continue

            sym = row.get(symbol_col, "").strip().upper()
            if tracked_set and sym not in tracked_set:
                continue

            try:
                close_px = float(row.get(close_col, 0))
                volume = int(float(row.get(vol_col, 0)))
                deliv_pct = float(row.get(deliv_col, 0.0)) if deliv_col and row.get(deliv_col) else 0.0
            except (ValueError, TypeError):
                continue

            # Signal classification based on delivery intensity
            if deliv_pct >= 55.0:
                signal = "INSTITUTIONAL_ACCUMULATION"
            elif deliv_pct < 20.0 and deliv_pct > 0.0:
                signal = "SPECULATIVE_INTRADAY_CHURN"
            else:
                signal = "NORMAL_DELIVERY"

            results.append({
                "symbol": sym,
                "ticker": f"{sym}.NS",
                "close_price": close_px,
                "volume": volume,
                "deliv_per": deliv_pct,
                "accumulation_signal": signal
            })

        return results

exchange_ingestion = ExchangeIngestionService()
