import os
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

EXPERT_FINANCIAL_SYSTEM_PROMPT = """You are FINN, an elite public-markets investment intelligence copilot at ENAM Holdings.
Your mission: Deliver dense, concise, quantified financial analysis for hedge fund portfolio managers.

STRICT GUARDRAILS:
1. NO AI SLOP: Zero conversational fluff, pleasantries, or generic advice.
2. PRIMARY GROUNDING ONLY: Analyze ONLY the provided primary documents (annual reports, concalls, exchange filings). NEVER cite secondary news, broker notes, or external web conjecture.
3. QUANTIFY EVERYTHING: Use exact numbers, basis points (bps), YoY/QoQ percentages, D/E ratios, and cash conversion multiples.
4. If a metric is not present in the primary documents, explicitly state: 'Not disclosed in primary filing'."""

class LLMRouter:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self.client = None

        if self.gemini_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.gemini_key)
                logger.info("Initialized Google GenAI client for FINN.")
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI client: {e}")

    def is_live_llm_available(self) -> bool:
        return self.client is not None

    def synthesize_research(self, ticker: str, company_name: str, primary_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Synthesizes research using Gemini 2.5 Flash if available.
        Returns parsed JSON or None if unavailable/failed.
        """
        if not self.client:
            return None

        prompt = f"""
{EXPERT_FINANCIAL_SYSTEM_PROMPT}

Analyze company: {company_name} ({ticker})
Primary Source Context:
{json.dumps(primary_context, indent=2)}

Generate a structured financial synthesis in strict JSON matching these keys:
{{
  "competitive_moat": "1-2 concise bullet-density lines on moat",
  "trajectory_summary": "1-2 lines on multi-year expansion/compression",
  "cash_quality_assessment": "1-2 lines analyzing CFO vs PAT and working capital",
  "bull_case": ["bullet 1 with numbers", "bullet 2 with numbers"],
  "bear_case": ["bullet 1 with numbers", "bullet 2 with numbers"]
}}
"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            if response.text:
                return json.loads(response.text)
        except Exception as e:
            logger.warning(f"Gemini LLM call failed, falling back to deterministic extraction: {e}")

        return None

llm_router = LLMRouter()
