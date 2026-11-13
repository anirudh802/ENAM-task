import React, { useState, useEffect } from 'react';
import { PullResearch } from '../../types';
import { api } from '../../services/api';
import {
  Search,
  CheckCircle2,
  XCircle,
  Shield,
  FileCheck,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Landmark,
  BadgeAlert,
  AlertCircle,
  Database
} from 'lucide-react';

interface DeepDiveViewProps {
  initialTicker?: string;
  onSelectNetworkForTicker: (ticker: string) => void;
}

export const DeepDiveView: React.FC<DeepDiveViewProps> = ({
  initialTicker = 'DIXON.NS',
  onSelectNetworkForTicker,
}) => {
  const [ticker, setTicker] = useState(initialTicker);
  const [searchInput, setSearchInput] = useState(initialTicker);
  const [research, setResearch] = useState<PullResearch | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'narrative' | 'financials' | 'thesis'>('narrative');
  const [expandedItems, setExpandedItems] = useState<Record<number, boolean>>({ 0: true });

  const popularTickers = [
    'DIXON.NS',
    'TRENT.NS',
    'TATAMOTORS.NS',
    'HDFCBANK.NS',
    'RELIANCE.NS',
    'KAYNES.NS',
    'CDSL.NS',
    'ZOMATO.NS',
  ];

  const fetchResearch = async (targetTicker: string) => {
    setIsLoading(true);
    try {
      const data = await api.getResearch(targetTicker);
      setResearch(data);
      setTicker(targetTicker);
      // Auto-expand first item
      setExpandedItems({ 0: true });
    } catch (err) {
      console.error('Failed to fetch research:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResearch(initialTicker);
  }, [initialTicker]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      let t = searchInput.trim().toUpperCase();
      if (!t.endsWith('.NS') && !t.endsWith('.BO')) t = `${t}.NS`;
      fetchResearch(t);
    }
  };

  const toggleExpand = (idx: number) => {
    setExpandedItems((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'BEAT':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1 shrink-0">
            <CheckCircle2 className="w-3 h-3" /> BEAT
          </span>
        );
      case 'MISSED':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 flex items-center gap-1 shrink-0">
            <XCircle className="w-3 h-3" /> MISSED
          </span>
        );
      case 'MET':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 flex items-center gap-1 shrink-0">
            <CheckCircle2 className="w-3 h-3" /> MET
          </span>
        );
      case 'QUALITATIVE':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 flex items-center gap-1 shrink-0">
            QUALITATIVE
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 shrink-0">
            PENDING
          </span>
        );
    }
  };

  return (
    <div className="space-y-3 pb-8 w-full max-w-full overflow-hidden">
      {/* Ticker Search & Quick Select */}
      <div className="finance-card p-3">
        <form onSubmit={handleSearchSubmit} className="relative mb-2.5">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search any NSE ticker (e.g. DIXON, HDFCBANK)..."
            className="w-full pl-8 pr-20 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" />
          <button
            type="submit"
            className="absolute right-1.5 top-1.5 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-[11px] font-semibold transition"
          >
            Research
          </button>
        </form>

        {/* Quick Tickers */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-0.5">
          {popularTickers.map((t) => (
            <button
              key={t}
              onClick={() => {
                setSearchInput(t);
                fetchResearch(t);
              }}
              className={`px-2 py-0.5 rounded-md text-[11px] font-semibold transition whitespace-nowrap ${
                ticker === t
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
              }`}
            >
              {t.replace('.NS', '')}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="finance-card p-8 text-center text-xs text-slate-500">
          Synthesizing primary filings, transcripts, and verified metrics...
        </div>
      ) : research ? (
        <div className="space-y-3">
          {/* Header Card */}
          <div className="finance-card p-4">
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-base font-extrabold text-slate-900 dark:text-white">
                    {research.company_name}
                  </h2>
                  <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
                    {research.ticker}
                  </span>
                  {research.template_type === 'BFSI_BANK_NBFC' && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 flex items-center gap-1">
                      <Landmark className="w-2.5 h-2.5" /> BFSI Bank
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {research.sector} • {research.market_cap_tier}
                </p>
              </div>

              <button
                onClick={() => onSelectNetworkForTicker(research.ticker)}
                className="px-2.5 py-1.5 rounded-lg bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800/60 text-purple-700 dark:text-purple-300 text-xs font-semibold hover:bg-purple-100 active:scale-95 transition flex items-center gap-1 shrink-0"
              >
                <span>Who to Call</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Cold Ticker / Ingest Coverage Indicator (D-08) */}
            {research.coverage_assessment && (
              <div className="mb-2.5 p-2 bg-slate-50 dark:bg-slate-800/60 rounded-lg flex items-center justify-between text-[11px]">
                <span className="text-slate-500 dark:text-slate-400 flex items-center gap-1">
                  <Database className="w-3 h-3 text-blue-500" /> Primary Disclosure Coverage:
                </span>
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  {research.coverage_assessment.coverage_pct}% ({research.coverage_assessment.status.replace('_', ' ')})
                </span>
              </div>
            )}

            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
              {research.business_snapshot.summary}
            </p>

            {/* Segment Breakdown */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-[11px]">
              {research.business_snapshot.segments.map((seg) => (
                <div key={seg.name} className="bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg">
                  <span className="text-slate-400 block truncate">{seg.name}</span>
                  <span className="font-bold text-slate-900 dark:text-white">
                    {seg.revenue_share_pct}% mix
                  </span>
                  <span className="text-[10px] text-slate-500 block">
                    {seg.margin_pct}% margin
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Sub-tabs */}
          <div className="flex items-center border-b border-slate-200 dark:border-slate-800 gap-4 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('narrative')}
              className={`pb-2 transition relative ${
                activeTab === 'narrative'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Promised vs. Delivered
            </button>
            <button
              onClick={() => setActiveTab('financials')}
              className={`pb-2 transition relative ${
                activeTab === 'financials'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {research.template_type === 'BFSI_BANK_NBFC' ? 'Banking Ratios & NPA' : 'Cash & Balance Sheet'}
            </button>
            <button
              onClick={() => setActiveTab('thesis')}
              className={`pb-2 transition relative ${
                activeTab === 'thesis'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Bull vs. Bear
            </button>
          </div>

          {/* TAB 1: Narrative vs. Numbers (Mobile Optimized D-10) */}
          {activeTab === 'narrative' && (
            <div className="space-y-2.5">
              <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400 flex items-center justify-between">
                <span>Concall guidance track record (tap to expand)</span>
                {research.citation_faithfulness_score !== undefined && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-semibold flex items-center gap-1">
                    <FileCheck className="w-3 h-3" /> {Math.round(research.citation_faithfulness_score * 100)}% Faithfulness Verified
                  </span>
                )}
              </div>

              {research.narrative_vs_numbers.length === 0 ? (
                <div className="finance-card p-6 text-center text-xs text-slate-500">
                  No historical guidance tracking records found for this ticker.
                </div>
              ) : (
                research.narrative_vs_numbers.map((item, idx) => {
                  const isExpanded = !!expandedItems[idx];
                  return (
                    <div
                      key={idx}
                      className="finance-card p-3 transition border border-slate-200/80 dark:border-slate-800"
                    >
                      {/* One-line verdict header (D-10) */}
                      <button
                        onClick={() => toggleExpand(idx)}
                        className="w-full flex items-center justify-between gap-2 text-left"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="text-xs font-extrabold text-slate-900 dark:text-white">
                              {item.metric}
                            </span>
                            <span className="text-[10px] font-semibold text-slate-400">
                              ({item.fiscal_quarter})
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5">
                            {item.variance}
                          </p>
                        </div>
                        <div className="flex items-center gap-1.5 shrink-0">
                          {getStatusBadge(item.status)}
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-slate-400" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                          )}
                        </div>
                      </button>

                      {/* Expandable Quarter Details */}
                      {isExpanded && (
                        <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/80 space-y-2 text-xs animate-in fade-in-50 duration-150">
                          {/* Promised vs Delivered Grid */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg border border-slate-200/60 dark:border-slate-700/60">
                              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                                Promised (Guidance)
                              </span>
                              <p className="text-slate-800 dark:text-slate-200 leading-snug">
                                {item.promised_guidance}
                              </p>
                            </div>

                            <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg border border-slate-200/60 dark:border-slate-700/60">
                              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                                Delivered (Audited Actuals)
                              </span>
                              <p className="text-slate-800 dark:text-slate-200 leading-snug">
                                {item.delivered_actual}
                              </p>
                            </div>
                          </div>

                          {/* Verbatim Management Quote & Source Provenance */}
                          <div className="bg-blue-50/50 dark:bg-blue-950/20 p-2.5 rounded-lg border border-blue-100 dark:border-blue-900/40 space-y-1">
                            <div className="flex items-center justify-between text-[10px] text-blue-900 dark:text-blue-300 font-bold">
                              <span>VERBATIM MANAGEMENT QUOTE</span>
                              {item.citation_verified && (
                                <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                                  <FileCheck className="w-3 h-3" /> Verified
                                </span>
                              )}
                            </div>
                            <p className="italic text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                              "{item.management_quote}"
                            </p>
                            {item.source_doc_ref && (
                              <p className="text-[10px] text-slate-400 pt-1">
                                📍 Source: {item.source_doc_ref}
                              </p>
                            )}
                          </div>

                          {/* Delivery Notes */}
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/40 p-2 rounded-lg">
                            <span className="font-semibold text-slate-700 dark:text-slate-300">Analysis:</span>{' '}
                            {item.delivery_notes}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* TAB 2: Financials & Cash Quality (Industrial vs BFSI Bank D-12) */}
          {activeTab === 'financials' && (
            <div className="space-y-3">
              {research.template_type === 'BFSI_BANK_NBFC' ? (
                /* Bank & NBFC Template (D-12) */
                <div className="space-y-3">
                  <div className="finance-card p-3.5">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                        <Landmark className="w-3.5 h-3.5 text-blue-500" /> Bank & NBFC Operating Metrics
                      </h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
                        NII: ₹{research.financial_snapshot.net_interest_income_cr?.toLocaleString()} Cr
                      </span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Net Interest Margin (NIM)</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.financial_snapshot.nim_bps} bps
                        </span>
                        <span className="text-[10px] text-slate-400 block">
                          ({research.financial_snapshot.nim_pct}% on assets)
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Gross NPA / Net NPA</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.financial_snapshot.gross_npa_pct}% / {research.financial_snapshot.net_npa_pct}%
                        </span>
                        <span className="text-emerald-500 font-semibold text-[10px] block">
                          Pristine Quality
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Provision Coverage (PCR)</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.financial_snapshot.provision_coverage_ratio_pct}%
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">RoA / RoE</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.financial_snapshot.return_on_assets_pct}% / {research.financial_snapshot.return_on_equity_pct}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Bank Liquidity Assessment */}
                  <div className="finance-card p-3.5">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                      Liquidity & Balance Sheet Quality
                    </h4>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-lg">
                      💡 {research.cash_quality.assessment}
                    </p>
                  </div>
                </div>
              ) : (
                /* Industrial Equity Template */
                <div className="space-y-3">
                  <div className="finance-card p-3.5">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                      Headline Ratios & Multipliers
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Revenue</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          ₹{research.financial_snapshot.current_revenue_cr?.toLocaleString()} Cr
                        </span>
                        <span className="text-emerald-500 font-semibold text-[10px] block">
                          +{research.financial_snapshot.revenue_yoy_growth_pct}% YoY
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">EBITDA Margin</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.financial_snapshot.ebitda_margin_pct}%
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">ROCE / ROE</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.financial_snapshot.roce_pct}% / {research.financial_snapshot.roe_pct}%
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Debt to Equity</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.financial_snapshot.debt_to_equity}x
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Cash Quality & Working Capital */}
                  <div className="finance-card p-3.5">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        Cash Conversion Quality
                      </h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                        CFO / PAT: {research.cash_quality.cash_conversion_ratio}x
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 mb-3 text-xs">
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Cash From Ops</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          ₹{research.cash_quality.cfo_cr} Cr
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Free Cash Flow</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          ₹{research.cash_quality.free_cash_flow_cr} Cr
                        </span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/60 p-2 rounded-lg">
                        <span className="text-slate-400 text-[10px] block">Working Capital</span>
                        <span className="font-bold text-slate-900 dark:text-white">
                          {research.cash_quality.working_capital_days} days
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-lg">
                      💡 {research.cash_quality.assessment}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Bull vs. Bear */}
          {activeTab === 'thesis' && (
            <div className="space-y-3">
              {/* Competitive Moat */}
              <div className="finance-card p-3.5 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-blue-950/20 dark:to-indigo-950/20">
                <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900 dark:text-blue-300 mb-1">
                  <Shield className="w-3.5 h-3.5" />
                  <span>Competitive Moat</span>
                </div>
                <p className="text-xs text-slate-700 dark:text-slate-200">
                  {research.business_snapshot.competitive_moat}
                </p>
              </div>

              {/* Bull Case */}
              <div className="finance-card p-3.5 border-l-4 border-l-emerald-500">
                <h4 className="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider mb-2">
                  Bull Thesis (High Conviction Catalysts)
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-200">
                  {research.bull_case.map((b, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Bear Case */}
              <div className="finance-card p-3.5 border-l-4 border-l-rose-500">
                <h4 className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider mb-2">
                  Bear Risks & Downside Triggers
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-200">
                  {research.bear_case.map((b, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-rose-500 font-bold">•</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Primary Sources Grounding Stamp */}
              <div className="finance-card p-3 bg-slate-50 dark:bg-slate-900/60">
                <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1">
                  <FileCheck className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Strict Primary Sources Cited:</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {research.primary_sources_cited.map((src, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[10px] font-medium text-slate-600 dark:text-slate-300"
                    >
                      {src}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Regulatory SEBI Research Analyst Disclaimer (D-09) */}
          {research.sebi_research_disclaimer && (
            <div className="p-3 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 text-[10px] text-amber-800 dark:text-amber-300/90 leading-relaxed flex items-start gap-2">
              <BadgeAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <span>{research.sebi_research_disclaimer}</span>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
};
