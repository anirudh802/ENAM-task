# FINN — AI Build History & Agent Trajectory Log

**Project:** FINN (Financial Intelligence & Network Navigator)  
**Candidate:** Anirudh (`anirudh802` / `basalt802@gmail.com`) — IIT Kanpur  
**Challenge:** ENAM Holdings — Founding AI Engineer Build Challenge (2027)  
**Build Environment:** Antigravity CLI Autonomous AI Agent (Google DeepMind)  
**Target Repository:** `git@github.com:anirudh802/ENAM-task.git`  
**Live PWA:** `https://finn-frontend-lac.vercel.app`  

---

## 1. Build Methodology & Agentic Workflow

FINN was engineered using test-driven, autonomous AI agent workflows structured around strict institutional constraints:
1. **Strict Primary-Source Grounding:** Absolute prohibition against hallucinated LLM arithmetic or web-scraped broker commentaries.
2. **Deterministic-First Routing:** Zero LLM involvement for financial math, SEBI LODR regex classification, volatility Z-scores, or corporate split adjustments.
3. **Multi-Tenant Privacy:** Separation of private investor personal networks from public market feeds.
4. **Institutional Ergonomics:** 375px mobile-first layout with high financial information density.

---

## 2. Chronological Sub-Phase Progression

### Phase 0: Groundwork, Multi-Tenant Database & ISIN Master
- **Objective:** Establish the unified SQLite WAL storage engine, tenant isolation, and canonical Indian ISIN company master.
- **Agent Actions:**
  - Designed 20-table SQLite schema with WAL pragma (`PRAGMA journal_mode=WAL;`, 64MB RAM page cache).
  - Seeded canonical portfolio (`RELIANCE.NS`, `TATAMOTORS.NS`, `DIXON.NS`, `TRENT.NS`, `KAYNES.NS`, `CDSL.NS`, `HDFCBANK.NS`, `DEEPAKNTR.NS`).
  - Implemented tenant isolation tests (`test_tenant_isolation.py`).
- **Outcome:** Clean passing tests for tenant portfolio holdings and network graphs.

### Phase 1: Proactive Push & Anomaly Detection Hardening
- **Objective:** Create the windowed digest (Pulse) and technical outlier detector (Radar).
- **Agent Actions:**
  - Implemented 17 SEBI LODR Schedule III category classifiers (`FilingsEngine`).
  - Added corporate action stock split adjustment (1:5 split handling) to prevent false -80% crash alerts.
  - Implemented 60-day volatility-normalized Z-score evaluation.
  - Added alert fatigue safeguards (6-hour duplicate cooldowns and 3 alert/ticker/day caps).
  - Created Web Push protocol integration (VAPID keys, service worker notifications).
- **Outcome:** All 5 anomaly hardening tests and 7 service tests passing.

### Phase 2: Grounded Diligence & Guidance Schema v2 ("Promised vs. Delivered")
- **Objective:** Deliver the primary-source research engine with multi-quarter forward guidance evaluation.
- **Agent Actions:**
  - Built `ResearchEngine` with `CitationVerifier` substring matching gate.
  - Implemented Guidance v2 schema evaluating `RANGE`, `NUMERIC`, and `QUALITATIVE` guidance as `BEAT`, `MET`, or `MISSED`.
  - Added specialized BFSI metrics (NIM in bps, Gross/Net NPA %, PCR, LCR) and $\text{CFO}/\text{PAT}$ cash conversion.
  - Added cold-ticker coverage percentage assessment before diligence execution.
- **Outcome:** 100% pass on golden claim verification and zero-hallucination tests.

### Phase 3: Nexus Intelligence Layer & Compliance Guardrails
- **Objective:** Connect the investor's latent network to market events while strictly obeying SEBI PIT rules.
- **Agent Actions:**
  - Built `NetworkEngine` using `NetworkX` graph traversals.
  - Implemented mathematical relevance formula:
    $$\text{Relevance} = (\text{Tenure} \times 0.25) + (\text{Seniority} \times 0.25) + (\text{Strength} \times 0.25) + (\text{Materiality} \times 0.25) + \text{Starred Boost (+2.0)}$$
  - Added SEBI PIT classification (`CURRENT_INSIDER` vs `FORMER_EMPLOYEE_SAFE`).
  - Implemented firm-wide restricted list enforcement (blocking outreach on active mandates, e.g. Dixon Technologies embargoed until 18 Nov 2026).
  - Added second-degree reach mapping (e.g. mutual IIT Kanpur alumni bridges).
- **Outcome:** Passed all 6 nexus intelligence tests and compliance assertion suites.

### Phase 4: Omnipresent Ask Intelligence & UI Refinement
- **Objective:** Surface an omnipresent command bar across all tabs and refine UI ergonomics.
- **Agent Actions:**
  - Created `AskBar` with quick prompt chips, voice trigger, and intent-routed slide-up drawer.
  - Refined action buttons into unified, sleek `<ActionButton />` components taking minimal vertical space.
  - Added accessible close buttons and improved text contrast meeting WCAG AA standards.
  - Automated headless Brave browser verification at 375px mobile viewport across dark and light modes.
- **Outcome:** Saved 40–80px of vertical height across all card variants, verified on headless browser screenshots.

### Phase 5: Pre-Submission Hardening & Compliance Refinement
- **Objective:** Fix copy slips, guard zero-guidance cases, enforce consistent compliance states, and prepare deployment.
- **Agent Actions:**
  - Decided firm restricted status for Dixon Technologies; updated Ask drawer, Nexus feed, and Who-to-Call modal to display disabled "Blocked" lock buttons.
  - Guarded 0/0 guidance case to display honest `"No guidance extracted for this company"` empty states.
  - Replaced overclaiming banners with institutional disclosures (*"Seeded demo filing"*, *"In your network"*, *"Scuttlebutt-safe questions"*).
  - Configured `frontend/vercel.json` and root `render.yaml` for instant cloud hosting.
  - Verified 72/72 backend tests passing in 8.74s and clean frontend build.

---

## 3. Test & Verification Artifacts Summary

- **Backend Pytest Suite:** 72 passed in 8.74 seconds (`pytest tests/ -v`).
- **Frontend Build:** `npm run build` completed in 1.83 seconds with 0 errors and 0 warnings.
- **Verification Visuals:** 375px mobile viewport screenshots captured using Brave CDP across Dark and Light themes under `screenshots/`.
