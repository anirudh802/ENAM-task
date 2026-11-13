import { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { BottomNav, TabType } from './components/layout/BottomNav';
import { PinnedAlertCard } from './components/pulse/PinnedAlertCard';
import { WindowedDigest } from './components/pulse/WindowedDigest';
import { RadarView } from './components/radar/RadarView';
import { DeepDiveView } from './components/deepdive/DeepDiveView';
import { NexusView } from './components/nexus/NexusView';
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

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const [dig, pinned, anoms, prefs] = await Promise.all([
        api.getDigest(selectedHours, selectedCategory),
        api.getPinnedAlert(),
        api.getAlerts(),
        api.getPreferences(),
      ]);
      setDigest(dig);
      setPinnedAlert(pinned);
      setAnomalies(anoms);
      setPreferences(prefs);
    } catch (err) {
      console.error('Failed to load FINN data:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedHours, selectedCategory]);

  const handleDismissPinned = async (id: string) => {
    try {
      await api.dismissAlert(id);
      setPinnedAlert(null);
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
      await loadData();
    } catch (err) {
      console.error('Failed to update preferences:', err);
    }
  };

  const handleInvestigateTicker = (ticker: string) => {
    setDeepDiveTicker(ticker);
    setActiveTab('deepdive');
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
          onRefresh={loadData}
          isRefreshing={isRefreshing}
        />

        {/* Contact Toast Banner */}
        {contactToast && (
          <div className="bg-emerald-600 text-white text-xs font-semibold py-2 px-4 text-center animate-fade-in shadow-md">
            📞 {contactToast}
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 p-3.5 pb-24 overflow-y-auto">
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
