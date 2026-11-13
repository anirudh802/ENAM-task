"""
Deterministic Financial Metrics Engine (D-03, D-04, D-12)
Strict mathematical computations for variances, bps deltas, growth rates, CFO-to-PAT,
Guidance v2 status evaluation, and Bank/NBFC metrics.
Ensures zero LLM arithmetic hallucinations.
"""

from typing import Dict, Any, Optional, Tuple
from app.core.financial_units import (
    calculate_growth_pct,
    calculate_margin_bps_delta,
    bps_to_pct,
    pct_to_bps,
    crore_to_inr,
    lakh_to_inr,
    inr_to_crore
)

class MetricsCalculator:
    @staticmethod
    def calculate_growth_yoy(current_period: float, prior_year_period: float) -> float:
        """Computes Year-over-Year (YoY) percentage growth."""
        return calculate_growth_pct(current_period, prior_year_period)

    @staticmethod
    def calculate_growth_qoq(current_period: float, prior_quarter: float) -> float:
        """Computes Quarter-over-Quarter (QoQ) percentage growth."""
        return calculate_growth_pct(current_period, prior_quarter)

    @staticmethod
    def calculate_ebitda_margin(ebitda_cr: float, revenue_cr: float) -> float:
        """Computes EBITDA margin percentage rounded to 2 decimal places."""
        if revenue_cr <= 0:
            return 0.0
        return round((ebitda_cr / revenue_cr) * 100.0, 2)

    @staticmethod
    def calculate_pat_margin(pat_cr: float, revenue_cr: float) -> float:
        """Computes PAT margin percentage rounded to 2 decimal places."""
        if revenue_cr <= 0:
            return 0.0
        return round((pat_cr / revenue_cr) * 100.0, 2)

    @staticmethod
    def calculate_margin_spread_bps(current_margin_pct: float, base_margin_pct: float) -> float:
        """Computes basis point margin expansion (+) or compression (-)."""
        return calculate_margin_bps_delta(current_margin_pct, base_margin_pct)

    @staticmethod
    def calculate_cfo_to_pat(cfo_cr: float, pat_cr: float) -> float:
        """
        Computes Cash Flow from Operations (CFO) to Net Profit (PAT) conversion ratio.
        Standard institutional quality benchmark: > 0.80x is healthy; < 0.50x raises working capital red flags.
        """
        if pat_cr == 0:
            return 0.0
        return round(cfo_cr / pat_cr, 2)

    @staticmethod
    def evaluate_guidance_v2(
        guidance_type: str,
        delivered_actual: float,
        min_guidance: Optional[float] = None,
        max_guidance: Optional[float] = None,
        target: Optional[float] = None,
        is_margin_or_rate: bool = False
    ) -> Tuple[str, str]:
        """
        Evaluates Guidance Schema v2 (D-04):
        - RANGE:
            - If delivered_actual < min_guidance: MISSED
            - If delivered_actual > max_guidance: BEAT
            - If min_guidance <= delivered_actual <= max_guidance: MET
        - NUMERIC:
            - If delivered_actual >= target: MET (or BEAT if > 5% above target)
            - If delivered_actual < target: MISSED
        - QUALITATIVE:
            - Returns ('QUALITATIVE', 'Qualitative delivery narrative')
        """
        g_type = guidance_type.upper().strip()

        if g_type == "QUALITATIVE":
            return "QUALITATIVE", "Qualitative guidance; assessed via management commentary"

        if g_type == "RANGE":
            if min_guidance is None or max_guidance is None:
                raise ValueError("RANGE guidance requires both min_guidance and max_guidance.")

            if delivered_actual < min_guidance:
                deficit = min_guidance - delivered_actual
                if is_margin_or_rate:
                    bps = round(deficit * 100, 1)
                    return "MISSED", f"-{bps} bps below lower band ({min_guidance}%)"
                pct = round((deficit / min_guidance) * 100, 1)
                return "MISSED", f"-{pct}% below lower band ({min_guidance})"

            elif delivered_actual > max_guidance:
                surplus = delivered_actual - max_guidance
                if is_margin_or_rate:
                    bps = round(surplus * 100, 1)
                    return "BEAT", f"+{bps} bps above upper band ({max_guidance}%)"
                pct = round((surplus / max_guidance) * 100, 1)
                return "BEAT", f"+{pct}% above upper band ({max_guidance})"

            else:
                return "MET", f"Delivered within guided range [{min_guidance}, {max_guidance}]"

        elif g_type == "NUMERIC":
            tgt = target if target is not None else min_guidance
            if tgt is None:
                raise ValueError("NUMERIC guidance requires target or min_guidance.")

            if is_margin_or_rate:
                diff_bps = round((delivered_actual - tgt) * 100, 1)
                if diff_bps >= 50.0: # 50 bps beat
                    return "BEAT", f"+{diff_bps} bps beat vs target ({tgt}%)"
                elif diff_bps >= -20.0: # Within 20 bps tolerance
                    return "MET", f"Met target within tolerance ({delivered_actual}% vs {tgt}%)"
                else:
                    return "MISSED", f"{diff_bps} bps compression vs target ({tgt}%)"
            else:
                pct_diff = round(((delivered_actual - tgt) / abs(tgt)) * 100.0, 1)
                if pct_diff >= 5.0:
                    return "BEAT", f"+{pct_diff}% beat vs target ({tgt})"
                elif pct_diff >= -1.0:
                    return "MET", f"Met target ({delivered_actual} vs {tgt})"
                else:
                    return "MISSED", f"{pct_diff}% deficit vs target ({tgt})"

        return "PENDING", "Pending evaluation"

    @staticmethod
    def calculate_bank_metrics(
        nii_cr: float,
        total_assets_cr: float,
        gross_npa_cr: float,
        net_npa_cr: float,
        gross_advances_cr: float,
        pat_cr: float,
        total_equity_cr: float,
        provisions_cr: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates Bank and NBFC specialized financial template metrics (D-12).
        Includes NIM, Gross NPA %, Net NPA %, Provision Coverage Ratio (PCR), RoA, and RoE.
        """
        # Net Interest Margin (NIM)
        nim_pct = round((nii_cr / total_assets_cr) * 100.0, 2) if total_assets_cr > 0 else 0.0
        nim_bps = pct_to_bps(nim_pct)

        # Asset Quality
        gnpa_pct = round((gross_npa_cr / gross_advances_cr) * 100.0, 2) if gross_advances_cr > 0 else 0.0
        nnpa_pct = round((net_npa_cr / gross_advances_cr) * 100.0, 2) if gross_advances_cr > 0 else 0.0

        # Provision Coverage Ratio (PCR)
        if gross_npa_cr > 0:
            if provisions_cr is not None and provisions_cr > 0:
                pcr_pct = round((provisions_cr / gross_npa_cr) * 100.0, 2)
            else:
                pcr_pct = round(((gross_npa_cr - net_npa_cr) / gross_npa_cr) * 100.0, 2)
        else:
            pcr_pct = 100.0

        # Return Ratios
        roa_pct = round((pat_cr / total_assets_cr) * 100.0, 2) if total_assets_cr > 0 else 0.0
        roe_pct = round((pat_cr / total_equity_cr) * 100.0, 2) if total_equity_cr > 0 else 0.0

        return {
            "template_type": "BFSI_BANK_NBFC",
            "net_interest_income_cr": nii_cr,
            "nim_pct": nim_pct,
            "nim_bps": nim_bps,
            "gross_npa_pct": gnpa_pct,
            "net_npa_pct": nnpa_pct,
            "provision_coverage_ratio_pct": pcr_pct,
            "return_on_assets_pct": roa_pct,
            "return_on_equity_pct": roe_pct,
            "is_asset_quality_healthy": gnpa_pct <= 2.5 and nnpa_pct <= 0.8
        }
