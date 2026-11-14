# Covering Note & Submission Document

**To:** assessment@enam.com  
**Subject:** IIT Kanpur – Founding AI Engineer - 2027  
**Candidate:** Anirudh (`anirudh802` / `basalt802@gmail.com`)  
**Product:** FINN — Financial Investment Agent (PWA)

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
   - Strictly grounded in primary sources (audited annual reports, quarterly concall transcripts, exchange filings). No broker notes, no secondary news slop.
   - **Golden-Set Faithfulness Verification:** Every extracted claim and quote is validated against stored primary text (`CitationVerifier`). Fake or hallucinated quotes fail verification and are dropped.
   - **Guidance Schema v2 (Promised vs. Delivered):** Multi-quarter tracking comparing management forward guidance against audited delivered actuals with deterministic status rules (`RANGE`, `NUMERIC`, `QUALITATIVE` -> `BEAT`, `MET`, `MISSED`).
   - **Bank & NBFC Specialized Template:** Dedicated financial metrics for BFSI (Net Interest Income, Net Interest Margin in bps, Gross NPA %, Net NPA %, Provision Coverage Ratio, Liquidity Coverage Ratio).
   - **Cash Quality Evaluation:** Operating cash flow vs. accounting PAT ($\text{CFO} / \text{PAT}$ cash conversion ratio), free cash flow, and working capital cycles.
   - **Cold-Ticker Coverage Assessment:** Ingestion pipeline reporting document coverage percentage before diligence runs.
   - **SEBI Research Analyst Notice:** Institutional disclaimer displayed prominently on generated diligence.
3. **Nexus (Network Intelligence Layer):**
   - Integrates the investor's private network directly into market events with tenant boundary isolation.
   - **Documented Relevance Score Formula:**
     $$\text{Relevance} = (\text{Tenure} \times 0.25) + (\text{Seniority} \times 0.25) + (\text{Relationship Strength} \times 0.25) + (\text{Event Materiality} \times 0.25) + \text{Starred Boost (+2.0)}$$
   - **"Who to Call":** Surfaces direct former employees, competitor contacts, and supplier contacts with targeted questions.
   - **SEBI MNPI Guardrails:** Distinguishes current employees (flagged with `CURRENT_INSIDER` caution banners under SEBI PIT Regulations) from former employees (`FORMER_EMPLOYEE_SAFE`). Restricted list checking blocks calling suggestions on active mandates.
   - **Scuttlebutt Audit Log:** Persists an audit trail of scuttlebutt calls certifying non-MNPI compliance.
   - **Contact Import & Staleness:** CSV/vCard contact import with automated staleness detection (> 180 days).
   - **DPDP Act Controls:** Data Portability export and Right to Erasure deletion.
   - **Second-Degree Reach:** Maps mutual connectors (e.g. IIT Kanpur alumni networks) to target executives with warm introduction asks.
4. **Interaction Model: Omnipresent Ask Intelligence (Phase 4):**
   - Omnipresent command bar docked across all tabs (`Pulse`, `Radar`, `DeepDive`, `Nexus`) answering who/what questions with real FINN cards.
   - Voice search trigger using the Web Speech API (`SpeechRecognition`) with visual audio pulse indicator and graceful fallback.
   - Horizontal-scrolling quick prompt chips (`👥 Who knows Dixon order flow?`, `📊 Trent promised vs delivered`, `👥 Who do I know at Kaynes?`, `📋 Dixon Q2 results`, `⚡ CDSL volume anomaly`).
   - Interactive slide-up drawer displaying intent badges (`NETWORK INTEL`, `GUIDANCE TRACK RECORD`, `RESULTS DISCLOSURE`, `ANOMALY DETECTION`), institutional verdict summaries, embedded FINN cards (with SEBI compliance locks or one-click call triggers), and deep-navigation links.
   - Company-grouped anomaly cards in Radar (e.g. CDSL volume surge 4.2x + price breakout +8.4% merged into one unified card).
   - 16-company mock portfolio strip in DeepDive with visible violet network indicators on tickers with active network ties (`DIXON`, `TRENT`, `KAYNES`, `DEEPAKNTR`).
   - Quarantined empty state for unindexed tickers (`Parse Quality < 0.60` / `Insufficient Coverage`).
5. **Beacon (Native Web Push Notifications):**
   - Uses the Web Push protocol (VAPID) and Service Workers to dispatch OS-level system notifications on physical phones and desktops when critical anomalies occur in the background.
   - **Privacy Mode:** User setting to mask ticker and figures on lock screens (`"Critical alert detected for your portfolio"`).
   - Automatic cleanup of expired (410 Gone) subscriptions.
6. **Ergonomics & Themes:**
   - Full support for **Dark Mode** and **Light Mode** with zero-transition rendering.
   - Built-in toggleable Phone Simulator Frame for desktop reviewers and seamless full-screen mobile layout (usable at 375px viewport without sideways scroll).

