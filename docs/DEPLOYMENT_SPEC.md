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

## 3. LLM Provider, Cost & Latency Budgets

| Task | Primary Model | Fallback | Latency Budget | Estimated Cost / Query |
| :--- | :--- | :--- | :--- | :--- |
| **Research Synthesis (DeepDive)** | Google Gemini 2.5 Flash | Deterministic expert template | $< 2.5$ seconds | $\approx \$0.0015$ / query |
| **Filing Materiality Scoring** | Regex + heuristic scoring | Lightweight prompt assist | $< 100$ ms | $\$0.00$ (Local CPU) |
| **Guidance Variance Math** | Deterministic Python Engine | N/A | $< 5$ ms | $\$0.00$ (Local CPU) |

**Secrets Handling:**
All API keys (`GEMINI_API_KEY`, VAPID keys) are loaded strictly via environment variables managed by `pydantic-settings`. Plaintext keys in Git or repository files are strictly prohibited.
