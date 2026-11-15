# Covering Note & Submission Document

**To:** assessment@enam.com  
**Subject:** IIT Kanpur – Founding AI Engineer - 2027  
**Candidate:** Anirudh (`anirudh802` / `basalt802@gmail.com`)  
**Product:** FINN — Financial Investment Agent (PWA)  
**Live Deployed App (HTTPS):** [https://finn-frontend-lac.vercel.app](https://finn-frontend-lac.vercel.app)  
**GitHub Repository:** [https://github.com/anirudh802/ENAM-task](https://github.com/anirudh802/ENAM-task)  

---

## What Was Built

FINN is a mobile-first, installable Progressive Web Application (PWA) engineered specifically for high-conviction public-market investors at ENAM Holdings. It bridges real-time exchange filings, market technicals, primary-source disclosures, and the investor’s latent personal network into a single, high-density workflow:

1. **Pulse (Proactive Windowed Push):**
   - Windowed digest (24h, 7d, 30d) across the investor's confidential portfolio (`tenant_holdings`).
   - Categorizes announcements into the **17 standard SEBI LODR Schedule III categories** with deterministic materiality scores (1 to 10).
   - De-duplicates cross-exchange corporate announcements across BSE and NSE within 3-hour windows.
   - Intelligently collapses routine compliance paperwork (ESOP allotments, Reg 74 certificates, secretarial filings) to eradicate noise.
   - Pinned critical cards for material events (e.g., sudden CXO resignation, 4.8x volume explosion) with direct outreach actions.
   - **Corporate Action Price Adjustment:** Stock splits (e.g., 1:5 split) and bonus issues are adjusted automatically to prevent false -80% crash alerts.
   - **Volatility-Normalized Z-Scores:** Daily returns evaluated against a 60-day historical baseline ($\mu, \sigma$).
   - **Alert-Fatigue Controls:** 6-hour duplicate cooldowns and a daily cap (max 3 alerts/ticker/day).
2. **DeepDive (Grounded Primary Research):**
   - Strictly grounded in primary sources (audited annual reports, quarterly concall transcripts, exchange filings). No broker notes, no secondary news.
   - **Faithfulness Verification:** Extracted claims and quotes are validated against stored primary text using `CitationVerifier` on a golden set of 3 primary claims. Hallucinated quotes fail verification and are rejected.
   - **Guidance Schema v2 (Promised vs. Delivered):** Multi-quarter tracking comparing management forward guidance against audited delivered actuals with deterministic status rules (`RANGE`, `NUMERIC`, `QUALITATIVE` -> `BEAT`, `MET`, `MISSED`).
   - **Bank & NBFC Specialized Template:** Dedicated financial metrics for BFSI (Net Interest Income, Net Interest Margin in bps, Gross NPA %, Net NPA %, Provision Coverage Ratio, Liquidity Coverage Ratio).
   - **Cash Quality Evaluation:** Operating cash flow vs. accounting PAT ($\text{CFO} / \text{PAT}$ cash conversion ratio), free cash flow, and working capital cycles.
   - **Cold-Ticker Coverage Assessment:** Ingestion pipeline reporting document coverage percentage before diligence runs (e.g., `25% Coverage • 0 of 4 transcripts, annual report found` on unindexed tickers like `MARUTI.NS`).
   - **Honest Empty State:** Returns explicit `"No primary filings indexed yet"` and `"No guidance extracted for this company"` rather than synthesized placeholders.
   - **SEBI Research Analyst Notice:** Institutional disclaimer displayed prominently on generated diligence.
3. **Nexus (Network Intelligence Layer):**
   - Integrates the investor's private network directly into market events with tenant boundary isolation.
   - **Documented Relevance Score Formula:**
     $$\text{Relevance} = (\text{Tenure} \times 0.25) + (\text{Seniority} \times 0.25) + (\text{Relationship Strength} \times 0.25) + (\text{Event Materiality} \times 0.25) + \text{Starred Boost (+2.0)}$$
   - **"Who to Call":** Surfaces direct former employees, competitor contacts, and supplier contacts with targeted scuttlebutt questions.
   - **SEBI PIT Guardrails:** Distinguishes current employees (flagged with `CURRENT_INSIDER` caution banners under SEBI PIT Regulations) from former employees (`FORMER_EMPLOYEE_SAFE`). Firm-wide restricted list embargoes (e.g., Dixon Technologies embargoed until 18 Nov 2026 due to active mandates) actively disable calling buttons across Ask, Nexus, and Who-to-Call.
   - **Second-Degree Reach:** Maps mutual connectors (e.g. IIT Kanpur alumni networks) to target executives with warm introduction asks.
4. **Interaction Model: Omnipresent Ask Intelligence:**
   - Omnipresent command bar docked across all tabs (`Pulse`, `Radar`, `DeepDive`, `Nexus`) answering who/what questions with real FINN cards.
   - Horizontal-scrolling quick prompt chips (`👥 Who knows Dixon order flow?`, `📊 Trent promised vs delivered`, `👥 Who do I know at Kaynes?`, `📋 Dixon Q2 results`, `⚡ CDSL volume anomaly`).
   - Interactive slide-up drawer displaying intent badges (`NETWORK INTEL`, `GUIDANCE TRACK RECORD`, `RESULTS DISCLOSURE`, `ANOMALY DETECTION`), institutional verdict summaries, embedded FINN cards (with SEBI compliance locks or one-click call triggers), and deep-navigation links.
   - Company-grouped anomaly cards in Radar (e.g. CDSL volume surge 4.2x + price breakout +8.4% merged into one unified card).
   - 16-company mock portfolio strip in DeepDive with visible violet network indicators on tickers with active network ties (`DIXON`, `TRENT`, `KAYNES`, `DEEPAKNTR`).
5. **Beacon (Native Web Push Notifications):**
   - Uses the Web Push protocol (VAPID) and Service Workers to dispatch OS-level system notifications on physical phones and desktops when critical anomalies occur in the background.
   - Header notification bell displays active subscription state.
6. **Ergonomics & Themes:**
   - Full support for **Dark Mode** and **Light Mode** with zero-transition rendering.
   - Usable at 375px mobile viewport without sideways scroll.

---

## "Live vs. Seeded" Data Disclosure

To ensure complete transparency regarding data origins:
- **Live Market Data:** End-of-Day pricing, 60-day moving averages, and volume multiples are pulled live via `yfinance`.
- **Seeded Primary Disclosures:** Corporate announcements, quarterly results, and concall transcripts for tracked portfolio tickers are seeded from primary exchange filings (labeled in the UI as *"Seeded demo filing"* where demonstration data is used).
- **Synthetic Network Graph:** Contact profiles and relationships are synthetic mock data designed around DPDP and SEBI PIT principles with strict multi-tenant isolation.

---

## Feature Implementation Status & Demonstration

| Feature | Status | Verification & Evidence |
| :--- | :--- | :--- |
| **SEBI LODR Classification (17 Categories)** | ✅ Fully Implemented | Unit tested in `test_filings_classification.py` + Live in Pulse view |
| **Corporate Action Split Adjustment** | ✅ Fully Implemented | Unit tested in `test_anomaly_hardening.py` |
| **Promised vs Delivered (Guidance v2)** | ✅ Fully Implemented | Evaluated in `test_metrics_calculator.py` + Live in DeepDive |
| **Dixon Restricted List Compliance Embargo** | ✅ Fully Implemented | Re-screenshotted in Ask, Nexus, and Who-to-Call modal |
| **Cold-Ticker Coverage % Readout** | ✅ Fully Implemented | Tested on `MARUTI.NS` (25% coverage displayed in UI) |
| **Voice Search (SpeechRecognition)** | ⚙️ Implemented, not shown | Web Speech API integrated in `AskBar.tsx` (browser-dependent) |
| **Contact CSV Import & Staleness** | ⚙️ Implemented, not shown | Backend engine in `network_engine.py` (tested in `test_nexus_intelligence.py`) |
| **DPDP Export & Erasure** | ⚙️ Implemented, not shown | Endpoints in `network_engine.py` (tested in `test_nexus_intelligence.py`) |
| **Scuttlebutt Call Audit Log** | ⚙️ Implemented, not shown | Backend persistence in `network_engine.py` (tested in `test_nexus_intelligence.py`) |
| **OS Push Notification Trigger** | ⚙️ Implemented, not shown | Active green bell in UI; VAPID outbox pipeline in `push_service.py` |

---

## Verification & Test Results

The backend test suite contains **72 automated unit and integration tests** achieving a **100% pass rate in 8.74 seconds**:

```
tests/test_anomaly_hardening.py        5 passed (100%)
tests/test_api.py                      7 passed (100%)
tests/test_ask_service.py              7 passed (100%)  <-- Phase 4 Ask Engine & Zero-Guidance Guard
tests/test_citation_verifier.py        4 passed (100%)
tests/test_cold_ticker_research.py     3 passed (100%)  <-- Cold Ticker Generalization
tests/test_document_pipeline.py        4 passed (100%)
tests/test_filings_classification.py   4 passed (100%)
tests/test_financial_units.py          2 passed (100%)
tests/test_golden_claims.py            3 passed (100%)  <-- Phase 1 Exit Gate
tests/test_metrics_calculator.py       7 passed (100%)
tests/test_nexus_intelligence.py       6 passed (100%)  <-- Phase 3 Exit Gate & Compliance Embargo
tests/test_production_desk.py          9 passed (100%)  <-- Direct Ingestion, XBRL, Outbox, Backup
tests/test_services.py                 7 passed (100%)
tests/test_tenant_isolation.py         2 passed (100%)  <-- Phase 0 Exit Gate
tests/test_user_alert_state.py         1 passed (100%)
============================= 72 passed in 8.74s ==============================
```

Frontend production build verification:
```bash
cd frontend && npm run build
# ✓ built in 1.83s (0 errors, 0 warnings)
```

---

## Key Decisions & Engineering Trade-offs

1. **EOD Market Data vs. Tick-by-Tick Streaming:**  
   We deliberately used End-of-Day (EOD) closing prices and volume multiples (`yfinance` + 60-day historical baseline) rather than maintaining paid WebSocket tick feeds. For high-conviction fundamental investors running 3–5 year horizons, intraday micro-tick oscillations generate alert fatigue; EOD volume multiples (e.g. 4.8x 20-day SMA) isolate genuine institutional positioning.
2. **Curated & Compliant CSV Graph Ingestion vs. Headless LinkedIn Scraping:**  
   LinkedIn strictly prohibits automated scraping under its Terms of Service and serves Cloudflare/CAPTCHA challenges. Rather than relying on fragile scrapers, we designed contact ingestion around SEBI PIT and DPDP principles with verified alumni/company bridges (and documented how production enterprise deployments connect to Affinity CRM or Microsoft Graph via authorized OAuth).
3. **SQLite WAL Single-Node Engine vs. Distributed Postgres + Neo4j:**  
   For a boutique high-conviction investment office managing 15–50 core portfolio companies and <10,000 professional contacts, SQLite in WAL mode combined with an in-memory `NetworkX` graph engine executes <5ms path traversals on the 20-node benchmark graph with zero operational overhead, no network serialization cost, and instant single-file encrypted tenant backups.
4. **Deep Single-Company Primary Grounding vs. Shallow Peer Comparison Grids:**  
   We prioritized exhaustive, citation-verified multi-quarter tracking (`Promised vs. Delivered` across 4 quarters with verbatim page/speaker citations) for individual companies over broad, superficial cross-sector comparison tables. In high-conviction investing, forensic depth on capital allocation beats broad surface-level metrics.

---

## Architectural Decision Records & System Specifications

All foundational architectural decisions and technical specifications are formally documented under `docs/`:
- [Production Desk Engineering Roadmap](docs/PRODUCTION_DESK_ROADMAP.md) *(Pragmatic zero-cost desk roadmap: Direct BSE/NSE feeds, XBRL parsing, delivery %, hardened SQLite WAL, outbox & SSE)*
- [Complete System Architecture Specification](docs/FINN_SYSTEM_ARCHITECTURE.md) *(Full-depth architectural breakdown across Backend, Frontend, SQLite WAL DB, and Deployment)*
- [ADR-001: PWA Mobile-First Architecture](docs/adr/ADR-001-pwa-mobile-first.md)
- [ADR-002: Centralized SQLite Store with WAL Mode](docs/adr/ADR-002-centralized-anomaly-store.md)
- [ADR-003: Tenant Privacy & Personal Network Graph Engine](docs/adr/ADR-003-tenant-privacy-graph.md)
- [ADR-004: Primary Source-of-Truth Policy](docs/adr/ADR-004-source-of-truth-policy.md)
- [ADR-005: Tenant Privacy & Encryption Architecture](docs/adr/ADR-005-tenant-privacy-encryption.md)
- [ADR-006: ISIN-Keyed Company Master](docs/adr/ADR-006-isin-company-master.md)
- [Deployment Specification & Budget](docs/DEPLOYMENT_SPEC.md)

---

## How to Run & Verify

```bash
# 1. Live Deployment
# Frontend: https://finn-frontend-lac.vercel.app

# 2. Local Development One-Line Launcher
./run.sh

# 3. Backend Test Suite (All 72 tests)
cd backend && ./venv/bin/pytest -v

# 4. Production Frontend Build
cd frontend && npm run build
```
