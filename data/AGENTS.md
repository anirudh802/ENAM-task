# Data AGENTS.md — Financial & Network Seed Data

## Role & Responsibilities
The `data/` directory (and `backend/app/data/`) manages the canonical datasets:
1. **Mock Portfolio (18 Stocks):** Diverse Indian listed companies across sectors and market cap brackets, explicitly including requested tickers:
   - `RELIANCE.NS`, `TATAMOTORS.NS`, `DIXON.NS`, `TRENT.NS`, `KAYNES.NS`, `CDSL.NS`.
   - Plus `HDFCBANK.NS`, `DEEPAKNTR.NS`, `POLYCAB.NS`, `PERSISTENT.NS`, `SUNPHARMA.NS`, `LT.NS`, `TITAN.NS`, `ZOMATO.NS`, `DIVISLAB.NS`, etc.
2. **Exchange Filings Feed:** Realistic filings mapped to the 17 standardized categories in `2. ENAM_Build_Challenge_Reference.pdf`, with routine filings (ESOPs, compliance certs) tagged for automatic collapsing.
3. **Primary-Source Concall Data:** Historical guidance statements vs delivered numbers for the "Narrative vs. Numbers" analyzer.
4. **Investor Network Graph:** 25+ realistic professional profiles with IIT Kanpur alumni, ex-promoters, suppliers, competitors, and CXO ties.

## Data Integrity Rules
1. **Tickers:** Always use `.NS` suffix for NSE equities.
2. **Financial Precision:** Percentages must be explicit (e.g. `+18.4% YoY`), margins in bps or %, and currency in INR Crores (₹ Cr).
3. **Primary vs. Secondary Boundary:** Never include third-party broker opinions or speculative news articles in the company research data.
