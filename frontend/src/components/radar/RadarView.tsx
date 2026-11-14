import React, { useState } from 'react';
import { Anomaly, UserPreferences } from '../../types';
import { Sliders, Pin, ArrowUpRight, Zap } from 'lucide-react';
import { ActionButton } from '../common/ActionButton';

interface RadarViewProps {
  anomalies: Anomaly[];
  preferences: UserPreferences | null;
  onUpdatePreferences: (volume: number, price: number) => void;
  onTogglePin: (id: string, isPinned: boolean) => void;
  onInvestigateTicker: (ticker: string) => void;
}

export const RadarView: React.FC<RadarViewProps> = ({
  anomalies,
  preferences,
  onUpdatePreferences,
  onTogglePin,
  onInvestigateTicker,
}) => {
  const [showConfig, setShowConfig] = useState(false);
  const [volMultiplier, setVolMultiplier] = useState(
    preferences?.volume_multiplier_threshold || 2.0
  );
  const [priceMove, setPriceMove] = useState(
    preferences?.price_move_pct_threshold || 3.5
  );

  // Live preview matching anomalies count
  const matchingCount = anomalies.filter((a) => {
    const vol = a.metrics?.volume_multiple || 1.0;
    const price = Math.abs(a.metrics?.daily_return_pct || 0);
    return vol >= volMultiplier || price >= priceMove;
  }).length;

  // Group anomalies by company so dual-rule anomalies (e.g. CDSL volume + price) merge into one card (Report Item 101)
  const groupedAnomalies = React.useMemo(() => {
    const map = new Map<string, {
      id: string;
      ticker: string;
      company_name: string;
      is_pinned: boolean;
      severity: string;
      headline: string;
      detail: string;
      timestamp: string;
      anomalies: Anomaly[];
      rulesFired: Array<{ label: string; rule: string; value: string; color: string }>;
      volume_multiple?: number;
      daily_return_pct?: number;
      z_score?: number;
      sigma_60d?: number;
    }>();

    anomalies.forEach((a) => {
      const vol = a.metrics?.volume_multiple;
      const price = a.metrics?.daily_return_pct;
      const z = a.metrics?.z_score;
      const sigma = a.metrics?.sigma_60d;

      const ruleList: Array<{ label: string; rule: string; value: string; color: string }> = [];
      if (vol && vol >= volMultiplier) {
        ruleList.push({
          label: 'Volume Surge',
          rule: `≥${volMultiplier}x`,
          value: `${vol}x Vol`,
          color: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800',
        });
      }
      if (price !== undefined && Math.abs(price) >= priceMove) {
        ruleList.push({
          label: 'Price Shock',
          rule: `≥±${priceMove}%`,
          value: `${price > 0 ? '+' : ''}${price}%`,
          color: price >= 0
            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
            : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-200 dark:border-rose-800',
        });
      }
      if (ruleList.length === 0 && a.anomaly_type) {
        ruleList.push({
          label: a.anomaly_type.replace('_', ' '),
          rule: 'Triggered',
          value: a.severity,
          color: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700',
        });
      }

      if (map.has(a.ticker)) {
        const existing = map.get(a.ticker)!;
        existing.anomalies.push(a);
        existing.is_pinned = existing.is_pinned || a.is_pinned;
        if (a.severity === 'CRITICAL') existing.severity = 'CRITICAL';
        existing.rulesFired = [...existing.rulesFired, ...ruleList];
        if (vol && (!existing.volume_multiple || vol > existing.volume_multiple)) {
          existing.volume_multiple = vol;
        }
        if (price !== undefined) existing.daily_return_pct = price;
        if (z !== undefined) existing.z_score = z;
        if (sigma !== undefined) existing.sigma_60d = sigma;
        existing.detail = `${existing.detail} · ${a.detail}`;
      } else {
        map.set(a.ticker, {
          id: a.id,
          ticker: a.ticker,
          company_name: a.company_name,
          is_pinned: a.is_pinned,
          severity: a.severity,
          headline: a.headline,
          detail: a.detail,
          timestamp: a.metrics?.as_of || '2026-11-12 15:30 IST (EOD)',
          anomalies: [a],
          rulesFired: ruleList,
          volume_multiple: vol,
          daily_return_pct: price,
          z_score: z,
          sigma_60d: sigma,
        });
      }
    });

    return Array.from(map.values()).sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) return a.is_pinned ? -1 : 1;
      if (a.severity === 'CRITICAL' && b.severity !== 'CRITICAL') return -1;
      if (b.severity === 'CRITICAL' && a.severity !== 'CRITICAL') return 1;
      return 0;
    });
  }, [anomalies, volMultiplier, priceMove]);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-50 text-rose-700 dark:bg-rose-950/80 dark:text-rose-300 border-rose-200 dark:border-rose-900/60';
      case 'HIGH':
        return 'bg-amber-50 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300 border-amber-200 dark:border-amber-900/60';
      case 'MEDIUM':
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300';
    }
  };

  const renderSeverityGlyph = (sev: string) => {
    if (sev === 'CRITICAL') return '▲';
    return '●';
  };

  return (
    <div className="space-y-3">
      {/* Configuration Header */}
      <div className="finance-card p-3.5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-blue-500" />
              Anomaly Detection Radar
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Thresholds: &gt;{volMultiplier}x Vol SMA | &gt;±{priceMove}% Return
            </p>
          </div>
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-1 transition"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>{showConfig ? 'Close' : 'Adjust'}</span>
          </button>
        </div>

        {/* Sliders Drawer */}
        {showConfig && (
          <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 space-y-3">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-slate-600 dark:text-slate-300">Volume Surge Multiplier</span>
                <span className="font-bold text-blue-600 dark:text-blue-400">{volMultiplier}x</span>
              </div>
              <input
                type="range"
                min="1.5"
                max="5.0"
                step="0.1"
                value={volMultiplier}
                onChange={(e) => setVolMultiplier(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>1.5x (Sensitive)</span>
                <span>2.0x (Standard / Default)</span>
                <span>3.5x (High)</span>
                <span>5.0x (Extreme)</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-slate-600 dark:text-slate-300">Daily Price Shock %</span>
                <span className="font-bold text-blue-600 dark:text-blue-400">±{priceMove}%</span>
              </div>
              <input
                type="range"
                min="2.0"
                max="10.0"
                step="0.5"
                value={priceMove}
                onChange={(e) => setPriceMove(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>±2.0%</span>
                <span>±3.5% (Standard)</span>
                <span>±5.0%</span>
                <span>±10.0%</span>
              </div>
            </div>

            {/* Live Filter Counter */}
            <div className="text-[11px] text-slate-700 dark:text-slate-300 font-medium text-center bg-slate-100 dark:bg-slate-800/80 p-2 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center justify-center gap-1.5 font-num">
              <Sliders className="w-3.5 h-3.5 text-blue-500 dark:text-blue-400 shrink-0" />
              <span>Live Threshold Preview: <span className="font-mono font-semibold tabular-nums underline">{matchingCount} of {anomalies.length}</span> alerts match these settings</span>
            </div>

            <button
              onClick={() => {
                onUpdatePreferences(volMultiplier, priceMove);
                setShowConfig(false);
              }}
              className="w-full min-h-[44px] py-2 bg-blue-600/90 hover:bg-blue-500 text-white font-medium text-xs rounded-lg border border-blue-400/20 transition shadow-sm flex items-center justify-center active:scale-95"
            >
              Apply Sensitivity Settings ({anomalies.length} → {matchingCount} alerts)
            </button>
          </div>
        )}
      </div>

      {/* Ranked Anomalies Feed - Grouped by Company (Report Item 101) */}
      <div className="space-y-2.5">
        {!groupedAnomalies || groupedAnomalies.length === 0 ? (
          <div className="text-center py-8 text-slate-500 dark:text-slate-400 text-xs">
            No active anomalies matching sensitivity thresholds.
          </div>
        ) : (
          groupedAnomalies.map((anom) => (
          <div
            key={anom.id}
            className={`finance-card p-3.5 transition relative ${
              anom.is_pinned
                ? 'border-blue-400/80 dark:border-blue-500/60 bg-blue-50/20 dark:bg-blue-950/20'
                : ''
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span
                  className={`text-[10px] font-bold font-mono px-1.5 py-0.5 rounded border flex items-center gap-1 ${getSeverityBadge(
                    anom.severity
                  )}`}
                >
                  <span className="text-[9px]">{renderSeverityGlyph(anom.severity)}</span>
                  <span>{anom.severity}</span>
                </span>
                <span className="font-bold text-xs text-blue-600 dark:text-blue-400 font-mono">
                  {anom.ticker}
                </span>
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  {anom.company_name}
                </span>
              </div>

              {/* Pin Action */}
              <button
                onClick={() => onTogglePin(anom.id, !anom.is_pinned)}
                title={anom.is_pinned ? 'Unpin from top' : 'Pin to top'}
                className={`min-w-[44px] min-h-[44px] flex items-center justify-center rounded-md transition ${
                  anom.is_pinned
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
                }`}
              >
                <Pin className={`w-4 h-4 ${anom.is_pinned ? 'fill-current' : ''}`} />
              </button>
            </div>

            {/* Exact Timestamp & Exchange Tag */}
            <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono font-num mb-1.5">
              NSE · {anom.timestamp}
            </div>

            {/* Rules Fired Chips */}
            {anom.rulesFired && anom.rulesFired.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap mb-2">
                {anom.rulesFired.map((rf, rfIdx) => (
                  <span
                    key={rfIdx}
                    className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-md border flex items-center gap-1 ${rf.color}`}
                  >
                    <span>{rf.label}:</span>
                    <span className="font-bold">{rf.value}</span>
                    <span className="opacity-70 text-[9px]">({rf.rule})</span>
                  </span>
                ))}
              </div>
            )}

            <h4 className="text-xs font-bold text-slate-900 dark:text-white mb-1 leading-snug">
              {anom.headline}
            </h4>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mb-2.5">
              {anom.detail}
            </p>

            {/* Metrics Chips & Action */}
            <div className="flex items-center justify-between pt-1.5 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-[10px] flex-wrap">
                {anom.volume_multiple !== undefined && (
                  <span className="font-mono font-semibold font-num tabular-nums text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-1.5 py-0.5 rounded">
                    {anom.volume_multiple}x Vol
                  </span>
                )}
                {anom.daily_return_pct !== undefined && (
                  <span
                    className={`font-mono font-semibold font-num tabular-nums px-1.5 py-0.5 rounded border ${
                      anom.daily_return_pct >= 0
                        ? 'text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/40'
                        : 'text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800/40'
                    }`}
                  >
                    {anom.daily_return_pct >= 0 ? '+' : ''}
                    {anom.daily_return_pct}%
                  </span>
                )}
                {anom.z_score !== undefined && (
                  <span className="font-mono font-num tabular-nums text-slate-600 dark:text-slate-400 font-medium">
                    Z: {anom.z_score > 0 ? `+${anom.z_score.toFixed(1)}` : anom.z_score.toFixed(1)}σ
                  </span>
                )}
                {anom.sigma_60d !== undefined && (
                  <span className="font-mono font-num tabular-nums text-slate-500 dark:text-slate-400">
                    60d σ: {anom.sigma_60d}%
                  </span>
                )}
              </div>

              <ActionButton
                variant="ghost"
                icon={ArrowUpRight}
                label="DeepDive"
                onClick={() => onInvestigateTicker(anom.ticker)}
              />
            </div>
          </div>
        ))
      )}
    </div>
  </div>
);
};
