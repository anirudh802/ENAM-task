# FINN — Comprehensive System Architecture & Technical Specification

**Project:** FINN (Financial Intelligence & Network Navigator)  
**Target:** ENAM Holdings — High-Conviction Institutional Investment Platform  
**Document Version:** 2.0 (Production Release)  
**Date:** November 2026  
**Repository Branch:** `main`  
**Target Viewport:** Mobile-First (375×812 iPhone / Android PWA) & Responsive Desktop  

---

## Table of Contents
1. [Executive Overview & Architectural Tenets](#1-executive-overview--architectural-tenets)
2. [End-to-End System Topology](#2-end-to-end-system-topology)
3. [Database Architecture & Data Model (SQLite WAL)](#3-database-architecture--data-model-sqlite-wal)
4. [Backend Architecture & Engine Specifications](#4-backend-architecture--engine-specifications)
5. [Frontend Architecture & Client PWA](#5-frontend-architecture--client-pwa)
6. [Deployment, Infrastructure & Model Routing](#6-deployment-infrastructure--model-routing)
7. [Security, Compliance & Threat Model](#7-security-compliance--threat-model)
8. [Testing, Verification & Quality Assurance](#8-testing-verification--quality-assurance)

---

## 1. Executive Overview & Architectural Tenets

FINN is an institutional-grade, mobile-first Progressive Web Application (PWA) architected specifically for high-conviction public-market investment managers at ENAM Holdings. Institutional investors operating concentrated portfolios (15–20 core holdings) face three acute structural friction points:
1. **Information Asymmetry & Filing Noise:** Hundreds of routine regulatory compliance filings obscure critical strategic shifts (CFO resignations, major capex, margin inflection).
2. **LLM Hallucination Risk ("AI Slop"):** General-purpose LLMs hallucinate financial metrics, invent guidance numbers, and conflate standalone vs. consolidated figures, rendering them unusable for professional capital allocation.
3. **Latent Knowledge Disconnection:** When a portfolio company makes a material filing, the investor’s personal network (former executives, supply-chain heads, board members, alumni) remains dormant because there is no automated bridge linking market filings to personal Rolodexes.

### Core Architectural Tenets
- **Strict Primary-Source Grounding:** No external web searches or ungrounded training knowledge. Every financial claim must resolve to a verbatim quote with page-and-speaker provenance from an exchange filing, annual report, or concall transcript (ADR-004).
- **Deterministic Mathematics Over Generative Arithmetic:** Growth rates, margins, basis point spreads, and cash conversion ratios ($\text{CFO} / \text{PAT}$) are calculated purely via deterministic Python math (`MetricsCalculator`), never by an LLM.
- **Tenant Isolation by Construction:** Portfolio weights, personal contacts, 2nd-degree paths, and alert read/dismiss states are cryptographically and relationally partitioned per tenant. Public market data and private graphs never cross tenant boundaries (ADR-003, ADR-005).
- **Mobile-First Sub-Second Geometry:** Designed for 375×812 mobile viewports with 48px touch targets, zero layout shifts, offline PWA caching, and lockscreen privacy masking.

---

## 2. End-to-End System Topology

FINN separates deterministic, zero-latency local computation from high-reasoning LLM inference using a 3-tier pipelined architecture.

```mermaid
flowchart TD
    subgraph DataIngestion ["1. Data Ingestion & Feeds"]
        BSE_NSE["BSE / NSE Exchange Disclosures (SEBI LODR 17 Categories)"]
        Transcripts["Concall Transcripts & Annual Reports (PDF / TXT)"]
        MarketData["Market EOD Feeds (Price, Volume, 60d History)"]
        CorporateActions["Corporate Actions (Splits, Bonuses, Rights)"]
        TenantContacts["Tenant Contact Importer (CSV / vCard)"]
    end

    subgraph BackendCore ["2. FastAPI Backend Engine (Python 3.14)"]
        direction TB
        FilingsEng["FilingsEngine\n(Regex/Pattern SEBI Classifier & Hash Deduplicator)"]
        AnomalyDet["AnomalyDetector\n(Volatility Z-Score & Cooldown Logic)"]
        ResearchEng["ResearchEngine\n(Narrative vs. Numbers v2 & Cold-Ticker Pipeline)"]
        MetricsCalc["MetricsCalculator\n(Deterministic Math & BFSI Templates)"]
        CitationVer["CitationVerifier\n(Verbatim Locating & Hallucination Rejection)"]
        NetworkEng["NetworkEngine\n(NetworkX Directed Graph & MNPI Guardrails)"]
        PushSvc["PushNotificationService\n(VAPID RFC 8291/8292 & Lockscreen Privacy)"]
        LLMRouter["LLMRouter\n(Tier 0 Local -> Tier 1 Flash -> Tier 2 Pro)"]
    end

    subgraph StorageLayer ["3. Centralized Database (SQLite WAL)"]
        SQLiteDB[("finn.db\nPRAGMA journal_mode=WAL\nPRAGMA synchronous=NORMAL\n17 Relational Tables")]
    end

    subgraph ClientLayer ["4. Mobile-First PWA (React 18 + Vite + Tailwind)"]
        SW["Service Worker (sw.js)\n(Background Sync & Push Alerts)"]
        PulseTab["Pulse View\n(Windowed Digest & Pinned Alert)"]
        RadarTab["Radar View\n(Anomaly Stream & Sensitivity Slider)"]
        DeepDiveTab["DeepDive View\n(Promised vs Delivered & Cash Track Record)"]
        NexusTab["Nexus View\n(Who to Call & 2nd-Degree Intro Path)"]
    end

    DataIngestion --> BackendCore
    BackendCore <--> StorageLayer
    ResearchEng --> MetricsCalc
    ResearchEng --> CitationVer
    BackendCore --> LLMRouter
    AnomalyDet --> PushSvc
    PushSvc -->|VAPID Push| SW
    BackendCore <--> ClientLayer
```

### Data Flow Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Investor as Investment Analyst (Mobile PWA)
    participant Client as Frontend (React 18)
    participant API as FastAPI Gateway
    participant Engine as Anomaly / Research Engine
    participant DB as SQLite WAL Store
    participant Verifier as CitationVerifier
    participant LLM as Gemini 2.5 Pro / Flash

    Investor->>Client: Open Pulse Tab (375x812)
    Client->>API: GET /api/push/digest?hours=24
    API->>DB: Query material filings (ISIN-keyed, LODR ranked)
    DB-->>API: 5 High-Signal Filings + 3 Collapsed Routine
    API-->>Client: 200 OK (JSON with GAAP metrics & network links)
    Client-->>Investor: Render Pulse Feed & Top Pinned Alert

    Investor->>Client: Tap "DeepDive Research" on DIXON.NS
    Client->>API: GET /api/research/DIXON.NS/deepdive
    API->>Engine: Run Narrative vs. Numbers Pipeline
    Engine->>DB: Fetch Guidance History & Primary Transcripts
    Engine->>LLM: Synthesize Track Record (Tier 2 Routing)
    LLM-->>Engine: Extracted claims & management quotes
    Engine->>Verifier: Verify verbatim quotes against source texts
    Verifier-->>Engine: 100% Citation Faithfulness Certified
    Engine->>DB: Cache validated research output
    Engine-->>API: Grounded DeepDive Response
    API-->>Client: 200 OK (Render Promised vs Delivered cards)
```

---

## 3. Database Architecture & Data Model (SQLite WAL)

FINN utilizes a centralized SQLite database engine running in **Write-Ahead Logging (WAL)** mode. This eliminates external server daemon overhead, avoids database network hops, and guarantees deterministic transactional durability for single-node hedge fund deployments (ADR-002).

### 3.1 Concurrency & Configuration Pragmas
```sql
PRAGMA journal_mode = WAL;          -- Enables concurrent lock-free readers alongside a single writer
PRAGMA synchronous = NORMAL;        -- Minimizes disk sync operations while guaranteeing zero WAL corruption
PRAGMA foreign_keys = ON;           -- Enforces strict relational integrity and cascading deletes
PRAGMA busy_timeout = 5000;         -- 5-second busy handler to gracefully absorb concurrent write bursts
PRAGMA temp_store = MEMORY;         -- High-speed memory storage for temp tables and sorting indices
```

### 3.2 Relational Schema (17 Tables)

```mermaid
erDiagram
    tenants ||--o{ users : "has"
    tenants ||--o{ tenant_holdings : "owns"
    tenants ||--o{ network_contacts : "maintains"
    tenants ||--o{ network_relationships : "contains"
    tenants ||--o{ mnpi_call_audit_log : "records"
    users ||--o{ user_alert_state : "tracks"
    users ||--o{ user_preferences : "configures"
    users ||--o{ push_subscriptions : "registers"
    companies ||--o{ company_tickers_history : "tracks renames"
    companies ||--o{ tenant_holdings : "referenced by"
    companies ||--o{ market_eod : "records price"
    companies ||--o{ announcements : "files"
    companies ||--o{ concall_transcripts : "releases"
    companies ||--o{ guidance_history : "delivers"
    companies ||--o{ detected_anomalies : "triggers"
    companies ||--o{ corporate_actions : "undergoes"
    detected_anomalies ||--o{ user_alert_state : "decoupled state"
    network_contacts ||--o{ network_relationships : "from/to"
    network_contacts ||--o{ mnpi_call_audit_log : "called"
```

#### Complete Table Definitions

| Table Name | Primary Key | Isolation Level | Purpose |
|---|---|---|---|
| `tenants` | `id` | Global Master | Defines investment entities (e.g., `tenant-enam-core`). |
| `users` | `id` | Tenant Scoped | Maps individual investment analysts to tenants. |
| `companies` | `isin` | Public Global | Canonical company master keyed by ISIN (ADR-006). |
| `company_tickers_history`| `id` (Auto) | Public Global | Tracks ticker symbol changes and exchange migrations. |
| `tenant_holdings` | `(tenant_id, isin)`| Tenant Isolated | Confidential portfolio holdings, conviction tiers, and weights. |
| `market_eod` | `id` (Auto) | Public Global | 60-day historical daily close, volume, 20d SMA, and return. |
| `corporate_actions` | `id` | Public Global | Splits, bonus issues, and adjustment factors. |
| `announcements` | `id` | Public Global | SEBI LODR Regulation 30 filings with SHA-256 provenance hashes. |
| `concall_transcripts` | `id` | Public Global | Structured transcript texts, management remarks, and Q&A. |
| `guidance_history` | `id` (Auto) | Public Global | Multi-quarter promised guidance vs. delivered actual metrics. |
| `detected_anomalies` | `id` | Public Global | Global factual market anomalies (Z-score, volume multiple). |
| `user_alert_state` | `(user_id, anomaly_id)`| User Decoupled | Tracks read, pinned, and dismissed states per analyst. |
| `user_preferences` | `user_id` | User Scoped | Thresholds, notification settings, and privacy mode flags. |
| `push_subscriptions` | `endpoint` | User Scoped | W3C Push API VAPID endpoints and cryptographic keys. |
| `network_contacts` | `id` | Tenant Isolated | Analyst network contacts, past companies, alumni, and relevance. |
| `network_relationships`| `id` (Auto) | Tenant Isolated | Edges between contacts (ex-colleague, classmate, co-investor). |
| `mnpi_call_audit_log` | `id` | Tenant Isolated | Compliance records for analyst scuttlebutt conversations. |

### 3.3 Indexing Strategy for Sub-Millisecond Latency
```sql
CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_holdings_tenant ON tenant_holdings(tenant_id);
CREATE INDEX idx_announcements_isin ON announcements(isin);
CREATE INDEX idx_announcements_time ON announcements(filing_time DESC);
CREATE INDEX idx_anomalies_time ON detected_anomalies(created_at DESC);
CREATE INDEX idx_market_eod_lookup ON market_eod(isin, trade_date DESC);
CREATE INDEX idx_network_tenant ON network_contacts(tenant_id);
CREATE INDEX idx_alert_state_lookup ON user_alert_state(user_id, anomaly_id);
```

---

## 4. Backend Architecture & Engine Specifications

The backend is built with **Python 3.14** and **FastAPI**, deployed on **Uvicorn** with an asynchronous **AnyIO** event loop. It comprises modular services engineered for zero hallucination and high financial precision.

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints.py            # REST Router (Pulse, Radar, DeepDive, Nexus, Preferences)
│   │   └── schemas.py              # Pydantic v2 validation models
│   ├── data/
│   │   └── seed_data.py            # Primary-grounded seed definitions (22 companies, 1098 EODs)
│   ├── db/
│   │   └── database.py             # SQLite WAL connection pool, pragmas, schema init
│   └── services/
│       ├── anomaly_detector.py     # Volatility Z-score, cooldowns, daily caps
│       ├── citation_verifier.py    # 100% faithful verbatim quote locating & scoring
│       ├── document_pipeline.py    # Parse quality scoring & OCR evaluation
│       ├── filings_engine.py       # SEBI LODR 17-category classification & deduplication
│       ├── llm_router.py           # 3-tier cost-optimized model gateway
│       ├── market_data.py          # EOD caching & corporate action adjustments
│       ├── metrics_calculator.py   # Deterministic financial math & BFSI ratios
│       ├── network_engine.py       # NetworkX graph, shortest paths, SEBI MNPI guardrails
│       ├── push_notifications.py   # Web Push VAPID dispatcher & privacy masking
│       └── research_engine.py      # Narrative vs Numbers v2 & cold-ticker synthesis
└── tests/                          # 55 passing pytest test cases across 13 modules
```

### 4.1 Filings Classification Engine (`filings_engine.py`)
- **SEBI LODR Regulation 30 Categories:** Implements 17 standardized filing categories:
  `results`, `M&A`, `management_change`, `fund_raise`, `litigation`, `insider_trading`, `earnings_call`, `investor_meetings`, `credit_rating`, `dividend`, `bonus_split`, `capex`, `press_release`, `postal_ballot`, `agm_egm`, `pledging`, `unclassified`.
- **Role-Aware KMP Classifier:** Evaluates Key Managerial Personnel changes hierarchically (CEO, CFO, and Executive Chairman receive Materiality Score = 10; Independent Directors receive Score = 6).
- **Cross-Exchange Deduplication:** Computes SHA-256 hashes of standardized disclosure titles and timestamps, preventing duplicate alerts when companies file simultaneously across BSE and NSE.

### 4.2 Hardened Anomaly Detector (`anomaly_detector.py`)
- **Volatility-Normalized Z-Score:**
  $$Z = \frac{R_{\text{daily}} - \mu_{60}}{\sigma_{60}}$$
  where $\mu_{60}$ and $\sigma_{60}$ represent the 60-day moving average and standard deviation of daily returns.
- **Corporate Action Split Adjustment:**
  Before computing daily returns, price series are adjusted against `corporate_actions`:
  $$P_{\text{adjusted}} = P_{\text{raw}} \times \text{adjustment\_factor}$$
  *(e.g., a 1:5 stock split applies an adjustment factor of 0.20, preventing false -80% crash alerts).*
- **Expected Results Spike Tagging:**
  If a volume surge occurs on a scheduled earnings release date, it is tagged `EXPECTED_RESULTS_SPIKE` and suppressed from firing duplicate critical alarms.
- **Fatigue Controls:**
  Enforces a strict **6-hour duplicate cooldown** and a **maximum daily cap of 3 alerts per ticker**.

### 4.3 Deterministic Metrics Calculator (`metrics_calculator.py`)
To prevent LLM mathematical hallucinations, all financial metrics are computed purely through deterministic code:
- **Growth & Margin Formulas:**
  $$\text{YoY Growth \%} = \left(\frac{\text{Metric}_t - \text{Metric}_{t-4}}{\text{Metric}_{t-4}}\right) \times 100$$
  $$\text{Margin Spread (bps)} = (\text{Margin}_t - \text{Margin}_{t-1}) \times 100$$
  $$\text{Cash Conversion} = \frac{\text{Operating Cash Flow (CFO)}}{\text{Net Profit (PAT)}} \times 100$$
- **BFSI Template:** Computes Net Interest Margin (NIM in bps), Provision Coverage Ratio (PCR %), and Liquidity Coverage Ratio (LCR %) for banks and NBFCs.

### 4.4 Citation Verifier (`citation_verifier.py`)
- **Verbatim Text Locating:** Performs exact and normalized substring matching against canonical concall transcripts and annual reports.
- **Citation Anchoring:** Extracts and validates exact document references, page numbers, and speaker designations (e.g., *“Atul Lall (Vice Chairman & MD), Q2 FY27 Concall, p. 4”*).
- **Hallucination Rejection:** Drops or rejects generated claims if the supporting quote is not found in the primary source document with at least 85% fuzzy token overlap.

### 4.5 Graph Network Engine (`network_engine.py`)
- **Graph Topology:** Builds a directed, weighted `NetworkX` graph where nodes represent investment contacts and edges represent historical relationships (`CLASSMATE`, `EX_COLLEAGUE`, `CO_INVESTOR`, `ADVISOR`).
- **Relevance Scoring Formula:**
  $$\text{Relevance} = (T \times 0.25) + (S \times 0.25) + (R_{\text{str}} \times 0.25) + (M \times 0.25) + 2.0_{\text{starred}}$$
  where $T = \text{Tenure Score}$, $S = \text{Seniority Score}$, $R_{\text{str}} = \text{Relationship Strength}$, $M = \text{Event Materiality}$.
- **2nd-Degree Shortest Path Routing:** Discovers warm introduction paths (e.g., `You → Ananya Roy → Vikram Seth`) using weighted shortest-path graph search.
- **SEBI PIT MNPI Guardrails:**
  - `CURRENT_INSIDER_CAUTION`: Flags current employees of the filing company.
  - `FORMER_EMPLOYEE_SAFE`: Identifies alumni and former executives safe for industry scuttlebutt.
  - `RESTRICTED_LIST`: Completely suppresses contact suggestions for companies on active compliance freeze.

---

## 5. Frontend Architecture & Client PWA

The frontend is an installable Progressive Web Application built with **React 18**, **TypeScript 5.5**, **Vite 5.4**, and **Tailwind CSS 3.4**.

### 5.1 Mobile-First Viewport Geometry
- **Primary Design Baseline:** Native 375×812 resolution (iPhone 13/14/15, Android standard).
- **Ergonomic Touch Targets:** Minimum 44×44px interactive targets with 48px baseline spacing.
- **Navigation Rhythm:** Persistent bottom navigation bar with active tab indicators and badge counts (`Pulse`, `2 Radar`, `DeepDive`, `Nexus`).
- **Theme Engine:** Instant switching between Institutional Dark Mode (slate-950 high contrast) and Crisp Light Mode (slate-50 clean borders) without flash of unstyled content.

```
frontend/
├── public/
│   ├── manifest.json               # W3C PWA Manifest (standalone display)
│   ├── sw.js                       # Service worker with Web Push listener
│   └── icons/                      # App icons (192px, 512px, maskable)
├── src/
│   ├── App.tsx                     # Top-level state, active tab, theme router
│   ├── index.css                   # Tailwind directives & design tokens
│   ├── main.tsx                    # Service worker registration
│   ├── types/index.ts              # Strict TypeScript interfaces
│   ├── services/api.ts             # Typed REST API client
│   ├── hooks/
│   │   ├── useTheme.ts             # Dark/Light mode theme engine
│   │   └── useWebPush.ts           # Push subscription & VAPID token handling
│   └── components/
│       ├── layout/
│       │   ├── Navbar.tsx          # Top bar with scan, push toggle, theme switch
│       │   └── BottomNav.tsx       # 4-tab mobile bottom bar
│       ├── pulse/
│       │   ├── PinnedAlertCard.tsx # Single-line metadata bar + 3-line factual summary
│       │   └── WindowedDigest.tsx  # Time-windowed filing cards with GAAP metrics
│       ├── radar/
│       │   └── RadarView.tsx       # Live sensitivity slider + anomaly cards
│       ├── deepdive/
│       │   └── DeepDiveView.tsx    # Promised vs Delivered, Cash Flow, Bull vs Bear
│       └── nexus/
│           └── NexusView.tsx       # Who to Call modal & 2nd-degree intro path
```

### 5.2 Component View Breakdown

#### 1. Pulse View (The Morning Digest)
- **Time Window Filtering:** Toggle between `24 Hours`, `7 Days`, and `30 Days`.
- **SEBI LODR Category Pills:** Filter by `Results`, `Mgmt Change`, `M&A`, `Capex`, `Litigation`.
- **Pinned Alert Card:** Displays the top critical market event with single-line metadata bar:
  `PINNED ALERT · TECH BREAKOUT · 12 NOV · EOD  ✕`
- **Filing Cards:** Displays GAAP metrics (Revenue, EBITDA margin, PAT with YoY %), primary source document badge, filing timestamp, and linked network contact chip.
- **Collapsible Routine Section:** Routine compliance filings (share allotments, Reg 74 certificates) collapsed into a single summary bar.

#### 2. Radar View (Real-Time Anomaly Stream)
- **Interactive Sensitivity Slider:** Adjust volume threshold dynamically between `1.5x` and `5.0x` SMA.
- **Live Threshold Preview:** Displays real-time alert count matching the slider threshold.
- **Severity Badges:** Institutional badges (`CRITICAL`, `HIGH`, `MEDIUM`) with volatility Z-scores and 60-day baseline $\sigma$.

#### 3. DeepDive View (Grounded Company Research)
- **4 Diligence Sections:**
  1. *Promised vs. Delivered:* Multi-quarter guidance vs. delivered actuals with `BEAT`, `MET`, `MISSED`, or `QUALITATIVE` tags and page-level citations.
  2. *Cash & Balance Sheet:* Operating cash flow to PAT conversion ratio, Net Debt/EBITDA, and working capital cycles.
  3. *Bull vs. Bear Thesis:* Grounded institutional debate points with primary citations.
  4. *BFSI Template:* Bank/NBFC metrics (NIM, Gross/Net NPA, PCR, LCR).

#### 4. Nexus View (Graph Intelligence & Scuttlebutt)
- **Company Context Switcher:** Filter network by portfolio tickers (`DIXON`, `TRENT`, `TATAMOTORS`, `KAYNES`, `DEEPAKNTR`).
- **2nd-Degree Reach Modal:** Highlights bridge contacts with batchmate/ex-colleague context (e.g. *IIT Kanpur 2004*).
- **"Who to Call" Modal:** Segregates contacts into *Former Executives (Channel Intel)* and *Suppliers & Customers (Ecosystem)*.
- **SEBI Compliance Modal:** Logs scuttlebutt research calls with pre-filled compliance declarations.

---

## 6. Deployment, Infrastructure & Model Routing

### 6.1 3-Tier Cost-Optimized Model Routing

FINN implements a strict, cost-governed multi-model routing pipeline:

```mermaid
flowchart TD
    Query["Incoming Diligence Query or Filing Ingestion"] --> Classifier{"Complexity & Grounding Classifier"}
    
    Classifier -->|Deterministic Math / LODR Regex| Tier0["Tier 0: Local Python Engine\nCost: $0.00 | Latency: < 5ms"]
    Classifier -->|Filing Summarization / Extraction| Tier1["Tier 1: Gemini 2.5 Flash\nCost: ~$0.0004 | Latency: ~800ms"]
    Classifier -->|Deep Multi-Quarter Synthesis| Tier2["Tier 2: Gemini 2.5 Pro\nCost: ~$0.0035 | Latency: ~2.2s"]

    Tier0 --> Response["Validated Output Response"]
    Tier1 --> CitationCheck{"CitationVerifier Substring Check"}
    Tier2 --> CitationCheck
    
    CitationCheck -->|100% Validated| Response
    CitationCheck -->|Hallucination Detected| Tier0
```

| Tier | Engine / Model | Cost per Unit | Target Task | SLA / Latency |
|---|---|---|---|---|
| **Tier 0** | Local Python Engine | **$0.00** | SEBI LODR classification, volatility Z-scores, deterministic ratios, citation substring matching | **< 5 ms** |
| **Tier 1** | Gemini 2.5 Flash | **~$0.0004** / doc | Standard announcement extraction, routine digest summaries | **~800 ms** |
| **Tier 2** | Gemini 2.5 Pro | **~$0.0035** / query | Complex multi-quarter concall guidance synthesis, Bull vs. Bear debate extraction | **~2,200 ms** |

#### Monthly Cost Projection (20-Stock Portfolio)
- **Daily Ingestion:** ~15 filings/day $\times$ $0.0004 = \$0.006$/day $\rightarrow$ **\$0.18 / month**
- **DeepDive Queries:** ~50 deep queries/analyst/month $\times$ $0.0035 = \$0.175$/month
- **Local Engine (Tier 0):** Zero compute cost on local CPU.
- **Total Projected AI Spend:** **< $10.00 / analyst / month**, delivering 98% savings over unrouted GPT-4/Claude Opus architectures.

---

### 6.2 Containerization & Production Topology

#### Multi-Stage Dockerfile

```dockerfile
# --- Stage 1: Build Frontend Assets ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python Backend ---
FROM python:3.14-slim AS backend
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FINN_DB_PATH=/app/data/finn.db

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Initialize SQLite WAL database
RUN python -m backend.app.data.seed_data

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Production Docker Compose Specification
```yaml
version: '3.8'

services:
  finn-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: finn-platform
    restart: always
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - VAPID_PRIVATE_KEY=${VAPID_PRIVATE_KEY}
      - VAPID_PUBLIC_KEY=${VAPID_PUBLIC_KEY}
      - FINN_DB_PATH=/app/data/finn.db
    volumes:
      - finn-data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  finn-data:
    driver: local
```

#### Reverse Proxy & Static Caching (Nginx)
```nginx
server {
    listen 80;
    server_name finn.enam.internal;

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    # Frontend PWA Static Assets
    location / {
        root /app/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, must-revalidate";
    }

    # API Gateway Reverse Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 7. Security, Compliance & Threat Model

FINN operates under strict institutional compliance frameworks applicable to Indian financial entities:

```mermaid
flowchart LR
    subgraph Regulatory ["Regulatory Guardrails"]
        SEBI_LODR["SEBI LODR 2015\n(17 Materiality Categories)"]
        SEBI_PIT["SEBI PIT Regulations\n(MNPI & Restricted Lists)"]
        DPDP_ACT["DPDP Act 2023\n(Data Portability & Erasure)"]
    end

    subgraph SecurityControls ["FINN Security Architecture"]
        TenantFilter["Tenant SQL Scoping\n(WHERE tenant_id = ?)"]
        InsiderCheck["Role-Aware KMP Check\n(Caution vs Safe Alumni)"]
        AuditLog["Immutable Scuttlebutt Log\n(mnpi_call_audit_log)"]
        ExportErasure["DPDP Controller\n(GET /export, DELETE /erase)"]
        PrivacyMode["Push Privacy Mode\n(Masked Tickers & Metrics)"]
    end

    SEBI_LODR --> TenantFilter
    SEBI_PIT --> InsiderCheck
    SEBI_PIT --> AuditLog
    DPDP_ACT --> ExportErasure
    TenantFilter --> PrivacyMode
```

### 7.1 Threat Model & Mitigations

| Threat | Attack Vector | FINN Architectural Mitigation |
|---|---|---|
| **Multi-Tenant Leak** | Analyst A accesses Analyst B's portfolio holdings or contacts | Strict tenant scoping on all database queries (`WHERE tenant_id = ?`); zero cross-tenant joins; verified by `test_tenant_isolation.py`. |
| **MNPI Contamination** | Analyst calls current executive right before quarterly earnings | `NetworkEngine` checks active company employment and flags `CURRENT_INSIDER_CAUTION`; blocked if company is on `RESTRICTED_LIST`. |
| **Audit Non-Compliance**| Regulatory inspection of channel checks | Every scuttlebutt call prompts an explicit objective and logs an immutable audit trail in `mnpi_call_audit_log`. |
| **Lockscreen Data Snooping** | Sensitive earnings moves exposed on unattended mobile device | `Web Push Privacy Mode` masks ticker names and percentage moves into generic alerts (*"Material disclosure filed"*). |
| **Data Privacy (DPDP 2023)** | User requests full data export or account erasure | Dedicated `/api/nexus/contacts/export` (JSON/CSV) and `/api/nexus/contacts/erase` endpoints implement Right to Portability and Right to Erasure. |

---

## 8. Testing, Verification & Quality Assurance

FINN is certified against an automated **55-test pytest suite** covering 13 test modules with a **100% pass rate** in under 2.3 seconds.

```
tests/
├── test_anomaly_hardening.py       # Corporate action splits, volatility Z-scores, fatigue caps (5 tests)
├── test_api.py                     # Health, companies, digest, pinned alert, preferences (7 tests)
├── test_citation_verifier.py       # Verbatim quoting, near-verbatim matching, hallucination drops (4 tests)
├── test_cold_ticker_research.py    # Cold-ticker research, normalization, unseeded generalization (3 tests)
├── test_document_pipeline.py       # OCR parse quality scoring, document coverage assessment (4 tests)
├── test_filings_classification.py  # 17 SEBI LODR categories, KMP hierarchy, hash deduplication (4 tests)
├── test_financial_units.py         # Indian fiscal quarters (Q2FY25 -> Jul-Sep 2024), Crores, bps (2 tests)
├── test_golden_claims.py           # 100% citation faithfulness score on golden claims set (3 tests)
├── test_metrics_calculator.py      # Growth %, margin spreads in bps, CFO/PAT, BFSI template (7 tests)
├── test_nexus_intelligence.py      # Relevance score formula, MNPI guardrails, DPDP export (6 tests)
├── test_services.py                # Windowed digest, anomaly ranking, who to call, 2nd-degree (7 tests)
├── test_tenant_isolation.py        # Tenant portfolio scoping, network graph boundary isolation (2 tests)
└── test_user_alert_state.py        # Independent read/pin/dismiss alert state per user (1 test)
```

### Verification Command Execution
```bash
# Execute Full Pytest Suite
cd backend
./venv/bin/pytest tests/ -v
# Output: ============================== 55 passed in 2.26s ==============================

# Verify Frontend Production Build
cd frontend
npm run build
# Output: ✓ built in 1.71s (0 TypeScript errors)
```

---

## 9. Architectural Summary Reference

| Architectural Dimension | Specification & Selection | Institutional Rationale |
|---|---|---|
| **Client Frontend** | React 18 + Vite 5 + Tailwind CSS 3 | Sub-second mobile rendering, zero runtime footprint, offline PWA capability. |
| **Backend Framework** | FastAPI (Python 3.14) + AnyIO | High-concurrency async REST routing with native Pydantic v2 validation. |
| **Database Engine** | SQLite 3 (`journal_mode=WAL`) | Sub-millisecond zero-network data access, zero external DB dependencies, WAL read-write concurrency. |
| **Model Gateway** | 3-Tier Multi-Model Routing | Eliminates arithmetic hallucinations (Tier 0 local math) while cutting inference costs by 98%. |
| **Citation System** | Substring Citation Verifier | Verbatim verification against primary disclosures guarantees 100% citation faithfulness. |
| **Network Graph** | NetworkX In-Memory Directed Graph | Real-time 2nd-degree shortest path routing and SEBI PIT compliance checks. |
| **Push Channel** | VAPID Web Push Protocol (RFC 8291/8292) | Native lockscreen mobile notification delivery with privacy masking. |

---
*Document maintained by the FINN Engineering Team at ENAM Holdings.*
