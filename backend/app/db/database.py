import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

DB_PATH = os.environ.get("FINN_DB_PATH", str(Path(__file__).resolve().parent.parent.parent / "finn.db"))

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency between background writer and API readers
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes SQLite schema for FINN with multi-tenant isolation and ISIN company master."""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Tenants Table (F-03)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        # 2. Users Table (F-03)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'ANALYST',
            created_at TEXT NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );
        """)

        # 3. Companies Table — Keyed by ISIN Master (F-06)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            isin TEXT PRIMARY KEY,
            ticker TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            sector TEXT NOT NULL,
            market_cap_tier TEXT NOT NULL,
            market_cap_cr REAL NOT NULL,
            screener_slug TEXT NOT NULL,
            description TEXT NOT NULL
        );
        """)

        # 4. Company Ticker History (F-06 — rename handling)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_tickers_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isin TEXT NOT NULL,
            exchange TEXT NOT NULL,
            ticker TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            valid_to TEXT,
            is_primary INTEGER DEFAULT 1,
            FOREIGN KEY (isin) REFERENCES companies(isin)
        );
        """)

        # 5. Tenant Holdings Table — Confidential Portfolio Scoping (F-04)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenant_holdings (
            tenant_id TEXT NOT NULL,
            isin TEXT NOT NULL,
            ticker TEXT NOT NULL,
            shares_held REAL DEFAULT 0,
            conviction_level TEXT DEFAULT 'HIGH',
            created_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, isin),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
            FOREIGN KEY (isin) REFERENCES companies(isin)
        );
        """)

        # 6. Market EOD History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_eod (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isin TEXT NOT NULL,
            ticker TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            close_price REAL NOT NULL,
            volume INTEGER NOT NULL,
            volume_sma_20d REAL NOT NULL,
            daily_return_pct REAL NOT NULL,
            volume_multiple REAL NOT NULL,
            FOREIGN KEY (isin) REFERENCES companies(isin),
            UNIQUE(isin, trade_date)
        );
        """)

        # 7. Announcements & Filings Table (F-01, F-08 — SHA-256 Provenance)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id TEXT PRIMARY KEY,
            isin TEXT NOT NULL,
            ticker TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            filing_time TEXT NOT NULL,
            materiality_score INTEGER NOT NULL,
            content_hash TEXT,                -- SHA-256 hash of source filing
            financial_basis TEXT DEFAULT 'CONSOLIDATED', -- CONSOLIDATED or STANDALONE
            headline_metrics TEXT,            -- JSON
            executive_profile TEXT,           -- JSON
            network_connection TEXT,          -- JSON
            FOREIGN KEY (isin) REFERENCES companies(isin)
        );
        """)

        # 8. Concall Transcripts Table (F-08 — Content Hash)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS concall_transcripts (
            id TEXT PRIMARY KEY,
            isin TEXT NOT NULL,
            ticker TEXT NOT NULL,
            fiscal_quarter TEXT NOT NULL,
            transcript_date TEXT NOT NULL,
            content_hash TEXT,
            management_remarks TEXT,
            guidance_excerpts TEXT,
            analyst_qa_excerpts TEXT,
            FOREIGN KEY (isin) REFERENCES companies(isin)
        );
        """)

        # 9. Guidance Track Record (Narrative vs Numbers)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS guidance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isin TEXT NOT NULL,
            ticker TEXT NOT NULL,
            fiscal_quarter TEXT NOT NULL,
            metric TEXT NOT NULL,
            guidance_type TEXT NOT NULL DEFAULT 'NUMERIC', -- NUMERIC, RANGE, QUALITATIVE
            min_guidance REAL,
            max_guidance REAL,
            promised_guidance TEXT NOT NULL,
            delivered_actual TEXT NOT NULL,
            variance TEXT NOT NULL,
            status TEXT NOT NULL,              -- BEAT, MET, MISSED, PENDING
            management_quote TEXT NOT NULL,
            source_doc_ref TEXT,               -- Document and section/page
            delivery_notes TEXT NOT NULL,
            FOREIGN KEY (isin) REFERENCES companies(isin)
        );
        """)

        # 10. Detected Anomalies (Canonical Facts)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS detected_anomalies (
            id TEXT PRIMARY KEY,
            isin TEXT NOT NULL,
            ticker TEXT NOT NULL,
            anomaly_type TEXT NOT NULL,        -- VOLUME_SURGE, PRICE_BREAKOUT, MATERIAL_FILING, etc.
            severity TEXT NOT NULL,            -- CRITICAL, HIGH, MEDIUM
            headline TEXT NOT NULL,
            detail TEXT NOT NULL,
            metrics TEXT NOT NULL,             -- JSON
            created_at TEXT NOT NULL,
            FOREIGN KEY (isin) REFERENCES companies(isin)
        );
        """)

        # 11. User Alert State (F-05 — Decoupled Per-User Dismiss/Pin State)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_alert_state (
            user_id TEXT NOT NULL,
            anomaly_id TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            is_dismissed INTEGER DEFAULT 0,
            notified_at TEXT,
            PRIMARY KEY (user_id, anomaly_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (anomaly_id) REFERENCES detected_anomalies(id)
        );
        """)

        # 12. User Preferences & Thresholds Table (Per-User Scoped)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            volume_multiplier_threshold REAL DEFAULT 2.0,
            price_move_pct_threshold REAL DEFAULT 3.5,
            auto_notify_critical INTEGER DEFAULT 1,
            starred_tickers TEXT DEFAULT '[]',
            enabled_categories TEXT DEFAULT '["results","M&A","management_change","fund_raise","litigation","capex"]',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)

        # 13. Web Push Subscriptions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            endpoint TEXT PRIMARY KEY,
            user_id TEXT,
            p256dh TEXT NOT NULL,
            auth TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)

        # 14. Network Contacts — Tenant Isolated (F-02, F-03)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_contacts (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            current_title TEXT NOT NULL,
            current_company TEXT NOT NULL,
            current_company_ticker TEXT,
            relationship_strength INTEGER DEFAULT 3,
            is_starred INTEGER DEFAULT 0,
            past_companies TEXT,               -- JSON array of {company, role, start_year, end_year}
            education TEXT,                    -- JSON array of {institution, degree, year}
            themes TEXT,                       -- JSON array of strings
            relevance_score REAL DEFAULT 0.0,
            recent_development_summary TEXT,
            notes TEXT,
            last_verified TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );
        """)

        # 15. Network Relationships (Tenant-Scoped Edges)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            from_contact_id TEXT NOT NULL,
            to_contact_id TEXT NOT NULL,
            connection_type TEXT NOT NULL,     -- CLASSMATE, EX_COLLEAGUE, CO_INVESTOR, ADVISOR
            mutual_strength INTEGER DEFAULT 3,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
            FOREIGN KEY (from_contact_id) REFERENCES network_contacts(id),
            FOREIGN KEY (to_contact_id) REFERENCES network_contacts(id)
        );
        """)

        # 16. Corporate Actions Table (P-07 — Split & Bonus Adjustment)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS corporate_actions (
            id TEXT PRIMARY KEY,
            isin TEXT NOT NULL,
            ticker TEXT NOT NULL,
            action_type TEXT NOT NULL,         -- SPLIT, BONUS, RIGHTS
            ratio_from REAL NOT NULL,
            ratio_to REAL NOT NULL,
            record_date TEXT NOT NULL,
            ex_date TEXT NOT NULL,
            adjustment_factor REAL NOT NULL,
            FOREIGN KEY (isin) REFERENCES companies(isin)
        );
        """)

        # Indices for sub-millisecond query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_holdings_tenant ON tenant_holdings(tenant_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcements_isin ON announcements(isin);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcements_time ON announcements(filing_time DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_time ON detected_anomalies(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_eod_lookup ON market_eod(isin, trade_date DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_network_tenant ON network_contacts(tenant_id);")
