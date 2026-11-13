import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.db.database import get_db
from app.models.schemas import AnnouncementCategory

MATERIAL_CATEGORIES = {"results", "M&A", "management_change", "fund_raise", "litigation", "capex"}
ROUTINE_CATEGORIES = {"unclassified", "postal_ballot", "agm_egm", "pledging"}

class FilingsEngine:
    @staticmethod
    def classify_announcement(title: str, description: str) -> Dict[str, Any]:
        """
        Rule-based classifier that assigns one of the 17 standard categories
        and computes a Materiality Score (1 to 10).
        """
        combined = f"{title} {description}".lower()

        # 1. Results
        if any(w in combined for w in ["financial results", "un-audited results", "audited results", "quarter ended", "half year ended", "board meeting to consider results"]):
            return {"category": "results", "is_material": True, "materiality_score": 10 if "results" in title.lower() else 7}

        # 2. Management Change
        if any(w in combined for w in ["resignation of", "appointment of", "chief financial officer", "chief executive officer", "managing director", "coo", "cfo", "key managerial personnel", "director resigned"]):
            return {"category": "management_change", "is_material": True, "materiality_score": 9}

        # 3. M&A
        if any(w in combined for w in ["acquisition", "merger", "demerger", "joint venture", "jv with", "slump sale", "stake purchase", "divestment"]):
            return {"category": "M&A", "is_material": True, "materiality_score": 9}

        # 4. Capex
        if any(w in combined for w in ["capex", "capacity expansion", "new plant", "manufacturing facility", "groundbreaking", "new unit", "sanand"]):
            return {"category": "capex", "is_material": True, "materiality_score": 8}

        # 5. Litigation
        if any(w in combined for w in ["lawsuit", "court", "nclt", "tax demand", "regulatory order", "penalty", "search and seizure", "it department", "investigation"]):
            return {"category": "litigation", "is_material": True, "materiality_score": 8}

        # 6. Fund Raise
        if any(w in combined for w in ["rights issue", "qip", "preferential allotment", "commercial paper", "ncd", "debentures", "buyback"]):
            return {"category": "fund_raise", "is_material": True, "materiality_score": 7}

        # 7. Credit Rating
        if any(w in combined for w in ["crisil", "icra", "care", "credit rating", "downgrade", "upgrade", "rating reaffirm"]):
            return {"category": "credit_rating", "is_material": True, "materiality_score": 6}

        # 8. Dividend & Bonus
        if "dividend" in combined:
            return {"category": "dividend", "is_material": True, "materiality_score": 6}
        if any(w in combined for w in ["bonus issue", "stock split", "sub-division"]):
            return {"category": "bonus_split", "is_material": True, "materiality_score": 6}

        # 9. Earnings Call
        if any(w in combined for w in ["earnings call", "concall transcript", "audio recording", "investor presentation"]):
            return {"category": "earnings_call", "is_material": False, "materiality_score": 4}

        # 10. Investor Meetings
        if any(w in combined for w in ["investor meet", "analyst meet", "conference"]):
            return {"category": "investor_meetings", "is_material": False, "materiality_score": 3}

        # 11. Routine / Low-relevance Paperwork (unclassified)
        if any(w in combined for w in ["esop", "stock option", "duplicate share", "reg. 74(5)", "compliance certificate", "loss of share", "secretarial"]):
            return {"category": "unclassified", "is_material": False, "materiality_score": 1}

        return {"category": "unclassified", "is_material": False, "materiality_score": 2}

    @staticmethod
    def get_windowed_digest(hours: int = 24, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves filings within the specified time window (24h, 7d/168h, 30d/720h).
        Separates high-materiality filings from collapsed routine paperwork.
        """
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        with get_db() as conn:
            cursor = conn.cursor()
            query = """
            SELECT a.id, a.ticker, c.name as company_name, a.category, a.title, a.description,
                   a.filing_time, a.is_material, a.materiality_score, a.headline_metrics,
                   a.executive_profile, a.network_connection
            FROM announcements a
            JOIN companies c ON a.ticker = c.ticker
            WHERE a.filing_time >= ?
            """
            params: List[Any] = [cutoff_time]

            if category_filter and category_filter != "all":
                query += " AND a.category = ?"
                params.append(category_filter)

            query += " ORDER BY a.materiality_score DESC, a.filing_time DESC;"
            cursor.execute(query, params)
            rows = cursor.fetchall()

        material_filings = []
        routine_filings = []

        for r in rows:
            item = {
                "id": r["id"],
                "ticker": r["ticker"],
                "company_name": r["company_name"],
                "category": r["category"],
                "title": r["title"],
                "description": r["description"],
                "filing_time": r["filing_time"],
                "is_material": bool(r["is_material"]),
                "materiality_score": r["materiality_score"],
                "headline_metrics": json.loads(r["headline_metrics"]) if r["headline_metrics"] else None,
                "executive_profile": json.loads(r["executive_profile"]) if r["executive_profile"] else None,
                "network_connection": json.loads(r["network_connection"]) if r["network_connection"] else None,
            }

            if r["category"] in ROUTINE_CATEGORIES or r["materiality_score"] <= 3:
                routine_filings.append(item)
            else:
                material_filings.append(item)

        return {
            "window_hours": hours,
            "total_count": len(rows),
            "material_count": len(material_filings),
            "routine_count": len(routine_filings),
            "material_filings": material_filings,
            "routine_filings": routine_filings
        }
