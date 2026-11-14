import React from 'react';
import { Sun, Moon, Bell, BellOff, Smartphone, Monitor, RefreshCw } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';
import { useWebPush } from '../../hooks/useWebPush';

interface NavbarProps {
  isPhoneFrame: boolean;
  setIsPhoneFrame: (val: boolean) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  isPhoneFrame,
  setIsPhoneFrame,
  onRefresh,
  isRefreshing,
}) => {
  const { isDark, toggleTheme } = useTheme();
  const { isSupported, isSubscribed, subscribe, triggerTestAlert, isLoading } = useWebPush();

  return (
    <header className="sticky top-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3">
      <div className="flex items-center justify-between max-w-5xl mx-auto">
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-950 font-mono font-bold tracking-tighter border border-slate-700/50 flex items-center justify-center shadow-sm">
            <span className="text-sm">F</span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold tracking-tight text-base text-slate-900 dark:text-white">FINN</span>
              <span className="text-[10px] font-mono font-semibold uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200 border border-slate-300 dark:border-slate-700">ENAM</span>
            </div>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">Investment Intelligence</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          {/* Refresh / Scan */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            title="Scan for fresh market & filing anomalies"
            className="p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition active:scale-95"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-blue-500' : ''}`} />
          </button>

          {/* Web Push Notification Bell */}
          {isSupported && (
            <button
              onClick={() => {
                if (isSubscribed) {
                  triggerTestAlert();
                } else {
                  subscribe();
                }
              }}
              disabled={isLoading}
              title={isSubscribed ? 'Web Push Active (Click to send test alert)' : 'Enable native push notifications'}
              className={`p-2 rounded-lg transition active:scale-95 flex items-center gap-1 text-xs font-medium ${
                isSubscribed
                  ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40'
                  : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              {isSubscribed ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
            </button>
          )}

          {/* Theme Toggle (Light / Dark) */}
          <button
            onClick={toggleTheme}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition active:scale-95"
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
          </button>

          {/* Phone Frame vs Edge-to-Edge Desktop Toggle (Visible on lg screens) */}
          <button
            onClick={() => setIsPhoneFrame(!isPhoneFrame)}
            title={isPhoneFrame ? 'Expand to Desktop View' : 'Simulate Mobile Frame'}
            className="hidden md:flex p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition active:scale-95"
          >
            {isPhoneFrame ? <Monitor className="w-4 h-4" /> : <Smartphone className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
};
