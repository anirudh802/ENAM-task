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
4. **Beacon (Native Web Push Notifications):**
   - Uses the Web Push protocol (VAPID) and Service Workers to dispatch OS-level system notifications on physical phones and desktops when critical anomalies occur in the background.
   - **Privacy Mode:** User setting to mask ticker and figures on lock screens (`"Critical alert detected for your portfolio"`).
   - Automatic cleanup of expired (410 Gone) subscriptions.
5. **Ergonomics & Themes:**
   - Full support for **Dark Mode** and **Light Mode**.
   - Built-in toggleable Phone Simulator Frame for desktop reviewers and seamless full-screen mobile layout (usable at 375px viewport without sideways scroll).

---

## Verification & Test Results

The backend test suite contains **52 automated unit and integration tests** achieving a **100% pass rate**:

```
tests/test_anomaly_hardening.py        5 passed (100%)
tests/test_api.py                      7 passed (100%)
tests/test_citation_verifier.py        4 passed (100%)
tests/test_document_pipeline.py        4 passed (100%)
tests/test_filings_classification.py   4 passed (100%)
tests/test_financial_units.py          2 passed (100%)
tests/test_golden_claims.py            3 passed (100%)  <-- Phase 1 Exit Gate
tests/test_metrics_calculator.py       7 passed (100%)
tests/test_nexus_intelligence.py       6 passed (100%)  <-- Phase 3 Exit Gate
tests/test_services.py                 7 passed (100%)
tests/test_tenant_isolation.py         2 passed (100%)  <-- Phase 0 Exit Gate
tests/test_user_alert_state.py         1 passed (100%)
============================= 52 passed in 20.33s ==============================
```

---

## Architectural Decision Records (ADRs)

All foundational architectural decisions are formally documented under `docs/adr/`:
- [ADR-001: PWA Mobile-First Architecture](file:///home/runcandel/enam/docs/adr/ADR-001-pwa-mobile-first-architecture.md)
- [ADR-002: Centralized SQLite Store with WAL Mode](file:///home/runcandel/enam/docs/adr/ADR-002-centralized-sqlite-wal-store.md)
- [ADR-003: Grounded LLM Routing Policy](file:///home/runcandel/enam/docs/adr/ADR-003-grounded-llm-routing-policy.md)
- [ADR-004: Primary Source-of-Truth Policy](file:///home/runcandel/enam/docs/adr/ADR-004-source-of-truth-policy.md)
- [ADR-005: Tenant Privacy & Encryption Architecture](file:///home/runcandel/enam/docs/adr/ADR-005-tenant-privacy-encryption.md)
- [ADR-006: ISIN-Keyed Company Master](file:///home/runcandel/enam/docs/adr/ADR-006-isin-company-master.md)
- [Deployment Specification & Budget](file:///home/runcandel/enam/docs/DEPLOYMENT_SPEC.md)

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
