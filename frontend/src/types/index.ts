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
  revenue_qoq_pct?: number;
  revenue_yoy_pct?: number;
  ebitda_cr?: number;
  ebitda_margin_pct?: number;
  ebitda_qoq_pct?: number;
  ebitda_yoy_pct?: number;
  pbt_cr?: number;
  pbt_qoq_pct?: number;
  pbt_yoy_pct?: number;
  pat_cr?: number;
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
    why_line?: string;
    is_blocked?: boolean;
    compliance_status?: string;
    compliance?: {
      status?: string;
      is_blocked?: boolean;
      label?: string;
      reason?: string;
      block_ends?: string | null;
    } | null;
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
  id?: number;
  fiscal_quarter: string;
  metric: string;
  guidance_type?: 'NUMERIC' | 'RANGE' | 'QUALITATIVE';
  min_guidance?: number | null;
  max_guidance?: number | null;
  promised_guidance: string;
  delivered_actual: string;
  variance: string;
  status: 'BEAT' | 'MET' | 'MISSED' | 'QUALITATIVE' | 'PENDING';
  management_quote: string;
  source_doc_ref?: string;
  delivery_notes: string;
  citation_verified?: boolean;
}

export interface PullResearch {
  isin?: string;
  ticker: string;
  company_name: string;
  sector: string;
  market_cap_tier: string;
  template_type?: 'INDUSTRIAL_EQUITY' | 'BFSI_BANK_NBFC';
  citation_faithfulness_score?: number;
  verification_status?: string;
  sebi_research_disclaimer?: string;
  model_version?: string;
  prompt_version?: string;
  cache_hit?: boolean;
  coverage_assessment?: {
    coverage_pct: number;
    status: string;
    coverage_line?: string;
    available_documents?: string[];
    missing_documents?: string[];
    breakdown: {
      concall_transcripts_available: number;
      latest_concall_quarter?: string | null;
      regulatory_announcements_count: number;
      guidance_track_records_count: number;
    };
    is_ready_for_deepdive: boolean;
  };
  coverage_line?: string;
  available_documents?: string[];
  missing_documents?: string[];
  business_snapshot: {
    summary: string;
    segments: Array<{ name: string; revenue_share_pct: number; margin_pct: number }>;
    competitive_moat: string;
  };
  financial_snapshot: {
    current_revenue_cr?: number;
    revenue_yoy_growth_pct?: number;
    ebitda_margin_pct?: number;
    pat_cr?: number;
    pat_yoy_growth_pct?: number;
    roce_pct?: number;
    roe_pct?: number;
    debt_to_equity?: number;
    // Bank / NBFC fields
    net_interest_income_cr?: number;
    nim_pct?: number;
    nim_bps?: number;
    gross_npa_pct?: number;
    net_npa_pct?: number;
    provision_coverage_ratio_pct?: number;
    return_on_assets_pct?: number;
    return_on_equity_pct?: number;
    is_asset_quality_healthy?: boolean;
    [key: string]: any;
  };
  trajectory: {
    multi_year_trend: string;
    expanding_drivers: string[];
    compressing_risks: string[];
    multi_year_financials?: Array<{
      fiscal_year: string;
      revenue_cr: number;
      ebitda_margin_pct: number;
      pat_cr: number;
      cfo_cr: number;
      cfo_to_pat: number;
    }>;
  };
  cash_quality: {
    cfo_cr?: number | null;
    pat_cr?: number;
    cash_conversion_ratio?: number | null;
    free_cash_flow_cr?: number | null;
    working_capital_days?: number | null;
    liquidity_coverage_ratio_pct?: number | null;
    assessment: string;
    [key: string]: any;
  };
  narrative_vs_numbers: GuidanceItem[];
  bull_case: string[];
  bear_case: string[];
  primary_sources_cited: string[];
  has_reg33_filing?: boolean;
  xbrl_filing_grounded?: boolean;
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
  last_contacted_date?: string | null;
  compliance_restricted?: boolean;
  compliance_reason?: string | null;
  compliance_status?: string;
  is_blocked?: boolean;
  compliance?: Record<string, any>;
}

export interface WhoToCallResponse {
  ticker: string;
  company_name: string;
  sector: string;
  direct_contacts: NetworkContact[];
  competitor_contacts: NetworkContact[];
  supplier_contacts: NetworkContact[];
  suggested_questions: string[];
  is_restricted?: boolean;
  compliance_status?: string;
  compliance_label?: string;
  restricted_status_message?: string;
}

export interface SecondDegreeTie {
  type: string;
  description: string;
  detail: string;
  strength: number;
  is_primary: boolean;
}

export interface SecondDegreePath {
  target_person: string;
  target_role: string;
  target_company: string;
  connector_name: string;
  connector_title?: string;
  connector_company?: string;
  connector_relationship: string;
  path_strength: number;
  recommended_intro_ask: string;
  ties?: SecondDegreeTie[];
}

export type AskIntent = 'NETWORK' | 'GUIDANCE' | 'RESULTS' | 'ANOMALY' | 'SYNTHESIS' | 'EMPTY' | 'GENERAL';

export interface AskAction {
  type: 'navigate_tab';
  tab: 'pulse' | 'radar' | 'deepdive' | 'nexus';
  ticker?: string;
  label: string;
}

export interface AskCard {
  card_type: 'network_contact' | 'guidance_track_record' | 'results_disclosure' | 'radar_anomaly' | 'research_synthesis';
  data: any;
}

export interface AskResponse {
  query: string;
  intent: AskIntent;
  matched_ticker?: string | null;
  company_name?: string | null;
  answer_summary: string;
  cards: AskCard[];
  actions: AskAction[];
}

