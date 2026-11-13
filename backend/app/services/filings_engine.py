"""
Filings Engine & SEBI LODR 17-Category Classifier (P-01, P-02, P-03)
Publishes the full 17 SEBI LODR Schedule III categories, role-aware KMP classifier,
cross-exchange (BSE/NSE) de-duplication, and windowed digest filtering.
"""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from app.db.database import get_db

# 17 Standard SEBI LODR Schedule III Categories
SEBI_LODR_CATEGORIES = [
    "financial_results",        # 1. Audited/Unaudited Quarterly and Annual Results
    "management_change",       # 2. Resignation/Appointment of KMP (MD, CEO, CFO, WTD)
    "mergers_acquisitions",    # 3. Mergers, Demergers, Acquisitions, JVs, Slump Sales
    "capex_expansion",         # 4. New Plants, Capacity Expansion, Commercial Production
    "litigation_regulatory",   # 5. Tax Demands, Penalties, NCLT, Search & Seizures
    "fund_raise",              # 6. Rights Issue, QIP, Preferential Allotment, NCDs, CP
    "credit_rating",           # 7. Credit Rating Revisions, Upgrades, Downgrades
    "dividend_distribution",   # 8. Dividend Declarations, Special Dividends, Record Dates
    "bonus_split",             # 9. Bonus Shares, Stock Splits, Sub-divisions
    "concall_presentation",    # 10. Earnings Call Audio, Transcripts, Investor Decks
    "investor_meetings",       # 11. Institutional Investor & Analyst Meet Schedules
    "esop_allotments",         # 12. Employee Stock Option Allotments
    "share_certificates",      # 13. Loss of Share Certificates, Duplicate Share Issues
    "compliance_certificates", # 14. Reg 74(5) Demat, Reg 40(9) Secretarial Certificates
    "shareholding_pattern",    # 15. Quarterly Shareholding, Promoter Pledges/Revocations
    "board_reconstitution",    # 16. Independent Director Additions, Committee Changes
    "general_announcements"    # 17. Press Releases, Brand Launches, Other Material Contracts
]

ROUTINE_CATEGORIES = {
    "esop_allotments",
    "share_certificates",
    "compliance_certificates",
    "shareholding_pattern",
    "investor_meetings",
    "concall_presentation"
}

