import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.db.database import get_db

class LLMCacheService:
    """
    Layer 1 Content-Addressed LLM Cache:
    Keyed by (doc_sha256, prompt_version).
    Guarantees immutable zero-cost re-inference across repeated queries on identical filings.
    """

    CURRENT_PROMPT_VERSION = "v2.0_grounded_primary"

    @classmethod
    def compute_sha256(cls, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    def get(cls, doc_sha256: str, prompt_ver: str = CURRENT_PROMPT_VERSION) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT output_json FROM llm_cache WHERE doc_sha256 = ? AND prompt_ver = ?",
                (doc_sha256, prompt_ver)
            )
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["output_json"])
                except Exception:
                    return None
        return None

    @classmethod
    def set(cls, doc_sha256: str, output: Dict[str, Any], model: str = "gemini-2.5-flash", prompt_ver: str = CURRENT_PROMPT_VERSION) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO llm_cache (doc_sha256, prompt_ver, output_json, model, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (
                doc_sha256,
                prompt_ver,
                json.dumps(output),
                model,
                datetime.now(timezone.utc).isoformat()
            ))

llm_cache = LLMCacheService()
