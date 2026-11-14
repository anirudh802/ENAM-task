import React, { useState, useEffect } from 'react';
import { NetworkContact, WhoToCallResponse, SecondDegreePath } from '../../types';
import { api } from '../../services/api';
import { ActionButton } from '../common/ActionButton';
import {
  Star,
  Phone,
  Users,
  ArrowRight,
  Share2,
  GraduationCap,
  ArrowUpRight,
  X,
  Lock,
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Info,
  Building2
} from 'lucide-react';

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
  const [expandedScoreIds, setExpandedScoreIds] = useState<Record<string, boolean>>({});

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

  const toggleScoreBreakdown = (contactId: string) => {
    setExpandedScoreIds((prev) => ({ ...prev, [contactId]: !prev[contactId] }));
  };

  const getScoreBreakdown = (contact: NetworkContact) => {
    const isCxo =
      contact.current_title.toLowerCase().includes('partner') ||
      contact.current_title.toLowerCase().includes('director') ||
      contact.current_title.toLowerCase().includes('vp') ||
      contact.current_title.toLowerCase().includes('officer');
    const seniority = isCxo ? 2.5 : 1.5;
    const strength = Math.min(2.5, contact.relationship_strength * 2.0 * 0.25);
    const materiality = 2.0;
    const tenure = Math.min(
      2.5,
      Math.max(1.0, contact.relevance_score - (contact.is_starred ? 2.0 : 0.0) - seniority - strength - materiality)
    );
    const starredBoost = contact.is_starred ? 2.0 : 0.0;

    return {
      tenure: Math.round(tenure * 10) / 10,
      seniority,
      strength: Math.round(strength * 10) / 10,
      materiality,
      starredBoost,
      total: contact.relevance_score,
    };
  };

  const renderRelevanceMeter = (contact: NetworkContact) => {
    const isExpanded = expandedScoreIds[contact.id];
    const filledCount = Math.min(5, Math.max(1, Math.round(contact.relevance_score / 2.0)));
    const breakdown = getScoreBreakdown(contact);

    return (
      <div className="space-y-1.5 w-full sm:w-auto">
        <button
          onClick={() => toggleScoreBreakdown(contact.id)}
          className="min-h-[44px] flex items-center gap-2 hover:opacity-80 transition text-left group"
          title="Tap to see mathematical relevance score breakdown"
        >
          <span className="text-[10px] text-slate-400 font-medium font-mono uppercase tracking-wider">
            Relevance:
          </span>
          <div className="flex gap-0.5">
            {[1, 2, 3, 4, 5].map((seg) => (
              <span
                key={seg}
                className={`w-3.5 h-1.5 rounded-xs transition-colors ${
                  seg <= filledCount
                    ? 'bg-violet-600 dark:bg-violet-400'
                    : 'bg-slate-200 dark:bg-slate-700'
                }`}
              />
            ))}
          </div>
          <span className="font-mono font-num tabular-nums text-xs font-bold text-slate-800 dark:text-slate-200">
            {contact.relevance_score.toFixed(1)}/10
          </span>
          {isExpanded ? (
            <ChevronUp className="w-3 h-3 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200" />
          ) : (
            <ChevronDown className="w-3 h-3 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200" />
          )}
        </button>

        {/* Expandable Score Breakdown */}
        {isExpanded && (
          <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 text-[10px] font-mono animate-in fade-in-50 duration-150">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-1.5 pb-1 border-b border-slate-200 dark:border-slate-700">
              <span className="font-bold uppercase tracking-wider">Score Breakdown (N-03 Formula)</span>
              <span className="font-sans text-[9px] text-slate-400">Max: 10.0 pts</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div>
                <span className="text-slate-400 block font-sans">Tenure in Domain</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">{breakdown.tenure} / 2.5</span>
              </div>
              <div>
                <span className="text-slate-400 block font-sans">Seniority / CXO</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">{breakdown.seniority} / 2.5</span>
              </div>
              <div>
                <span className="text-slate-400 block font-sans">Relationship Edge</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">{breakdown.strength} / 2.5</span>
              </div>
              <div>
                <span className="text-slate-400 block font-sans">Event Materiality</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">{breakdown.materiality} / 2.5</span>
              </div>
            </div>
            {breakdown.starredBoost > 0 && (
              <div className="mt-1.5 pt-1 border-t border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between text-amber-700 dark:text-amber-300 font-semibold">
                <span>Pinned Institutional Priority Boost</span>
                <span>+{breakdown.starredBoost.toFixed(1)} pts</span>
              </div>
            )}
          </div>
        )}
      </div>
    );
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
      <div className="finance-card p-3.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-slate-100 flex items-center gap-1.5 font-mono">
              <Users className="w-3.5 h-3.5 text-violet-600 dark:text-violet-400 stroke-[1.75]" />
              Nexus Intelligence Layer
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Personal network activated with primary exchange disclosures
            </p>
          </div>

          <ActionButton
            variant="secondary"
            icon={Users}
            label="Who to Call?"
            onClick={() => fetchWhoToCall(selectedTicker)}
          />
        </div>

        {/* Ticker pills for quick who to call */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar pt-1">
          <span className="text-[10px] font-semibold text-slate-400 shrink-0 font-mono">Company Context:</span>
          {['DIXON.NS', 'TRENT.NS', 'TATAMOTORS.NS', 'KAYNES.NS', 'DEEPAKNTR.NS'].map((t) => (
            <button
              key={t}
              onClick={() => {
                setSelectedTicker(t);
                fetchWhoToCall(t);
              }}
              className={`h-6 px-2.5 rounded text-[10px] font-mono font-semibold transition flex items-center ${
                selectedTicker === t
                  ? 'bg-violet-600 text-white dark:bg-violet-600 dark:text-white border border-violet-500 shadow-xs'
                  : 'bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/80 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {t.replace('.NS', '')}
            </button>
          ))}
        </div>
      </div>

      {/* Prominent Synthetic Profile Disclosure Label (Report Items 7, 39, 150) */}
      <div className="px-3 py-2 rounded-lg bg-slate-100/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-[10px] text-slate-500 dark:text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-1.5 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-500"></span>
          SYNTHETIC PROFILES · Anonymized Institutional Mock Data (Designed around DPDP principles)
        </span>
        <span className="font-mono text-[9px] uppercase tracking-wider text-slate-400">
          Tenant: ENAM Holdings
        </span>
      </div>

      {/* 1. NOTICINGS FEED (Report Items 5, 37, 116–126) */}
      <div className="finance-card p-3.5 bg-gradient-to-br from-violet-50/50 via-white to-slate-50/50 dark:from-violet-950/20 dark:via-slate-900 dark:to-slate-900 border border-violet-200/60 dark:border-violet-900/40">
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-violet-600 dark:text-violet-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-slate-100 font-mono">
              Network Noticings Feed
            </h3>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-violet-100 text-violet-800 dark:bg-violet-950 dark:text-violet-300 border border-violet-200 dark:border-violet-800/40">
            4 Active Triggers
          </span>
        </div>

        <p className="text-[11px] text-slate-500 dark:text-slate-400 mb-3">
          Proactive network intelligence: warm reconnect triggers and second-degree bridges surfaced against primary market filings.
        </p>

        <div className="space-y-2.5">
          {/* Notice 1: Warm Reconnect (Pooja Singhania / Trent results) */}
          <div className="p-3 rounded-lg bg-white dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700/80 space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-mono flex items-center gap-1 border border-emerald-200 dark:border-emerald-800/40 shrink-0">
                <Clock className="w-3 h-3" /> Warm Reconnect Hook
              </span>
              <ActionButton
                variant="primary"
                icon={Phone}
                label="Reconnect"
                onClick={() => onCallContact && onCallContact('Pooja Singhania')}
              />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                Pooja Singhania — Chief Merchandising Officer, Nykaa Fashion
              </h4>
              <p className="text-[10px] font-mono text-slate-400 dark:text-slate-500 mt-0.5">
                Last Contact: 14 Aug 2026 (92d ago)
              </p>
              <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed mt-1">
                Ex-Head of Zudio Merchandising at Trent. Her former employer <strong>Trent Ltd</strong> disclosed Q2 results today (+39.1% YoY revenue growth, crossing 570 stores). Recommended hook: retail replenishment velocity and tier 2/3 apparel demand.
              </p>
            </div>
          </div>

          {/* Notice 2: Client Sourcing Intel (Rohan Deshmukh / Dixon) */}
          <div className="p-3 rounded-lg bg-white dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700/80 space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-mono flex items-center gap-1 border border-blue-200 dark:border-blue-800/40 shrink-0">
                <Users className="w-3 h-3" /> Key Client Channel Check
              </span>
              <ActionButton
                variant="primary"
                icon={Phone}
                label="Channel check"
                onClick={() => {
                  setSelectedTicker('DIXON.NS');
                  fetchWhoToCall('DIXON.NS');
                }}
              />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                Rohan Deshmukh — Director of Sourcing, Xiaomi India
              </h4>
              <p className="text-[10px] font-mono text-slate-400 dark:text-slate-500 mt-0.5">
                Last Contact: 12 Sep 2026 (63d ago)
              </p>
              <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed mt-1">
                Ex-Dixon operations manager (2018–21), now leading component sourcing at Xiaomi (Dixon's anchor smartphone OEM client). Best placed to cross-check general mobile component lead times and festive retail sell-through.
              </p>
            </div>
          </div>

          {/* Notice 3: Executive Transition Diligence (Vikram Seth / Kaynes via Ananya Roy) */}
          <div className="p-3 rounded-lg bg-white dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700/80 space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-50 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-mono flex items-center gap-1 border border-amber-200 dark:border-amber-800/40 shrink-0">
                <Share2 className="w-3 h-3" /> 2nd-Degree Executive Transition Bridge
              </span>
              <ActionButton
                variant="primary"
                icon={Share2}
                label="Intro path"
                onClick={() => fetchSecondDegree('Vikram Seth', 'Chief Operating Officer', 'Kaynes Technology India Ltd')}
              />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                Vikram Seth — Chief Operating Officer, Kaynes Technology
              </h4>
              <p className="text-[10px] font-mono text-slate-400 dark:text-slate-500 mt-0.5">
                Target: External Leadership
              </p>
              <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed mt-1">
                Newly appointed COO at Kaynes (former Senior VP Manufacturing at Dixon Technologies). 2nd-degree bridge identified via <strong>Ananya Roy</strong> (Ex-colleagues at Foxconn India, IIT Kanpur 2004 Batchmate).
              </p>
            </div>
          </div>

          {/* Notice 4: Feedstock Advisory (Dr. Arvind Swaminathan / Deepak Nitrite) */}
          <div className="p-3 rounded-lg bg-white dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700/80 space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 font-mono flex items-center gap-1 border border-indigo-200 dark:border-indigo-800/40 shrink-0">
                <Info className="w-3 h-3" /> Chemical Feedstock Cycle Advisory
              </span>
              <ActionButton
                variant="primary"
                icon={Phone}
                label="Consult"
                onClick={() => onCallContact && onCallContact('Dr. Arvind Swaminathan')}
              />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                Dr. Arvind Swaminathan — Specialty Chemicals Technical Advisor
              </h4>
              <p className="text-[10px] font-mono text-slate-400 dark:text-slate-500 mt-0.5">
                Last Contact: 04 Aug 2026 (102d ago)
              </p>
              <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed mt-1">
                Global phenol & acetone benchmark spreads expanded 140 bps this week. Dr. Swaminathan is your primary technical expert on industry-wide chemical feedstock cycles and benzene cost pass-through dynamics.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Theme Filter Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
        {themes.map((th) => (
          <button
            key={th}
            onClick={() => setSelectedTheme(th)}
            className={`min-h-[32px] px-3 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition border ${
              selectedTheme === th
                ? 'bg-violet-600 border-violet-600 text-white shadow-sm font-semibold'
                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60'
            }`}
          >
            {th === 'all' ? 'All Domains' : th}
          </button>
        ))}
      </div>

      {/* 2. DIRECTORY LOOKUP: Starred on top, then relevance ranked */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
            Contact Directory & Knowledge Map
          </span>
          <span className="text-[10px] font-mono text-slate-400">
            {filteredContacts.length} Contacts
          </span>
        </div>

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
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300 font-semibold font-mono">
                      Starred
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-600 dark:text-slate-400">
                  {contact.current_title} at{' '}
                  <span className="font-semibold text-slate-800 dark:text-slate-200">
                    {contact.current_company}
                  </span>
                </p>
                {contact.last_contacted_date && (
                  <p className="text-[10px] font-mono text-slate-400 mt-0.5 flex items-center gap-1">
                    <Clock className="w-2.5 h-2.5 text-slate-400" />
                    <span>Last contacted: {contact.last_contacted_date}</span>
                    {contact.name === 'Pooja Singhania' && (
                      <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                        (Warm Hook Ready)
                      </span>
                    )}
                  </p>
                )}
              </div>

              {/* Star Action */}
              <button
                onClick={() => handleToggleStar(contact.id)}
                title={contact.is_starred ? 'Unstar contact' : 'Star contact'}
                className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-md text-amber-400 hover:scale-110 transition"
              >
                <Star
                  className={`w-4 h-4 ${
                    contact.is_starred ? 'fill-amber-400 text-amber-500' : 'text-slate-300 dark:text-slate-600'
                  }`}
                />
              </button>
            </div>

            {/* 1-2 Line Summary of Recent Developments */}
            {contact.recent_development_summary && (
              <div className="bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 border-l-2 border-l-violet-500/80 p-2.5 rounded-md my-2 text-xs text-slate-800 dark:text-slate-200">
                <span className="font-semibold text-[10px] uppercase text-violet-700 dark:text-violet-400 block mb-0.5 font-mono">
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
                <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-mono">
                  Ex-{p.company}
                </span>
              ))}
              {contact.education.slice(0, 1).map((e, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-medium font-mono"
                >
                  <GraduationCap className="w-3 h-3 text-blue-500 dark:text-blue-400 stroke-[1.75]" />
                  <span>
                    {e.institution} '{e.year?.slice(-2)}
                  </span>
                </span>
              ))}
            </div>

            {/* External Bridge for Ananya Roy (De-duplicated Intro Path) */}
            {contact.name === 'Ananya Roy' && (
              <div className="mb-2 bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 border-l-2 border-l-blue-500 p-2 rounded-md text-xs">
                <div className="flex items-center justify-between gap-1.5">
                  <span className="font-bold text-slate-900 dark:text-slate-100 text-[11px] flex items-center gap-1 min-w-0 truncate">
                    <ArrowUpRight className="w-3.5 h-3.5 text-blue-500 dark:text-blue-400 stroke-[1.75] shrink-0" />
                    <span className="truncate">2nd-Degree Reach: Vikram Seth (COO, Kaynes Tech)</span>
                  </span>
                  <ActionButton
                    variant="ghost"
                    icon={Share2}
                    label="Intro path"
                    onClick={() => fetchSecondDegree('Vikram Seth', 'Chief Operating Officer', 'Kaynes Technology India Ltd')}
                  />
                </div>
                <p className="text-[10px] text-slate-600 dark:text-slate-400 mt-0.5">
                  Ex-colleagues at Foxconn India (Primary) & IIT Kanpur alumni bridge available.
                </p>
              </div>
            )}

            {/* Action Bar with 5-Segment Relevance Meter and Inline Action Buttons */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-xs gap-2">
              <div className="min-w-0 flex-1">
                {renderRelevanceMeter(contact)}
              </div>

              <div className="flex items-center gap-1.5 shrink-0 ml-auto">
                <ActionButton
                  variant="icon"
                  icon={Info}
                  label="Channel Intel"
                  title="Channel Intel"
                  aria-label="Channel Intel"
                  onClick={() => {
                    setSelectedTicker(contact.current_company_ticker || 'DIXON.NS');
                    fetchWhoToCall(contact.current_company_ticker || 'DIXON.NS');
                  }}
                />

                {contact.compliance_restricted ? (
                  <ActionButton
                    disabled
                    disabledReason={contact.compliance_reason || 'Restricted List: Active MNPI Embargo'}
                    label="Restricted"
                    aria-label={contact.compliance_reason || 'Restricted List: Active MNPI Embargo'}
                  />
                ) : (
                  <ActionButton
                    variant="primary"
                    icon={Phone}
                    label="Channel check"
                    onClick={() => onCallContact && onCallContact(contact.name)}
                  />
                )}
              </div>
            </div>

            {/* Compliance Reason Subtext if Restricted */}
            {contact.compliance_restricted && contact.compliance_reason && (
              <div className="mt-1 text-[10px] text-amber-700 dark:text-amber-400 font-mono flex items-center gap-1 justify-end">
                <AlertCircle className="w-3 h-3 text-amber-500" />
                <span>{contact.compliance_reason}</span>
              </div>
            )}
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
                <span className="text-xs text-blue-600 dark:text-blue-400 font-semibold font-mono">
                  {whoToCallData.ticker} • {whoToCallData.sector}
                </span>
              </div>
              <button
                onClick={() => setShowWhoToCallModal(false)}
                className="min-w-[44px] min-h-[44px] flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                aria-label="Close"
              >
                <X className="w-4 h-4 stroke-[1.75]" />
              </button>
            </div>

            {/* Direct Contacts */}
            <div>
              <h4 className="text-xs font-bold uppercase text-slate-400 mb-1.5 font-mono">
                Direct / Past Employees
              </h4>
              {whoToCallData.direct_contacts.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No direct former employees in your network.</p>
              ) : (
                whoToCallData.direct_contacts.map((dc) => (
                  <div
                    key={dc.id}
                    className="p-2.5 rounded-md bg-slate-50 dark:bg-slate-800/60 mb-1.5 text-xs border border-slate-200/50 dark:border-slate-700/50"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900 dark:text-white">{dc.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold font-mono border border-slate-200 dark:border-slate-700">
                        Synthetic
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 dark:text-slate-300">
                      {dc.name === 'Rohan Deshmukh'
                        ? 'Director of Sourcing, Xiaomi India (Key OEM Client) · Ex-Ops Manager, Dixon Tech (2018–21)'
                        : `${dc.current_title} (${dc.current_company})`}
                    </p>
                    <p className="text-[10px] text-slate-500 mt-0.5">{dc.recent_development_summary}</p>
                  </div>
                ))
              )}
            </div>

            {/* Supplier / Client Contacts */}
            <div>
              <h4 className="text-xs font-bold uppercase text-slate-400 mb-1.5 font-mono">
                Suppliers & Component Vendors
              </h4>
              {whoToCallData.supplier_contacts.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No component suppliers in network for this ticker.</p>
              ) : (
                whoToCallData.supplier_contacts.map((sc) => (
                  <div
                    key={sc.id}
                    className="p-2.5 rounded-md bg-slate-50 dark:bg-slate-800/60 mb-1.5 text-xs border border-slate-200/50 dark:border-slate-700/50"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900 dark:text-white">{sc.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300 font-semibold font-mono">
                        Vendor Intel
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 dark:text-slate-300">
                      {sc.current_title} ({sc.current_company})
                    </p>
                    <p className="text-[10px] text-slate-500 mt-0.5">{sc.notes}</p>
                  </div>
                ))
              )}
            </div>

            {/* Suggested Diligence Questions & SEBI PIT Caution */}
            <div className="bg-slate-50 dark:bg-slate-900/80 p-3 rounded-md border border-slate-200 dark:border-slate-800 border-l-2 border-l-amber-500 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                  Diligence Questions (Channel check):
                </h4>
                {whoToCallData.compliance_status === 'CLEAR' && (
                  <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200 font-mono">
                    SEBI PIT Compliant
                  </span>
                )}
              </div>
              <ul className="space-y-1 text-xs text-slate-700 dark:text-slate-300">
                {whoToCallData.suggested_questions.map((q, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-slate-400">•</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 italic pt-1 border-t border-slate-200 dark:border-slate-800">
                Notice: Inquiries must strictly focus on generalized sector trends and public value-chain turnaround. Do not seek confidential client or company forward guidance.
              </p>
            </div>

            <button
              onClick={() => setShowWhoToCallModal(false)}
              className="w-full min-h-[44px] py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 font-medium text-xs text-slate-900 dark:text-slate-100 rounded-md border border-slate-300 dark:border-slate-700 transition"
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
                className="min-w-[44px] min-h-[44px] flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                aria-label="Close"
              >
                <X className="w-4 h-4 stroke-[1.75]" />
              </button>
            </div>

            {/* Connection Visualizer */}
            <div className="flex items-center justify-between bg-slate-50 dark:bg-slate-800/60 p-3 rounded-lg text-center text-xs border border-slate-200/60 dark:border-slate-700/60">
              <div className="flex-1">
                <span className="block font-bold text-violet-600 dark:text-violet-400">You</span>
                <span className="text-[10px] text-slate-400 font-mono">Investor</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 stroke-[1.75]" />
              <div className="flex-1 px-1">
                <span className="block font-bold text-slate-900 dark:text-slate-100 truncate">
                  {secondDegreePath.connector_name}
                </span>
                <span className="text-[10px] text-slate-400 truncate block font-mono">1st Degree Contact</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 stroke-[1.75]" />
              <div className="flex-1">
                <span className="block font-bold text-slate-900 dark:text-white truncate">
                  {secondDegreePath.target_person}
                </span>
                <span className="text-[10px] text-slate-400 truncate block font-mono">Target Exec</span>
              </div>
            </div>

            {/* Link-Strength Meter (Item 9) */}
            <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-lg border border-slate-200/60 dark:border-slate-700/60">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Link-Strength Meter:
                </span>
                <span className="text-xs font-bold font-mono text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                  <span>{secondDegreePath.path_strength ?? 5}/5</span>
                  <span className="text-[10px] font-normal text-slate-500 dark:text-slate-400">
                    ({(secondDegreePath.path_strength ?? 5) >= 5 ? 'Highest Conviction' : 'Warm Conviction'})
                  </span>
                </span>
              </div>
              <div className="grid grid-cols-5 gap-1.5 h-2">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div
                    key={level}
                    className={`rounded-full h-full transition-all ${
                      level <= (secondDegreePath.path_strength ?? 5)
                        ? 'bg-emerald-500 dark:bg-emerald-400'
                        : 'bg-slate-200 dark:bg-slate-700'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Mutual Link Context - Leading with Strongest Tie (Foxconn) before Alumni */}
            <div className="text-xs bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-200/60 dark:border-slate-700/60 space-y-2">
              <span className="font-semibold text-slate-900 dark:text-white block text-xs">
                Relationship Bridges (Ranked by Tie Strength):
              </span>
              <div className="space-y-1.5 font-mono text-[11px]">
                {/* Tie 1: Primary Workplace Tie (Foxconn) */}
                <div className="p-2 rounded bg-emerald-50/80 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-emerald-800 dark:text-emerald-300">
                        1. Ex-colleagues at Foxconn India
                      </span>
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-emerald-200/70 text-emerald-900 dark:bg-emerald-900/60 dark:text-emerald-200">
                        Strength 5/5 · Primary
                      </span>
                    </div>
                    <span className="text-[10px] text-emerald-700/80 dark:text-emerald-400/80 block mt-0.5">
                      Direct operational workplace overlap in electronics manufacturing & supply chain.
                    </span>
                  </div>
                </div>
                {/* Tie 2: Secondary Alumni Tie (IIT Kanpur) */}
                <div className="p-2 rounded bg-slate-100/80 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-800 dark:text-slate-200">
                        2. IIT Kanpur 2004 Alumni
                      </span>
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300">
                        Strength 4/5 · Secondary
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 block mt-0.5">
                      Shared academic cohort and alumni directory connection.
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-xs bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-md border border-slate-200/60 dark:border-slate-700/60">
              <span className="font-semibold text-slate-900 dark:text-white block mb-0.5">
                Recommended Warm Ask:
              </span>
              <p className="text-slate-600 dark:text-slate-400">
                {secondDegreePath.recommended_intro_ask}
              </p>
            </div>

            <button
              onClick={() => setShowSecondDegreeModal(false)}
              className="w-full min-h-[40px] py-2 bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-100 font-medium text-xs rounded-md border border-slate-700 transition"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
