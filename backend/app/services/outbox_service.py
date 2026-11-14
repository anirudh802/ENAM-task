import json
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from app.db.database import get_db

class NotificationOutboxService:
    """
    Transactional Outbox Pattern for Non-Blocking Alert Delivery:
    - Writes notification payload atomically with anomaly detection
    - Background dispatcher drains PENDING notifications
    - Automatic purge of dead (HTTP 410/404) subscriptions
    - Exponential backoff retry on 429 / 5xx gateway errors
    """

    @classmethod
    def enqueue(cls, user_id: str, anomaly_id: str, payload: Dict[str, Any]) -> str:
        outbox_id = f"outbox-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO notification_outbox (id, user_id, anomaly_id, payload, status, attempts, next_retry_at, created_at)
            VALUES (?, ?, ?, ?, 'PENDING', 0, ?, ?);
            """, (outbox_id, user_id, anomaly_id, json.dumps(payload), now_iso, now_iso))
        return outbox_id

    @classmethod
    def get_pending(cls, limit: int = 25) -> List[Dict[str, Any]]:
        now_iso = datetime.now(timezone.utc).isoformat()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, user_id, anomaly_id, payload, attempts, next_retry_at
            FROM notification_outbox
            WHERE status = 'PENDING' AND next_retry_at <= ?
            ORDER BY created_at ASC
            LIMIT ?;
            """, (now_iso, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    @classmethod
    def mark_sent(cls, outbox_id: str) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE notification_outbox
            SET status = 'SENT', sent_at = ?
            WHERE id = ?;
            """, (now_iso, outbox_id))

    @classmethod
    def mark_retry(cls, outbox_id: str, attempts: int, error: str) -> None:
        # Exponential backoff: 2s, 8s, 32s, max 3 attempts
        if attempts >= 3:
            status = 'FAILED'
            next_retry = datetime.now(timezone.utc) + timedelta(days=365)
        else:
            status = 'PENDING'
            delay_sec = 2 ** (attempts * 2)
            next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay_sec)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE notification_outbox
            SET status = ?, attempts = ?, next_retry_at = ?, error_message = ?
            WHERE id = ?;
            """, (status, attempts, next_retry.isoformat(), error[:500], outbox_id))

    @classmethod
    def purge_dead_subscription(cls, user_id: str) -> None:
        """Purges 410 Gone / 404 Not Found push endpoints."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM push_subscriptions WHERE user_id = ?;", (user_id,))

    @classmethod
    def get_outbox_stats(cls) -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM notification_outbox WHERE status = 'PENDING';")
            pending = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM notification_outbox WHERE status = 'SENT';")
            sent = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM notification_outbox WHERE status = 'FAILED';")
            failed = cursor.fetchone()["count"]

            return {
                "pending_notifications": pending,
                "sent_notifications": sent,
                "failed_notifications": failed
            }

outbox_service = NotificationOutboxService()
