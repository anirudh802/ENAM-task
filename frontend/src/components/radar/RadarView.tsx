import React, { useState } from 'react';
import { Anomaly, UserPreferences } from '../../types';
import { Sliders, Pin, ArrowUpRight, Zap } from 'lucide-react';

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

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300 border-red-300 dark:border-red-800';
      case 'HIGH':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 dark:border-amber-800';
      case 'MEDIUM':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-300 dark:border-blue-800';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300';
    }
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
            <div className="text-[11px] text-blue-700 dark:text-blue-300 font-semibold text-center bg-blue-50/80 dark:bg-blue-950/40 p-2 rounded-lg border border-blue-200/60 dark:border-blue-800/40">
              📊 Live Threshold Preview: <span className="underline">{matchingCount} of {anomalies.length}</span> alerts match these settings
            </div>

            <button
              onClick={() => {
                onUpdatePreferences(volMultiplier, priceMove);
                setShowConfig(false);
              }}
              className="w-full min-h-[44px] py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl transition shadow-sm flex items-center justify-center"
            >
              Apply Sensitivity Settings
            </button>
          </div>
        )}
      </div>

      {/* Ranked Anomalies Feed */}
      <div className="space-y-2.5">
        {anomalies.map((anom) => (
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
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${getSeverityBadge(
                    anom.severity
                  )}`}
                >
                  {anom.severity}
                </span>
                <span className="font-bold text-xs text-blue-600 dark:text-blue-400">
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
                className={`min-w-[36px] min-h-[36px] flex items-center justify-center rounded-md transition ${
                  anom.is_pinned
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
                }`}
              >
                <Pin className={`w-4 h-4 ${anom.is_pinned ? 'fill-current' : ''}`} />
              </button>
            </div>

            {/* Exact Timestamp & Exchange Tag */}
            <div className="text-[10px] text-slate-500 dark:text-slate-400 font-medium mb-1.5">
              📍 NSE • {anom.metrics?.as_of || '2026-11-12 15:30 IST (EOD)'}
            </div>

            <h4 className="text-xs font-bold text-slate-900 dark:text-white mb-1 leading-snug">
              {anom.headline}
            </h4>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mb-2.5">
              {anom.detail}
            </p>

            {/* Metrics Chips & Action */}
            <div className="flex items-center justify-between pt-1.5 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-[10px] flex-wrap">
                {anom.metrics?.volume_multiple && (
                  <span className="font-semibold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 px-1.5 py-0.5 rounded">
                    {anom.metrics.volume_multiple}x Vol
                  </span>
                )}
                {anom.metrics?.daily_return_pct !== undefined && (
                  <span
                    className={`font-semibold px-1.5 py-0.5 rounded ${
                      anom.metrics.daily_return_pct >= 0
                        ? 'text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-300'
                        : 'text-rose-700 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300'
                    }`}
                  >
                    {anom.metrics.daily_return_pct >= 0 ? '+' : ''}
                    {anom.metrics.daily_return_pct}%
                  </span>
                )}
                {anom.metrics?.z_score !== undefined && (
                  <span className="text-slate-600 dark:text-slate-400 font-medium">
                    Z: {anom.metrics.z_score > 0 ? `+${anom.metrics.z_score.toFixed(1)}` : anom.metrics.z_score.toFixed(1)}σ
                  </span>
                )}
                {anom.metrics?.sigma_60d !== undefined && (
                  <span className="text-slate-500 dark:text-slate-400">
                    60d σ: {anom.metrics.sigma_60d}%
                  </span>
                )}
              </div>

              <button
                onClick={() => onInvestigateTicker(anom.ticker)}
                className="min-h-[44px] px-3 py-1 text-xs text-blue-600 dark:text-blue-400 font-semibold hover:underline flex items-center gap-1 shrink-0"
              >
                <span>DeepDive</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
