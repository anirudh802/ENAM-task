import React from 'react';
import { Anomaly } from '../../types';
import { X, ArrowUpRight, Phone, TrendingUp, UserCheck } from 'lucide-react';

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

  return (
    <div className="mb-4 rounded-xl border border-red-500/40 dark:border-red-500/30 bg-gradient-to-br from-red-50/90 via-white to-red-50/50 dark:from-red-950/40 dark:via-slate-900 dark:to-red-950/20 p-4 shadow-sm relative overflow-hidden transition-all">
      {/* Glow highlight */}
      <div className="absolute top-0 left-0 w-1.5 h-full bg-red-500" />

      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-red-700 dark:text-red-400">
            Pinned Critical Alert
          </span>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-red-100 dark:bg-red-900/60 text-red-800 dark:text-red-300">
            {alert.anomaly_type.replace('_', ' ')}
          </span>
        </div>

        {/* Close / Dismiss */}
        <button
          onClick={() => onDismiss(alert.id)}
          title="Dismiss pinned alert"
          className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 p-1 rounded-md transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-snug mb-1">
        {alert.headline}
      </h3>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
        {alert.detail}
      </p>

      {/* Metric / Network Highlights & Timestamp */}
      <div className="flex flex-wrap items-center gap-2 mb-2.5 text-[11px]">
        {alert.metrics?.volume_multiple && (
          <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 font-semibold flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            {alert.metrics.volume_multiple}x Vol Multiple
          </span>
        )}
        {alert.metrics?.daily_return_pct !== undefined && (
          <span className={`px-2 py-0.5 rounded font-semibold ${
            alert.metrics.daily_return_pct >= 0
              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
              : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
          }`}>
            {alert.metrics.daily_return_pct >= 0 ? '+' : ''}{alert.metrics.daily_return_pct}% Today
          </span>
        )}
        {alert.metrics?.connected_contact && (
          <span className="px-2 py-0.5 rounded bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 font-semibold flex items-center gap-1">
            <UserCheck className="w-3 h-3" />
            Network: {alert.metrics.connected_contact}
          </span>
        )}
      </div>

      {/* Freshness Timestamp & Exchange Tag */}
      <div className="text-[10px] text-slate-500 dark:text-slate-400 font-medium mb-3 flex items-center gap-1.5">
        <span>📍 NSE • Trade Date: {alert.metrics?.as_of || '2026-11-12 15:30 IST (EOD)'}</span>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-1 border-t border-red-200/60 dark:border-red-900/40">
        <button
          onClick={() => onInvestigate(alert.ticker)}
          className="flex-1 min-h-[44px] py-2 px-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition active:scale-95 shadow-sm"
        >
          <span>Research {alert.ticker}</span>
          <ArrowUpRight className="w-4 h-4" />
        </button>

        {alert.metrics?.connected_contact && onCallContact && (
          <button
            onClick={() => onCallContact(alert.metrics.connected_contact)}
            className="min-h-[44px] py-2 px-3 rounded-xl border border-purple-300 dark:border-purple-700 text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-950/40 text-xs font-semibold flex items-center gap-1.5 transition active:scale-95"
          >
            <Phone className="w-3.5 h-3.5" />
            <span>Scuttlebutt</span>
          </button>
        )}
      </div>
    </div>
  );
};
