import os
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.llm_cache_service import llm_cache

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
        Synthesizes research using Layer 1 Content-Addressed LLM Cache or Gemini 2.5 Flash.
        Returns parsed JSON or None if unavailable/failed.
        """
        # 1. Check content-addressed cache (zero-cost re-inference)
        context_str = json.dumps(primary_context, sort_keys=True)
        doc_sha256 = llm_cache.compute_sha256(context_str)
        cached_result = llm_cache.get(doc_sha256)
        if cached_result:
            logger.info(f"LLM Cache Hit for {ticker} (doc_sha256: {doc_sha256[:10]}). Zero-cost response returned.")
            return cached_result

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
        models_to_try = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-2.5-flash"]
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                if response.text:
                    parsed = json.loads(response.text)
                    # Store in content-addressed cache
                    llm_cache.set(doc_sha256, parsed, model=model_name)
                    return parsed
            except Exception as e:
                logger.warning(f"Gemini LLM call failed on {model_name}: {e}")
                continue

        return None

llm_router = LLMRouter()
