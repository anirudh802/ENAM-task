"""
Nexus Intelligence & Compliance Tests (N-01 through N-07)
Phase 3 Verification:
- Documented relevance score formula (N-03)
- SEBI MNPI guardrails, restricted list, and audit logging (N-06)
- Function and tenure-based who-to-call ranking (N-05)
- CSV contact import and staleness detection (N-01)
- DPDP Act data portability export and erasure (N-07)
- Second-degree network reach (N-02)
"""

import pytest
from app.db.database import get_db
from app.services.network_engine import NetworkEngine, network_engine

def test_relevance_score_formula_fixed_inputs():
    """
    N-03 Test:
    Formula: (Tenure * 0.25) + (Seniority * 0.25) + (Strength * 0.25) + (Materiality * 0.25) + Starred (+2.0)
    """
    # 1. Non-starred CXO, 5 years tenure, strength 5, materiality 10
    # Tenure score: 5 * 1.5 = 7.5
    # Seniority score: 10.0
    # Strength score: 5 * 2.0 = 10.0
    # Materiality: 10.0
    # Expected: (7.5*0.25) + (10*0.25) + (10*0.25) + (10*0.25) = 1.875 + 2.5 + 2.5 + 2.5 = 9.375 -> 9.38
    score = NetworkEngine.calculate_relevance_score(
        tenure_years=5.0,
        is_cxo_or_lead=True,
        relationship_strength=5,
        event_materiality=10,
        is_starred=False
    )
    assert score == 9.38

    # 2. Starred boost (+2.0) capped at 10.0
    starred_score = NetworkEngine.calculate_relevance_score(
        tenure_years=5.0,
        is_cxo_or_lead=True,
        relationship_strength=5,
        event_materiality=10,
        is_starred=True
    )
    assert starred_score == 10.0

def test_sebi_mnpi_guardrails_and_restricted_list():
    """
    N-06 Test:
    SEBI PIT guardrails:
    - Current employee of target is flagged as CURRENT_INSIDER with caution notice.
    - Former employee is classified as FORMER_EMPLOYEE_SAFE.
    - Restricted list match blocks calling suggestions.
    """
    # 1. Who to call for Dixon without restriction
    dixon_call = network_engine.get_who_to_call("DIXON.NS", tenant_id="tenant-enam-01")
    assert dixon_call["is_restricted"] is False
    assert len(dixon_call["direct_contacts"]) > 0

    # Rohan Deshmukh is former employee of Dixon -> FORMER_EMPLOYEE_SAFE
    rohan = next((c for c in dixon_call["direct_contacts"] if "Rohan" in c["name"]), None)
    assert rohan is not None
    assert rohan["compliance_role"] == "FORMER_EMPLOYEE_SAFE"
    assert rohan["compliance_status"] == "CLEAR"
    assert dixon_call["compliance_status"] == "CLEAR"

    # Verify sector-level questions (no capacity utilization / yield)
    assert any("component lead times" in q for q in dixon_call["suggested_questions"])
    assert any("festive retail sell-through" in q for q in dixon_call["suggested_questions"])
    assert not any("capacity" in q.lower() or "yield" in q.lower() or "deferral" in q.lower() for q in dixon_call["suggested_questions"])

    # 2. Restricted list match blocks suggestions
    blocked_call = network_engine.get_who_to_call(
        "DIXON.NS",
        tenant_id="tenant-enam-01",
        restricted_list=["DIXON.NS", "RELIANCE.NS"]
    )
    assert blocked_call["is_restricted"] is True
    assert blocked_call["compliance_status"] == "BLOCKED"
    assert "CALLING BLOCKED" in blocked_call["restricted_status_message"]
    assert len(blocked_call["direct_contacts"]) == 0

def test_mnpi_call_audit_logging():
    """N-06 Test: Audit log recorded for compliance verification."""
    audit = network_engine.log_mnpi_call(
        contact_id="net-01",
        ticker="DIXON.NS",
        call_objective="Scuttlebutt check on component lead times and factory floor yields",
        tenant_id="tenant-enam-01",
        user_id="user-enam-01"
    )
    assert audit["compliance_status"] == "LOGGED_AND_CERTIFIED"
    assert audit["audit_id"].startswith("mnpi-audit-")

    # Verify persisted in database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT call_objective FROM mnpi_call_audit_log WHERE id = ?;", (audit["audit_id"],))
        row = cursor.fetchone()
        assert row is not None
        assert "Scuttlebutt" in row[0]

def test_contact_csv_import_and_staleness():
    """
    N-01 Test:
    Imports contacts from CSV and verifies staleness detection (> 180 days).
    """
    sample_csv = """name,current_title,current_company,current_company_ticker,relationship_strength,education,themes,notes
Priya Nair,VP Procurement,Foxconn India,None,4,"[{""institution"": ""IIT Kanpur"", ""year"": ""2008""}]","[""Electronics EMS""]",Key contact for component sourcing
Amitabh Sen,Independent Director,Tata Motors,TATAMOTORS.NS,5,"[{""institution"": ""IIM Ahmedabad"", ""year"": ""1995""}]","[""Automotive""]",Board member
"""
    count, errors = network_engine.import_contacts_csv(sample_csv, tenant_id="tenant-enam-01")
    assert count == 2
    assert len(errors) == 0

    feed = network_engine.get_network_feed(tenant_id="tenant-enam-01")
    priya = next((c for c in feed if c["name"] == "Priya Nair"), None)
    assert priya is not None
    assert priya["is_stale"] is False # Just imported today

def test_dpdp_act_export_and_erasure():
    """
    N-07 Test:
    DPDP Act Data Portability (Export) and Right to Erasure (Delete).
    """
    # 1. Export tenant contacts
    export_data = network_engine.export_tenant_contacts("tenant-enam-01")
    assert export_data["tenant_id"] == "tenant-enam-01"
    assert export_data["contact_count"] > 0
    assert "DPDP" in export_data["compliance_standard"]

    # 2. Erasure of a contact
    feed_before = network_engine.get_network_feed("tenant-enam-01")
    target_to_delete = feed_before[-1]["id"]
    success = network_engine.delete_tenant_contact(target_to_delete, "tenant-enam-01")
    assert success is True

    feed_after = network_engine.get_network_feed("tenant-enam-01")
    assert not any(c["id"] == target_to_delete for c in feed_after)

def test_second_degree_reach_tenant_graph():
    """N-02 Test: Discovers 2nd degree bridge path through tenant network."""
    path = network_engine.get_second_degree_reach(
        target_person_name="Vikram Seth",
        target_role="COO",
        target_company="Kaynes Technology",
        tenant_id="tenant-enam-01"
    )
    assert path is not None
    assert path["target_person"] == "Vikram Seth"
    assert "connector_name" in path
    assert path["path_strength"] == 5
    assert "Foxconn" in path["connector_relationship"]
    assert "IIT Kanpur" in path["connector_relationship"]
    assert path["connector_relationship"].find("Foxconn") < path["connector_relationship"].find("IIT Kanpur")
