import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
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
            SELECT trade_date, close_price, volume, volume_sma_20d, daily_return_pct, volume_multiple
            FROM market_eod
            WHERE ticker = ?
            ORDER BY trade_date DESC LIMIT 1;
            """, (ticker,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    def fetch_live_or_cached_eod(ticker: str) -> Dict[str, Any]:
        """
        Attempts to fetch the latest price and volume from yfinance.
        If unavailable, rate-limited, or offline, falls back seamlessly to the cached database record.
        """
        cached = MarketDataService.get_latest_eod(ticker)

        if yf is None:
            return cached or MarketDataService._default_market_metrics(ticker)

        try:
            # Indian tickers on Yahoo Finance use .NS for National Stock Exchange
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

                # Compute 20-day SMA of volume
                sma_20d = float(hist["Volume"].tail(20).mean()) if len(hist) >= 5 else volume
                volume_multiple = round(volume / sma_20d, 2) if sma_20d > 0 else 1.0
                trade_date = str(latest.name.date())

                # Upsert into SQLite
                with get_db() as conn:
                    conn.execute("""
                    INSERT OR REPLACE INTO market_eod (ticker, trade_date, close_price, volume, volume_sma_20d, daily_return_pct, volume_multiple)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    """, (ticker, trade_date, close_price, volume, sma_20d, daily_return_pct, volume_multiple))

                return {
                    "trade_date": trade_date,
                    "close_price": close_price,
                    "volume": volume,
                    "volume_sma_20d": sma_20d,
                    "daily_return_pct": daily_return_pct,
                    "volume_multiple": volume_multiple
                }
        except Exception:
            # Graceful fallback to cached data
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
