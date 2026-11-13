import pytest
from app.services.network_engine import network_engine
from app.db.database import get_db
from app.data.seed_data import seed_database
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_tenant_portfolio_holdings_isolation():
    # 1. Query companies for ENAM tenant (tenant-enam-01)
    res_enam = client.get("/api/companies?portfolio_only=true&tenant_id=tenant-enam-01")
    assert res_enam.status_code == 200
    enam_companies = res_enam.json()
    assert len(enam_companies) == 18
    for c in enam_companies:
        assert c["is_portfolio"] is True

    # 2. Query companies for Peer tenant (tenant-test-02)
    res_peer = client.get("/api/companies?portfolio_only=true&tenant_id=tenant-test-02")
    assert res_peer.status_code == 200
    peer_companies = res_peer.json()
    # Tenant B has no holdings seeded; must return 0 holdings!
    assert len(peer_companies) == 0

def test_tenant_network_graph_isolation():
    # 1. ENAM tenant query: must return ENAM contacts and NEVER peer contacts
    enam_contacts = network_engine.get_network_feed(tenant_id="tenant-enam-01")
    enam_names = [c["name"] for c in enam_contacts]
    assert "Ananya Roy" in enam_names
    assert "Rohan Deshmukh" in enam_names
    # Peer fund contact must NOT leak into ENAM network!
    assert "Confidential Peer Advisor" not in enam_names

    # 2. Peer tenant query: must return ONLY peer contacts
    peer_contacts = network_engine.get_network_feed(tenant_id="tenant-test-02")
    peer_names = [c["name"] for c in peer_contacts]
    assert "Confidential Peer Advisor" in peer_names
    assert "Ananya Roy" not in peer_names
