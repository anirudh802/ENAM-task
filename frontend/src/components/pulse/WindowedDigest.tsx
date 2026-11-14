import React, { useState } from 'react';
import { DigestResponse } from '../../types';
import { ChevronDown, ChevronUp, ArrowUpRight, UserCheck, Layers, User, GraduationCap, FileText, Sparkles, Phone } from 'lucide-react';
import { ActionButton } from '../common/ActionButton';

interface WindowedDigestProps {
  digest: DigestResponse | null;
  selectedHours: number;
  setSelectedHours: (hours: number) => void;
  selectedCategory: string;
  setSelectedCategory: (cat: string) => void;
  onSelectTicker: (ticker: string) => void;
  onCallContact?: (contactName: string) => void;
}

export const WindowedDigest: React.FC<WindowedDigestProps> = ({
  digest,
  selectedHours,
  setSelectedHours,
  selectedCategory,
  setSelectedCategory,
  onSelectTicker,
  onCallContact,
}) => {
  const [showRoutine, setShowRoutine] = useState(false);

  const formatFilingDate = (isoTime: string) => {
    try {
      const dt = new Date(isoTime);
      if (isNaN(dt.getTime())) return isoTime;
      const yyyy = dt.getFullYear();
      const mm = String(dt.getMonth() + 1).padStart(2, '0');
      const dd = String(dt.getDate()).padStart(2, '0');
      const hh = String(dt.getHours()).padStart(2, '0');
      const min = String(dt.getMinutes()).padStart(2, '0');
      return `${yyyy}-${mm}-${dd} ${hh}:${min} IST`;
    } catch {
      return isoTime;
    }
  };

  const formatFreshness = (isoTime: string) => {
    try {
      const dt = new Date(isoTime);
      if (isNaN(dt.getTime())) return 'Recently';
      // Demo clock reference: 13 Nov 18:45 IST
      const refTime = new Date('2026-11-13T18:45:00');
      const diffMs = refTime.getTime() - dt.getTime();
      if (Math.abs(diffMs) <= 1800000) {
        return '18:45 IST';
      }
      const diffHours = Math.round(diffMs / (1000 * 60 * 60));
      if (diffHours <= 0) return '18:45 IST';
      if (diffHours < 24) return `${diffHours}h ago`;
      const days = Math.round(diffHours / 24);
      return `${days}d ago`;
    } catch {
      return 'Today';
    }
  };

  const categories = [
    { id: 'all', label: 'All Feeds' },
    { id: 'results', label: 'Results' },
    { id: 'management_change', label: 'Mgmt Change' },
    { id: 'M&A', label: 'M&A' },
    { id: 'capex', label: 'Capex' },
    { id: 'litigation', label: 'Litigation' },
  ];

  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'results':
        return 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60';
      case 'management_change':
        return 'bg-indigo-50 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800/60';
      case 'M&A':
        return 'bg-purple-50 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-200 dark:border-purple-800/60';
      case 'capex':
        return 'bg-cyan-50 text-cyan-800 dark:bg-cyan-950/60 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800/60';
      case 'litigation':
        return 'bg-rose-50 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-800/60';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700';
    }
  };

  const renderMaterialityBadge = (score: number) => {
    if (score >= 9) {
      return (
        <span className="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded border bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-900/60 flex items-center gap-1 shrink-0">
          <span className="text-[9px]">▲</span>
          <span>{score}/10 CRITICAL</span>
        </span>
      );
    }
    if (score >= 7) {
      return (
        <span className="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded border bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-900/60 flex items-center gap-1 shrink-0">
          <span className="text-[9px]">●</span>
          <span>{score}/10 HIGH</span>
        </span>
      );
    }
    return (
      <span className="text-[10px] font-medium font-mono px-1.5 py-0.5 rounded border bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 flex items-center gap-1 shrink-0">
        <span className="text-[9px]">●</span>
        <span>{score}/10 ROUTINE</span>
      </span>
    );
  };

  const renderDeltaChip = (val?: number, label?: string) => {
    if (val === undefined || val === null) return null;
    const isPositive = val >= 0;
    return (
      <span
        className={`text-[10px] font-mono font-medium tabular-nums inline-flex items-center gap-0.5 ${
          isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
        }`}
      >
        <span>{isPositive ? '↑' : '↓'}</span>
        <span>{isPositive ? `+${val}%` : `${val}%`}</span>
        {label && <span className="text-slate-400 dark:text-slate-500 font-sans text-[9px]">{label}</span>}
      </span>
    );
  };

  // Compute feed summary counts
  const criticalCount = digest?.material_filings.filter((f) => f.materiality_score >= 9).length || 0;
  const highCount = digest?.material_filings.filter((f) => f.materiality_score >= 7 && f.materiality_score < 9).length || 0;
  const routineCount = digest?.routine_count || 0;

  return (
    <div>
      {/* Time Window Segmented Bar */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-1 bg-slate-200/80 dark:bg-slate-800/80 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setSelectedHours(24)}
            className={`min-h-[32px] px-3 py-1 rounded-lg transition-all ${
              selectedHours === 24
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            24 Hours
          </button>
          <button
            onClick={() => setSelectedHours(168)}
            className={`min-h-[32px] px-3 py-1 rounded-lg transition-all ${
              selectedHours === 168
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            7 Days
          </button>
          <button
            onClick={() => setSelectedHours(720)}
            className={`min-h-[32px] px-3 py-1 rounded-lg transition-all ${
              selectedHours === 720
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            30 Days
          </button>
        </div>

        {digest && (
          <span className="text-[11px] font-mono font-num tabular-nums text-slate-500 dark:text-slate-400">
            <span className="font-semibold text-slate-700 dark:text-slate-300">{digest.material_count}</span> high-signal filings
          </span>
        )}
      </div>

      {/* Category Filter Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-2 no-scrollbar">
        {categories.map((cat) => {
          const isSelected = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`min-h-[32px] px-3 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition border ${
                isSelected
                  ? 'bg-blue-600 border-blue-600 text-white shadow-sm'
                  : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60'
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Daily Load Summary Bar */}
      {digest && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px] font-mono px-3 py-1.5 mb-3 rounded-lg bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 text-slate-600 dark:text-slate-400">
          <div className="flex items-center gap-1.5 whitespace-nowrap">
            <span className="text-rose-600 dark:text-rose-400 font-semibold">{criticalCount} critical</span>
            <span>·</span>
            <span className="text-amber-600 dark:text-amber-400 font-semibold">{highCount} high</span>
            <span>·</span>
            <span>{routineCount} routine</span>
          </div>
          <span className="text-[10px] text-slate-500 whitespace-nowrap sm:text-right">
            Demo data as of 13 Nov 18:45 IST
          </span>
        </div>
      )}

      {/* Material Filings List */}
      <div className="space-y-3 mb-4">
        {!digest || digest.material_filings.length === 0 ? (
          <div className="text-center py-8 text-slate-500 dark:text-slate-400 text-xs">
            {!digest ? 'Loading primary exchange disclosures...' : 'No material filings recorded in this time window.'}
          </div>
        ) : (
          digest.material_filings.map((filing) => (
            <div
              key={filing.id}
              className="finance-card p-3.5 hover:border-slate-300 dark:hover:border-slate-700 transition"
            >
              {/* Card Fixed Signal Strip: Severity, Ticker, Company, Category, Freshness, Research Link */}
              <div className="flex items-start justify-between gap-2 mb-2 pb-2 border-b border-slate-100 dark:border-slate-800/80">
                <div className="flex items-center gap-1.5 flex-wrap">
                  {renderMaterialityBadge(filing.materiality_score)}
                  <span className="font-bold text-xs text-blue-600 dark:text-blue-400 tracking-tight font-mono">
                    {filing.ticker}
                  </span>
                  <span className="text-slate-300 dark:text-slate-700">•</span>
                  <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[150px]">
                    {filing.company_name}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${getCategoryColor(
                      filing.category
                    )}`}
                  >
                    {filing.category.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  <span
                    className="text-[10px] text-slate-500 dark:text-slate-400 font-mono"
                    title={`Filing: ${formatFilingDate(filing.filing_time)}`}
                  >
                    {formatFreshness(filing.filing_time)}
                  </span>
                  <ActionButton
                    variant="ghost"
                    icon={ArrowUpRight}
                    label="DeepDive"
                    onClick={() => onSelectTicker(filing.ticker)}
                    title={`DeepDive pull research for ${filing.ticker}`}
                    aria-label={`Open DeepDive for ${filing.ticker}`}
                  />
                </div>
              </div>

              {/* Title & Description */}
              <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 mb-1 leading-snug">
                {filing.title}
              </h4>
              <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mb-2.5">
                {filing.description}
              </p>

              {/* 4-Metric Grid for Results: Revenue, EBITDA, PBT, PAT with QoQ and YoY */}
              {filing.headline_metrics && (
                <div className="border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 my-2.5 bg-slate-50/70 dark:bg-slate-950/40">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    {/* 1. Revenue */}
                    <div className="border-r border-slate-200/80 dark:border-slate-800/80 pr-2 last:border-r-0">
                      <span className="text-[9px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-semibold block">
                        Revenue
                      </span>
                      <span className="text-sm font-mono font-bold tabular-nums text-slate-900 dark:text-slate-100 block">
                        ₹{filing.headline_metrics.revenue_cr?.toLocaleString()} Cr
                      </span>
                      <div className="flex flex-col gap-0.5 mt-0.5">
                        {renderDeltaChip(filing.headline_metrics.revenue_yoy_pct, 'YoY')}
                        {renderDeltaChip(filing.headline_metrics.revenue_qoq_pct, 'QoQ')}
                      </div>
                    </div>

                    {/* 2. EBITDA */}
                    <div className="border-r border-slate-200/80 dark:border-slate-800/80 pr-2 last:border-r-0">
                      <span className="text-[9px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-semibold block">
                        EBITDA ({filing.headline_metrics.ebitda_margin_pct}%)
                      </span>
                      <span className="text-sm font-mono font-bold tabular-nums text-slate-900 dark:text-slate-100 block">
                        ₹{filing.headline_metrics.ebitda_cr?.toLocaleString()} Cr
                      </span>
                      <div className="flex flex-col gap-0.5 mt-0.5">
                        {renderDeltaChip(filing.headline_metrics.ebitda_yoy_pct, 'YoY')}
                        {renderDeltaChip(filing.headline_metrics.ebitda_qoq_pct, 'QoQ')}
                      </div>
                    </div>

                    {/* 3. PBT */}
                    <div className="border-r border-slate-200/80 dark:border-slate-800/80 pr-2 last:border-r-0">
                      <span className="text-[9px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-semibold block">
                        PBT
                      </span>
                      <span className="text-sm font-mono font-bold tabular-nums text-slate-900 dark:text-slate-100 block">
                        ₹{filing.headline_metrics.pbt_cr?.toLocaleString()} Cr
                      </span>
                      <div className="flex flex-col gap-0.5 mt-0.5">
                        {renderDeltaChip(filing.headline_metrics.pbt_yoy_pct, 'YoY')}
                        {renderDeltaChip(filing.headline_metrics.pbt_qoq_pct, 'QoQ')}
                      </div>
                    </div>

                    {/* 4. PAT (Net) */}
                    <div>
                      <span className="text-[9px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-semibold block">
                        PAT (Net)
                      </span>
                      <span className="text-sm font-mono font-bold tabular-nums text-slate-900 dark:text-slate-100 block">
                        ₹{filing.headline_metrics.pat_cr?.toLocaleString()} Cr
                      </span>
                      <div className="flex flex-col gap-0.5 mt-0.5">
                        {renderDeltaChip(filing.headline_metrics.pat_yoy_pct, 'YoY')}
                        {renderDeltaChip(filing.headline_metrics.pat_qoq_pct, 'QoQ')}
                      </div>
                    </div>
                  </div>

                  <div className="mt-2 pt-1.5 border-t border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                    <span className="flex items-center gap-1">
                      <FileText className="w-3 h-3 text-slate-400" />
                      {filing.category === 'results' && filing.headline_metrics ? 'Reg 33 XBRL Grounded · Primary Disclosure' : 'Seeded demo data'}
                    </span>
                    <span>Consolidated</span>
                  </div>
                </div>
              )}

              {/* Executive Profile with Synthetic Transparency Label */}
              {filing.executive_profile && (
                <div className="bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 border-l-2 border-l-indigo-500 p-2.5 rounded-lg mb-2 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                      <span>{filing.executive_profile.name} — {filing.executive_profile.role}</span>
                    </div>
                    <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                      Synthetic Profile · Disclosures Grounded
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-300">
                    Prior: {filing.executive_profile.previous_title} at {filing.executive_profile.previous_employer}
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1.5 font-mono">
                    <GraduationCap className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>{filing.executive_profile.education}</span>
                  </div>
                </div>
              )}

              {/* Dedicated Violet Personal Network Strip with Explicit "Why" Reason */}
              {filing.network_connection && (
                <div className="bg-violet-50/70 dark:bg-violet-950/20 border border-violet-200/80 dark:border-violet-900/50 border-l-2 border-l-violet-500 p-2.5 rounded-lg text-xs mt-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 min-w-0 flex-wrap">
                      <div className="p-1 rounded bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300 shrink-0">
                        <UserCheck className="w-3.5 h-3.5 stroke-[2]" />
                      </div>
                      <span className="font-semibold text-slate-900 dark:text-slate-100 text-[11px] truncate">
                        {filing.network_connection.connected_person_name}
                      </span>
                      <span className="text-[9px] text-violet-700 dark:text-violet-300 font-mono font-medium px-1.5 py-0.2 rounded bg-violet-100 dark:bg-violet-900/60 shrink-0">
                        {filing.network_connection.degree_of_separation === 1 ? '1st Degree' : '2nd Degree'}
                      </span>
                      <span className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                        • {filing.network_connection.relationship}
                      </span>
                    </div>
                    {onCallContact && (
                      <ActionButton
                        variant="icon"
                        icon={Phone}
                        label="Channel check"
                        title={`Channel check: ${filing.network_connection.connected_person_name}`}
                        aria-label={`Channel check outreach to ${filing.network_connection.connected_person_name}`}
                        onClick={() => onCallContact(filing.network_connection!.connected_person_name)}
                      />
                    )}
                  </div>
                  {filing.network_connection.why_line && (
                    <p className="text-[12px] text-slate-700 dark:text-slate-200 mt-1.5 leading-snug">
                      <span className="text-violet-700 dark:text-violet-300 font-semibold">Why to call: </span>
                      {filing.network_connection.why_line}
                    </p>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Collapsed Routine Paperwork Accordion */}
      {digest && digest.routine_filings.length > 0 && (
        <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden bg-slate-50/60 dark:bg-slate-900/40">
          <button
            onClick={() => setShowRoutine(!showRoutine)}
            className="w-full min-h-[44px] px-3 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition"
          >
            <div className="flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              <span>
                {digest.routine_count} routine compliance filings collapsed
              </span>
            </div>
            {showRoutine ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showRoutine && (
            <div className="divide-y divide-slate-200 dark:divide-slate-800 px-3 py-1 bg-white dark:bg-slate-950">
              {digest.routine_filings.map((rf) => (
                <div key={rf.id} className="py-2 text-[11px]">
                  <div className="flex items-center justify-between text-slate-500 mb-0.5">
                    <span className="font-bold text-slate-700 dark:text-slate-300 font-mono">{rf.ticker}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 uppercase font-medium">
                      {rf.category}
                    </span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 truncate">{rf.title}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
