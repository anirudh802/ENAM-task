from __future__ import annotations
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# 17 Announcement Categories from Reference Document
AnnouncementCategory = Literal[
    "results",
    "M&A",
    "fund_raise",
    "management_change",
    "litigation",
    "insider_trading",
    "earnings_call",
    "investor_meetings",
    "credit_rating",
    "dividend",
    "bonus_split",
    "capex",
    "press_release",
    "postal_ballot",
    "agm_egm",
    "pledging",
    "unclassified",
]

AnomalySeverity = Literal["CRITICAL", "HIGH", "MEDIUM"]
AnomalyType = Literal[
    "VOLUME_SURGE",
    "PRICE_BREAKOUT",
    "MATERIAL_FILING",
    "MANAGEMENT_CHANGE",
    "EARNINGS_SURPRISE",
]
GuidanceStatus = Literal["BEAT", "MET", "MISSED", "PENDING"]

# --- Company Schemas ---
class CompanyBase(BaseModel):
    ticker: str
    name: str
    sector: str
    market_cap_tier: Literal["Large Cap", "Mid Cap", "Small Cap"]
    market_cap_cr: float
    is_portfolio: bool = True
    screener_slug: str
    description: str

class CompanyResponse(CompanyBase):
    current_price: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[int] = None
    volume_multiple: Optional[float] = None

# --- Market EOD & Technicals ---
class MarketEOD(BaseModel):
    trade_date: str
    close_price: float
    volume: int
    volume_sma_20d: float
    daily_return_pct: float
    volume_multiple: float

# --- Corporate Announcements & Filings ---
class HeadlineMetrics(BaseModel):
    revenue_cr: Optional[float] = None
    revenue_qoq_pct: Optional[float] = None
    revenue_yoy_pct: Optional[float] = None
    ebitda_cr: Optional[float] = None
    ebitda_margin_pct: Optional[float] = None
    ebitda_qoq_pct: Optional[float] = None
    ebitda_yoy_pct: Optional[float] = None
    pbt_cr: Optional[float] = None
    pbt_qoq_pct: Optional[float] = None
    pbt_yoy_pct: Optional[float] = None
    pat_cr: Optional[float] = None
    pat_qoq_pct: Optional[float] = None
    pat_yoy_pct: Optional[float] = None

class FilingResponse(BaseModel):
    id: str
    ticker: str
    company_name: str
    category: AnnouncementCategory
    title: str
    description: str
    filing_time: str
    is_material: bool
    materiality_score: int = Field(ge=1, le=10)
    headline_metrics: Optional[HeadlineMetrics] = None
    executive_profile: Optional[Dict[str, Any]] = None
    network_connection: Optional[Dict[str, Any]] = None

# --- Anomalies & Alerts ---
class AnomalyResponse(BaseModel):
    id: str
    ticker: str
    company_name: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    headline: str
    detail: str
    metrics: Dict[str, Any]
    created_at: str
    is_pinned: bool = False
    is_dismissed: bool = False

# --- Guidance & Narrative vs Numbers ---
class GuidanceItem(BaseModel):
    fiscal_quarter: str
    metric: str
    promised_guidance: str
    delivered_actual: str
    variance: str
    status: GuidanceStatus
    management_quote: str
    delivery_notes: str

# --- Pull Primary Research ---
class BusinessSnapshot(BaseModel):
    summary: str
    segments: List[Dict[str, Any]]
    competitive_moat: str

class FinancialSnapshot(BaseModel):
    current_revenue_cr: float
    revenue_yoy_growth_pct: float
    ebitda_margin_pct: float
    pat_cr: float
    pat_yoy_growth_pct: float
    roce_pct: float
    roe_pct: float
    debt_to_equity: float

class TrajectoryAnalysis(BaseModel):
    multi_year_trend: str
    expanding_drivers: List[str]
    compressing_risks: List[str]

class CashQualityAnalysis(BaseModel):
    cfo_cr: float
    pat_cr: float
    cash_conversion_ratio: float  # CFO / PAT
    free_cash_flow_cr: float
    working_capital_days: int
    assessment: str

class PullResearchResponse(BaseModel):
    ticker: str
    company_name: str
    sector: str
    market_cap_tier: str
    business_snapshot: BusinessSnapshot
    financial_snapshot: FinancialSnapshot
    trajectory: TrajectoryAnalysis
    cash_quality: CashQualityAnalysis
    narrative_vs_numbers: List[GuidanceItem]
    bull_case: List[str]
    bear_case: List[str]
    primary_sources_cited: List[str]
    coverage_assessment: Optional[Dict[str, Any]] = None
    coverage_line: Optional[str] = None
    available_documents: Optional[List[str]] = None
    missing_documents: Optional[List[str]] = None
    has_reg33_filing: bool = False
    xbrl_filing_grounded: bool = False

# --- Network Domain ---
class NetworkContact(BaseModel):
    id: str
    name: str
    current_title: str
    current_company: str
    current_company_ticker: Optional[str] = None
    relationship_strength: int = Field(ge=1, le=5)
    is_starred: bool = False
    past_companies: List[Dict[str, Any]] = []
    education: List[Dict[str, str]] = []
    themes: List[str] = []
    relevance_score: float = 0.0
    recent_development_summary: Optional[str] = None
    notes: Optional[str] = None
    last_contacted_date: Optional[str] = None
    compliance_restricted: bool = False
    compliance_reason: Optional[str] = None

class SecondDegreePath(BaseModel):
    target_person: str
    target_role: str
    target_company: str
    connector_name: str
    connector_title: Optional[str] = None
    connector_company: Optional[str] = None
    connector_relationship: str
    path_strength: int
    recommended_intro_ask: str
    ties: Optional[List[Dict[str, Any]]] = None

class WhoToCallResponse(BaseModel):
    ticker: str
    company_name: str
    direct_contacts: List[NetworkContact]
    competitor_contacts: List[NetworkContact]
    supplier_contacts: List[NetworkContact]
    suggested_questions: List[str]
    is_restricted: bool = False
    compliance_status: str = "CLEAR"
    compliance_label: str = "SEBI PIT COMPLIANT"
    restricted_status_message: Optional[str] = None

# --- User Preferences & Web Push ---
class UserThresholdPreferences(BaseModel):
    volume_multiplier_threshold: float = 2.0
    price_move_pct_threshold: float = 3.5
    auto_notify_critical: bool = True
    starred_tickers: List[str] = []
    enabled_categories: List[AnnouncementCategory] = [
        "results",
        "M&A",
        "management_change",
        "fund_raise",
        "litigation",
        "capex",
    ]

class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str

class PushSubscriptionPayload(BaseModel):
    endpoint: str
    keys: PushSubscriptionKeys
