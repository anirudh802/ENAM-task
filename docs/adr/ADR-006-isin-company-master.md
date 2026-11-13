# ADR-006: ISIN-Keyed Company Master & Ticker History

## Status
Accepted

## Context
In Indian public equity markets, stock tickers change frequently due to corporate rebrandings, demergers, and restructuring:
- e.g., Tata Motors (`TATAMOTORS.NS`) demerging its commercial vehicles and passenger vehicles divisions.
- e.g., Zomato Ltd proposing corporate name changes to Eternal.
- e.g., L&T Technology Services or Motherson Sumi renames.

Relying on exchange ticker strings (e.g. `DIXON.NS`) as foreign keys across historical price tables (`market_eod`), filings (`announcements`), and portfolio holdings (`tenant_holdings`) causes join failures, broken historical trends, and orphaned records whenever a ticker is modified by the exchanges.

## Decision
1. **Canonical Master Key: International Securities Identification Number (ISIN):**
   - The primary identifier for all listed securities is standardized as the 12-character alphanumeric **ISIN** (e.g., `INE806N01020` for Dixon Technologies, `INE002A01018` for Reliance Industries).
   - The `companies` table is keyed by `isin`.
2. **Ticker History Table (`company_tickers`):**
   - Stores the history of exchange symbols assigned to an ISIN:
     - `isin` (FK)
     - `exchange` (`NSE` or `BSE`)
     - `ticker` (e.g., `DIXON`, `RELIANCE`)
     - `valid_from`, `valid_to`, `is_primary`
3. **API & Search Layer:**
   - The API continues to accept user-friendly ticker symbols (e.g., `/api/pull/research/DIXON.NS`), resolving the symbol to its canonical ISIN before executing underlying queries.

## Consequences
- **Positive:** Robust corporate restructuring handling, permanent join integrity across decades of historical filings and market data.
- **Negative:** Requires an initial mapping lookup from ticker to ISIN during ingestion.
