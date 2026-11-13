from datetime import date, datetime
from typing import Tuple, Dict, Any, Optional

def date_to_fiscal_quarter(d: date) -> str:
    """
    Converts a calendar date to Indian Fiscal Quarter format (Apr-Mar fiscal year).
    - Apr to Jun -> Q1 FY(Year+1)
    - Jul to Sep -> Q2 FY(Year+1)
    - Oct to Dec -> Q3 FY(Year+1)
    - Jan to Mar -> Q4 FY(Year)
    Example: August 2024 -> Q2FY25
    """
    year = d.year
    month = d.month

    if 4 <= month <= 6:
        fy = (year + 1) % 100
        return f"Q1FY{fy:02d}"
    elif 7 <= month <= 9:
        fy = (year + 1) % 100
        return f"Q2FY{fy:02d}"
    elif 10 <= month <= 12:
        fy = (year + 1) % 100
        return f"Q3FY{fy:02d}"
    else: # Jan to Mar
        fy = year % 100
        return f"Q4FY{fy:02d}"

def fiscal_quarter_to_date_range(fq: str) -> Tuple[str, str]:
    """
    Converts Indian Fiscal Quarter (e.g. Q2FY25) to calendar date range (YYYY-MM-DD, YYYY-MM-DD).
    Example: Q2FY25 -> ('2024-07-01', '2024-09-30')
    """
    fq = fq.strip().upper()
    quarter = fq[:2] # Q1, Q2, Q3, Q4
    fy_year = 2000 + int(fq[4:])

    if quarter == "Q1":
        return (f"{fy_year - 1}-04-01", f"{fy_year - 1}-06-30")
    elif quarter == "Q2":
        return (f"{fy_year - 1}-07-01", f"{fy_year - 1}-09-30")
    elif quarter == "Q3":
        return (f"{fy_year - 1}-10-01", f"{fy_year - 1}-12-31")
    elif quarter == "Q4":
        return (f"{fy_year}-01-01", f"{fy_year}-03-31")
    else:
        raise ValueError(f"Invalid fiscal quarter format: {fq}")

# --- Unit Conversion Helpers ---
def crore_to_inr(cr: float) -> float:
    """Converts Crores to raw INR (1 Crore = 10,000,000 INR)."""
    return cr * 10_000_000.0

def lakh_to_inr(lakh: float) -> float:
    """Converts Lakhs to raw INR (1 Lakh = 100,000 INR)."""
    return lakh * 100_000.0

def inr_to_crore(inr: float) -> float:
    """Converts raw INR to Crores (rounded to 2 decimals)."""
    return round(inr / 10_000_000.0, 2)

def inr_to_lakh(inr: float) -> float:
    """Converts raw INR to Lakhs (rounded to 2 decimals)."""
    return round(inr / 100_000.0, 2)

def bps_to_pct(bps: float) -> float:
    """Converts basis points to percentage (100 bps = 1.00%)."""
    return round(bps / 100.0, 4)

def pct_to_bps(pct: float) -> float:
    """Converts percentage to basis points (1.00% = 100 bps)."""
    return round(pct * 100.0, 1)

def calculate_growth_pct(current: float, base: float) -> float:
    """Computes percentage growth (YoY or QoQ)."""
    if base == 0:
        return 0.0
    return round(((current - base) / abs(base)) * 100.0, 2)

def calculate_margin_bps_delta(current_margin_pct: float, base_margin_pct: float) -> float:
    """Computes basis point margin expansion or contraction."""
    diff_pct = current_margin_pct - base_margin_pct
    return round(diff_pct * 100.0, 1)
