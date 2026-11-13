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
                <span>3.0x (Standard)</span>
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
                <span>±5.0%</span>
                <span>±10.0%</span>
              </div>
            </div>

            <button
              onClick={() => {
                onUpdatePreferences(volMultiplier, priceMove);
                setShowConfig(false);
              }}
              className="w-full py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg transition"
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
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-1.5">
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
                className={`p-1 rounded-md transition ${
                  anom.is_pinned
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
                }`}
              >
                <Pin className={`w-3.5 h-3.5 ${anom.is_pinned ? 'fill-current' : ''}`} />
              </button>
            </div>

            <h4 className="text-xs font-bold text-slate-900 dark:text-white mb-1">
              {anom.headline}
            </h4>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mb-2.5">
              {anom.detail}
            </p>

            {/* Metrics Chips & Action */}
            <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-[10px]">
                {anom.metrics?.volume_multiple && (
                  <span className="font-semibold text-blue-600 dark:text-blue-400">
                    {anom.metrics.volume_multiple}x Vol
                  </span>
                )}
                {anom.metrics?.daily_return_pct !== undefined && (
                  <span
                    className={`font-semibold ${
                      anom.metrics.daily_return_pct >= 0 ? 'text-emerald-500' : 'text-rose-500'
                    }`}
                  >
                    {anom.metrics.daily_return_pct >= 0 ? '+' : ''}
                    {anom.metrics.daily_return_pct}%
                  </span>
                )}
              </div>

              <button
                onClick={() => onInvestigateTicker(anom.ticker)}
                className="text-xs text-blue-600 dark:text-blue-400 font-semibold hover:underline flex items-center gap-0.5"
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
