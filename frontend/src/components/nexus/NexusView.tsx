import React, { useState, useEffect } from 'react';
import { NetworkContact, WhoToCallResponse, SecondDegreePath } from '../../types';
import { api } from '../../services/api';
import { Star, Phone, Users, Sparkles, ArrowRight, Share2 } from 'lucide-react';

interface NexusViewProps {
  initialTicker?: string;
  onCallContact?: (contactName: string) => void;
}

export const NexusView: React.FC<NexusViewProps> = ({
  initialTicker,
  onCallContact,
}) => {
  const [contacts, setContacts] = useState<NetworkContact[]>([]);
  const [selectedTicker, setSelectedTicker] = useState(initialTicker || 'DIXON.NS');
  const [whoToCallData, setWhoToCallData] = useState<WhoToCallResponse | null>(null);
  const [secondDegreePath, setSecondDegreePath] = useState<SecondDegreePath | null>(null);
  const [showWhoToCallModal, setShowWhoToCallModal] = useState(false);
  const [showSecondDegreeModal, setShowSecondDegreeModal] = useState(false);
  const [selectedTheme, setSelectedTheme] = useState<string>('all');

  const fetchNetwork = async () => {
    try {
      const data = await api.getNetworkFeed();
      setContacts(data);
    } catch (err) {
      console.error('Failed to load network feed:', err);
    }
  };

  const fetchWhoToCall = async (ticker: string) => {
    try {
      const res = await api.getWhoToCall(ticker);
      setWhoToCallData(res);
      setShowWhoToCallModal(true);
    } catch (err) {
      console.error('Failed to fetch who to call:', err);
    }
  };

  const fetchSecondDegree = async (name: string, role: string, company: string) => {
    try {
      const res = await api.getSecondDegreeReach(name, role, company);
      setSecondDegreePath(res);
      setShowSecondDegreeModal(true);
    } catch (err) {
      console.error('Failed to fetch 2nd degree path:', err);
    }
  };

  useEffect(() => {
    fetchNetwork();
    if (initialTicker) {
      setSelectedTicker(initialTicker);
    }
  }, [initialTicker]);

  const handleToggleStar = async (contactId: string) => {
    try {
      const res = await api.toggleStarContact(contactId);
      setContacts((prev) =>
        prev
          .map((c) => (c.id === contactId ? { ...c, is_starred: res.is_starred } : c))
          .sort((a, b) => {
            if (a.is_starred === b.is_starred) {
              return b.relevance_score - a.relevance_score;
            }
            return a.is_starred ? -1 : 1;
          })
      );
    } catch (err) {
      console.error('Failed to toggle star:', err);
    }
  };

  const themes = [
    'all',
    'Electronics EMS',
    'Specialty Chemicals',
    'Retail',
    'Automotive',
    'Fintech',
  ];

  const filteredContacts = contacts.filter((c) => {
    if (selectedTheme === 'all') return true;
    return c.themes.includes(selectedTheme);
  });

  return (
    <div className="space-y-3 pb-8">
      {/* Network Header with Who To Call Trigger */}
      <div className="finance-card p-3.5 bg-gradient-to-r from-purple-50/70 via-white to-blue-50/70 dark:from-purple-950/20 dark:via-slate-900 dark:to-blue-950/20">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-purple-900 dark:text-purple-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
              Nexus Intelligence Layer
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Personal network activated with primary market disclosures
            </p>
          </div>

          <button
            onClick={() => fetchWhoToCall(selectedTicker)}
            className="px-2.5 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold flex items-center gap-1 transition shadow-sm"
          >
            <Users className="w-3.5 h-3.5" />
            <span>Who to Call?</span>
          </button>
        </div>

        {/* Ticker pills for quick who to call */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pt-1">
          <span className="text-[10px] font-semibold text-slate-400 shrink-0">Company Context:</span>
          {['DIXON.NS', 'TRENT.NS', 'TATAMOTORS.NS', 'KAYNES.NS', 'DEEPAKNTR.NS'].map((t) => (
            <button
              key={t}
              onClick={() => {
                setSelectedTicker(t);
                fetchWhoToCall(t);
              }}
              className={`px-2 py-0.5 rounded text-[10px] font-semibold transition ${
                selectedTicker === t
                  ? 'bg-purple-600 text-white'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
              }`}
            >
              {t.replace('.NS', '')}
            </button>
          ))}
        </div>
      </div>

      {/* Theme Filter Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
        {themes.map((th) => (
          <button
            key={th}
            onClick={() => setSelectedTheme(th)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition border ${
              selectedTheme === th
                ? 'bg-purple-600 border-purple-600 text-white'
                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50'
            }`}
          >
            {th === 'all' ? 'All Domains' : th}
          </button>
        ))}
      </div>

      {/* Contacts List: Starred on top, then relevance ranked */}
      <div className="space-y-2.5">
        {filteredContacts.map((contact) => (
          <div
            key={contact.id}
            className={`finance-card p-3.5 transition relative ${
              contact.is_starred
                ? 'border-amber-300 dark:border-amber-500/40 bg-amber-50/20 dark:bg-amber-950/10'
                : ''
            }`}
          >
            {/* Header */}
            <div className="flex items-start justify-between gap-2 mb-1">
              <div>
                <div className="flex items-center gap-1.5">
                  <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                    {contact.name}
                  </h4>
                  {contact.is_starred && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300 font-semibold">
                      Starred
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-600 dark:text-slate-400">
                  {contact.current_title} at <span className="font-semibold text-slate-800 dark:text-slate-200">{contact.current_company}</span>
                </p>
              </div>

              {/* Star Action */}
              <button
                onClick={() => handleToggleStar(contact.id)}
                title={contact.is_starred ? 'Unstar contact' : 'Star contact'}
                className="p-1 rounded-md text-amber-400 hover:scale-110 transition"
              >
                <Star
                  className={`w-4 h-4 ${
                    contact.is_starred ? 'fill-amber-400 text-amber-500' : 'text-slate-300 dark:text-slate-600'
                  }`}
                />
              </button>
            </div>

            {/* 1-2 Line Summary of Recent Developments (User Specification) */}
            {contact.recent_development_summary && (
              <div className="bg-purple-50/60 dark:bg-purple-950/20 border border-purple-100 dark:border-purple-900/30 p-2 rounded-lg my-2 text-xs text-purple-950 dark:text-purple-200">
                <span className="font-semibold text-[10px] uppercase text-purple-600 dark:text-purple-400 block mb-0.5">
                  Recent Development Context:
                </span>
                <p className="text-[11px] leading-relaxed">
                  {contact.recent_development_summary}
                </p>
              </div>
            )}

            {/* Past Employers & Education Tags */}
            <div className="flex flex-wrap items-center gap-1.5 text-[10px] text-slate-500 dark:text-slate-400 mb-2.5">
              {contact.past_companies.slice(0, 2).map((p, idx) => (
                <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800">
                  Ex-{p.company}
                </span>
              ))}
              {contact.education.slice(0, 1).map((e, idx) => (
                <span key={idx} className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-medium">
                  🎓 {e.institution} '{e.year?.slice(-2)}
                </span>
              ))}
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-1.5 border-t border-slate-100 dark:border-slate-800 text-xs">
              <span className="text-[10px] text-slate-400 font-medium">
                Relevance: {contact.relevance_score.toFixed(1)} / 10
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    if (onCallContact) onCallContact(contact.name);
                    fetchSecondDegree(contact.name, contact.current_title, contact.current_company);
                  }}
                  className="px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-[11px] font-semibold flex items-center gap-1 transition"
                >
                  <Share2 className="w-3 h-3" />
                  <span>2nd Degree Reach</span>
                </button>

                <button
                  onClick={() => onCallContact && onCallContact(contact.name)}
                  className="px-2.5 py-1 rounded bg-purple-600 hover:bg-purple-700 text-white text-[11px] font-semibold flex items-center gap-1 transition active:scale-95 shadow-sm"
                >
                  <Phone className="w-3 h-3" />
                  <span>Reach Out</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* "Who Should I Call?" Modal */}
      {showWhoToCallModal && whoToCallData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-4 shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  Outreach Intel: {whoToCallData.company_name}
                </h3>
                <span className="text-xs text-blue-600 dark:text-blue-400 font-semibold">
                  {whoToCallData.ticker} • {whoToCallData.sector}
                </span>
              </div>
              <button
                onClick={() => setShowWhoToCallModal(false)}
                className="text-slate-400 hover:text-slate-700 p-1"
              >
                ✕
              </button>
            </div>

            {/* Direct Contacts */}
            <div>
              <h4 className="text-xs font-bold uppercase text-slate-400 mb-1.5">
                Direct / Past Employees
              </h4>
              {whoToCallData.direct_contacts.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No direct former employees in your network.</p>
              ) : (
                whoToCallData.direct_contacts.map((dc) => (
                  <div key={dc.id} className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/60 mb-1.5 text-xs">
                    <span className="font-bold text-slate-900 dark:text-white">{dc.name}</span> — {dc.current_title}
                    <p className="text-[11px] text-slate-500">{dc.recent_development_summary}</p>
                  </div>
                ))
              )}
            </div>

            {/* Supplier / Client Contacts */}
            <div>
              <h4 className="text-xs font-bold uppercase text-slate-400 mb-1.5">
                Suppliers & Component Vendors
              </h4>
              {whoToCallData.supplier_contacts.map((sc) => (
                <div key={sc.id} className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/60 mb-1.5 text-xs">
                  <span className="font-bold text-slate-900 dark:text-white">{sc.name}</span> — {sc.current_title} ({sc.current_company})
                  <p className="text-[11px] text-slate-500">{sc.notes}</p>
                </div>
              ))}
            </div>

            {/* Suggested Diligence Questions */}
            <div className="bg-purple-50 dark:bg-purple-950/30 p-3 rounded-xl border border-purple-200 dark:border-purple-800">
              <h4 className="text-xs font-bold text-purple-950 dark:text-purple-200 mb-1.5">
                Questions to Ask:
              </h4>
              <ul className="space-y-1 text-xs text-purple-900 dark:text-purple-300">
                {whoToCallData.suggested_questions.map((q, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span>•</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => setShowWhoToCallModal(false)}
              className="w-full py-2 bg-slate-200 dark:bg-slate-800 font-semibold text-xs rounded-xl"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* 2nd-Degree Path Modal */}
      {showSecondDegreeModal && secondDegreePath && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-md w-full p-4 shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                2nd-Degree Reach Path
              </h3>
              <button
                onClick={() => setShowSecondDegreeModal(false)}
                className="text-slate-400 hover:text-slate-700 p-1"
              >
                ✕
              </button>
            </div>

            {/* Connection Visualizer */}
            <div className="flex items-center justify-between bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl text-center text-xs">
              <div className="flex-1">
                <span className="block font-bold text-blue-600 dark:text-blue-400">You</span>
                <span className="text-[10px] text-slate-400">Investor</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400" />
              <div className="flex-1 px-1">
                <span className="block font-bold text-purple-600 dark:text-purple-400 truncate">
                  {secondDegreePath.connector_name}
                </span>
                <span className="text-[10px] text-slate-400 truncate block">1st Degree Contact</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400" />
              <div className="flex-1">
                <span className="block font-bold text-slate-900 dark:text-white truncate">
                  {secondDegreePath.target_person}
                </span>
                <span className="text-[10px] text-slate-400 truncate block">Target Exec</span>
              </div>
            </div>

            <div className="text-xs bg-blue-50/60 dark:bg-blue-950/20 p-2.5 rounded-xl border border-blue-100 dark:border-blue-900/40">
              <span className="font-semibold text-blue-900 dark:text-blue-300 block mb-0.5">
                Mutual Link Context:
              </span>
              <p className="text-slate-700 dark:text-slate-300">
                {secondDegreePath.connector_relationship}
              </p>
            </div>

            <div className="text-xs bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-xl border border-slate-200/60 dark:border-slate-700/60">
              <span className="font-semibold text-slate-900 dark:text-white block mb-0.5">
                Recommended Warm Ask:
              </span>
              <p className="text-slate-600 dark:text-slate-400">
                {secondDegreePath.recommended_intro_ask}
              </p>
            </div>

            <button
              onClick={() => setShowSecondDegreeModal(false)}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
