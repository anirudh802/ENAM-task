# ADR-005: Multi-Tenant Privacy Model & Data-Layer Isolation

## Status
Accepted

## Context
The investor's personal network (alumni ties, former colleagues, promoters, direct phone contacts) and a fund's portfolio holdings (`tenant_holdings`) represent strictly confidential, high-value proprietary intellectual property. 

The initial prototype stored `is_portfolio` directly on the shared `companies` table and handled contacts in a global `network_contacts` table. If multiple investment teams or tenant funds share the backend instance, one tenant's portfolio or contact notes would be exposed to another. Furthermore, claiming "client-side zero-knowledge encryption" while executing server-side `NetworkX` graph traversal and relevance scoring is an architectural contradiction, because server-side graph algorithms require plaintext graph structures.

## Decision
We implement a **Server-Side Tenant-Isolated Architecture with Data-Layer Scoping**:
1. **Explicit Multi-Tenancy:**
   - Introduce `tenants` and `users` tables. Every authenticated session resolves to a verified `(tenant_id, user_id)`.
2. **Confidential Portfolio Holdings:**
   - Remove `is_portfolio` from the shared public `companies` table.
   - Introduce `tenant_holdings` (`tenant_id`, `isin`, `ticker`, `shares_held`, `conviction_level`, `created_at`). A company is only considered part of a portfolio in the context of the querying tenant.
3. **Tenant-Isolated Contact Graphs:**
   - All network tables (`network_contacts`, `network_relationships`) are partitioned by `tenant_id`.
   - In-memory `NetworkX` graphs are instantiated per tenant context. The graph traversal engine never loads or mixes nodes from different tenants.
4. **Threat Model & Protections:**
   - **Cross-Tenant Data Leakage:** Prevented by mandatory `tenant_id = ?` filters at the database repository layer. Verified by automated tenant isolation test suites (`X-02`).
   - **Rest Encryption:** SQLite database files and encrypted backups utilize AES-256 at rest.
   - **No Marketing / Public Mixing:** Contacts are never aggregated into a global contact directory or shared with third-party advertising networks.

## Consequences
- **Positive:** Resolves the architectural contradiction; enables institutional-grade compliance and true multi-tenant deployment; preserves high-performance server-side graph intelligence.
- **Negative:** Every API query requires tenant context resolution.