---

## Verification & Test Results

The backend test suite contains **69 automated unit and integration tests** achieving a **100% pass rate**:

```
tests/test_anomaly_hardening.py        5 passed (100%)
tests/test_api.py                      7 passed (100%)
tests/test_ask_service.py              5 passed (100%)  <-- Phase 4 Ask Engine
tests/test_citation_verifier.py        4 passed (100%)
tests/test_cold_ticker_research.py     3 passed (100%)  <-- Cold Ticker Generalization
tests/test_document_pipeline.py        4 passed (100%)
tests/test_filings_classification.py   4 passed (100%)
tests/test_financial_units.py          2 passed (100%)
tests/test_golden_claims.py            3 passed (100%)  <-- Phase 1 Exit Gate
tests/test_metrics_calculator.py       7 passed (100%)
tests/test_nexus_intelligence.py       6 passed (100%)  <-- Phase 3 Exit Gate
tests/test_production_desk.py          9 passed (100%)  <-- Direct Ingestion, XBRL, Outbox, Backup
tests/test_services.py                 7 passed (100%)
tests/test_tenant_isolation.py         2 passed (100%)  <-- Phase 0 Exit Gate
tests/test_user_alert_state.py         1 passed (100%)
============================= 69 passed in 4.31s ==============================
```

---

## Key Decisions, Trade-offs & What Was Deliberately Left Out

To maximize signal density and deliver institutional reliability within the challenge timeframe, several conscious engineering trade-offs were made:

1. **EOD Market Data vs. Tick-by-Tick Streaming:**  
   We deliberately used End-of-Day (EOD) closing prices and volume multiples (`yfinance` + 60-day historical baseline) rather than maintaining paid WebSocket tick feeds. For high-conviction fundamental investors running 3–5 year horizons, intraday micro-tick oscillations generate alert fatigue; EOD volume multiples (e.g. 4.8x 20-day SMA) isolate genuine institutional positioning.
2. **Curated & Compliant CSV Graph Ingestion vs. Headless LinkedIn Scraping:**  
   LinkedIn strictly prohibits automated scraping under its Terms of Service and aggressively serves Cloudflare/CAPTCHA challenges. Rather than relying on fragile, legally questionable scrapers, we built a SEBI/DPDP-compliant CSV/vCard contact ingestion engine with verified alumni/company bridges (and documented how production enterprise deployments connect to Affinity CRM or Microsoft Graph via authorized OAuth).
3. **SQLite WAL Single-Node Engine vs. Distributed Postgres + Neo4j:**  
   For a boutique high-conviction investment office managing 15–50 core portfolio companies and <10,000 professional contacts, SQLite in WAL mode combined with an in-memory `NetworkX` graph engine executes sub-5ms path traversals with zero operational overhead, no network serialization cost, and instant single-file encrypted tenant backups (`tenant_01.db`).
4. **Deep Single-Company Primary Grounding vs. Shallow Peer Comparison Grids:**  
   We prioritized exhaustive, citation-verified multi-quarter tracking (`Promised vs. Delivered` across 4 quarters with verbatim page/speaker citations) for individual companies over broad, superficial cross-sector comparison tables. In high-conviction investing, forensic depth on capital allocation beats broad surface-level metrics.

---

## Where We Would Take FINN Next (Production Roadmap)

1. **Automated BSE/NSE RSS & XBRL Poller + Table OCR:**  
   Direct socket connection to exchange disclosure feeds to ingest PDF/XBRL filings within 60 seconds of publication, coupled with `pdfplumber`/`marker` table extraction pipelines for balance sheet schedules.
2. **Passive Workspace Graph Sync (Zero-Effort Network Updates):**  
   Read-only integration with Google Workspace and Microsoft 365 (calendar invites and email headers) to continuously refresh contact interaction dates (`last_verified_at`) and uncover warm firm-wide introduction paths without requiring manual CSV uploads.
3. **Audio Earnings Call Ingestion & Tone Shift Detection:**  
   Streaming concall audio ingestion via Whisper / Gemini Multimodal to flag executive hesitation, evasive Q&A tone, and voice stress before official transcripts are released to the public.
4. **Cross-Portfolio Supply-Chain Contagion Alerts:**  
   Activating the `Nexus` supplier/customer dependency graph so that if a major vendor (e.g. `KAYNES.NS` or a display component supplier) reports factory downtime or capex deferral, an automatic portfolio impact advisory is dispatched to investors holding the OEM (`DIXON.NS`).

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
# One-line launcher (Starts backend on :8000 and frontend Vite dev on :5173)
./run.sh

# Run backend test suite
cd backend && ./venv/bin/pytest -v

# Run production frontend build
cd frontend && npm run build
```
