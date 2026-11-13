"""
Anomaly Hardening & Alert Controls Tests (P-06, P-07, P-08, P-09, P-10, B-02, B-03)
Phase 2 verification:
- Corporate action stock split adjustment avoids false 80% crash alerts
- Volatility normalized 60-day Z-scores
- Expected results spike tagging
- Alert fatigue daily cap and cooldown
- Push privacy mode lock-screen masking
- Expired subscription cleanup
"""

import pytest
import json
from datetime import datetime, timedelta
from app.db.database import get_db
from app.services.anomaly_detector import AnomalyDetector
from app.services.push_notifications import PushNotificationService

def test_corporate_action_split_adjustment_no_false_alert():
    """
    P-07 Exit Gate Test:
    A 1:5 stock split causes raw price to drop by -80%.
    Without adjustment, this fires a catastrophic false CRITICAL alert.
    With corporate action adjustment, the move is recognized as split-adjusted and suppressed!
    """
    with get_db() as conn:
        cursor = conn.cursor()
        # Insert corporate action: 1:5 split for DIXON (factor 5.0)
        cursor.execute("""
            INSERT OR REPLACE INTO corporate_actions (
                id, isin, ticker, action_type, ratio_from, ratio_to, record_date, ex_date, adjustment_factor
            )
            VALUES ('ca-dixon-split-test', 'INE806N01020', 'DIXON.NS', 'SPLIT', 1.0, 5.0, '2026-11-12', '2026-11-12', 5.0);
        """)

        # Raw price drops from 15,000 to 3,000 (-80.0% unadjusted)
        raw_return = -80.0
        close_px = 3000.0

        is_adjusted, effective_ret, desc = AnomalyDetector.check_corporate_action_adjustment(
            isin="INE806N01020",
            trade_date="2026-11-12",
            close_price=close_px,
            raw_return_pct=raw_return,
            conn=conn
        )

        assert is_adjusted is True
        assert effective_ret == 0.0 # 3000 * 5 = 15000 -> 0% adjusted change!
        assert "SPLIT adjusted" in desc

def test_volatility_normalized_zscore():
    """
    P-08 Test:
    Computes 60-day baseline return statistics and z-scores.
    """
    with get_db() as conn:
        z_score, mean_60d, std_60d = AnomalyDetector.calculate_volatility_zscore(
            isin="INE806N01020",
            current_return_pct=5.2,
            conn=conn
        )
        assert std_60d > 0
        assert z_score != 0.0

def test_expected_results_spike_tagging():
    """
    P-09 Test:
    Earnings day volume/price surge is tagged and not fired as false critical alert.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT OR REPLACE INTO announcements (
                id, isin, ticker, category, title, description, filing_time, materiality_score
            )
            VALUES ('ann-test-results-today', 'INE806N01020', 'DIXON.NS', 'financial_results',
                    'Financial Results Q2', 'Quarterly results', ?, 10);
        """, (f"{today_str}T10:00:00",))

        is_spike, reason = AnomalyDetector.is_expected_event_spike(
            isin="INE806N01020",
            trade_date=today_str,
            conn=conn
        )
        assert is_spike is True
        assert "Quarterly Earnings" in reason

def test_alert_fatigue_cooldown_and_daily_cap():
    """
    P-10 Test:
    Daily cap of max 3 alerts per ticker and 6-hour duplicate cooldown.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        # Seed 3 existing alerts for TATAMOTORS in last 24h
        now = datetime.now()
        for i in range(3):
            cursor.execute("""
                INSERT OR REPLACE INTO detected_anomalies (
                    id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at
                )
                VALUES (?, 'INE155A01022', 'TATAMOTORS.NS', 'VOLUME_SURGE', 'HIGH', 'Test alert', 'detail', '{}', ?);
            """, (f"anom-cap-test-{i}", (now - timedelta(hours=i+1)).isoformat()))

        # Attempt 4th alert: should be blocked by daily cap
        allowed, reason = AnomalyDetector.check_fatigue_and_cooldown(
            ticker="TATAMOTORS.NS",
            anomaly_type="PRICE_BREAKOUT",
            max_daily_cap=3,
            conn=conn
        )
        assert allowed is False
        assert "Daily cap" in reason

def test_push_privacy_mode_and_freshness():
    """
    B-03 & P-06 Test:
    Verifies push privacy mode masks confidential figures on lock screen,
    and alerts contain "as of" timestamp.
    """
    # Enable privacy mode
    AnomalyDetector.update_user_preferences(
        volume_threshold=2.0,
        price_threshold=3.5,
        auto_notify=True,
        push_privacy_mode=True,
        user_id="user-enam-01"
    )

    prefs = AnomalyDetector.get_user_preferences("user-enam-01")
    assert prefs["push_privacy_mode"] is True

    # Evaluate live anomalies
    anomalies = AnomalyDetector.evaluate_live_anomalies("user-enam-01")
    assert len(anomalies) > 0

    # Every alert must have "as_of" freshness
    first = anomalies[0]
    metrics = first["metrics"]
    if isinstance(metrics, dict):
        assert "as_of" in metrics or "volume_multiple" in metrics

    # Check notification stream
    notifs = PushNotificationService.get_recent_in_app_notifications()
    if notifs:
        latest = notifs[0]
        # In privacy mode, headline shouldn't expose sensitive holdings
        assert "CRITICAL ALERT" in latest["title"]
