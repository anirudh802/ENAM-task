import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.services.push_notifications import PushNotificationService

DEFAULT_USER_ID = "user-enam-01"
DEFAULT_TENANT_ID = "tenant-enam-01"

class AnomalyDetector:
    @staticmethod
    def get_user_preferences(user_id: str = DEFAULT_USER_ID) -> Dict[str, Any]:
        """Loads user-configurable thresholds from SQLite for the specific user."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical, starred_tickers, enabled_categories
            FROM user_preferences WHERE user_id = ?;
            """, (user_id,))
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
    def update_user_preferences(
        volume_threshold: float,
        price_threshold: float,
        auto_notify: bool,
        user_id: str = DEFAULT_USER_ID
    ) -> Dict[str, Any]:
        with get_db() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO user_preferences (user_id, volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical)
            VALUES (?, ?, ?, ?);
            """, (user_id, volume_threshold, price_threshold, 1 if auto_notify else 0))
        return AnomalyDetector.get_user_preferences(user_id)

    @staticmethod
    def get_ranked_anomalies(user_id: str = DEFAULT_USER_ID, include_dismissed: bool = False) -> List[Dict[str, Any]]:
        """
        Returns anomalies joined with user_alert_state (F-05: split alert state).
        One user's dismissal or pin state does not affect other users.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            query = """
            SELECT da.id, da.isin, da.ticker, c.name as company_name, da.anomaly_type, da.severity,
                   da.headline, da.detail, da.metrics, da.created_at,
                   COALESCE(uas.is_pinned, 0) as is_pinned,
                   COALESCE(uas.is_dismissed, 0) as is_dismissed
            FROM detected_anomalies da
            JOIN companies c ON da.isin = c.isin
            LEFT JOIN user_alert_state uas ON da.id = uas.anomaly_id AND uas.user_id = ?
            """
            params: List[Any] = [user_id]
            if not include_dismissed:
                query += " WHERE COALESCE(uas.is_dismissed, 0) = 0"

            query += """
            ORDER BY COALESCE(uas.is_pinned, 0) DESC,
                     CASE da.severity
                         WHEN 'CRITICAL' THEN 1
                         WHEN 'HIGH' THEN 2
                         WHEN 'MEDIUM' THEN 3
                         ELSE 4
                     END,
                     da.created_at DESC;
            """
            cursor.execute(query, params)
            rows = cursor.fetchall()

        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "isin": r["isin"],
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
    def get_top_pinned_alert(user_id: str = DEFAULT_USER_ID) -> Optional[Dict[str, Any]]:
        """Retrieves the highest-priority pinned critical alert for the specific user."""
        anomalies = AnomalyDetector.get_ranked_anomalies(user_id=user_id, include_dismissed=False)
        for a in anomalies:
            if a["is_pinned"] and a["severity"] == "CRITICAL":
                return a
        for a in anomalies:
            if a["severity"] == "CRITICAL":
                return a
        return None

    @staticmethod
    def set_pinned_status(anomaly_id: str, is_pinned: bool, user_id: str = DEFAULT_USER_ID) -> bool:
        """Sets pin status on user_alert_state (F-05)."""
        with get_db() as conn:
            conn.execute("""
            INSERT INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_pinned = excluded.is_pinned;
            """, (user_id, anomaly_id, 1 if is_pinned else 0))
        return True

    @staticmethod
    def dismiss_anomaly(anomaly_id: str, user_id: str = DEFAULT_USER_ID) -> bool:
        """Dismisses an alert for this user only without affecting colleagues."""
        with get_db() as conn:
            conn.execute("""
            INSERT INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed)
            VALUES (?, ?, 0, 1)
            ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_dismissed = 1;
            """, (user_id, anomaly_id))
        return True

    @staticmethod
    def evaluate_live_anomalies(user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
        """
        Evaluates current EOD market data against user-defined thresholds.
        Writes canonical facts to detected_anomalies and pins critical alerts in user_alert_state.
        """
        prefs = AnomalyDetector.get_user_preferences(user_id)
        vol_threshold = prefs["volume_multiplier_threshold"]
        price_threshold = prefs["price_move_pct_threshold"]
        new_anomalies = []

        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            SELECT m.isin, m.ticker, c.name as company_name, m.close_price, m.volume, m.volume_sma_20d, m.daily_return_pct, m.volume_multiple
            FROM market_eod m
            JOIN companies c ON m.isin = c.isin
            WHERE m.trade_date = (SELECT MAX(trade_date) FROM market_eod);
            """)
            market_rows = cursor.fetchall()

            for m in market_rows:
                isin = m["isin"]
                ticker = m["ticker"]
                name = m["company_name"]
                vol_mult = m["volume_multiple"]
                ret_pct = m["daily_return_pct"]

                # Volume Surge Check
                if vol_mult >= vol_threshold:
                    anomaly_id = f"anom-vol-{ticker.split('.')[0].lower()}"
                    headline = f"{name}: {vol_mult}x Volume Surge ({ret_pct:+.1f}%)"
                    detail = f"Traded volume reached {vol_mult}x the 20-day moving average. Daily return: {ret_pct:+.2f}%."
                    severity = "CRITICAL" if vol_mult >= 3.0 else "HIGH"

                    cursor.execute("""
                    INSERT OR REPLACE INTO detected_anomalies (id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at)
                    VALUES (?, ?, ?, 'VOLUME_SURGE', ?, ?, ?, ?, ?);
                    """, (
                        anomaly_id, isin, ticker, severity, headline, detail,
                        json.dumps({"volume_multiple": vol_mult, "daily_return_pct": ret_pct, "close": m["close_price"]}),
                        datetime.now().isoformat()
                    ))

                    if severity == "CRITICAL":
                        cursor.execute("""
                        INSERT INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed)
                        VALUES (?, ?, 1, 0)
                        ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_pinned = 1;
                        """, (user_id, anomaly_id))

                    new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity})

                # Price Breakout Check
                if abs(ret_pct) >= price_threshold:
                    anomaly_id = f"anom-price-{ticker.split('.')[0].lower()}"
                    direction = "Breakout" if ret_pct > 0 else "Plunge"
                    severity = "CRITICAL" if abs(ret_pct) >= 5.0 else "HIGH"
                    headline = f"{name}: Sharp {ret_pct:+.1f}% Price {direction}"
                    detail = f"Stock experienced an abnormal intraday move of {ret_pct:+.2f}%. Volume multiple: {vol_mult}x."

                    cursor.execute("""
                    INSERT OR REPLACE INTO detected_anomalies (id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at)
                    VALUES (?, ?, ?, 'PRICE_BREAKOUT', ?, ?, ?, ?, ?);
                    """, (
                        anomaly_id, isin, ticker, severity, headline, detail,
                        json.dumps({"daily_return_pct": ret_pct, "volume_multiple": vol_mult, "close": m["close_price"]}),
                        datetime.now().isoformat()
                    ))

                    if severity == "CRITICAL":
                        cursor.execute("""
                        INSERT INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed)
                        VALUES (?, ?, 1, 0)
                        ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_pinned = 1;
                        """, (user_id, anomaly_id))

                    new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity})

        if prefs["auto_notify_critical"]:
            criticals = [a for a in new_anomalies if a["severity"] == "CRITICAL"]
            if criticals:
                top = criticals[0]
                PushNotificationService.send_broadcast_alert(
                    title=f"🚨 CRITICAL ALERT: {top['headline']}",
                    body="Immediate market or filing anomaly detected across your portfolio.",
                    data={"anomaly_id": top["id"]}
                )

        return AnomalyDetector.get_ranked_anomalies(user_id=user_id)
