import pytest
from app.services.metrics_calculator import MetricsCalculator
from app.core.financial_units import (
    crore_to_inr,
    lakh_to_inr,
    inr_to_crore,
    inr_to_lakh,
    bps_to_pct,
    pct_to_bps
)

def test_financial_units_conversions():
    # Crore conversions
    assert crore_to_inr(1.0) == 10_000_000.0
    assert crore_to_inr(250.5) == 2_505_000_000.0
    assert inr_to_crore(15_000_000.0) == 1.50

    # Lakh conversions
    assert lakh_to_inr(1.0) == 100_000.0
    assert lakh_to_inr(50.0) == 5_000_000.0
    assert inr_to_lakh(350_000.0) == 3.50

    # Basis points conversions
    assert bps_to_pct(100.0) == 1.0000
    assert bps_to_pct(35.5) == 0.3550
    assert pct_to_bps(1.50) == 150.0
    assert pct_to_bps(0.36) == 36.0

def test_deterministic_growth_and_margins():
    # YoY growth
    yoy = MetricsCalculator.calculate_growth_yoy(11534.0, 5233.0)
    assert yoy == 120.41 # ~120.4%

    # QoQ growth
    qoq = MetricsCalculator.calculate_growth_qoq(11534.0, 6580.0)
    assert qoq == 75.29

    # EBITDA margin
    margin = MetricsCalculator.calculate_ebitda_margin(420.0, 11534.0)
    assert margin == 3.64

    # PAT margin
    pat_margin = MetricsCalculator.calculate_pat_margin(412.0, 11534.0)
    assert pat_margin == 3.57

    # Margin spread bps
    spread = MetricsCalculator.calculate_margin_spread_bps(3.64, 4.00)
    assert spread == -36.0 # -36 bps compression

def test_cash_conversion_cfo_to_pat():
    # Healthy cash conversion (> 1.0x)
    ratio = MetricsCalculator.calculate_cfo_to_pat(1040.0, 920.0)
    assert ratio == 1.13

    # Strained working capital (< 0.5x)
    ratio_strained = MetricsCalculator.calculate_cfo_to_pat(200.0, 500.0)
    assert ratio_strained == 0.40

def test_guidance_v2_range_evaluation():
    # 1. Inside Range -> MET
    status, note = MetricsCalculator.evaluate_guidance_v2(
        guidance_type="RANGE",
        delivered_actual=175.0,
        min_guidance=150.0,
        max_guidance=200.0
    )
    assert status == "MET"
    assert "within guided range" in note

    # 2. Above Range -> BEAT
    status_beat, note_beat = MetricsCalculator.evaluate_guidance_v2(
        guidance_type="RANGE",
        delivered_actual=220.0,
        min_guidance=150.0,
        max_guidance=200.0
    )
    assert status_beat == "BEAT"
    assert "+10.0% above upper band" in note_beat

    # 3. Below Range -> MISSED
    status_miss, note_miss = MetricsCalculator.evaluate_guidance_v2(
        guidance_type="RANGE",
        delivered_actual=120.0,
        min_guidance=150.0,
        max_guidance=200.0
    )
    assert status_miss == "MISSED"
    assert "-20.0% below lower band" in note_miss

def test_guidance_v2_margin_range_evaluation():
    # Margin range evaluation in bps
    status, note = MetricsCalculator.evaluate_guidance_v2(
        guidance_type="RANGE",
        delivered_actual=3.46,
        min_guidance=3.40,
        max_guidance=3.60,
        is_margin_or_rate=True
    )
    assert status == "MET"

    # Margin miss in bps
    status_miss, note_miss = MetricsCalculator.evaluate_guidance_v2(
        guidance_type="RANGE",
        delivered_actual=3.20,
        min_guidance=3.40,
        max_guidance=3.60,
        is_margin_or_rate=True
    )
    assert status_miss == "MISSED"
    assert "-20.0 bps below lower band" in note_miss

def test_guidance_v2_qualitative_evaluation():
    status, note = MetricsCalculator.evaluate_guidance_v2(
        guidance_type="QUALITATIVE",
        delivered_actual=0.0
    )
    assert status == "QUALITATIVE"

def test_bank_nbfc_financial_template():
    # HDFC Bank test metrics
    metrics = MetricsCalculator.calculate_bank_metrics(
        nii_cr=30110.0,
        total_assets_cr=3750000.0,
        gross_npa_cr=34200.0,
        net_npa_cr=10200.0,
        gross_advances_cr=2510000.0,
        pat_cr=16820.0,
        total_equity_cr=440000.0,
        provisions_cr=2700.0
    )

    assert metrics["template_type"] == "BFSI_BANK_NBFC"
    assert metrics["nim_pct"] == 0.80 # 30110 / 3750000
    assert metrics["gross_npa_pct"] == 1.36 # 34200 / 2510000
    assert metrics["net_npa_pct"] == 0.41 # 10200 / 2510000
    assert metrics["is_asset_quality_healthy"] is True
    assert metrics["return_on_assets_pct"] == 0.45
    assert metrics["return_on_equity_pct"] == 3.82
