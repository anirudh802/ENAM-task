import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.services.push_notifications import PushNotificationService

class AnomalyDetector:
    @staticmethod
    def get_user_preferences() -> Dict[str, Any]:
        """Loads user-configurable thresholds from SQLite."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical, starred_tickers, enabled_categories
            FROM user_preferences WHERE id = 1;
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "volume_multiplier_threshold": row["volume_multiplier_threshold"],
                    "price_move_pct_threshold": row["price_move_pct_threshold"],
                    "auto_notify_critical": bool(row["auto_notify_critical"]),
                    "starred_tickers": json.loads(row["starred_tickers"] or "[]"),
                    "enabled_categories": json.loads(row["enabled_categories"] or "[]")
                }
        return {
            "volume_multiplier_threshold": 2.0,
            "price_move_pct_threshold": 3.5,
            "auto_notify_critical": True,
            "starred_tickers": [],
            "enabled_categories": ["results", "M&A", "management_change", "fund_raise", "litigation", "capex"]
        }

    @staticmethod
    def update_user_preferences(volume_threshold: float, price_threshold: float, auto_notify: bool) -> Dict[str, Any]:
        with get_db() as conn:
            conn.execute("""
            UPDATE user_preferences
            SET volume_multiplier_threshold = ?, price_move_pct_threshold = ?, auto_notify_critical = ?
            WHERE id = 1;
            """, (volume_threshold, price_threshold, 1 if auto_notify else 0))
        return AnomalyDetector.get_user_preferences()

    @staticmethod
    def get_ranked_anomalies(include_dismissed: bool = False) -> List[Dict[str, Any]]:
        """
        Returns anomalies with pinned items first, then ordered by severity (CRITICAL > HIGH > MEDIUM)
        and creation timestamp.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            query = """
            SELECT da.id, da.ticker, c.name as company_name, da.anomaly_type, da.severity,
                   da.headline, da.detail, da.metrics, da.created_at, da.is_pinned, da.is_dismissed
            FROM detected_anomalies da
            JOIN companies c ON da.ticker = c.ticker
            """
            if not include_dismissed:
                query += " WHERE da.is_dismissed = 0"

            query += """
            ORDER BY da.is_pinned DESC,
                     CASE da.severity
                         WHEN 'CRITICAL' THEN 1
                         WHEN 'HIGH' THEN 2
                         WHEN 'MEDIUM' THEN 3
                         ELSE 4
                     END,
                     da.created_at DESC;
            """
            cursor.execute(query)
            rows = cursor.fetchall()

        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "ticker": r["ticker"],
                "company_name": r["company_name"],
                "anomaly_type": r["anomaly_type"],
                "severity": r["severity"],
                "headline": r["headline"],
                "detail": r["detail"],
                "metrics": json.loads(r["metrics"]) if r["metrics"] else {},
                "created_at": r["created_at"],
                "is_pinned": bool(r["is_pinned"]),
                "is_dismissed": bool(r["is_dismissed"]),
            })
        return result

    @staticmethod
    def get_top_pinned_alert() -> Optional[Dict[str, Any]]:
        """Retrieves the single highest-priority pinned critical alert for the top digest card."""
        anomalies = AnomalyDetector.get_ranked_anomalies(include_dismissed=False)
        for a in anomalies:
            if a["is_pinned"] and a["severity"] == "CRITICAL":
                return a
        # Fallback to any unpinned CRITICAL alert if none are explicitly pinned
        for a in anomalies:
            if a["severity"] == "CRITICAL":
                return a
        return None

    @staticmethod
    def set_pinned_status(anomaly_id: str, is_pinned: bool) -> bool:
        with get_db() as conn:
            conn.execute("UPDATE detected_anomalies SET is_pinned = ? WHERE id = ?;", (1 if is_pinned else 0, anomaly_id))
        return True

    @staticmethod
    def dismiss_anomaly(anomaly_id: str) -> bool:
        with get_db() as conn:
            conn.execute("UPDATE detected_anomalies SET is_dismissed = 1 WHERE id = ?;", (anomaly_id,))
        return True

    @staticmethod
    def evaluate_live_anomalies() -> List[Dict[str, Any]]:
        """
        Evaluates the current state of market EOD data and recent announcements against
        user preferences, registering any new anomalies and notifying via Web Push.
        """
        prefs = AnomalyDetector.get_user_preferences()
        vol_threshold = prefs["volume_multiplier_threshold"]
        price_threshold = prefs["price_move_pct_threshold"]
        new_anomalies = []

        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Scan Market Technicals
            cursor.execute("""
            SELECT m.ticker, c.name as company_name, m.close_price, m.volume, m.volume_sma_20d, m.daily_return_pct, m.volume_multiple
            FROM market_eod m
            JOIN companies c ON m.ticker = c.ticker
            WHERE m.trade_date = (SELECT MAX(trade_date) FROM market_eod);
            """)
            market_rows = cursor.fetchall()

            for m in market_rows:
                ticker = m["ticker"]
                name = m["company_name"]
                vol_mult = m["volume_multiple"]
                ret_pct = m["daily_return_pct"]

                # Volume Surge Check
                if vol_mult >= vol_threshold:
                    anomaly_id = f"anom-vol-{ticker.split('.')[0].lower()}"
                    headline = f"{name}: {vol_mult}x Volume Surge ({ret_pct:+.1f}%)"
                    detail = f"Traded volume exceeded {vol_mult}x the 20-day moving average. Daily return: {ret_pct:+.2f}%."
                    severity = "CRITICAL" if vol_mult >= 3.0 else "HIGH"

                    cursor.execute("""
                    INSERT OR REPLACE INTO detected_anomalies (id, ticker, anomaly_type, severity, headline, detail, metrics, created_at, is_pinned, is_dismissed)
                    VALUES (?, ?, 'VOLUME_SURGE', ?, ?, ?, ?, ?, ?, 0);
                    """, (
                        anomaly_id, ticker, severity, headline, detail,
                        json.dumps({"volume_multiple": vol_mult, "daily_return_pct": ret_pct, "close": m["close_price"]}),
                        datetime.now().isoformat(),
                        1 if severity == "CRITICAL" else 0
                    ))
                    new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity})

                # Price Breakout / Shock Check
                if abs(ret_pct) >= price_threshold:
                    anomaly_id = f"anom-price-{ticker.split('.')[0].lower()}"
                    direction = "Breakout" if ret_pct > 0 else "Plunge"
                    severity = "CRITICAL" if abs(ret_pct) >= 5.0 else "HIGH"
                    headline = f"{name}: Sharp {ret_pct:+.1f}% Price {direction}"
                    detail = f"Stock experienced an abnormal intraday move of {ret_pct:+.2f}%. Volume multiple: {vol_mult}x."

                    cursor.execute("""
                    INSERT OR REPLACE INTO detected_anomalies (id, ticker, anomaly_type, severity, headline, detail, metrics, created_at, is_pinned, is_dismissed)
                    VALUES (?, ?, 'PRICE_BREAKOUT', ?, ?, ?, ?, ?, ?, 0);
                    """, (
                        anomaly_id, ticker, severity, headline, detail,
                        json.dumps({"daily_return_pct": ret_pct, "volume_multiple": vol_mult, "close": m["close_price"]}),
                        datetime.now().isoformat(),
                        1 if severity == "CRITICAL" else 0
                    ))
                    new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity})

        # Broadcast push notification if any CRITICAL anomaly was detected
        if prefs["auto_notify_critical"]:
            criticals = [a for a in new_anomalies if a["severity"] == "CRITICAL"]
            if criticals:
                top = criticals[0]
                PushNotificationService.send_broadcast_alert(
                    title=f"🚨 CRITICAL ALERT: {top['headline']}",
                    body="Immediate market or filing anomaly detected across your portfolio.",
                    data={"anomaly_id": top["id"]}
                )

        return AnomalyDetector.get_ranked_anomalies()
