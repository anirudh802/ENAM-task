from fastapi.testclient import TestClient
from app.main import app
from app.data.seed_data import seed_database

client = TestClient(app)

def setup_module():
    seed_database()

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_companies_endpoint():
    response = client.get("/api/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) >= 18
    # Verify explicitly requested tickers are in the portfolio
    tickers = [c["ticker"] for c in companies]
    assert "RELIANCE.NS" in tickers
    assert "TATAMOTORS.NS" in tickers
    assert "DIXON.NS" in tickers
    assert "TRENT.NS" in tickers
    assert "KAYNES.NS" in tickers
    assert "CDSL.NS" in tickers

def test_digest_endpoint():
    response = client.get("/api/push/digest?hours=48")
    assert response.status_code == 200
    data = response.json()
    assert "material_filings" in data
    assert "routine_filings" in data
    assert data["total_count"] > 0

def test_pinned_alert_endpoint():
    response = client.get("/api/push/pinned-alert")
    assert response.status_code == 200
    alert = response.json()
    assert alert is not None
    assert alert["severity"] == "CRITICAL"

def test_preferences_endpoint():
    # 1. Get default preferences
    get_res = client.get("/api/preferences")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["volume_multiplier_threshold"] == 2.0

    # 2. Update preferences
    put_res = client.put("/api/preferences", json={
        "volume_multiplier": 3.0,
        "price_move_pct": 4.5,
        "auto_notify_critical": True
    })
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["volume_multiplier_threshold"] == 3.0
    assert updated["price_move_pct_threshold"] == 4.5

def test_research_endpoint():
    response = client.get("/api/pull/research/DIXON.NS")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "DIXON.NS"
    assert "narrative_vs_numbers" in data
    assert len(data["bull_case"]) > 0
    assert len(data["bear_case"]) > 0

def test_network_feed_and_starring():
    response = client.get("/api/network/feed")
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) > 0
    first_id = contacts[0]["id"]

    # Toggle star
    star_res = client.post(f"/api/network/contacts/{first_id}/star")
    assert star_res.status_code == 200
    assert "is_starred" in star_res.json()
