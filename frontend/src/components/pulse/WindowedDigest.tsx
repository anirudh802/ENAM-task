import React, { useState } from 'react';
import { DigestResponse } from '../../types';
import { ChevronDown, ChevronUp, ArrowUpRight, UserCheck, Layers } from 'lucide-react';

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
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60';
      case 'management_change':
        return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/80 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800/60';
      case 'M&A':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-950/80 dark:text-purple-300 border-purple-200 dark:border-purple-800/60';
      case 'capex':
        return 'bg-cyan-100 text-cyan-800 dark:bg-cyan-950/80 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800/60';
      case 'litigation':
        return 'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-300 border-rose-200 dark:border-rose-800/60';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700';
    }
  };

  return (
    <div>
      {/* Time Window Segmented Bar */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-1 bg-slate-200/80 dark:bg-slate-800/80 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setSelectedHours(24)}
            className={`px-3 py-1 rounded-lg transition-all ${
              selectedHours === 24
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            24 Hours
          </button>
          <button
            onClick={() => setSelectedHours(168)}
            className={`px-3 py-1 rounded-lg transition-all ${
              selectedHours === 168
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            7 Days
          </button>
          <button
            onClick={() => setSelectedHours(720)}
            className={`px-3 py-1 rounded-lg transition-all ${
              selectedHours === 720
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            30 Days
          </button>
        </div>

        {digest && (
          <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
            {digest.material_count} high-signal filings
          </span>
        )}
      </div>

      {/* Category Filter Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-3 scrollbar-none">
        {categories.map((cat) => {
          const isSelected = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition border ${
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

      {/* Material Filings List */}
      <div className="space-y-3 mb-4">
        {digest?.material_filings.length === 0 ? (
          <div className="text-center py-8 text-slate-500 dark:text-slate-400 text-xs">
            No material filings recorded in this time window.
          </div>
        ) : (
          digest?.material_filings.map((filing) => (
            <div
              key={filing.id}
              className="finance-card p-3.5 hover:border-slate-300 dark:hover:border-slate-700 transition"
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="font-bold text-xs text-blue-600 dark:text-blue-400 tracking-tight">
                    {filing.ticker}
                  </span>
                  <span className="text-slate-400 dark:text-slate-600">•</span>
                  <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[160px]">
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

                <button
                  onClick={() => onSelectTicker(filing.ticker)}
                  className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition"
                  title="DeepDive research"
                >
                  <ArrowUpRight className="w-4 h-4" />
                </button>
              </div>

              {/* Title & Description */}
              <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 mb-1 leading-snug">
                {filing.title}
              </h4>
              <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mb-2.5">
                {filing.description}
              </p>

              {/* Headline Numbers for Results */}
              {filing.headline_metrics && (
                <div className="grid grid-cols-3 gap-1.5 bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg mb-2 text-[10px]">
                  <div>
                    <span className="text-slate-400 block">Revenue</span>
                    <span className="font-bold text-slate-900 dark:text-white">
                      ₹{filing.headline_metrics.revenue_cr?.toLocaleString()} Cr
                    </span>
                    {filing.headline_metrics.revenue_yoy_pct && (
                      <span className="text-emerald-600 dark:text-emerald-400 font-semibold block">
                        +{filing.headline_metrics.revenue_yoy_pct}% YoY
                      </span>
                    )}
                  </div>
                  <div>
                    <span className="text-slate-400 block">EBITDA Margin</span>
                    <span className="font-bold text-slate-900 dark:text-white">
                      {filing.headline_metrics.ebitda_margin_pct}%
                    </span>
                    <span className="text-slate-500 block">₹{filing.headline_metrics.ebitda_cr} Cr</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">PAT (Net)</span>
                    <span className="font-bold text-slate-900 dark:text-white">
                      ₹{filing.headline_metrics.pat_cr?.toLocaleString()} Cr
                    </span>
                    {filing.headline_metrics.pat_yoy_pct && (
                      <span className="text-emerald-600 dark:text-emerald-400 font-semibold block">
                        +{filing.headline_metrics.pat_yoy_pct}% YoY
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Executive Profile & Network Context for Management Changes */}
              {filing.executive_profile && (
                <div className="bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200/60 dark:border-indigo-900/40 p-2.5 rounded-lg mb-2 text-xs">
                  <div className="font-semibold text-indigo-950 dark:text-indigo-200 mb-0.5">
                    👤 {filing.executive_profile.name} — {filing.executive_profile.role}
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-300">
                    Prior: {filing.executive_profile.previous_title} at {filing.executive_profile.previous_employer}
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">
                    🎓 {filing.executive_profile.education}
                  </div>
                </div>
              )}

              {filing.network_connection && (
                <div className="bg-purple-50/70 dark:bg-purple-950/30 border border-purple-200/60 dark:border-purple-900/40 p-2 rounded-lg flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400 shrink-0" />
                    <div>
                      <span className="font-semibold text-purple-950 dark:text-purple-200 text-[11px]">
                        Network: {filing.network_connection.connected_person_name}
                      </span>
                      <p className="text-[10px] text-purple-800 dark:text-purple-300">
                        {filing.network_connection.relationship}
                      </p>
                    </div>
                  </div>
                  {onCallContact && (
                    <button
                      onClick={() => onCallContact(filing.network_connection!.connected_person_name)}
                      className="px-2 py-1 rounded bg-purple-600 text-white text-[10px] font-semibold hover:bg-purple-700 active:scale-95 transition"
                    >
                      Connect
                    </button>
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
            className="w-full px-3 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition"
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
                    <span className="font-bold text-slate-700 dark:text-slate-300">{rf.ticker}</span>
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
