import pytest
from app.services.filings_engine import FilingsEngine
from app.services.anomaly_detector import AnomalyDetector
from app.services.network_engine import network_engine
from app.services.research_engine import ResearchEngine
from app.data.seed_data import seed_database

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_filing_classification():
    # 1. Test results category
    res = FilingsEngine.classify_announcement(
        "Financial Results for Quarter Ended Sept 30",
        "The Board approved unaudited quarterly results."
    )
    assert res["category"] == "results"
    assert res["is_material"] is True
    assert res["materiality_score"] == 10

    # 2. Test management change
    res = FilingsEngine.classify_announcement(
        "Resignation of Chief Financial Officer",
        "Mr. Sanjay Upadhyay tendered his resignation."
    )
    assert res["category"] == "management_change"
    assert res["is_material"] is True
    assert res["materiality_score"] == 9

    # 3. Test unclassified routine paperwork
    res = FilingsEngine.classify_announcement(
        "Allotment of Equity Shares under ESOP",
        "Allotment of 10,000 shares under employee stock option scheme."
    )
    assert res["category"] == "unclassified"
    assert res["is_material"] is False
    assert res["materiality_score"] == 1

def test_windowed_digest():
    digest = FilingsEngine.get_windowed_digest(hours=48)
    assert digest["total_count"] > 0
    assert len(digest["material_filings"]) > 0
    # Routine filings (ESOPs, compliance certificates) must be collapsed
    for rf in digest["routine_filings"]:
        assert rf["category"] in ["unclassified", "postal_ballot", "agm_egm", "pledging"] or rf["materiality_score"] <= 3

def test_anomaly_ranking_and_top_pinned():
    anomalies = AnomalyDetector.get_ranked_anomalies()
    assert len(anomalies) > 0
    # Pinned items must come first
    assert anomalies[0]["is_pinned"] is True

    top_pinned = AnomalyDetector.get_top_pinned_alert()
    assert top_pinned is not None
    assert top_pinned["severity"] == "CRITICAL"

def test_network_feed_starred_priority():
    feed = network_engine.get_network_feed()
    assert len(feed) > 0
    # First item must be starred
    assert feed[0]["is_starred"] is True
    # Verify recent development summary exists
    assert feed[0]["recent_development_summary"] is not None

def test_who_to_call():
    outreach = network_engine.get_who_to_call("DIXON.NS")
    assert outreach["ticker"] == "DIXON.NS"
    # Should identify Rohan Deshmukh (former Dixon head of vendor quality)
    names = [c["name"] for c in outreach["direct_contacts"]]
    assert "Rohan Deshmukh" in names
    assert len(outreach["suggested_questions"]) > 0

def test_second_degree_reach():
    path = network_engine.get_second_degree_reach("Vikram Seth", "COO", "Kaynes Technology")
    assert path["target_person"] == "Vikram Seth"
    assert path["connector_name"] is not None
    assert "IIT Kanpur" in path["connector_relationship"]

def test_pull_research_narrative_vs_numbers():
    research = ResearchEngine.get_company_research("DIXON.NS")
    assert research["ticker"] == "DIXON.NS"
    assert "business_snapshot" in research
    assert "financial_snapshot" in research
    assert "narrative_vs_numbers" in research
    assert len(research["narrative_vs_numbers"]) >= 2
    # Check that guidance statuses are valid
    for item in research["narrative_vs_numbers"]:
        assert item["status"] in ["BEAT", "MET", "MISSED", "PENDING"]
