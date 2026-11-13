import pytest
from app.services.anomaly_detector import AnomalyDetector
from app.data.seed_data import seed_database
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_split_user_alert_state_dismissal():
    # User 1 dismisses Dixon volume surge anomaly
    user1 = "user-enam-01"
    user2 = "user-test-02"
    anomaly_id = "anom-dixon-vol-01"

    # Verify both users initially have the anomaly
    u1_before = client.get(f"/api/push/alerts?user_id={user1}").json()
    u2_before = client.get(f"/api/push/alerts?user_id={user2}").json()
    assert any(a["id"] == anomaly_id for a in u1_before)
    assert any(a["id"] == anomaly_id for a in u2_before)

    # User 1 dismisses the anomaly
    dismiss_res = client.post(f"/api/push/alerts/{anomaly_id}/dismiss?user_id={user1}")
    assert dismiss_res.status_code == 200

    # User 1 query: anomaly is gone
    u1_after = client.get(f"/api/push/alerts?user_id={user1}").json()
    assert not any(a["id"] == anomaly_id for a in u1_after)

    # User 2 query: anomaly remains ACTIVE and visible! (F-05 verified)
    u2_after = client.get(f"/api/push/alerts?user_id={user2}").json()
    assert any(a["id"] == anomaly_id for a in u2_after)
