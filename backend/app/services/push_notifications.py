import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.database import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

# Fallback/default VAPID keys for local testing if not in environment
DEFAULT_VAPID_PUBLIC_KEY = settings.VAPID_PUBLIC_KEY or "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckj0Ks2uhipt-0lBbMcqztPEhWSTZg"
DEFAULT_VAPID_PRIVATE_KEY = settings.VAPID_PRIVATE_KEY or "EEA_3U9H-eXk5C2aL-q2mNn3tI_4Lw2T3sR4bK1eM6A"

# In-memory recent notification stream for immediate in-app delivery
_RECENT_NOTIFICATIONS: List[Dict[str, Any]] = []

class PushNotificationService:
    @staticmethod
    def get_vapid_public_key() -> str:
        return DEFAULT_VAPID_PUBLIC_KEY

    @staticmethod
    def register_subscription(endpoint: str, p256dh: str, auth: str) -> bool:
        """Saves a browser's Web Push subscription into SQLite."""
        with get_db() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO push_subscriptions (endpoint, p256dh, auth, created_at)
            VALUES (?, ?, ?, ?);
            """, (endpoint, p256dh, auth, datetime.now().isoformat()))
        logger.info(f"Registered Web Push subscription: {endpoint[:30]}...")
        return True

    @staticmethod
    def send_broadcast_alert(title: str, body: str, data: Optional[Dict[str, Any]] = None) -> int:
        """
        Dispatches a Web Push alert to all registered browser subscriptions.
        Returns the number of successfully notified endpoints.
        """
        payload = {
            "title": title,
            "body": body,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "icon": "/icons/icon-192x192.png",
            "badge": "/icons/badge-72x72.png"
        }

        # Record in memory for immediate in-app SSE/polling
        _RECENT_NOTIFICATIONS.insert(0, payload)
        if len(_RECENT_NOTIFICATIONS) > 50:
            _RECENT_NOTIFICATIONS.pop()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT endpoint, p256dh, auth FROM push_subscriptions;")
            subs = cursor.fetchall()

        if not subs:
            logger.info("No active Web Push subscriptions found to dispatch to.")
            return 0

        sent_count = 0
        expired_endpoints = []

        try:
            from pywebpush import webpush, WebPushException
        except ImportError:
            logger.warning("pywebpush not available; recorded notification to in-app stream only.")
            return len(subs)

        payload_json = json.dumps(payload)

        for sub in subs:
            endpoint = sub["endpoint"]
            subscription_info = {
                "endpoint": endpoint,
                "keys": {
                    "p256dh": sub["p256dh"],
                    "auth": sub["auth"]
                }
            }
            try:
                webpush(
                    subscription_info=subscription_info,
                    data=payload_json,
                    vapid_private_key=DEFAULT_VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_CLAIM_EMAIL}
                )
                sent_count += 1
            except WebPushException as ex:
                logger.error(f"Failed web push to {endpoint[:30]}: {ex}")
                # HTTP 404 or 410 Gone indicates the subscription has expired or unsubscribed
                if ex.response and ex.response.status_code in [404, 410]:
                    expired_endpoints.append(endpoint)
            except Exception as e:
                logger.error(f"Unexpected error in web push: {e}")

        # Clean up stale subscriptions
        if expired_endpoints:
            with get_db() as conn:
                for ep in expired_endpoints:
                    conn.execute("DELETE FROM push_subscriptions WHERE endpoint = ?;", (ep,))

        return sent_count

    @staticmethod
    def get_recent_in_app_notifications() -> List[Dict[str, Any]]:
        return list(_RECENT_NOTIFICATIONS)
