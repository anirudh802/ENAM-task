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
1. **Tickers & ISINs:** Always use `.NS` suffix for NSE equities. Every company master record is uniquely keyed by its 12-character ISIN (e.g., `INE806N01020` for Dixon).
2. **Indian Fiscal Calendar:**
   - Financial year runs April 1 to March 31.
   - `Q1`: April 1 to June 30 (Q1FY25 = Apr–Jun 2024).
   - `Q2`: July 1 to September 30 (Q2FY25 = Jul–Sep 2024).
   - `Q3`: October 1 to December 31 (Q3FY25 = Oct–Dec 2024).
   - `Q4`: January 1 to March 31 (Q4FY25 = Jan–Mar 2025).
3. **Unit Standards:**
   - Currency: All reported totals must be normalized to INR Crores (₹ Cr, $10^7$ INR).
   - Variances & Margins: Margins and delta changes must be reported in Basis Points (1 bps = 0.01% = 0.0001) or explicit percentages.
4. **Financial Basis & Restatements:**
   - Always tag metrics as `CONSOLIDATED` (default for holding/multi-entity firms) or `STANDALONE`.
   - Never compare Standalone figures in one quarter against Consolidated figures in the prior quarter.
   - Maintain `restatement_flag` when historical financials are restated by the company.
5. **Primary vs. Secondary Boundary:** Never include third-party broker opinions or speculative news articles in the company research data. Extract solely from official exchange filings, audited annual reports, and verified concall transcripts.
