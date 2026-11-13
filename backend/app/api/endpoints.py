from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from app.db.database import get_db
from app.services.market_data import MarketDataService
from app.services.filings_engine import FilingsEngine
from app.services.anomaly_detector import AnomalyDetector
from app.services.network_engine import network_engine
from app.services.research_engine import ResearchEngine
from app.services.push_notifications import PushNotificationService
from app.services.llm_router import llm_router
from app.models.schemas import PushSubscriptionPayload

router = APIRouter()

# --- Health & Status ---
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FINN Backend Engine",
        "llm_live": llm_router.is_live_llm_available(),
        "database": "connected"
    }

# --- Companies & Portfolio ---
@router.get("/companies")
def get_companies(portfolio_only: bool = False):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT ticker, name, sector, market_cap_tier, market_cap_cr, is_portfolio, screener_slug, description FROM companies"
        if portfolio_only:
            query += " WHERE is_portfolio = 1"
        query += " ORDER BY is_portfolio DESC, market_cap_cr DESC;"
        cursor.execute(query)
        rows = cursor.fetchall()

    companies = []
    for r in rows:
        c_dict = dict(r)
        eod = MarketDataService.get_latest_eod(c_dict["ticker"])
        if eod:
            c_dict["current_price"] = eod["close_price"]
            c_dict["change_pct"] = eod["daily_return_pct"]
            c_dict["volume"] = eod["volume"]
            c_dict["volume_multiple"] = eod["volume_multiple"]
        companies.append(c_dict)
    return companies

# --- Push: Windowed Digest & Pinned Alert ---
@router.get("/push/digest")
def get_digest(hours: int = Query(24, description="Time window in hours: 24, 168 (7d), 720 (30d)"), category: Optional[str] = Query(None)):
    return FilingsEngine.get_windowed_digest(hours=hours, category_filter=category)

@router.get("/push/pinned-alert")
def get_pinned_alert():
    """Returns the top pinned critical alert card for the digest header."""
    return AnomalyDetector.get_top_pinned_alert()

# --- Push: Ranked Alerts Stream ---
@router.get("/push/alerts")
def get_alerts(include_dismissed: bool = False):
    return AnomalyDetector.get_ranked_anomalies(include_dismissed=include_dismissed)

@router.post("/push/alerts/{anomaly_id}/pin")
def pin_alert(anomaly_id: str, is_pinned: bool = Body(..., embed=True)):
    AnomalyDetector.set_pinned_status(anomaly_id, is_pinned)
    return {"id": anomaly_id, "is_pinned": is_pinned}

@router.post("/push/alerts/{anomaly_id}/dismiss")
def dismiss_alert(anomaly_id: str):
    AnomalyDetector.dismiss_anomaly(anomaly_id)
    return {"id": anomaly_id, "is_dismissed": True}

# --- User Preferences & Thresholds ---
@router.get("/preferences")
def get_preferences():
    return AnomalyDetector.get_user_preferences()

@router.put("/preferences")
def update_preferences(
    volume_multiplier: float = Body(..., embed=True),
    price_move_pct: float = Body(..., embed=True),
    auto_notify_critical: bool = Body(True, embed=True)
):
    return AnomalyDetector.update_user_preferences(
        volume_threshold=volume_multiplier,
        price_threshold=price_move_pct,
        auto_notify=auto_notify_critical
    )

# --- Web Push Notifications (Beacon) ---
@router.get("/notifications/vapid-key")
def get_vapid_key():
    return {"public_key": PushNotificationService.get_vapid_public_key()}

@router.post("/notifications/subscribe")
def subscribe_push(payload: PushSubscriptionPayload):
    success = PushNotificationService.register_subscription(
        endpoint=payload.endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth
    )
    return {"success": success}

@router.post("/notifications/test")
def trigger_test_notification():
    sent = PushNotificationService.send_broadcast_alert(
        title="🔔 FINN Test Notification",
        body="Real-time Web Push is active! You will receive critical market and management anomalies instantly.",
        data={"type": "TEST"}
    )
    return {"dispatched_to": sent, "status": "success"}

# --- Pull: Grounded Primary Research ---
@router.get("/pull/research/{ticker}")
def get_company_research(ticker: str):
    return ResearchEngine.get_company_research(ticker)

# --- Nexus: Network Intelligence ---
@router.get("/network/feed")
def get_network_feed():
    return network_engine.get_network_feed()

@router.post("/network/contacts/{contact_id}/star")
def toggle_star_contact(contact_id: str):
    new_state = network_engine.toggle_star(contact_id)
    return {"id": contact_id, "is_starred": new_state}

@router.get("/network/who-to-call/{ticker}")
def get_who_to_call(ticker: str):
    return network_engine.get_who_to_call(ticker)

@router.get("/network/second-degree")
def get_second_degree_reach(
    target_person: str = Query(..., description="Target executive name"),
    target_role: str = Query("Executive", description="Target role"),
    target_company: str = Query("Company", description="Target company")
):
    return network_engine.get_second_degree_reach(target_person, target_role, target_company)

# --- Pipeline Runner (On-demand trigger for demo/eval) ---
@router.post("/pipeline/run")
def run_pipeline():
    anomalies = AnomalyDetector.evaluate_live_anomalies()
    return {
        "status": "completed",
        "anomalies_evaluated": len(anomalies),
        "anomalies": anomalies
    }
