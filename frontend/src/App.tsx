import { useState, useEffect } from 'react';
import { Phone } from 'lucide-react';
import { Navbar } from './components/layout/Navbar';
import { BottomNav, TabType } from './components/layout/BottomNav';
import { PinnedAlertCard } from './components/pulse/PinnedAlertCard';
import { WindowedDigest } from './components/pulse/WindowedDigest';
import { RadarView } from './components/radar/RadarView';
import { DeepDiveView } from './components/deepdive/DeepDiveView';
import { NexusView } from './components/nexus/NexusView';
import { AskBar } from './components/ask/AskBar';
import { api } from './services/api';
import { DigestResponse, Anomaly, UserPreferences } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<TabType>('pulse');
  const [isPhoneFrame, setIsPhoneFrame] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Data states
  const [digest, setDigest] = useState<DigestResponse | null>(null);
  const [pinnedAlert, setPinnedAlert] = useState<Anomaly | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);

  // Filter states
  const [selectedHours, setSelectedHours] = useState(24);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [deepDiveTicker, setDeepDiveTicker] = useState('DIXON.NS');

  // Contact outreach simulation toast
  const [contactToast, setContactToast] = useState<string | null>(null);

  // Track dismissed alerts in session so closed critical cards stay closed
  const [dismissedAlertIds, setDismissedAlertIds] = useState<Set<string>>(() => {
    try {
      const saved = sessionStorage.getItem('finn_dismissed_alerts');
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch {
      return new Set();
    }
  });

  const loadInitialData = async () => {
    setIsRefreshing(true);
    try {
      const [digRes, pinnedRes, anomsRes, prefsRes] = await Promise.allSettled([
        api.getDigest(selectedHours, selectedCategory),
        api.getPinnedAlert(),
        api.getAlerts(),
        api.getPreferences(),
      ]);
      if (digRes.status === 'fulfilled') setDigest(digRes.value);
      if (pinnedRes.status === 'fulfilled') {
        const pinned = pinnedRes.value;
        if (pinned && !dismissedAlertIds.has(pinned.id)) {
          setPinnedAlert(pinned);
        } else {
          setPinnedAlert(null);
        }
      }
      if (anomsRes.status === 'fulfilled') setAnomalies(anomsRes.value);
      if (prefsRes.status === 'fulfilled') setPreferences(prefsRes.value);
    } catch (err) {
      console.error('Failed to load FINN data:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Initial mount load
  useEffect(() => {
    loadInitialData();
  }, []);

  // Changing the type of feed in the pulse bar (hours / category) only updates the digest feed!
  useEffect(() => {
    const updateDigestFeed = async () => {
      try {
        const dig = await api.getDigest(selectedHours, selectedCategory);
        setDigest(dig);
      } catch (err) {
        console.error('Failed to update digest feed:', err);
      }
    };
    updateDigestFeed();
  }, [selectedHours, selectedCategory]);

  const handleDismissPinned = async (id: string) => {
    try {
      await api.dismissAlert(id);
      setPinnedAlert(null);
      setDismissedAlertIds(prev => {
        const next = new Set(prev).add(id);
        try {
          sessionStorage.setItem('finn_dismissed_alerts', JSON.stringify(Array.from(next)));
        } catch {}
        return next;
      });
      setAnomalies(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      console.error('Failed to dismiss alert:', err);
    }
  };

  const handleTogglePin = async (id: string, isPinned: boolean) => {
    try {
      await api.pinAlert(id, isPinned);
      setAnomalies(prev =>
        prev
          .map(a => (a.id === id ? { ...a, is_pinned: isPinned } : a))
          .sort((a, b) => (b.is_pinned ? 1 : 0) - (a.is_pinned ? 1 : 0))
      );
      if (isPinned) {
        const found = anomalies.find(a => a.id === id);
        if (found) setPinnedAlert(found);
      } else if (pinnedAlert?.id === id) {
        setPinnedAlert(null);
      }
    } catch (err) {
      console.error('Failed to toggle pin:', err);
    }
  };

  const handleUpdatePreferences = async (volume: number, price: number) => {
    try {
      const updated = await api.updatePreferences(volume, price, true);
      setPreferences(updated);
      await api.runPipeline();
      await loadInitialData();
    } catch (err) {
      console.error('Failed to update preferences:', err);
    }
  };

  const handleInvestigateTicker = (ticker: string) => {
    setDeepDiveTicker(ticker);
    setActiveTab('deepdive');
  };

  const handleNavigateTab = (tab: TabType, ticker?: string) => {
    if (ticker) {
      setDeepDiveTicker(ticker);
    }
    setActiveTab(tab);
  };

  const handleSelectNetworkForTicker = (ticker: string) => {
    setDeepDiveTicker(ticker);
    setActiveTab('nexus');
  };

  const handleCallContact = (contactName: string) => {
    setContactToast(`Connecting with ${contactName}... Initiating secure dialer.`);
    setTimeout(() => setContactToast(null), 4000);
  };

  const criticalCount = anomalies.filter(a => a.severity === 'CRITICAL' && !a.is_dismissed).length;

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 flex flex-col items-center justify-start sm:p-4">
      {/* Container: Mobile Viewport or Desktop Phone Frame */}
      <div
        className={`w-full transition-all duration-300 flex flex-col bg-white dark:bg-[#0B0F19] ${
          isPhoneFrame
            ? 'max-w-[440px] sm:my-2 sm:rounded-[36px] sm:shadow-2xl sm:border-[8px] sm:border-slate-300 sm:dark:border-slate-800 sm:overflow-hidden min-h-[92vh]'
            : 'max-w-4xl min-h-screen'
        }`}
      >
        {/* Navigation Bar */}
        <Navbar
          isPhoneFrame={isPhoneFrame}
          setIsPhoneFrame={setIsPhoneFrame}
          onRefresh={loadInitialData}
          isRefreshing={isRefreshing}
        />

        {/* Contact Toast Banner */}
        {contactToast && (
          <div className="bg-emerald-600 text-white text-xs font-semibold py-2 px-4 text-center animate-fade-in shadow-md flex items-center justify-center gap-1.5">
            <Phone className="w-3.5 h-3.5 stroke-[1.75]" />
            <span>{contactToast}</span>
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 p-3.5 pb-40 overflow-y-auto">
          {activeTab === 'pulse' && (
            <div>
              {/* Pinned Dismissible Critical Alert Card */}
              <PinnedAlertCard
                alert={pinnedAlert}
                onDismiss={handleDismissPinned}
                onInvestigate={handleInvestigateTicker}
                onCallContact={handleCallContact}
              />

              {/* Windowed Digest */}
              <WindowedDigest
                digest={digest}
                selectedHours={selectedHours}
                setSelectedHours={setSelectedHours}
                selectedCategory={selectedCategory}
                setSelectedCategory={setSelectedCategory}
                onSelectTicker={handleInvestigateTicker}
                onCallContact={handleCallContact}
              />
            </div>
          )}

          {activeTab === 'radar' && (
            <RadarView
              anomalies={anomalies}
              preferences={preferences}
              onUpdatePreferences={handleUpdatePreferences}
              onTogglePin={handleTogglePin}
              onInvestigateTicker={handleInvestigateTicker}
            />
          )}

          {activeTab === 'deepdive' && (
            <DeepDiveView
              initialTicker={deepDiveTicker}
              onSelectNetworkForTicker={handleSelectNetworkForTicker}
            />
          )}

          {activeTab === 'nexus' && (
            <NexusView
              initialTicker={deepDiveTicker}
              onCallContact={handleCallContact}
            />
          )}
        </main>

        {/* Omnipresent Ask Intelligence Bar */}
        <AskBar
          onNavigateTab={handleNavigateTab}
          onCallContact={handleCallContact}
        />

        {/* Fixed Bottom Navigation Bar */}
        <BottomNav
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          unreadAlertCount={criticalCount}
        />
      </div>
    </div>
  );
}

export default App;
