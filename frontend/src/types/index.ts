export type AnnouncementCategory =
  | 'results'
  | 'M&A'
  | 'fund_raise'
  | 'management_change'
  | 'litigation'
  | 'insider_trading'
  | 'earnings_call'
  | 'investor_meetings'
  | 'credit_rating'
  | 'dividend'
  | 'bonus_split'
  | 'capex'
  | 'press_release'
  | 'postal_ballot'
  | 'agm_egm'
  | 'pledging'
  | 'unclassified';

export type AnomalySeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM';
export type AnomalyType =
  | 'VOLUME_SURGE'
  | 'PRICE_BREAKOUT'
  | 'MATERIAL_FILING'
  | 'MANAGEMENT_CHANGE'
  | 'EARNINGS_SURPRISE';

export interface Company {
  ticker: string;
  name: string;
  sector: string;
  market_cap_tier: string;
  market_cap_cr: number;
  is_portfolio: boolean;
  screener_slug: string;
  description: string;
  current_price?: number;
  change_pct?: number;
  volume?: number;
  volume_multiple?: number;
}

export interface HeadlineMetrics {
  revenue_cr?: number;
  ebitda_cr?: number;
  ebitda_margin_pct?: number;
  pbt_cr?: number;
  pat_cr?: number;
  revenue_qoq_pct?: number;
  revenue_yoy_pct?: number;
  pat_qoq_pct?: number;
  pat_yoy_pct?: number;
}

export interface Filing {
  id: string;
  ticker: string;
  company_name: string;
  category: AnnouncementCategory;
  title: string;
  description: string;
  filing_time: string;
  is_material: boolean;
  materiality_score: number;
  headline_metrics?: HeadlineMetrics | null;
  executive_profile?: {
    name: string;
    role: string;
    previous_employer: string;
    previous_title: string;
    education: string;
    tenure_past?: string;
  } | null;
  network_connection?: {
    connected_person_id: string;
    connected_person_name: string;
    relationship: string;
    degree_of_separation: number;
    context: string;
  } | null;
}

export interface DigestResponse {
  window_hours: number;
  total_count: number;
  material_count: number;
  routine_count: number;
  material_filings: Filing[];
  routine_filings: Filing[];
}

export interface Anomaly {
  id: string;
  ticker: string;
  company_name: string;
  anomaly_type: AnomalyType;
  severity: AnomalySeverity;
  headline: string;
  detail: string;
  metrics: Record<string, any>;
  created_at: string;
  is_pinned: boolean;
  is_dismissed: boolean;
}

export interface UserPreferences {
  volume_multiplier_threshold: number;
  price_move_pct_threshold: number;
  auto_notify_critical: boolean;
  starred_tickers: string[];
  enabled_categories: AnnouncementCategory[];
}

export interface GuidanceItem {
  fiscal_quarter: string;
  metric: string;
  promised_guidance: string;
  delivered_actual: string;
  variance: string;
  status: 'BEAT' | 'MET' | 'MISSED' | 'PENDING';
  management_quote: string;
  delivery_notes: string;
}

export interface PullResearch {
  ticker: string;
  company_name: string;
  sector: string;
  market_cap_tier: string;
  business_snapshot: {
    summary: string;
    segments: Array<{ name: string; revenue_share_pct: number; margin_pct: number }>;
    competitive_moat: string;
  };
  financial_snapshot: {
    current_revenue_cr: number;
    revenue_yoy_growth_pct: number;
    ebitda_margin_pct: number;
    pat_cr: number;
    pat_yoy_growth_pct: number;
    roce_pct: number;
    roe_pct: number;
    debt_to_equity: number;
  };
  trajectory: {
    multi_year_trend: string;
    expanding_drivers: string[];
    compressing_risks: string[];
  };
  cash_quality: {
    cfo_cr: number;
    pat_cr: number;
    cash_conversion_ratio: number;
    free_cash_flow_cr: number;
    working_capital_days: number;
    assessment: string;
  };
  narrative_vs_numbers: GuidanceItem[];
  bull_case: string[];
  bear_case: string[];
  primary_sources_cited: string[];
}

export interface NetworkContact {
  id: string;
  name: string;
  current_title: string;
  current_company: string;
  current_company_ticker?: string | null;
  relationship_strength: number;
  is_starred: boolean;
  past_companies: Array<{ company: string; role: string; start_year: number; end_year: number }>;
  education: Array<{ institution: string; degree: string; year: string }>;
  themes: string[];
  relevance_score: number;
  recent_development_summary?: string | null;
  notes?: string | null;
}

export interface WhoToCallResponse {
  ticker: string;
  company_name: string;
  sector: string;
  direct_contacts: NetworkContact[];
  competitor_contacts: NetworkContact[];
  supplier_contacts: NetworkContact[];
  suggested_questions: string[];
}

export interface SecondDegreePath {
  target_person: string;
  target_role: string;
  target_company: string;
  connector_name: string;
  connector_title: string;
  connector_company: string;
  connector_relationship: string;
  path_strength: number;
  recommended_intro_ask: string;
}