class FilingsEngine:
    @staticmethod
    def classify_management_role(text: str) -> Dict[str, Any]:
        """
        Role-aware classifier (P-03):
        Distinguishes Key Managerial Personnel (KMP) from secretarial or non-KMP roles.
        """
        lower = text.lower()

        # Tier 1: Core C-Suite / KMP (Score 9-10)
        cfo_match = bool(re.search(r"\b(cfo|chief financial officer|finance head|director finance)\b", lower))
        ceo_md_match = bool(re.search(r"\b(ceo|chief executive officer|managing director|md & ceo|whole[- ]time director|wtd|executive director)\b", lower))
        coo_match = bool(re.search(r"\b(coo|chief operating officer|president)\b", lower))

        if ceo_md_match:
            return {"role_tier": "KMP_TIER_1", "role_title": "CEO/MD", "materiality_score": 10}
        if cfo_match:
            return {"role_tier": "KMP_TIER_1", "role_title": "CFO", "materiality_score": 9}
        if coo_match:
            return {"role_tier": "KMP_TIER_1", "role_title": "COO/President", "materiality_score": 9}

        # Tier 2: Governance & Compliance (Score 7-8)
        is_cs = bool(re.search(r"\b(company secretary|compliance officer|secretarial auditor)\b", lower))
        is_independent_dir = bool(re.search(r"\b(independent director|audit committee chairman|nominee director)\b", lower))

        if is_cs:
            return {"role_tier": "GOVERNANCE_TIER_2", "role_title": "Company Secretary / Compliance Officer", "materiality_score": 7}
        if is_independent_dir:
            return {"role_tier": "GOVERNANCE_TIER_2", "role_title": "Independent Director", "materiality_score": 7}

        # Tier 3: Operational / Senior Management (Score 5-6)
        return {"role_tier": "OPERATIONAL_TIER_3", "role_title": "Senior Management", "materiality_score": 6}

    @staticmethod
    def classify_announcement(title: str, description: str) -> Dict[str, Any]:
        """
        Classifies an announcement into one of the 17 SEBI LODR Schedule III categories
        and assigns a deterministic Materiality Score (1 to 10) (P-01, P-03).
        - 9-10: CRITICAL
        - 8: HIGH
        - 4-7: MEDIUM / COLLAPSIBLE
        - 1-3: LOW / ROUTINE
        """
        combined = f"{title} {description}".lower()

        # 1. Financial Results / Board Meeting
        if "board meeting" in combined and ("results" in combined or "financial" in combined):
            return {"category": "financial_results", "is_material": False, "materiality_score": 6, "severity": "MEDIUM"}
        if any(w in combined for w in ["financial results", "un-audited results", "audited results", "quarterly results", "half year results"]):
            score = 10 if "results" in title.lower() else 7
            return {"category": "financial_results", "is_material": score >= 8, "materiality_score": score, "severity": "CRITICAL" if score >= 9 else "HIGH"}

        # 2. Management Change (Role-Aware P-03)
        if any(w in combined for w in ["resignation of", "appointment of", "stepping down", "superannuation", "cessation"]):
            role_eval = FilingsEngine.classify_management_role(combined)
            score = role_eval["materiality_score"]
            return {
                "category": "management_change",
                "is_material": score >= 8,
                "materiality_score": score,
                "role_details": role_eval,
                "severity": "CRITICAL" if score >= 9 else "HIGH"
            }

        # 3. Mergers & Acquisitions
        if any(w in combined for w in ["acquisition", "merger", "demerger", "joint venture", "jv with", "slump sale", "stake sale", "divestment"]):
            return {"category": "mergers_acquisitions", "is_material": True, "materiality_score": 9, "severity": "CRITICAL"}

        # 4. Capex & Capacity Expansion
        if any(w in combined for w in ["capex", "capacity expansion", "commercial production", "new manufacturing facility", "greenfield", "brownfield", "groundbreaking"]):
            return {"category": "capex_expansion", "is_material": True, "materiality_score": 8, "severity": "HIGH"}

        # 5. Litigation & Regulatory Actions
        if any(w in combined for w in ["tax demand", "penalty", "show cause notice", "nclt", "cbi", "ed search", "sebi order", "gst investigation", "litigation"]):
            return {"category": "litigation_regulatory", "is_material": True, "materiality_score": 8, "severity": "HIGH"}

        # 6. Fund Raise
        if any(w in combined for w in ["rights issue", "qip", "preferential allotment", "commercial paper", "ncd", "debentures", "qualified institutional placement"]):
            return {"category": "fund_raise", "is_material": False, "materiality_score": 6, "severity": "MEDIUM"}

        # 7. Credit Rating
        if any(w in combined for w in ["crisil", "icra", "care ratings", "india ratings", "credit rating upgrade", "credit rating downgrade", "reaffirmation"]):
            return {"category": "credit_rating", "is_material": False, "materiality_score": 5, "severity": "MEDIUM"}

        # 8. Dividend
        if "dividend" in combined:
            return {"category": "dividend_distribution", "is_material": False, "materiality_score": 6, "severity": "MEDIUM"}

        # 9. Bonus / Stock Split
        if any(w in combined for w in ["bonus issue", "stock split", "sub-division of shares", "face value"]):
            return {"category": "bonus_split", "is_material": False, "materiality_score": 6, "severity": "MEDIUM"}

        # 10. Concall & Audio Recording
        if any(w in combined for w in ["concall transcript", "audio recording", "investor presentation", "earnings call"]):
            return {"category": "concall_presentation", "is_material": False, "materiality_score": 4, "severity": "MEDIUM"}

        # 11. Investor & Analyst Meetings
        if any(w in combined for w in ["investor meet", "analyst meet", "schedule of conference"]):
            return {"category": "investor_meetings", "is_material": False, "materiality_score": 3, "severity": "LOW"}

        # 12. ESOP Allotment
        if any(w in combined for w in ["allotment of shares under esop", "esop scheme", "exercise of stock options", "under esop"]):
            return {"category": "esop_allotments", "is_material": False, "materiality_score": 2, "severity": "LOW"}

        # 13. Loss of Share Certificates
        if any(w in combined for w in ["loss of share", "duplicate share certificate", "letter of confirmation"]):
            return {"category": "share_certificates", "is_material": False, "materiality_score": 1, "severity": "LOW"}

        # 14. Compliance Certificates
        if any(w in combined for w in ["reg. 74(5)", "dematerialization", "reg. 40(9)", "secretarial audit", "compliance certificate"]):
            return {"category": "compliance_certificates", "is_material": False, "materiality_score": 1, "severity": "LOW"}

        # 15. Shareholding Pattern
        if any(w in combined for w in ["shareholding pattern", "promoter pledge", "revocation of pledge"]):
            return {"category": "shareholding_pattern", "is_material": False, "materiality_score": 4, "severity": "MEDIUM"}

        # 16. Board Reconstitution
        if any(w in combined for w in ["reconstitution of committee", "independent director appointment"]):
            return {"category": "board_reconstitution", "is_material": False, "materiality_score": 5, "severity": "MEDIUM"}

        # 17. General Announcements
        return {"category": "general_announcements", "is_material": False, "materiality_score": 4, "severity": "MEDIUM"}

    @staticmethod
    def deduplicate_filings(filings: List[Dict[str, Any]], window_hours: int = 3) -> List[Dict[str, Any]]:
        """
        De-duplicates cross-exchange announcements between BSE and NSE (P-02).
        If the same corporate disclosure is filed on both exchanges within window_hours,
        merges them into a single canonical event with exchanges: ['BSE', 'NSE'].
        """
        deduped = []
        seen_keys = {}

        for f in filings:
            isin = f.get("isin", "")
            title_norm = re.sub(r"[^a-zA-Z0-9]", "", f.get("title", "").lower()[:40])
            category = f.get("category", "")

            # Parsing timestamp for clustering
            try:
                filing_dt = datetime.fromisoformat(f.get("filing_time", "").replace("Z", ""))
            except Exception:
                filing_dt = datetime.now()

            matched = False
            for key, existing in seen_keys.items():
                e_isin, e_title, e_cat = key
                if e_isin == isin and (e_title in title_norm or title_norm in e_title) and e_cat == category:
                    time_diff = abs((filing_dt - existing["dt"]).total_seconds()) / 3600.0
                    if time_diff <= window_hours:
                        matched = True
                        # Merge exchange records
                        if "exchanges" not in existing["item"]:
                            existing["item"]["exchanges"] = ["NSE"]
                        if "BSE" not in existing["item"]["exchanges"]:
                            existing["item"]["exchanges"].append("BSE")
                        break

            if not matched:
                item_copy = dict(f)
                if "exchanges" not in item_copy:
                    item_copy["exchanges"] = ["NSE"]
                seen_keys[(isin, title_norm, category)] = {"dt": filing_dt, "item": item_copy}
                deduped.append(item_copy)

        return deduped

    @staticmethod
    def get_windowed_digest(hours: int = 24, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves filings within the specified time window (24h, 7d/168h, 30d/720h).
        Separates high-materiality filings (score >= 8) from collapsed routine paperwork.
        Applies de-duplication across exchanges (P-02).
        """
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        with get_db() as conn:
            cursor = conn.cursor()
            query = """
            SELECT a.id, a.isin, a.ticker, c.name as company_name, a.category, a.title, a.description,
                   a.filing_time, a.materiality_score, a.content_hash, a.financial_basis,
                   a.headline_metrics, a.executive_profile, a.network_connection
            FROM announcements a
            JOIN companies c ON a.isin = c.isin
            WHERE a.filing_time >= ?
            """
            params: List[Any] = [cutoff_time]

            if category_filter and category_filter != "all":
                query += " AND a.category = ?"
                params.append(category_filter)

            query += " ORDER BY a.materiality_score DESC, a.filing_time DESC;"
            cursor.execute(query, params)
            rows = cursor.fetchall()

        raw_filings = []
        for r in rows:
            raw_filings.append({
                "id": r["id"],
                "isin": r["isin"],
                "ticker": r["ticker"],
                "company_name": r["company_name"],
                "category": r["category"],
                "title": r["title"],
                "description": r["description"],
                "filing_time": r["filing_time"],
                "materiality_score": r["materiality_score"],
                "is_material": r["materiality_score"] >= 8,
                "content_hash": r["content_hash"],
                "financial_basis": r["financial_basis"],
                "headline_metrics": json.loads(r["headline_metrics"]) if r["headline_metrics"] else None,
                "executive_profile": json.loads(r["executive_profile"]) if r["executive_profile"] else None,
                "network_connection": json.loads(r["network_connection"]) if r["network_connection"] else None,
            })

        # Apply Cross-Exchange De-duplication (P-02)
        deduped = FilingsEngine.deduplicate_filings(raw_filings)

        material_filings = [f for f in deduped if f["materiality_score"] >= 8]
        routine_filings = [f for f in deduped if f["materiality_score"] < 8]

        return {
            "window_hours": hours,
            "total_count": len(deduped),
            "material_count": len(material_filings),
            "routine_count": len(routine_filings),
            "material_filings": material_filings,
            "routine_filings": routine_filings
        }
