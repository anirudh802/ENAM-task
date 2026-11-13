# ADR-003: Tenant-Isolated & Client-Cached Network Graph

## Status
Accepted

## Context
The investor's personal network (alumni ties, former colleagues, promoters, direct phone contacts) contains sensitive, personally identifiable information (PII). Mingling this with public financial market data or across users introduces grave data privacy and compliance risks.

## Decision
We implement a **Tenant-Isolated, Local-First Network Graph Architecture**:
1. **Strict Data Boundary:** The network domain (`network_contacts`, `employment_history`, `education`, `relationships`) is stored in isolated tenant tables, completely decoupled from canonical market feeds.
2. **Client-Side Cache (IndexedDB):** Contacts and cached relevance scores are synchronized to the client's local IndexedDB container for instant offline access and local-first security.
3. **In-Memory Traversal Engine:** The backend loads the tenant graph into an in-memory `NetworkX` graph upon session initialization to execute sub-millisecond graph traversals (`Who Should I Call?`, `Second-Degree Reach`, and `Expertise Map`).
4. **Contextual Relevance Hook:** When new filings or earnings are logged for a company, the engine queries the contact graph for former employers, generating a 1–2 line recent development summary and warm reconnect prompt without transmitting contact details to any third-party model.

## Consequences
- **Positive:** Guaranteed zero cross-tenant data contamination, full privacy compliance, sub-millisecond graph queries.
- **Negative:** Requires graph synchronization logic between server-side tenant store and client-side IndexedDB.
