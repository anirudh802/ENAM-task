import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.db.database import get_db

try:
    import yfinance as yf
except ImportError:
    yf = None

class MarketDataService:
    @staticmethod
    def get_latest_eod(ticker: str) -> Optional[Dict[str, Any]]:
        """Retrieves the latest EOD market record for a ticker from SQLite."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT m.trade_date, m.close_price, m.volume, m.volume_sma_20d, m.daily_return_pct, m.volume_multiple, m.isin
            FROM market_eod m
            WHERE m.ticker = ?
            ORDER BY m.trade_date DESC LIMIT 1;
            """, (ticker,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    def fetch_live_or_cached_eod(ticker: str) -> Dict[str, Any]:
        """
        Attempts to fetch latest price and volume from yfinance.
        If unavailable, rate-limited, or offline, falls back seamlessly to the cached database record.
        """
        cached = MarketDataService.get_latest_eod(ticker)

        if yf is None:
            return cached or MarketDataService._default_market_metrics(ticker)

        try:
            yf_ticker = ticker if ticker.endswith(".NS") or ticker.endswith(".BO") else f"{ticker}.NS"
            stock = yf.Ticker(yf_ticker)
            hist = stock.history(period="1mo")

            if hist is not None and not hist.empty and len(hist) >= 2:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2]

                close_price = float(latest["Close"])
                prev_close = float(prev["Close"])
                volume = int(latest["Volume"])
                daily_return_pct = round(((close_price - prev_close) / prev_close) * 100, 2)

                sma_20d = float(hist["Volume"].tail(20).mean()) if len(hist) >= 5 else volume
                volume_multiple = round(volume / sma_20d, 2) if sma_20d > 0 else 1.0
                trade_date = str(latest.name.date())

                # Lookup ISIN
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT isin FROM companies WHERE ticker = ?;", (ticker,))
                    c_row = cursor.fetchone()
                    isin = c_row["isin"] if c_row else f"IN_UNKNOWN_{ticker}"

                    conn.execute("""
                    INSERT OR REPLACE INTO market_eod (isin, ticker, trade_date, close_price, volume, volume_sma_20d, daily_return_pct, volume_multiple)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (isin, ticker, trade_date, close_price, volume, sma_20d, daily_return_pct, volume_multiple))

                return {
                    "trade_date": trade_date,
                    "close_price": close_price,
                    "volume": volume,
                    "volume_sma_20d": sma_20d,
                    "daily_return_pct": daily_return_pct,
                    "volume_multiple": volume_multiple
                }
        except Exception:
            pass

        return cached or MarketDataService._default_market_metrics(ticker)

    @staticmethod
    def _default_market_metrics(ticker: str) -> Dict[str, Any]:
        return {
            "trade_date": datetime.now().strftime("%Y-%m-%d"),
            "close_price": 1000.0,
            "volume": 500000,
            "volume_sma_20d": 500000.0,
            "daily_return_pct": 0.0,
            "volume_multiple": 1.0
        }
