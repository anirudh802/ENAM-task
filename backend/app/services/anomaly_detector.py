"""
Anomaly Detector & Hardened Alerts Pipeline (P-06, P-07, P-08, P-09, P-10)
Features:
- Corporate Action Price Adjustments (P-07: stock splits and bonus issues)
- Volatility-Normalized Z-Scores on 60-day historical window (P-08)
- Expected Event Spike Tagging & Suppression for Results/Expiry (P-09)
- Alert-Fatigue Controls: Cooldown and Daily Caps (P-10)
- Freshness timestamp ('as of' time) on every alert (P-06)
- Decoupled Per-User Alert State (F-05)
"""

import json
import uuid
import math
from typing import List, Dict, Any, Optional, Tuple
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
            SELECT volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical,
                   push_privacy_mode, max_daily_alerts_per_ticker, starred_tickers, enabled_categories
            FROM user_preferences WHERE user_id = ?;
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                keys = row.keys()
                return {
                    "volume_multiplier_threshold": row["volume_multiplier_threshold"],
                    "price_move_pct_threshold": row["price_move_pct_threshold"],
                    "auto_notify_critical": bool(row["auto_notify_critical"]),
                    "push_privacy_mode": bool(row["push_privacy_mode"]) if "push_privacy_mode" in keys else False,
                    "max_daily_alerts_per_ticker": row["max_daily_alerts_per_ticker"] if "max_daily_alerts_per_ticker" in keys else 3,
                    "starred_tickers": json.loads(row["starred_tickers"] or "[]"),
                    "enabled_categories": json.loads(row["enabled_categories"] or "[]")
                }
        return {
            "volume_multiplier_threshold": 2.0,
            "price_move_pct_threshold": 3.5,
            "auto_notify_critical": True,
            "push_privacy_mode": False,
            "max_daily_alerts_per_ticker": 3,
            "starred_tickers": [],
            "enabled_categories": ["results", "M&A", "management_change", "fund_raise", "litigation", "capex"]
        }

    @staticmethod
    def update_user_preferences(
        volume_threshold: float,
        price_threshold: float,
        auto_notify: bool,
        push_privacy_mode: bool = False,
        max_daily_cap: int = 3,
        user_id: str = DEFAULT_USER_ID
    ) -> Dict[str, Any]:
        with get_db() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO user_preferences (
                user_id, volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical,
                push_privacy_mode, max_daily_alerts_per_ticker
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """, (user_id, volume_threshold, price_threshold, 1 if auto_notify else 0,
                  1 if push_privacy_mode else 0, max_daily_cap))
        return AnomalyDetector.get_user_preferences(user_id)

    @staticmethod
    def check_corporate_action_adjustment(
        isin: str,
        trade_date: str,
        close_price: float,
        raw_return_pct: float,
        conn
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Adjusts price moves for corporate actions (P-07: stock splits, bonus issues).
        Returns: (is_adjusted, adjusted_return_pct, action_description)
        """
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action_type, ratio_from, ratio_to, adjustment_factor, record_date, ex_date
            FROM corporate_actions
            WHERE isin = ?;
        """, (isin,))
        ca_row = cursor.fetchone()

        if not ca_row:
            return False, raw_return_pct, None

        adj_factor = ca_row["adjustment_factor"]
        action_type = ca_row["action_type"]

        # Check if the raw drop matches the corporate action ratio
        # e.g., 1:5 split causes raw return of ~ -80.0%
        expected_unadjusted_drop = (1.0 - (1.0 / adj_factor)) * -100.0
        if math.isclose(raw_return_pct, expected_unadjusted_drop, abs_tol=5.0):
            # Compute adjusted return: (close * factor - prev_close) / prev_close
            adjusted_return_pct = round(((100.0 + raw_return_pct) * adj_factor) - 100.0, 2)
            desc = f"{action_type} adjusted (Ratio {ca_row['ratio_from']}:{ca_row['ratio_to']})"
            return True, adjusted_return_pct, desc

        return False, raw_return_pct, None

    @staticmethod
    def calculate_volatility_zscore(
        isin: str,
        current_return_pct: float,
        conn
    ) -> Tuple[float, float, float]:
        """
        Computes 60-day baseline return statistics excluding the current day (P-08).
        Returns: (z_score, mean_60d, std_60d)
        """
        cursor = conn.cursor()
        cursor.execute("""
            SELECT daily_return_pct
            FROM market_eod
            WHERE isin = ?
            ORDER BY trade_date DESC LIMIT 60 OFFSET 1;
        """, (isin,))
        returns = [r[0] for r in cursor.fetchall()]

        if not returns or len(returns) < 5:
            # Fallback when historical depth is insufficient
            return (round(current_return_pct / 1.5, 2), 0.0, 1.5)

        mean_ret = sum(returns) / len(returns)
        variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
        std_ret = math.sqrt(variance)

        if std_ret == 0:
            std_ret = 0.5

        z_score = round((current_return_pct - mean_ret) / std_ret, 2)
        return z_score, round(mean_ret, 2), round(std_ret, 2)

    @staticmethod
    def is_expected_event_spike(isin: str, trade_date: str, conn) -> Tuple[bool, Optional[str]]:
        """
        Detects scheduled corporate events like quarterly results days (P-09).
        Suppresses false CRITICAL alerts for anticipated high-volatility events.
        """
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, title
            FROM announcements
            WHERE isin = ? AND category IN ('financial_results', 'results')
            AND filing_time LIKE ?;
        """, (isin, f"{trade_date}%"))
        row = cursor.fetchone()

        if row:
            return True, "Quarterly Earnings Announcement Day"
        return False, None

    @staticmethod
    def check_fatigue_and_cooldown(
        ticker: str,
        anomaly_type: str,
        max_daily_cap: int,
        conn
    ) -> Tuple[bool, str]:
        """
        Alert fatigue controls (P-10):
        1. Maximum alerts per ticker per 24 hours.
        2. Cooldown of 6 hours for identical anomaly types on the same ticker.
        """
        cursor = conn.cursor()
        now = datetime.now()
        day_ago = (now - timedelta(hours=24)).isoformat()
        six_hours_ago = (now - timedelta(hours=6)).isoformat()

        # Check daily ticker cap
        cursor.execute("""
            SELECT COUNT(*) FROM detected_anomalies
            WHERE ticker = ? AND created_at >= ?;
        """, (ticker, day_ago))
        daily_count = cursor.fetchone()[0]
        if daily_count >= max_daily_cap:
            return False, f"Daily cap of {max_daily_cap} alerts reached for {ticker}"

        # Check cooldown for same anomaly type
        cursor.execute("""
            SELECT COUNT(*) FROM detected_anomalies
            WHERE ticker = ? AND anomaly_type = ? AND created_at >= ?;
        """, (ticker, anomaly_type, six_hours_ago))
        recent_same_type = cursor.fetchone()[0]
        if recent_same_type > 0:
            return False, f"Cooldown active: {anomaly_type} recently fired for {ticker}"

        return True, "Allowed"

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
            if a.get("is_pinned") and a.get("severity") == "CRITICAL":
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
            ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_dismissed = 1, is_pinned = 0;
            """, (user_id, anomaly_id))
        return True

    @staticmethod
    def evaluate_live_anomalies(user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
        """
        Evaluates current EOD market data against calibrated statistical thresholds.
        Includes corporate action adjustments, volatility Z-scores, expected spike suppression,
        and fatigue controls.
        """
        prefs = AnomalyDetector.get_user_preferences(user_id)
        vol_threshold = prefs["volume_multiplier_threshold"]
        price_threshold = prefs["price_move_pct_threshold"]
        daily_cap = prefs.get("max_daily_alerts_per_ticker", 3)
        new_anomalies = []

        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            SELECT m.isin, m.ticker, c.name as company_name, m.trade_date, m.close_price,
                   m.volume, m.volume_sma_20d, m.daily_return_pct, m.volume_multiple
            FROM market_eod m
            JOIN companies c ON m.isin = c.isin
            WHERE m.trade_date = (SELECT MAX(trade_date) FROM market_eod);
            """)
            market_rows = cursor.fetchall()

            for m in market_rows:
                isin = m["isin"]
                ticker = m["ticker"]
                name = m["company_name"]
                trade_date = m["trade_date"]
                vol_mult = m["volume_multiple"]
                raw_ret_pct = m["daily_return_pct"]
                close_px = m["close_price"]

                # 1. Corporate Action Price Adjustment (P-07)
                is_ca_adjusted, effective_ret_pct, ca_desc = AnomalyDetector.check_corporate_action_adjustment(
                    isin, trade_date, close_px, raw_ret_pct, conn
                )

                # 2. Volatility-Normalized Z-Score (P-08)
                z_score, mean_60d, std_60d = AnomalyDetector.calculate_volatility_zscore(
                    isin, effective_ret_pct, conn
                )

                # 3. Expected Event Spike Tagging (P-09)
                is_expected_spike, expected_reason = AnomalyDetector.is_expected_event_spike(
                    isin, trade_date, conn
                )

                # As of freshness timestamp (P-06)
                as_of_timestamp = f"{trade_date} 15:30 IST (EOD)"

                is_vol_surge = (vol_mult >= vol_threshold)
                price_condition = (abs(effective_ret_pct) >= price_threshold or abs(z_score) >= 2.5)

                # --- Consolidated Dual Technical Anomaly (Consolidates volume surge + price breakout) ---
                if is_vol_surge and price_condition:
                    allowed, reason = AnomalyDetector.check_fatigue_and_cooldown(
                        ticker, "DUAL_TECHNICAL_SURGE", daily_cap, conn
                    )
                    if allowed:
                        anomaly_id = f"anom-dual-{ticker.split('.')[0].lower()}-{trade_date}"
                        direction = "Breakout" if effective_ret_pct > 0 else "Plunge"
                        severity = "CRITICAL" if (vol_mult >= 3.0 or abs(z_score) >= 3.0) and not is_expected_spike else "HIGH"

                        headline = f"{name}: {effective_ret_pct:+.1f}% Price {direction} on {vol_mult}x Volume"
                        detail = f"Dual technical move: Traded volume reached {vol_mult}x 20-day SMA alongside {effective_ret_pct:+.2f}% return (Z-score: {z_score:+.1f}σ, 60-day σ: {std_60d}%)."
                        if is_ca_adjusted:
                            detail += f" [{ca_desc}]"
                        if is_expected_spike:
                            detail += f" [Tagged: {expected_reason}]"

                        metrics = {
                            "volume_multiple": vol_mult,
                            "daily_return_pct": effective_ret_pct,
                            "raw_return_pct": raw_ret_pct,
                            "z_score": z_score,
                            "sigma_60d": std_60d,
                            "close": close_px,
                            "as_of": as_of_timestamp,
                            "is_corporate_action_adjusted": is_ca_adjusted,
                            "is_expected_event_spike": is_expected_spike
                        }

                        cursor.execute("""
                        INSERT OR REPLACE INTO detected_anomalies (id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at)
                        VALUES (?, ?, ?, 'DUAL_TECHNICAL_SURGE', ?, ?, ?, ?, ?);
                        """, (
                            anomaly_id, isin, ticker, severity, headline, detail,
                            json.dumps(metrics), datetime.now().isoformat()
                        ))

                        if severity == "CRITICAL":
                            cursor.execute("""
                            INSERT INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed)
                            VALUES (?, ?, 1, 0)
                            ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_pinned = 1;
                            """, (user_id, anomaly_id))

                        # Enqueue into transactional outbox
                        now_str = datetime.now().isoformat()
                        cursor.execute("""
                        INSERT INTO notification_outbox (id, user_id, anomaly_id, payload, status, attempts, next_retry_at, created_at)
                        VALUES (?, ?, ?, ?, 'PENDING', 0, ?, ?);
                        """, (f"outbox-{uuid.uuid4().hex[:12]}", user_id, anomaly_id, json.dumps({"headline": headline, "ticker": ticker, "severity": severity}), now_str, now_str))

                        new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity, "ticker": ticker})

                # --- Single-Factor Volume Surge Evaluation ---
                elif is_vol_surge:
                    allowed, reason = AnomalyDetector.check_fatigue_and_cooldown(
                        ticker, "VOLUME_SURGE", daily_cap, conn
                    )
                    if allowed:
                        anomaly_id = f"anom-vol-{ticker.split('.')[0].lower()}-{trade_date}"
                        severity = "CRITICAL" if vol_mult >= 3.0 and not is_expected_spike else "HIGH"
                        if is_expected_spike and severity == "CRITICAL":
                            severity = "HIGH"

                        headline = f"{name}: {vol_mult}x Volume Surge ({effective_ret_pct:+.1f}%)"
                        detail = f"Traded volume reached {vol_mult}x 20-day SMA. Daily return: {effective_ret_pct:+.2f}% (Z-score: {z_score:+.1f}σ, 60-day σ: {std_60d}%)."
                        if is_expected_spike:
                            detail += f" [Tagged: {expected_reason}]"

                        metrics = {
                            "volume_multiple": vol_mult,
                            "daily_return_pct": effective_ret_pct,
                            "raw_return_pct": raw_ret_pct,
                            "z_score": z_score,
                            "sigma_60d": std_60d,
                            "close": close_px,
                            "as_of": as_of_timestamp,
                            "is_corporate_action_adjusted": is_ca_adjusted,
                            "is_expected_event_spike": is_expected_spike
                        }

                        cursor.execute("""
                        INSERT OR REPLACE INTO detected_anomalies (id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at)
                        VALUES (?, ?, ?, 'VOLUME_SURGE', ?, ?, ?, ?, ?);
                        """, (
                            anomaly_id, isin, ticker, severity, headline, detail,
                            json.dumps(metrics), datetime.now().isoformat()
                        ))

                        if severity == "CRITICAL":
                            cursor.execute("""
                            INSERT INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed)
                            VALUES (?, ?, 1, 0)
                            ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_pinned = 1;
                            """, (user_id, anomaly_id))

                        # Enqueue into transactional outbox
                        now_str = datetime.now().isoformat()
                        cursor.execute("""
                        INSERT INTO notification_outbox (id, user_id, anomaly_id, payload, status, attempts, next_retry_at, created_at)
                        VALUES (?, ?, ?, ?, 'PENDING', 0, ?, ?);
                        """, (f"outbox-{uuid.uuid4().hex[:12]}", user_id, anomaly_id, json.dumps({"headline": headline, "ticker": ticker, "severity": severity}), now_str, now_str))

                        new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity, "ticker": ticker})

                # --- Single-Factor Price Breakout Evaluation (Normalized & CA Adjusted) ---
                elif price_condition:
                    allowed, reason = AnomalyDetector.check_fatigue_and_cooldown(
                        ticker, "PRICE_BREAKOUT", daily_cap, conn
                    )
                    if allowed:
                        anomaly_id = f"anom-price-{ticker.split('.')[0].lower()}-{trade_date}"
                        direction = "Breakout" if effective_ret_pct > 0 else "Plunge"
                        severity = "CRITICAL" if abs(z_score) >= 3.0 and not is_expected_spike else "HIGH"

                        headline = f"{name}: {effective_ret_pct:+.1f}% Price {direction} (Z: {z_score:+.1f}σ)"
                        detail = f"Abnormal move of {effective_ret_pct:+.2f}% (60-day σ: {std_60d}%). Volume multiple: {vol_mult}x."
                        if is_ca_adjusted:
                            detail += f" [{ca_desc}]"
                        if is_expected_spike:
                            detail += f" [Tagged: {expected_reason}]"

                        metrics = {
                            "daily_return_pct": effective_ret_pct,
                            "raw_return_pct": raw_ret_pct,
                            "z_score": z_score,
                            "sigma_60d": std_60d,
                            "volume_multiple": vol_mult,
                            "close": close_px,
                            "as_of": as_of_timestamp,
                            "is_corporate_action_adjusted": is_ca_adjusted,
                            "is_expected_event_spike": is_expected_spike
                        }

                        cursor.execute("""
                        INSERT OR REPLACE INTO detected_anomalies (id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at)
                        VALUES (?, ?, ?, 'PRICE_BREAKOUT', ?, ?, ?, ?, ?);
                        """, (
                            anomaly_id, isin, ticker, severity, headline, detail,
                            json.dumps(metrics), datetime.now().isoformat()
                        ))

                        if severity == "CRITICAL":
                            cursor.execute("""
                            INSERT INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed)
                            VALUES (?, ?, 1, 0)
                            ON CONFLICT(user_id, anomaly_id) DO UPDATE SET is_pinned = 1;
                            """, (user_id, anomaly_id))

                        # Enqueue into transactional outbox
                        now_str = datetime.now().isoformat()
                        cursor.execute("""
                        INSERT INTO notification_outbox (id, user_id, anomaly_id, payload, status, attempts, next_retry_at, created_at)
                        VALUES (?, ?, ?, ?, 'PENDING', 0, ?, ?);
                        """, (f"outbox-{uuid.uuid4().hex[:12]}", user_id, anomaly_id, json.dumps({"headline": headline, "ticker": ticker, "severity": severity}), now_str, now_str))

                        new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity, "ticker": ticker})

                        new_anomalies.append({"id": anomaly_id, "headline": headline, "severity": severity, "ticker": ticker})

        # Push Notification with Privacy Mode check (B-03)
        if prefs["auto_notify_critical"]:
            criticals = [a for a in new_anomalies if a["severity"] == "CRITICAL"]
            if criticals:
                top = criticals[0]
                if prefs.get("push_privacy_mode"):
                    title = "🚨 CRITICAL ALERT"
                    body = "Critical anomaly detected for your portfolio. Tap to open FINN securely."
                else:
                    title = f"🚨 CRITICAL ALERT: {top['headline']}"
                    body = "Immediate market technical anomaly detected across your portfolio."

                PushNotificationService.send_broadcast_alert(
                    title=title,
                    body=body,
                    data={"anomaly_id": top["id"], "ticker": top.get("ticker")}
                )

        return AnomalyDetector.get_ranked_anomalies(user_id=user_id)
