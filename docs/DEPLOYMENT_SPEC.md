# FINN — Deployment Specification & Resource Budgets

**Version:** 1.0.0  
**Target:** ENAM Holdings Private Cloud / Containerized Edge  
**Date:** November 2026

---

## 1. Tracked Universe

| Tier | Count | Tickers / Selection | Update Cadence | Storage Policy |
| :--- | :--- | :--- | :--- | :--- |
| **Active Portfolio** | 18 | `RELIANCE.NS`, `TATAMOTORS.NS`, `DIXON.NS`, `TRENT.NS`, `KAYNES.NS`, `CDSL.NS`, `HDFCBANK.NS`, `DEEPAKNTR.NS`, `POLYCAB.NS`, `PERSISTENT.NS`, `SUNPHARMA.NS`, `LT.NS`, `TITAN.NS`, `KPITTECH.NS`, `ASTRAL.NS`, `PIIND.NS`, `SYNGENE.NS`, `CLEAN.NS` | Continuous background polling (5-min interval for filings; EOD at 16:00 IST for price/volume) | Permanent historical retention in SQLite WAL |
| **Core Watchlist** | 4 | `ZOMATO.NS`, `DIVISLAB.NS`, `HAL.NS`, `DMART.NS` | Same as portfolio | Permanent historical retention |
| **Broad Market (Any NSE)** | ~2,000 | Any valid NSE symbol | On-demand asynchronous cold-start ingestion (`D-08`) | Transient/cached with 30-day TTL |

---

## 2. Ingestion & Alert Latency Budgets

| Event Type | Target Latency | Ingestion Source | Evaluation Engine | Notification Channel |
| :--- | :--- | :--- | :--- | :--- |
| **Material Exchange Filings** (Results, M&A, Mgmt Change) | $< 3$ minutes | NSE/BSE corporate announcements feed | Rule-based regex + NLP materiality classifier (score 1–10) | Web Push (Beacon) + Top Pinned Card |
| **Price / Volume Outliers** | Post-Market (16:00 IST) | yfinance EOD / Exchange bhavcopy | Volatility-adjusted Z-score & volume multiple vs 20d SMA | Batched digest / Radar view |
| **Concall Transcript Guidance** | $< 4$ hours post-call | IR disclosure portals | Deterministic metrics calculator + Citation verifier | DeepDive Promised vs Delivered table |

---

## 3. LLM Provider, Cost & Latency Budgets (3-Tier Routing Architecture)

FINN enforces a strict **3-tier cost-optimized model routing architecture** to deliver sub-second responses, zero arithmetic hallucinations, and hedge-fund grade research at minimal compute cost:

| Tier | Role / Pipeline Stage | Model / Engine | Latency Budget | Estimated Cost / Unit | Operational Guardrail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 0** | **Deterministic Local Engine** (Classification, Math, Verification) | Local Python / Regex / SQLite | $< 5$ ms | **$0.00** (Local CPU) | Zero LLM math. Handles SEBI LODR 17-category classification, corporate action split adjustments (1:5), 60-day volatility Z-scores, `MetricsCalculator` (YoY/QoQ %, bps, CFO/PAT), and `CitationVerifier` substring matching. |
| **Tier 1** | **High-Throughput Bulk Extraction** (Guidance & Quote Parsing) | **Gemini 2.5 Flash** | $< 1.2$ s | **~$0.0004** / doc | High-throughput parsing of structured management guidance claims and verbatim quotes from dense 20+ page concall transcripts. |
| **Tier 2** | **High-Reasoning Synthesis** (DeepDive & Thesis Synthesis) | **Gemini 2.5 Pro** | $< 2.5$ s | **~$0.0035** / query | Complex multi-quarter `Narrative vs. Numbers` divergence synthesis, capital allocation evaluation, and Bull/Bear thesis construction. **Gated by `CitationVerifier` with deterministic fallback** if ungrounded. |

### Secrets & Security Handling
All sensitive credentials (`GEMINI_API_KEY`, VAPID public/private keypairs) are managed strictly via environment variables parsed by `pydantic-settings`. Direct hardcoding of plaintext API tokens or secrets in version control is strictly prohibited by pre-commit hooks and CI security scanners.
