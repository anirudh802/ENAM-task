import pytest
from app.services.ask_service import ask_service

def test_ask_service_who_knows_dixon_network():
    res = ask_service.answer_query("Who knows about Dixon mobile order book?")
    assert res["intent"] == "NETWORK"
    assert res["matched_ticker"] == "DIXON.NS"
    assert len(res["cards"]) > 0
    top_contact = res["cards"][0]["data"]
    assert "Rohan Deshmukh" in top_contact["name"]
    assert top_contact.get("compliance_restricted") is True
    assert "Restricted List" in top_contact.get("compliance_reason", "")
    assert res["actions"][0]["tab"] == "nexus"

def test_ask_service_trent_guidance():
    res = ask_service.answer_query("Trent promised vs delivered on Zudio stores")
    assert res["intent"] == "GUIDANCE"
    assert res["matched_ticker"] == "TRENT.NS"
    assert len(res["cards"]) > 0
    assert "guidance_items" in res["cards"][0]["data"]
    assert res["actions"][0]["tab"] == "deepdive"

def test_ask_service_dixon_results():
    res = ask_service.answer_query("What were Dixon Q2 financial results?")
    assert res["intent"] == "RESULTS"
    assert res["matched_ticker"] == "DIXON.NS"
    assert len(res["cards"]) > 0
    res_data = res["cards"][0]["data"]
    assert "extracted_data" in res_data
    assert res["actions"][0]["tab"] == "pulse"

def test_ask_service_cdsl_anomaly():
    res = ask_service.answer_query("What triggered CDSL volume surge anomaly?")
    assert res["intent"] == "ANOMALY"
    assert res["matched_ticker"] == "CDSL.NS"
    assert len(res["cards"]) > 0
    assert res["actions"][0]["tab"] == "radar"

def test_ask_service_empty_query():
    res = ask_service.answer_query("")
    assert res["intent"] == "EMPTY"
    assert len(res["cards"]) == 0
