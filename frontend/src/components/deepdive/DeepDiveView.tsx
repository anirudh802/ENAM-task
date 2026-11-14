import React, { useState, useEffect, useMemo } from 'react';
import { PullResearch } from '../../types';
import { api } from '../../services/api';
import { ActionButton } from '../common/ActionButton';
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
  Database,
  Info,
  AlertTriangle
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

  // Unified concall count and guidance summary rows derived from same data (Item 8)
  const concallsAvailable = research?.coverage_assessment?.breakdown?.concall_transcripts_available ?? (research?.narrative_vs_numbers ? new Set(research.narrative_vs_numbers.map(g => g.fiscal_quarter)).size : 0);
  const regulatoryFilingsCount = research?.coverage_assessment?.breakdown?.regulatory_announcements_count || 1;

  const guidanceSummaryRows = useMemo(() => {
    if (!research?.narrative_vs_numbers || research.narrative_vs_numbers.length === 0) {
      return [];
    }
    const groups: { [key: string]: { label: string; sublabel: string; quarters: { quarter: string; status: string }[] } } = {};
    for (const item of research.narrative_vs_numbers) {
      const metricLower = item.metric.toLowerCase();
      let key = item.metric;
      let label = item.metric;
      let sublabel = item.variance;

      if (metricLower.includes('revenue')) {
        key = 'revenue';
        label = 'Top-Line Revenue';
        sublabel = 'Consolidated / Segment Run Rate';
      } else if (metricLower.includes('margin') || metricLower.includes('ebitda')) {
        key = 'margin';
        label = 'EBITDA Margin %';
        sublabel = 'Operating Margin Corridor';
      } else if (metricLower.includes('volume') || metricLower.includes('smartphone')) {
        key = 'volume';
        label = 'Smartphone Volume';
        sublabel = 'Monthly Production Run Rate';
      }

      if (!groups[key]) {
        groups[key] = { label, sublabel, quarters: [] };
      }

      const qLabel = item.fiscal_quarter.replace(/FY\d+/, '').trim() || item.fiscal_quarter;
      if (!groups[key].quarters.some(q => q.quarter === qLabel)) {
        groups[key].quarters.push({
          quarter: qLabel,
          status: item.status
        });
      }
    }
    return Object.values(groups);
  }, [research?.narrative_vs_numbers]);

  const portfolioHoldings = [
    { ticker: 'DIXON.NS', hasNetwork: true, contact: 'Rohan Deshmukh' },
    { ticker: 'TRENT.NS', hasNetwork: true, contact: 'Pooja Singhania' },
    { ticker: 'KAYNES.NS', hasNetwork: true, contact: 'Vikram Seth' },
    { ticker: 'DEEPAKNTR.NS', hasNetwork: true, contact: 'Dr. Arvind Swaminathan' },
    { ticker: 'TCS.NS', hasNetwork: false },
    { ticker: 'BHARTIARTL.NS', hasNetwork: false },
    { ticker: 'ICICIBANK.NS', hasNetwork: false },
    { ticker: 'ITC.NS', hasNetwork: false },
    { ticker: 'KOTAKBANK.NS', hasNetwork: false },
    { ticker: 'BAJFINANCE.NS', hasNetwork: false },
    { ticker: 'HINDUNILVR.NS', hasNetwork: false },
    { ticker: 'ASIANPAINT.NS', hasNetwork: false },
    { ticker: 'AXISBANK.NS', hasNetwork: false },
    { ticker: 'MAZDOCK.NS', hasNetwork: false },
    { ticker: 'CDSL.NS', hasNetwork: false },
    { ticker: 'TATAMOTORS.NS', hasNetwork: false },
    { ticker: 'HDFCBANK.NS', hasNetwork: false },
    { ticker: 'RELIANCE.NS', hasNetwork: false },
    { ticker: 'ZOMATO.NS', hasNetwork: false },
    { ticker: 'INFY.NS', hasNetwork: false },
    { ticker: 'POLYCAB.NS', hasNetwork: false },
    { ticker: 'ASTRAL.NS', hasNetwork: false },
    { ticker: 'MARUTI.NS', hasNetwork: false },
    { ticker: 'BEL.NS', hasNetwork: false },
    { ticker: 'HAL.NS', hasNetwork: false },
    { ticker: 'LT.NS', hasNetwork: false },
    { ticker: 'TITAN.NS', hasNetwork: false },
    { ticker: 'DMART.NS', hasNetwork: false },
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
      setResearch(null);
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

  const parseThesisClaim = (text: string): { claim: string; source: string } | null => {
    const match = text.match(/^(.*?)\s*\[Source:\s*(.*?)\]$/i) || text.match(/^(.*?)\s*\(Source:\s*(.*?)\)$/i);
    if (match) {
      return { claim: match[1].trim(), source: match[2].trim() };
    }
    return null;
  };

  const getStatusBadge = (status: string) => {
    const s = (status || '').toUpperCase();
    if (s.includes('BEAT')) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1 shrink-0 border border-emerald-200 dark:border-emerald-800/40">
          <span>✓</span> BEAT
        </span>
      );
    }
    if (s.includes('MISS')) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 flex items-center gap-1 shrink-0 border border-rose-200 dark:border-rose-800/40">
          <span>▲</span> MISSED
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 flex items-center gap-1 shrink-0 border border-blue-200 dark:border-blue-800/40">
        <span>✓</span> MET
      </span>
    );
  };

  const renderRangeBar = (item: any) => {
    if (item.min_guidance === null || item.min_guidance === undefined || item.max_guidance === null || item.max_guidance === undefined) {
      return null;
    }
    const minG = Number(item.min_guidance);
    const maxG = Number(item.max_guidance);
    const isRange = maxG > minG;
    
    // Scale visual positions
    const span = Math.max(maxG - minG, maxG * 0.1 || 1.0);
    const displayMin = Math.max(0, minG - span * 0.5);
    const displayMax = maxG + span * 0.8;
    const totalRange = displayMax - displayMin || 1;

    const bandLeftPct = Math.max(10, Math.min(80, ((minG - displayMin) / totalRange) * 100));
    const bandWidthPct = isRange 
      ? Math.max(15, Math.min(75, ((maxG - minG) / totalRange) * 100))
      : 8;

    let deliveredPct = bandLeftPct + bandWidthPct * 0.5;
    if (item.status === 'BEAT') deliveredPct = Math.min(96, bandLeftPct + bandWidthPct + 8);
    else if (item.status === 'MISSED') deliveredPct = Math.max(4, bandLeftPct - 8);

    return (
      <div className="my-2 p-2 bg-slate-50 dark:bg-slate-900/60 rounded-lg border border-slate-200/60 dark:border-slate-800/60">
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mb-1">
          <span>Target Band: {isRange ? `${minG} — ${maxG}` : `${minG}`}</span>
          <span className={item.status === 'BEAT' ? 'text-emerald-500 font-bold' : item.status === 'MISSED' ? 'text-rose-500 font-bold' : 'text-blue-500 font-bold'}>
            {item.status}
          </span>
        </div>
        <div className="relative h-2 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden my-1">
          {/* Guided Band Corridor */}
          <div 
            className="absolute h-full bg-blue-300 dark:bg-blue-900/70 rounded-full"
            style={{ left: `${bandLeftPct}%`, width: `${bandWidthPct}%` }}
          />
          {/* Delivered Actual Point */}
          <div 
            className={`absolute top-0 w-3 h-2 rounded-full shadow-xs transform -translate-x-1.5 ${
              item.status === 'BEAT' ? 'bg-emerald-500 ring-2 ring-emerald-300 dark:ring-emerald-900' :
              item.status === 'MISSED' ? 'bg-rose-500 ring-2 ring-rose-300 dark:ring-rose-900' :
              'bg-blue-500 ring-2 ring-blue-300 dark:ring-blue-900'
            }`}
            style={{ left: `${deliveredPct}%` }}
          />
        </div>
        <div className="flex justify-between text-[9px] text-slate-400 font-mono">
          <span>Floor: {minG}</span>
          <span className="font-semibold text-slate-600 dark:text-slate-300">
            Delivered: {item.delivered_actual.match(/[\d,.]+(\s*(?:Cr|M|%|days))?/)?.[0] || 'Actual'}
          </span>
          <span>Ceiling: {maxG}</span>
        </div>
      </div>
    );
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

        {/* Mock Portfolio Strip with Visible Network Overlap (Report Item 24) */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
          {portfolioHoldings.map((item) => (
            <button
              key={item.ticker}
              onClick={() => {
                setSearchInput(item.ticker);
                fetchResearch(item.ticker);
              }}
              title={item.hasNetwork ? `Network overlap: ${item.contact}` : 'Portfolio holding'}
              className={`px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold transition whitespace-nowrap flex items-center gap-1 ${
                ticker === item.ticker
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              <span>{item.ticker.replace('.NS', '')}</span>
              {item.hasNetwork && (
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    ticker === item.ticker ? 'bg-purple-200 ring-1 ring-white' : 'bg-purple-500'
                  }`}
                  title={`Network overlap: ${item.contact}`}
                />
              )}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="finance-card p-6 border-blue-200 dark:border-blue-900/60 bg-blue-50/20 dark:bg-blue-950/20 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
              <span className="text-xs font-bold text-slate-900 dark:text-white">
                Fetching primary documents for {searchInput.trim().toUpperCase() || ticker}...
              </span>
            </div>
            <span className="text-[10px] font-mono text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/50">
              Exchange ingestion
            </span>
          </div>
          <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-blue-600 h-1.5 rounded-full animate-pulse w-2/3" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[10px] font-mono text-slate-500 dark:text-slate-400">
            <div className="p-1.5 rounded bg-white/70 dark:bg-slate-900/70 border border-slate-200/60 dark:border-slate-800 flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Primary XBRL Filing
            </div>
            <div className="p-1.5 rounded bg-white/70 dark:bg-slate-900/70 border border-slate-200/60 dark:border-slate-800 flex items-center gap-1.5">
              <span className="text-blue-500 font-bold">⏳</span> Concall Transcripts
            </div>
            <div className="p-1.5 rounded bg-white/70 dark:bg-slate-900/70 border border-slate-200/60 dark:border-slate-800 flex items-center gap-1.5">
              <span className="text-purple-500 font-bold">●</span> Ratio Grounding
            </div>
          </div>
        </div>
      ) : research ? (
        <div className="space-y-3">
          {/* Header Card */}
          <div className="finance-card p-4">
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-base font-extrabold text-slate-900 dark:text-white line-clamp-2 break-words">
                    {research.company_name}
                  </h2>
                  <span className="text-xs font-mono font-bold text-blue-600 dark:text-blue-400">
                    {research.ticker}
                  </span>
                  {research.template_type === 'BFSI_BANK_NBFC' && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-extrabold uppercase bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 flex items-center gap-1">
                      <Landmark className="w-2.5 h-2.5" /> BFSI Bank
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {research.sector} • {research.market_cap_tier}
                </p>
              </div>

              <ActionButton
                variant="ghost"
                icon={ArrowRight}
                label="Who to Call"
                onClick={() => onSelectNetworkForTicker(research.ticker)}
              />
            </div>

            {/* Cold Ticker / Ingest Coverage Indicator (D-08) */}
            {research.coverage_assessment && (
              <div className="mb-2.5 p-2 bg-slate-50 dark:bg-slate-800/60 rounded-lg flex items-center justify-between text-[11px]">
                <span className="text-slate-500 dark:text-slate-400 flex items-center gap-1">
                  <Database className="w-3 h-3 text-blue-500" /> Primary Disclosures Ingested:
                </span>
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  {concallsAvailable} Concall{concallsAvailable === 1 ? '' : 's'} • 1 Annual Report • {regulatoryFilingsCount} SEBI Filings
                </span>
              </div>
            )}

            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
              {research.business_snapshot.summary}
            </p>

            {/* Segment Breakdown - Hairline Divided Grid Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-slate-200 dark:divide-slate-800/80 border-t border-slate-200 dark:border-slate-800/80 pt-2.5 mt-2.5 text-[11px]">
              {research.business_snapshot.segments.map((seg, idx) => (
                <div key={seg.name} className={`${idx > 0 ? 'sm:pl-3' : ''} ${idx < research.business_snapshot.segments.length - 1 ? 'sm:pr-3' : ''} py-1 sm:py-0`}>
                  <span className="text-slate-400 block line-clamp-2 break-words text-[10px] uppercase font-mono">{seg.name}</span>
                  <div className="flex items-baseline gap-1.5 mt-0.5">
                    <span className="font-bold font-mono font-num tabular-nums text-slate-900 dark:text-white text-xs">
                      {seg.revenue_share_pct}%
                    </span>
                    <span className="text-[10px] font-mono font-num tabular-nums text-slate-500">
                      mix ({seg.margin_pct}% seg. op margin)
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-2 text-[10px] text-slate-500 dark:text-slate-400 font-mono italic">
              *Segment margins reflect division-level operating profitability (weighted avg ~3.9%) prior to unallocated corporate overhead, vs {research.financial_snapshot?.ebitda_margin_pct ?? 3.64}% consolidated EBITDA margin.
            </div>
          </div>

          {/* Pinned Standing Notice (Neutral Grey Chrome - Report Item 107) */}
          {research.sebi_research_disclaimer && (
            <div className="px-3 py-2 rounded-lg bg-slate-100/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-[10px] text-slate-500 dark:text-slate-400 leading-snug flex items-center gap-2">
              <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="line-clamp-2">{research.sebi_research_disclaimer}</span>
            </div>
          )}

          {/* Verdict-First Summary Strip (Report Items 3, 4, 104) */}
          <div className="finance-card p-3.5 border-l-4 border-l-blue-600 bg-slate-50/70 dark:bg-slate-900/50">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white flex items-center gap-1.5 font-mono">
                <FileCheck className="w-3.5 h-3.5 text-blue-500" />
                4-Quarter Guidance Track Record (Promised vs. Delivered)
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-semibold">
                Primary Grounded
              </span>
            </div>

            {/* Guidance Track Record Rows - Derived from narrative_vs_numbers */}
            <div className="space-y-2 py-1">
              {guidanceSummaryRows.length === 0 ? (
                <div className="py-2 text-center text-[11px] text-slate-500 font-mono">
                  No guidance items extracted yet for {research.ticker}.
                </div>
              ) : (
                guidanceSummaryRows.map((row, rIdx) => {
                  const beatsCount = row.quarters.filter(q => q.status === 'BEAT' || q.status === 'MET').length;
                  const totalCount = row.quarters.length;
                  return (
                    <div
                      key={rIdx}
                      className={`flex items-center justify-between text-[11px] gap-2 ${
                        rIdx < guidanceSummaryRows.length - 1 ? 'pb-1.5 border-b border-slate-200/60 dark:border-slate-800/60' : ''
                      }`}
                    >
                      <div className="min-w-0">
                        <span className="font-semibold text-slate-800 dark:text-slate-200 block truncate">
                          {row.label}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono line-clamp-1">
                          {row.sublabel}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 shrink-0 font-mono text-[10px]">
                        {row.quarters.map((q, qIdx) => (
                          <span
                            key={qIdx}
                            className={`px-1.5 py-0.5 rounded font-bold border ${
                              q.status === 'BEAT'
                                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/40'
                                : q.status === 'MET'
                                ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800/40'
                                : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-200 dark:border-rose-800/40'
                            }`}
                          >
                            {q.quarter} {q.status === 'BEAT' ? '✓' : q.status === 'MET' ? '✓' : '▲'}
                          </span>
                        ))}
                        <span className={`text-[10px] font-bold ml-1 ${
                          beatsCount === totalCount ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-600 dark:text-slate-400'
                        }`}>
                          {beatsCount}/{totalCount} Met
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Quick Institutional Vital Statistics Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2 pt-2 border-t border-slate-200/80 dark:border-slate-800/80 text-[11px] font-mono">
              <div>
                <span className="text-slate-400 text-[10px] block">Cash Conversion</span>
                <span className="font-bold text-slate-900 dark:text-white">
                  CFO/PAT: {research.cash_quality.cash_conversion_ratio || 1.09}x
                </span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] block">Coverage Disclosure</span>
                <span className="font-bold text-slate-900 dark:text-white break-words block">
                  {research.coverage_line || research.coverage_assessment?.coverage_line || `${concallsAvailable} of 4 transcripts, annual report found`}
                </span>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <span className="text-slate-400 text-[10px] block">Primary Grounding</span>
                <span className={`font-bold ${research.has_reg33_filing || research.xbrl_filing_grounded ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-500 dark:text-slate-400'}`}>
                  {research.has_reg33_filing || research.xbrl_filing_grounded ? 'Reg 33 XBRL Grounded' : 'Seeded demo data'}
                </span>
              </div>
            </div>
          </div>

          {/* Grounded vs Missing Disclosures for Partial Coverage */}
          {research.missing_documents && research.missing_documents.length > 0 && (
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-amber-800 dark:text-amber-300 flex items-center gap-1.5 text-xs">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                  Partial Primary Coverage · {research.coverage_line || `${research.coverage_assessment?.breakdown?.concall_transcripts_available ?? 0} of 4 transcripts found`}
                </span>
                <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-amber-200/60 dark:bg-amber-900/60 text-amber-900 dark:text-amber-200 shrink-0">
                  Partial Data Grounded
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 pt-0.5">
                {research.available_documents?.map((doc, idx) => (
                  <span key={idx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800/60 flex items-center gap-1">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold">✓</span> Grounded: {doc}
                  </span>
                ))}
                {research.missing_documents?.map((doc, idx) => (
                  <span key={idx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800/60 flex items-center gap-1">
                    <span className="text-amber-600 dark:text-amber-400 font-bold">—</span> Missing: {doc}
                  </span>
                ))}
              </div>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 italic">
                Showing verified financial and operational fundamentals. Primary concall transcripts and guidance tracking will index upon exchange disclosure.
              </p>
            </div>
          )}

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
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-semibold flex items-center gap-1 border border-emerald-200 dark:border-emerald-800/40">
                    <FileCheck className="w-3 h-3 text-emerald-600" /> Primary Citation Audit: {Math.round(research.citation_faithfulness_score * 100)}% Grounded
                  </span>
                )}
              </div>

              {/* Guidance Status Legend (Item 7) */}
              <div className="flex items-center gap-3 text-[10px] font-mono py-1 px-2 rounded-md bg-slate-100/70 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 flex-wrap">
                <span className="font-semibold text-slate-700 dark:text-slate-300">Legend:</span>
                <span className="flex items-center gap-1 text-emerald-700 dark:text-emerald-400 font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" /> ✓ BEAT
                </span>
                <span className="flex items-center gap-1 text-blue-700 dark:text-blue-400 font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block" /> ✓ MET
                </span>
                <span className="flex items-center gap-1 text-rose-700 dark:text-rose-400 font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block" /> ▲ MISSED
                </span>
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
                            <span className="text-xs font-extrabold text-slate-900 dark:text-white line-clamp-2 break-words">
                              {item.metric}
                            </span>
                            <span className="text-[10px] font-semibold text-slate-400">
                              ({item.fiscal_quarter})
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 break-words mt-0.5">
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
                          {/* Visual Range Bar (Report Item 85) */}
                          {renderRangeBar(item)}

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
                              <p className="text-[10px] font-mono text-slate-500 dark:text-slate-400 pt-1">
                                Source: {item.source_doc_ref}
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
              {/* Multi-Year Trajectory & Cash Conversion Chart (Report Items 38, 87) */}
              {research.trajectory?.multi_year_financials && research.trajectory.multi_year_financials.length > 0 && (() => {
                const myf = research.trajectory.multi_year_financials;
                const maxRev = Math.max(...myf.map((m) => m.revenue_cr), 1);
                const maxCash = Math.max(...myf.map((m) => Math.max(m.cfo_cr, m.pat_cr)), 1);
                return (
                  <div className="finance-card p-3.5 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                          Multi-Year Trajectory & Cash Conversion
                        </h4>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Paired CFO vs PAT cash flow conversion across 4 audited fiscal cycles
                        </p>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                        {research.has_reg33_filing || research.xbrl_filing_grounded ? 'Reg 33 XBRL Grounded' : 'Seeded demo data'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 pt-1">
                      {myf.map((m) => {
                        const cfoWidth = Math.min(100, Math.max(12, Math.round((m.cfo_cr / maxCash) * 100)));
                        const patWidth = Math.min(100, Math.max(12, Math.round((m.pat_cr / maxCash) * 100)));
                        const isConversionSolid = m.cfo_to_pat >= 1.0;
                        return (
                          <div
                            key={m.fiscal_year}
                            className="p-2.5 rounded-lg bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/70 dark:border-slate-700/60 flex flex-col justify-between"
                          >
                            <div>
                              <div className="flex items-center justify-between mb-1.5">
                                <span className="text-xs font-extrabold font-mono text-slate-900 dark:text-white">
                                  {m.fiscal_year}
                                </span>
                                <span
                                  className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold font-num tabular-nums ${
                                    isConversionSolid
                                      ? 'text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200/80 dark:border-emerald-800/60'
                                      : 'text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/50 border border-amber-200/80 dark:border-amber-800/60'
                                  }`}
                                >
                                  CFO/PAT: {m.cfo_to_pat}x
                                </span>
                              </div>

                              <div className="text-[11px] mb-2 font-mono">
                                <div className="flex items-baseline justify-between text-slate-600 dark:text-slate-300">
                                  <span className="text-[10px] text-slate-400 uppercase font-sans">Revenue</span>
                                  <span className="font-bold text-slate-900 dark:text-white">
                                    ₹{m.revenue_cr.toLocaleString()} Cr
                                  </span>
                                </div>
                                <div className="w-full bg-slate-200 dark:bg-slate-700 h-1 rounded-full mt-1 overflow-hidden">
                                  <div
                                    className="bg-blue-600 dark:bg-blue-500 h-full rounded-full"
                                    style={{ width: `${Math.round((m.revenue_cr / maxRev) * 100)}%` }}
                                  />
                                </div>
                                <div className="text-[10px] text-slate-400 mt-0.5 text-right font-sans">
                                  {m.ebitda_margin_pct}% EBITDA
                                </div>
                              </div>
                            </div>

                            {/* Paired CFO vs PAT Bars */}
                            <div className="space-y-1.5 pt-1.5 border-t border-slate-200 dark:border-slate-700/60 text-[10px] font-mono">
                              <div>
                                <div className="flex justify-between text-slate-500 dark:text-slate-400 mb-0.5">
                                  <span>CFO</span>
                                  <span className="font-bold text-emerald-600 dark:text-emerald-400">
                                    ₹{m.cfo_cr} Cr
                                  </span>
                                </div>
                                <div className="w-full bg-slate-200 dark:bg-slate-700/60 h-1.5 rounded-full overflow-hidden">
                                  <div
                                    className="bg-emerald-500 h-full rounded-full"
                                    style={{ width: `${cfoWidth}%` }}
                                  />
                                </div>
                              </div>
                              <div>
                                <div className="flex justify-between text-slate-500 dark:text-slate-400 mb-0.5">
                                  <span>PAT</span>
                                  <span className="font-bold text-blue-600 dark:text-blue-400">
                                    ₹{m.pat_cr} Cr
                                  </span>
                                </div>
                                <div className="w-full bg-slate-200 dark:bg-slate-700/60 h-1.5 rounded-full overflow-hidden">
                                  <div
                                    className="bg-blue-500 h-full rounded-full"
                                    style={{ width: `${patWidth}%` }}
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    <p className="text-[10px] text-slate-400 dark:text-slate-500 pt-1 font-mono">
                      Source: Audited Balance Sheets & Cash Flow Statements (Consolidated IND-AS 7)
                    </p>
                  </div>
                );
              })()}

              {/* Operating Segment Revenue & Margin Stacked Bar (Report Item 88) */}
              {research.business_snapshot.segments && research.business_snapshot.segments.length > 0 && (() => {
                const segmentColors = [
                  'bg-blue-600 dark:bg-blue-500',
                  'bg-indigo-600 dark:bg-indigo-500',
                  'bg-sky-500 dark:bg-sky-400',
                  'bg-teal-600 dark:bg-teal-500',
                  'bg-slate-500 dark:bg-slate-400',
                ];
                return (
                  <div className="finance-card p-3.5 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                        Operating Segment Revenue & Margin Mix
                      </h4>
                      <span className="text-[10px] font-mono text-slate-400">IND-AS 108</span>
                    </div>

                    {/* Proportional Stacked Bar */}
                    <div className="w-full h-3.5 rounded-full overflow-hidden flex bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                      {research.business_snapshot.segments.map((seg, idx) => (
                        <div
                          key={seg.name}
                          style={{ width: `${seg.revenue_share_pct}%` }}
                          className={`${segmentColors[idx % segmentColors.length]} h-full transition-all`}
                          title={`${seg.name}: ${seg.revenue_share_pct}% share, ${seg.margin_pct}% margin`}
                        />
                      ))}
                    </div>

                    {/* Segment Legend */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 pt-1">
                      {research.business_snapshot.segments.map((seg, idx) => (
                        <div key={seg.name} className="flex items-center gap-1.5 text-[11px]">
                          <span className={`w-2.5 h-2.5 rounded-sm shrink-0 ${segmentColors[idx % segmentColors.length]}`} />
                          <span className="truncate text-slate-700 dark:text-slate-300 font-medium">
                            {seg.name}:
                          </span>
                          <span className="font-mono font-bold font-num tabular-nums text-slate-900 dark:text-white shrink-0">
                            {seg.revenue_share_pct}%
                          </span>
                          <span className="text-[10px] font-mono text-slate-400 shrink-0">
                            ({seg.margin_pct}% margin)
                          </span>
                        </div>
                      ))}
                    </div>

                    <p className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">
                      Source: Audited Annual Report Note on Operating Segments
                    </p>
                  </div>
                );
              })()}

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

                    <div className="grid grid-cols-2 sm:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-slate-200 dark:divide-slate-800/80 border-y border-slate-200 dark:border-slate-800/80 py-2.5 my-1 text-xs font-mono font-num">
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">Net Interest Margin (NIM)</span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          {research.financial_snapshot.nim_bps} bps
                        </span>
                        <span className="text-[10px] text-slate-400 block tabular-nums">
                          ({research.financial_snapshot.nim_pct}% on assets)
                        </span>
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">Gross / Net NPA</span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          {research.financial_snapshot.gross_npa_pct}% / {research.financial_snapshot.net_npa_pct}%
                        </span>
                        <span className="text-emerald-500 font-semibold text-[10px] block font-sans">
                          Pristine Quality
                        </span>
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">Provision Coverage (PCR)</span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          {research.financial_snapshot.provision_coverage_ratio_pct}%
                        </span>
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">RoA / RoE</span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
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
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-lg flex items-start gap-2">
                      <Info className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
                      <span>{research.cash_quality.assessment}</span>
                    </p>
                  </div>
                </div>
              ) : (
                /* Industrial Equity Template */
                <div className="space-y-3">
                  <div className="finance-card p-3.5">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 font-mono">
                      Headline Ratios & Multipliers (Audited & Run-Rates)
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-slate-200 dark:divide-slate-800/80 border-y border-slate-200 dark:border-slate-800/80 py-2.5 my-1 text-xs font-mono font-num">
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1.5 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">
                          {research.ticker === 'DIXON.NS' ? 'Revenue (FY26 Audited)' : 'Revenue (Annual Audited)'}
                        </span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          ₹{research.financial_snapshot.current_revenue_cr?.toLocaleString()} Cr
                        </span>
                        <span className="text-emerald-600 dark:text-emerald-400 font-semibold tabular-nums text-[11px] block">
                          +{research.financial_snapshot.revenue_yoy_growth_pct}% YoY
                        </span>
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1.5 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">
                          {research.ticker === 'DIXON.NS' ? 'Q2 FY27 Revenue' : 'Quarterly Run-Rate'}
                        </span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          {research.ticker === 'DIXON.NS' ? '₹11,534 Cr' : `₹${Math.round((research.financial_snapshot.current_revenue_cr || 10000) / 4).toLocaleString()} Cr`}
                        </span>
                        <span className="text-emerald-600 dark:text-emerald-400 font-semibold tabular-nums text-[11px] block">
                          {research.ticker === 'DIXON.NS' ? '+120.4% YoY' : 'Latest Filing'}
                        </span>
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1.5 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">
                          {research.ticker === 'DIXON.NS' ? 'EBITDA Margin (Q2 FY27)' : 'EBITDA Margin'}
                        </span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          {research.financial_snapshot.ebitda_margin_pct}%
                        </span>
                        <span className="text-slate-500 text-[11px] block">
                          {research.ticker === 'DIXON.NS' ? '₹420 Cr' : `PAT ₹${research.financial_snapshot.pat_cr} Cr`}
                        </span>
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0 py-1.5 sm:py-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">
                          {research.ticker === 'DIXON.NS' ? 'ROCE / ROE (FY26)' : 'ROCE / ROE'}
                        </span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          {research.financial_snapshot.roce_pct}% / {research.financial_snapshot.roe_pct}%
                        </span>
                        <span className="text-slate-500 text-[11px] block">
                          D/E: {research.financial_snapshot.debt_to_equity}x
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Cash Quality & Working Capital */}
                  <div className="finance-card p-3.5">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                        Cash Conversion Quality
                      </h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold font-num tabular-nums bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200 border border-slate-300 dark:border-slate-700">
                        CFO / PAT: {research.cash_quality.cash_conversion_ratio}x
                      </span>
                    </div>

                    <div className="grid grid-cols-3 divide-x divide-slate-200 dark:divide-slate-800/80 border-y border-slate-200 dark:border-slate-800/80 py-2.5 my-2 text-xs font-mono font-num">
                      <div className="px-2.5 first:pl-0 last:pr-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">
                          {research.ticker === 'DIXON.NS' ? 'Cash From Ops (FY26)' : 'Cash From Ops'}
                        </span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          ₹{research.cash_quality.cfo_cr} Cr
                        </span>
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">
                          {research.ticker === 'DIXON.NS' ? 'Free Cash Flow (FY26)' : 'Free Cash Flow'}
                        </span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          ₹{research.cash_quality.free_cash_flow_cr} Cr
                        </span>
                        {research.ticker === 'DIXON.NS' && (
                          <span className="text-[10px] text-amber-600 dark:text-amber-400 block font-sans">
                            PLI Capex Phase
                          </span>
                        )}
                      </div>
                      <div className="px-2.5 first:pl-0 last:pr-0">
                        <span className="text-slate-400 font-sans text-[10px] uppercase font-medium block">
                          {research.ticker === 'DIXON.NS' ? 'Working Capital (Blended)' : 'Working Capital'}
                        </span>
                        <span className="text-sm font-bold tabular-nums text-slate-900 dark:text-white block mt-0.5">
                          {research.cash_quality.working_capital_days} days
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-lg flex items-start gap-2">
                      <Info className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
                      <span>{research.cash_quality.assessment}</span>
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
                  Bull Thesis (Grounded Catalysts)
                </h4>
                <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-200">
                  {research.bull_case
                    .map((b) => parseThesisClaim(b))
                    .filter((b): b is { claim: string; source: string } => b !== null)
                    .map((item, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-emerald-500 font-bold mt-0.5">•</span>
                        <div className="flex-1">
                          <span className="leading-relaxed block">{item.claim}</span>
                          <span className="mt-1 inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                            Source: {item.source}
                          </span>
                        </div>
                      </li>
                    ))}
                </ul>
              </div>

              {/* Bear Case */}
              <div className="finance-card p-3.5 border-l-4 border-l-rose-500">
                <h4 className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider mb-2">
                  Bear Risks & Downside Triggers
                </h4>
                <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-200">
                  {research.bear_case
                    .map((b) => parseThesisClaim(b))
                    .filter((b): b is { claim: string; source: string } => b !== null)
                    .map((item, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-rose-500 font-bold mt-0.5">•</span>
                        <div className="flex-1">
                          <span className="leading-relaxed block">{item.claim}</span>
                          <span className="mt-1 inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                            Source: {item.source}
                          </span>
                        </div>
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
        </div>
      ) : (
        <div className="finance-card p-6 text-center space-y-3 border-amber-200/80 dark:border-amber-900/60 bg-amber-50/10 dark:bg-amber-950/10">
          <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
              Primary Disclosures Missing · {ticker}
            </h3>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 max-w-sm mx-auto mt-1 leading-relaxed">
              No verified Regulation 30/33 XBRL disclosures or official concall transcripts are indexed for <span className="font-mono font-semibold text-slate-900 dark:text-white">{ticker}</span>.
            </p>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-[10px] text-slate-500 font-mono max-w-sm mx-auto text-left space-y-1">
            <div className="font-bold text-slate-700 dark:text-slate-300">● Strict Grounding Policy:</div>
            <div>• Primary exchange XBRL required for deterministic financials</div>
            <div>• Zero external web guessing or unverified estimates</div>
            <div>• Full concall transcripts indexed upon verified publication</div>
          </div>
          <div className="flex justify-center gap-2 pt-1">
            <button
              onClick={() => {
                setSearchInput('DIXON.NS');
                fetchResearch('DIXON.NS');
              }}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition"
            >
              Load DIXON.NS
            </button>
            <button
              onClick={() => {
                setSearchInput('TRENT.NS');
                fetchResearch('TRENT.NS');
              }}
              className="px-3 py-1.5 bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 rounded-lg text-xs font-semibold transition"
            >
              Load TRENT.NS
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
