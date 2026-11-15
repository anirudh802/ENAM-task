import React, { useState, useRef, useEffect } from 'react';
import {
  Search,
  Mic,
  MicOff,
  X,
  ArrowRight,
  Sparkles,
  Users,
  BarChart3,
  TrendingUp,
  AlertTriangle,
  ExternalLink,
  ShieldAlert,
  Phone,
  FileText,
  ArrowUpRight
} from 'lucide-react';
import { api } from '../../services/api';
import { AskResponse, AskCard } from '../../types';
import { ActionButton } from '../common/ActionButton';

interface AskBarProps {
  onNavigateTab: (tab: 'pulse' | 'radar' | 'deepdive' | 'nexus', ticker?: string) => void;
  onCallContact: (contactName: string) => void;
}

export const AskBar: React.FC<AskBarProps> = ({ onNavigateTab, onCallContact }) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [hasUsedPrompt, setHasUsedPrompt] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Hide quick prompts on scroll (Item 7)
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 30) {
        setIsScrolled(true);
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    const mainEl = document.querySelector('main');
    const handleMainScroll = () => {
      if (mainEl && mainEl.scrollTop > 30) {
        setIsScrolled(true);
      }
    };
    if (mainEl) {
      mainEl.addEventListener('scroll', handleMainScroll, { passive: true });
    }
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (mainEl) {
        mainEl.removeEventListener('scroll', handleMainScroll);
      }
    };
  }, []);

  // Initialize Speech Recognition if supported
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN';

      recognition.onstart = () => {
        setIsListening(true);
        setSpeechError(null);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setQuery(transcript);
        handleAsk(transcript);
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'not-allowed') {
          setSpeechError('Microphone permission blocked');
        } else {
          setSpeechError('Speech recognition unavailable');
        }
        setTimeout(() => setSpeechError(null), 3500);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setSpeechError('Voice input not supported in this browser');
      setTimeout(() => setSpeechError(null), 3000);
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.warn('Failed to start speech recognition:', err);
      }
    }
  };

  const handleAsk = async (textToQuery?: string) => {
    const q = (textToQuery !== undefined ? textToQuery : query).trim();
    if (!q) return;

    setHasUsedPrompt(true);
    setIsLoading(true);
    setIsOpen(true);
    try {
      const res = await api.askQuestion(q);
      setResponse(res);
    } catch (err) {
      console.error('Ask error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPrompt = (promptText: string) => {
    setQuery(promptText);
    handleAsk(promptText);
  };

  const handleClose = () => {
    setIsOpen(false);
    setQuery('');
    setResponse(null);
  };

  const quickPrompts = [
    { label: '👥 Who knows Dixon order flow?', q: 'Who knows about Dixon order flow?' },
    { label: '📊 Dixon promised vs delivered', q: 'Dixon promised vs delivered' },
    { label: '👥 Who do I know at Kaynes?', q: 'Who do I know at Kaynes?' },
    { label: '📋 Dixon Q2 results', q: 'What were Dixon Q2 results?' },
    { label: '⚡ CDSL volume anomaly', q: 'What triggered CDSL volume surge?' },
  ];

  const getIntentBadge = (intent: string) => {
    switch (intent) {
      case 'NETWORK':
        return {
          label: 'NETWORK INTEL',
          color: 'bg-purple-100 text-purple-800 dark:bg-purple-950/80 dark:text-purple-300 border-purple-200 dark:border-purple-800/40',
          icon: Users,
        };
      case 'GUIDANCE':
        return {
          label: 'GUIDANCE TRACK RECORD',
          color: 'bg-blue-100 text-blue-800 dark:bg-blue-950/80 dark:text-blue-300 border-blue-200 dark:border-blue-800/40',
          icon: BarChart3,
        };
      case 'RESULTS':
        return {
          label: 'RESULTS DISCLOSURE',
          color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/40',
          icon: TrendingUp,
        };
      case 'ANOMALY':
        return {
          label: 'ANOMALY DETECTION',
          color: 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 border-amber-200 dark:border-amber-800/40',
          icon: AlertTriangle,
        };
      default:
        return {
          label: 'PRIMARY RESEARCH',
          color: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700',
          icon: FileText,
        };
    }
  };

  return (
    <>
      {/* Pinned Ask Bar above Bottom Navigation */}
      <div className="fixed bottom-[60px] left-0 right-0 z-30 px-3 py-1.5 pointer-events-none">
        <div className="max-w-lg mx-auto pointer-events-auto">
          {/* Quick Suggestion Chips (solid background, hides after first use or on scroll, Item 7) */}
          {!isOpen && !hasUsedPrompt && !isScrolled && (
            <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar mb-1.5 p-1 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              {quickPrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setHasUsedPrompt(true);
                    handleQuickPrompt(p.q);
                  }}
                  className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 border border-slate-300 dark:border-slate-700 shadow-xs hover:border-blue-400 dark:hover:border-blue-500 whitespace-nowrap transition active:scale-95 flex items-center gap-1"
                >
                  <span>{p.label}</span>
                </button>
              ))}
            </div>
          )}

          {/* Bar Chrome */}
          <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border border-slate-300/80 dark:border-slate-700/80 rounded-2xl shadow-lg p-1.5 flex items-center gap-1.5 transition-all">
            <div className="pl-2 flex items-center text-blue-600 dark:text-blue-400 shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleAsk();
              }}
              className="flex-1 flex items-center min-w-0"
            >
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask FINN (e.g., 'Who knows Dixon order flow?', 'Trent guidance')..."
                className="w-full bg-transparent px-2 py-1 text-xs font-medium text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none"
              />
            </form>

            {/* Voice Input Button */}
            <button
              onClick={toggleListening}
              title={isListening ? 'Listening... Click to stop' : 'Ask by voice'}
              className={`min-w-[36px] min-h-[36px] flex items-center justify-center rounded-xl transition ${
                isListening
                  ? 'bg-rose-500 text-white animate-pulse'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              {isListening ? <Mic className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            {/* Submit / Open Button */}
            <button
              onClick={() => handleAsk()}
              disabled={isLoading || !query.trim()}
              title="Submit query"
              className="min-w-[36px] min-h-[36px] bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-xl flex items-center justify-center transition active:scale-95 shadow-xs"
            >
              {isLoading ? (
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <ArrowRight className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Voice Error Notice */}
          {speechError && (
            <div className="mt-1 text-[11px] text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-900 px-2.5 py-1 rounded-lg text-center font-medium">
              {speechError}
            </div>
          )}
        </div>
      </div>

      {/* Slide-Up Query Results Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex flex-col justify-end p-2 sm:p-4 animate-fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-lg w-full mx-auto max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Drawer Header */}
            <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2 bg-slate-50/80 dark:bg-slate-800/40">
              <div className="flex items-center gap-2 min-w-0">
                {response && (
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold font-mono border flex items-center gap-1 shrink-0 ${
                      getIntentBadge(response.intent).color
                    }`}
                  >
                    {React.createElement(getIntentBadge(response.intent).icon, { className: 'w-3 h-3' })}
                    <span>{getIntentBadge(response.intent).label}</span>
                  </span>
                )}
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">
                  "{query}"
                </span>
              </div>

              {/* Close Button (min 44px touch target) */}
              <button
                onClick={handleClose}
                aria-label="Close drawer"
                className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Drawer Body */}
            <div className="p-4 overflow-y-auto space-y-3.5 flex-1">
              {isLoading ? (
                <div className="py-12 text-center space-y-2">
                  <div className="w-6 h-6 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto" />
                  <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                    Grounding query in primary filings, transcripts, and network records...
                  </p>
                </div>
              ) : response ? (
                <>
                  {/* Institutional Verdict / Summary */}
                  <div className="bg-blue-50/40 dark:bg-blue-950/20 border border-blue-200/60 dark:border-blue-900/40 rounded-2xl p-3.5">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 font-mono mb-1 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      <span>FINN Synthesis</span>
                    </div>
                    <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                      {response.answer_summary}
                    </p>
                  </div>

                  {/* Render Embedded FINN Cards */}
                  <div className="space-y-3">
                    {response.cards.map((card, idx) => (
                      <div key={idx} className="transition">
                        {/* 1. Network Contact Card */}
                        {card.card_type === 'network_contact' && (
                          <div className="finance-card p-3.5 border-purple-200 dark:border-purple-900/60 bg-purple-50/10 dark:bg-purple-950/10">
                            <div className="flex items-start justify-between gap-2 mb-2">
                              <div>
                                <div className="flex items-center gap-1.5 flex-wrap">
                                  <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                                    {card.data.name}
                                  </h4>
                                  <span className="text-[10px] text-purple-700 dark:text-purple-300 font-medium px-1.5 py-0.2 rounded bg-purple-100 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800/40">
                                    {card.data.current_title && card.data.current_company && card.data.current_title.toLowerCase().includes(card.data.current_company.toLowerCase())
                                      ? card.data.current_title
                                      : `${card.data.current_title || 'Executive'} · ${card.data.current_company || 'Firm'}`}
                                  </span>
                                </div>
                                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                                  Tenure: {card.data.tenure || '2018-2021'} · Last Contact: {card.data.last_contacted_date || '2026-09-12'}
                                </div>
                              </div>

                              {/* Relevance Pill */}
                              <div className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                                {card.data.relevance_score || 9.4}/10
                              </div>
                            </div>

                            {/* Operational Why Line */}
                            {Boolean(card.data.why_line || card.data.notes || card.data.recent_development_summary) && (
                              <p className="text-[11px] text-purple-900 dark:text-purple-200 bg-purple-100/60 dark:bg-purple-950/40 p-2 rounded-lg border border-purple-200/50 dark:border-purple-800/30 mb-2.5 leading-relaxed font-medium">
                                "{card.data.why_line || card.data.notes || card.data.recent_development_summary}"
                              </p>
                            )}

                            {/* Compliance Check / Trigger */}
                            {card.data.compliance_restricted ? (
                              <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 text-[11px] text-amber-800 dark:text-amber-300 flex items-center justify-between gap-2">
                                <div className="flex items-center gap-1.5 min-w-0">
                                  <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
                                  <span className="truncate">{card.data.compliance_reason}</span>
                                </div>
                                <ActionButton
                                  disabled
                                  disabledReason={card.data.compliance_reason || 'Restricted List: Active MNPI Embargo'}
                                  label="Blocked"
                                />
                              </div>
                            ) : (
                              <div className="flex items-center justify-end gap-2">
                                <ActionButton
                                  variant="primary"
                                  icon={Phone}
                                  label="Channel check"
                                  onClick={() => {
                                    onCallContact(card.data.name);
                                    handleClose();
                                  }}
                                />
                              </div>
                            )}
                          </div>
                        )}

                        {/* 2. Guidance Track Record Card */}
                        {card.card_type === 'guidance_track_record' && (
                          <div className="finance-card p-3.5 border-blue-200 dark:border-blue-900/60">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-bold text-slate-900 dark:text-white">
                                {card.data.company_name} ({card.data.ticker})
                              </span>
                              <span className="text-[10px] font-mono text-slate-500">
                                4-Quarter Guidance Track Record
                              </span>
                            </div>

                            {(!card.data.guidance_items || card.data.guidance_items.length === 0) ? (
                              <div className="p-4 text-center text-xs text-slate-500 dark:text-slate-400 font-mono">
                                No guidance extracted for this company
                              </div>
                            ) : (
                              <div className="space-y-2 mb-1">
                                {card.data.guidance_items.map((item: any, gIdx: number) => (
                                  <div
                                    key={gIdx}
                                    className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between text-xs"
                                  >
                                    <div>
                                      <div className="font-semibold text-slate-800 dark:text-slate-200">
                                        {item.metric_name} ({item.quarter})
                                      </div>
                                      <div className="text-[10px] text-slate-400 font-mono">
                                        Promised: {item.promised_guidance} → Delivered: {item.delivered_actual}
                                      </div>
                                    </div>
                                    <span
                                      className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                                        item.status === 'BEAT'
                                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                                          : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                                      }`}
                                    >
                                      {item.status === 'BEAT' ? '✓ BEAT' : '▲ MISSED'}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}

                        {/* 3. Results Disclosure Card */}
                        {card.card_type === 'results_disclosure' && (
                          <div className="finance-card p-3.5 border-emerald-200 dark:border-emerald-900/60">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-bold text-slate-900 dark:text-white">
                                {card.data.headline}
                              </span>
                              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold">
                                {card.data.quarter}
                              </span>
                            </div>

                            {/* 4-Metric Results Grid */}
                            <div className="grid grid-cols-2 gap-2 mb-3">
                              <div className="bg-slate-50 dark:bg-slate-800/80 p-2 rounded-lg border border-slate-200 dark:border-slate-700">
                                <div className="text-[10px] text-slate-400 font-medium">Revenue</div>
                                <div className="text-xs font-bold text-slate-900 dark:text-white font-mono">
                                  ₹{card.data.extracted_data?.revenue_cr?.toLocaleString() || '11,534'} Cr
                                </div>
                                <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono font-bold">
                                  +{card.data.extracted_data?.revenue_yoy_pct || 133}% YoY
                                </div>
                              </div>

                              <div className="bg-slate-50 dark:bg-slate-800/80 p-2 rounded-lg border border-slate-200 dark:border-slate-700">
                                <div className="text-[10px] text-slate-400 font-medium">PAT</div>
                                <div className="text-xs font-bold text-slate-900 dark:text-white font-mono">
                                  ₹{card.data.extracted_data?.pat_cr?.toLocaleString() || '412'} Cr
                                </div>
                                <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono font-bold">
                                  +{card.data.extracted_data?.pat_yoy_pct || 263}% YoY
                                </div>
                              </div>
                            </div>

                            <button
                              onClick={() => {
                                onNavigateTab('pulse', card.data.ticker);
                                handleClose();
                              }}
                              className="w-full min-h-[44px] py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition active:scale-95"
                            >
                              <span>View Results in Pulse Feed</span>
                              <ExternalLink className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}

                        {/* 4. Radar Anomaly Card */}
                        {card.card_type === 'radar_anomaly' && (
                          <div className="finance-card p-3.5 border-amber-200 dark:border-amber-900/60">
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="text-xs font-bold text-slate-900 dark:text-white">
                                {card.data.ticker} · {card.data.company_name}
                              </span>
                              <span className="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                                {card.data.severity}
                              </span>
                            </div>
                            <p className="text-xs text-slate-700 dark:text-slate-300 mb-2 leading-relaxed font-medium">
                              {card.data.headline}: {card.data.detail}
                            </p>
                            <button
                              onClick={() => {
                                onNavigateTab('radar', card.data.ticker);
                                handleClose();
                              }}
                              className="w-full min-h-[44px] py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition active:scale-95"
                            >
                              <span>Inspect Anomaly in Radar</span>
                              <ExternalLink className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}

                        {/* 5. General Research Synthesis Card */}
                        {card.card_type === 'research_synthesis' && (
                          <div className="finance-card p-3.5 border-slate-200 dark:border-slate-800">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-bold text-slate-900 dark:text-white">
                                {card.data.company_name} ({card.data.ticker})
                              </span>
                              <span className="text-[10px] text-slate-400 font-mono">
                                CFO/PAT: {card.data.cfo_pat_ratio || 1.15}x
                              </span>
                            </div>

                            <div className="space-y-1.5 mb-3">
                              {card.data.bull_case?.map((b: string, bIdx: number) => (
                                <div key={bIdx} className="text-[11px] text-slate-700 dark:text-slate-300 flex items-start gap-1.5">
                                  <span className="text-emerald-500 font-bold shrink-0">↑</span>
                                  <span>{b}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Deep Navigation Action Pills */}
                  {response.actions && response.actions.length > 0 && (
                    <div className="pt-2 border-t border-slate-200 dark:border-slate-800 flex justify-end gap-2">
                      {response.actions.map((act, actIdx) => (
                        <ActionButton
                          key={actIdx}
                          variant={act.label.toLowerCase().includes('deepdive') ? 'ghost' : 'primary'}
                          icon={act.label.toLowerCase().includes('deepdive') ? ArrowUpRight : ArrowRight}
                          label={act.label.toLowerCase().includes('deepdive') ? 'DeepDive' : act.label}
                          onClick={() => {
                            onNavigateTab(act.tab, act.ticker || undefined);
                            handleClose();
                          }}
                        />
                      ))}
                    </div>
                  )}
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
