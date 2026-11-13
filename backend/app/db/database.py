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
    """Initializes SQLite schema for FINN."""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Companies Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            ticker TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            sector TEXT NOT NULL,
            market_cap_tier TEXT NOT NULL,
            market_cap_cr REAL NOT NULL,
            is_portfolio INTEGER DEFAULT 1,
            screener_slug TEXT NOT NULL,
            description TEXT NOT NULL
        );
        """)

        # 2. Market EOD History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_eod (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            close_price REAL NOT NULL,
            volume INTEGER NOT NULL,
            volume_sma_20d REAL NOT NULL,
            daily_return_pct REAL NOT NULL,
            volume_multiple REAL NOT NULL,
            FOREIGN KEY (ticker) REFERENCES companies(ticker),
            UNIQUE(ticker, trade_date)
        );
        """)

        # 3. Announcements & Filings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            filing_time TEXT NOT NULL,
            is_material INTEGER DEFAULT 0,
            materiality_score INTEGER NOT NULL,
            headline_metrics TEXT,          -- JSON
            executive_profile TEXT,         -- JSON
            network_connection TEXT,        -- JSON
            FOREIGN KEY (ticker) REFERENCES companies(ticker)
        );
        """)

        # 4. Concall Transcripts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS concall_transcripts (
            id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            fiscal_quarter TEXT NOT NULL,
            transcript_date TEXT NOT NULL,
            management_remarks TEXT,
            guidance_excerpts TEXT,
            analyst_qa_excerpts TEXT,
            FOREIGN KEY (ticker) REFERENCES companies(ticker)
        );
        """)

        # 5. Guidance Track Record (Narrative vs Numbers)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS guidance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            fiscal_quarter TEXT NOT NULL,
            metric TEXT NOT NULL,
            promised_guidance TEXT NOT NULL,
            delivered_actual TEXT NOT NULL,
            variance TEXT NOT NULL,
            status TEXT NOT NULL,            -- BEAT, MET, MISSED, PENDING
            management_quote TEXT NOT NULL,
            delivery_notes TEXT NOT NULL,
            FOREIGN KEY (ticker) REFERENCES companies(ticker)
        );
        """)

        # 6. Detected Anomalies Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS detected_anomalies (
            id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            anomaly_type TEXT NOT NULL,      -- VOLUME_SURGE, PRICE_BREAKOUT, MATERIAL_FILING, etc.
            severity TEXT NOT NULL,          -- CRITICAL, HIGH, MEDIUM
            headline TEXT NOT NULL,
            detail TEXT NOT NULL,
            metrics TEXT NOT NULL,           -- JSON
            created_at TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            is_dismissed INTEGER DEFAULT 0,
            FOREIGN KEY (ticker) REFERENCES companies(ticker)
        );
        """)

        # 7. User Preferences & Thresholds Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            volume_multiplier_threshold REAL DEFAULT 2.0,
            price_move_pct_threshold REAL DEFAULT 3.5,
            auto_notify_critical INTEGER DEFAULT 1,
            starred_tickers TEXT DEFAULT '[]',
            enabled_categories TEXT DEFAULT '["results","M&A","management_change","fund_raise","litigation","capex"]'
        );
        """)
        # Ensure default preferences exist
        cursor.execute("""
        INSERT OR IGNORE INTO user_preferences (id, volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical)
        VALUES (1, 2.0, 3.5, 1);
        """)

        # 8. Web Push Subscriptions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            endpoint TEXT PRIMARY KEY,
            p256dh TEXT NOT NULL,
            auth TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        # 9. Network Contacts (Private Domain)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            current_title TEXT NOT NULL,
            current_company TEXT NOT NULL,
            current_company_ticker TEXT,
            relationship_strength INTEGER DEFAULT 3,
            is_starred INTEGER DEFAULT 0,
            past_companies TEXT,             -- JSON array of {company, role, start_year, end_year}
            education TEXT,                  -- JSON array of {institution, degree, year}
            themes TEXT,                     -- JSON array of strings
            relevance_score REAL DEFAULT 0.0,
            recent_development_summary TEXT,
            notes TEXT
        );
        """)

        # 10. Network Relationships (Edges)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_contact_id TEXT NOT NULL,
            to_contact_id TEXT NOT NULL,
            connection_type TEXT NOT NULL,   -- CLASSMATE, EX_COLLEAGUE, CO_INVESTOR, ADVISOR
            mutual_strength INTEGER DEFAULT 3,
            FOREIGN KEY (from_contact_id) REFERENCES network_contacts(id),
            FOREIGN KEY (to_contact_id) REFERENCES network_contacts(id)
        );
        """)

        # Create indices for sub-millisecond query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcements_ticker ON announcements(ticker);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcements_time ON announcements(filing_time DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_time ON detected_anomalies(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_eod_lookup ON market_eod(ticker, trade_date DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guidance_ticker ON guidance_history(ticker);")
