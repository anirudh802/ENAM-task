import React from 'react';
import { Anomaly } from '../../types';
import { X, ArrowUpRight, Phone, TrendingUp, UserCheck } from 'lucide-react';
import { ActionButton } from '../common/ActionButton';

interface PinnedAlertCardProps {
  alert: Anomaly | null;
  onDismiss: (id: string) => void;
  onInvestigate: (ticker: string) => void;
  onCallContact?: (contactName: string) => void;
}

export const PinnedAlertCard: React.FC<PinnedAlertCardProps> = ({
  alert,
  onDismiss,
  onInvestigate,
  onCallContact,
}) => {
  if (!alert) return null;

  const formatAnomalyType = (type: string) => {
    if (type === 'DUAL_TECHNICAL_SURGE') return 'TECH BREAKOUT';
    return type.replace(/_/g, ' ');
  };

  const formatHeaderTimestamp = (raw?: string) => {
    if (!raw) return '12 Nov · EOD';
    return raw
      .replace('2026-11-12 15:30 IST (EOD)', '12 Nov · EOD')
      .replace('2026-11-12 15:30 IST', '12 Nov · 15:30')
      .replace('2026-11-12 14:15 IST', '12 Nov · 14:15')
      .replace('2026-11-12', '12 Nov');
  };

  return (
    <div className="mb-3.5 p-3.5 rounded-lg bg-slate-900 text-slate-100 border border-slate-800 border-l-4 border-l-rose-500 shadow-sm relative overflow-hidden transition-all">
      {/* Compact Metadata Bar: Status, Tag, Timestamp, Dismiss */}
      <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
        <div className="flex items-center gap-1.5 overflow-hidden">
          <span className="flex h-2 w-2 relative shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
          </span>
          <span className="font-bold text-rose-400 shrink-0">Pinned Alert</span>
          <span className="text-slate-600">·</span>
          <span className="text-slate-200 font-semibold shrink-0">{formatAnomalyType(alert.anomaly_type)}</span>
          <span className="text-slate-600">·</span>
          <span className="text-slate-400 shrink-0 font-num">{formatHeaderTimestamp(alert.metrics?.as_of)}</span>
        </div>

        {/* Close / Dismiss */}
        <button
          onClick={() => onDismiss(alert.id)}
          title="Dismiss pinned alert"
          className="text-slate-400 hover:text-white min-w-[44px] min-h-[44px] -mr-2 -mt-1 flex items-center justify-center rounded transition"
          aria-label="Dismiss alert"
        >
          <X className="w-3.5 h-3.5 stroke-[2]" />
        </button>
      </div>

      {/* Content: Factual Summary */}
      <h3 className="text-xs font-bold text-white leading-snug line-clamp-1 mb-1">
        {alert.headline}
      </h3>
      <p className="text-[11px] text-slate-300 leading-snug line-clamp-3 mb-2.5">
        {alert.detail}
      </p>

      {/* Single Shared Bottom Flex Row: Inline Metric Chips + Action Buttons */}
      <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-800 text-[10px] font-mono">
        <div className="flex items-center gap-1.5 flex-wrap overflow-hidden">
          {alert.metrics?.volume_multiple && (
            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 font-semibold font-num tabular-nums flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-slate-400" />
              {alert.metrics.volume_multiple}x Vol
            </span>
          )}
          {alert.metrics?.daily_return_pct !== undefined && (
            <span className={`px-1.5 py-0.5 rounded font-semibold font-num tabular-nums border ${
              alert.metrics.daily_return_pct >= 0
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60'
                : 'bg-rose-950/80 text-rose-300 border-rose-800/60'
            }`}>
              {alert.metrics.daily_return_pct >= 0 ? '+' : ''}{alert.metrics.daily_return_pct}%
            </span>
          )}
          {alert.metrics?.z_score !== undefined && (
            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-num tabular-nums hidden sm:inline">
              Z: {alert.metrics.z_score > 0 ? `+${alert.metrics.z_score.toFixed(1)}` : alert.metrics.z_score.toFixed(1)}σ
            </span>
          )}
          {alert.metrics?.pat_reported && (
            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-num tabular-nums">
              PAT ₹{alert.metrics.pat_reported} Cr
            </span>
          )}
          {alert.metrics?.connected_contact && (
            <span className="px-1.5 py-0.5 rounded bg-violet-950/60 text-violet-300 border border-violet-800/60 font-medium flex items-center gap-1">
              <UserCheck className="w-3 h-3 text-violet-400" />
              <span className="truncate max-w-[100px]">{alert.metrics.connected_contact}</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          {alert.metrics?.connected_contact && onCallContact && (
            <ActionButton
              variant="primary"
              icon={Phone}
              label="Channel check"
              onClick={() => onCallContact(alert.metrics.connected_contact)}
            />
          )}

          <ActionButton
            variant="ghost"
            icon={ArrowUpRight}
            label={`Research ${alert.ticker.replace('.NS', '')}`}
            onClick={() => onInvestigate(alert.ticker)}
          />
        </div>
      </div>
    </div>
  );
};
