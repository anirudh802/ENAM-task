# Backend AGENTS.md — FINN Backend Engine

## Role & Responsibilities
The `backend/` directory houses the FastAPI application responsible for:
1. Ingesting EOD market data (via `yfinance` with fallback caching).
2. Classifying exchange announcements across the 17 standard categories and computing materiality scores.
3. Centralized SQLite database management (WAL mode) for events, anomalies, and user threshold preferences.
4. Background anomaly detection pipeline (statistical $Z$-scores, volume multiples $>2\times$, price shocks).
5. Web Push notification dispatcher (VAPID) for native device alerts.
6. `NetworkX` graph traversal for 1st-degree/2nd-degree paths, expertise clustering, and recent development summaries.
7. Hybrid LLM router supporting Gemini 2.5 with deterministic fallback templates.

## Architecture & Directory Structure
```
backend/
├── app/
│   ├── api/             # FastAPI REST routes (push, pull, network, notifications, preferences)
│   ├── core/            # Config, security, VAPID key management
│   ├── db/              # SQLite database connection (WAL mode) and schema migrations
│   ├── models/          # Pydantic v2 schemas and data transfer objects
│   ├── services/        # Anomaly detector, market data, filing classifier, graph engine, LLM router
│   ├── data/            # Seed datasets and database initialization scripts
│   └── main.py          # FastAPI app entry point with CORS and error handlers
├── tests/               # Pytest suite for services, calculators, and API routes
├── requirements.txt     # Python dependencies
└── AGENTS.md            # Backend agent instructions
```

## Discrete Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed data
python -m app.data.seed_data

# Run dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run automated tests
pytest tests/ -v
```

## Guardrails & Forbidden Practices
1. **No External Network Calls During Offline Tests:** Tests must run against mocked or seed data without failing if yfinance or an external API is down.
2. **Zero Secondary Noise in Pull:** Pull research routes must only query primary disclosures. Do not pull news articles or broker reports into the model context.
3. **Database Concurrency:** Always use SQLite WAL mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`) to prevent database lock contention between background workers and API readers.
4. **No Plaintext Secrets:** Never hardcode VAPID private keys or LLM API keys in code; always pull from `.env` via `pydantic-settings`.

## SEBI LODR Schedule III 17-Category Filing Rubric (P-01)
Exchange filings are classified into 17 standard SEBI Listing Regulations categories with deterministic materiality scores (1-10):

| Category | Description | Materiality Score | Severity |
|---|---|---|---|
| `financial_results` | Audited/Unaudited quarterly & annual results | 10 (Results) / 6 (Board meet) | CRITICAL / MEDIUM |
| `management_change` | Resignation/Appointment of KMP (MD, CEO, CFO, WTD) | 9-10 (KMP) / 7 (CS/Dir) | CRITICAL / HIGH |
| `mergers_acquisitions` | Mergers, Demergers, Acquisitions, JVs, Slump Sales | 9 | CRITICAL |
| `capex_expansion` | Capacity additions, new plant/unit commercial production | 8 | HIGH |
| `litigation_regulatory`| Regulatory enforcement, tax demands, NCLT, penalties | 8 | HIGH |
| `fund_raise` | Rights issues, QIP, preferential allotment, NCDs, CP | 6 | MEDIUM |
| `credit_rating` | Revisions/reaffirmations by CRISIL, ICRA, CARE | 5 | MEDIUM |
| `dividend_distribution`| Dividend declarations, special dividends, record dates | 6 | MEDIUM |
| `bonus_split` | Bonus shares, stock splits, sub-divisions | 6 | MEDIUM |
| `concall_presentation` | Investor conference call transcripts, investor decks | 4 | MEDIUM |
| `investor_meetings` | Intimation of institutional investor meet schedules | 3 | LOW |
| `esop_allotments` | Routine ESOP exercises and equity allotments | 2 | LOW |
| `share_certificates` | Duplicate share certificate intimations, lost certificates | 1 | LOW |
| `compliance_certificates`| Reg 74(5) Demat, Reg 40(9) Secretarial certificates | 1 | LOW |
| `shareholding_pattern`| Quarterly shareholding patterns, promoter pledge disclosures | 4 | MEDIUM |
| `board_reconstitution`| Independent director appointments/retirements, committee changes | 5 | MEDIUM |
| `general_announcements`| Press releases, brand launches, general material contracts | 4 | MEDIUM |

- **CRITICAL (Score 9-10):** Triggers immediate push notification & pinned card on top of feed.
- **HIGH (Score 8):** Displayed prominently in material digest section.
- **MEDIUM / LOW (Score 1-7):** Collapsed into routine paperwork section by default.

