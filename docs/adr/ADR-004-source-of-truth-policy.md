# ADR-004: Primary Source-of-Truth Policy & Filing Provenance

## Status
Accepted

## Context
FINN is built for institutional investors at ENAM Holdings. A central rule of the mandate is:
> "Strict primary-source grounding: ground it in the primary sources (annual reports + transcripts). No broker notes, no news, no research reports, and don't lean on the model's own outside knowledge of the company."

Financial data aggregators like Screener.in or Yahoo Finance standardize and normalize metrics across companies. While valuable for discovering document links and high-level screening, secondary aggregators frequently restate, adjust, or smooth numbers (e.g., classifying operating lease expenses, exceptional items, or capital work-in-progress differently than management reported). Relying on an aggregator's normalized table as the source of truth violates the institutional primary-source discipline.

## Decision
1. **Source of Truth Definition:**
   - Canonical financial data must originate directly from **primary regulatory filings**:
     - Exchange Disclosures under SEBI LODR Regulations filed with BSE & NSE.
     - Audited Annual Reports (Balance Sheet, P&L, Cash Flow Statements, and Notes to Accounts).
     - Official Earnings Conference Call Transcripts published by the company's Investor Relations.
   - **Screener.in Role:** Utilized exclusively as an automated document discovery index (to retrieve URLs and filing metadata for annual reports and concall transcripts), never as the authoritative factual truth.
2. **Provenance & Audit Trail:**
   - Every financial metric extracted into the database or displayed in DeepDive must capture:
     - `document_name` / `filing_id`
     - `document_sha256` (content hash for immutability)
     - `page_or_offset` (page number in annual report or transcript section)
     - `financial_basis` (`CONSOLIDATED` vs `STANDALONE`)
     - `restatement_flag` (boolean indicating if the figure was restated in subsequent filings).

## Consequences
- **Positive:** Unimpeachable data integrity. Analysts can verify any figure in FINN against the exact page of the company's exchange filing.
- **Negative:** Requires PDF and transcript text extraction and archival pipelines rather than querying pre-aggregated APIs.
