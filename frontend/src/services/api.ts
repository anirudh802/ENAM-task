import {
  Company,
  DigestResponse,
  Anomaly,
  UserPreferences,
  PullResearch,
  NetworkContact,
  WhoToCallResponse,
  SecondDegreePath,
} from '../types';

const API_BASE = window.location.port === '5173' ? 'http://127.0.0.1:8000/api' : '/api';

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  // Companies
  getCompanies: async (portfolioOnly = false): Promise<Company[]> => {
    const res = await fetch(`${API_BASE}/companies?portfolio_only=${portfolioOnly}`);
    return res.json();
  },

  // Push: Digest & Pinned Alert
  getDigest: async (hours = 24, category?: string): Promise<DigestResponse> => {
    let url = `${API_BASE}/push/digest?hours=${hours}`;
    if (category && category !== 'all') {
      url += `&category=${category}`;
    }
    const res = await fetch(url);
    return res.json();
  },

  getPinnedAlert: async (): Promise<Anomaly | null> => {
    const res = await fetch(`${API_BASE}/push/pinned-alert`);
    return res.json();
  },

  // Push: Ranked Alerts Stream
  getAlerts: async (): Promise<Anomaly[]> => {
    const res = await fetch(`${API_BASE}/push/alerts`);
    return res.json();
  },

  pinAlert: async (anomalyId: string, isPinned: boolean): Promise<any> => {
    const res = await fetch(`${API_BASE}/push/alerts/${anomalyId}/pin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_pinned: isPinned }),
    });
    return res.json();
  },

  dismissAlert: async (anomalyId: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/push/alerts/${anomalyId}/dismiss`, {
      method: 'POST',
    });
    return res.json();
  },

  // Preferences & Thresholds
  getPreferences: async (): Promise<UserPreferences> => {
    const res = await fetch(`${API_BASE}/preferences`);
    return res.json();
  },

  updatePreferences: async (
    volumeMultiplier: number,
    priceMovePct: number,
    autoNotify = true
  ): Promise<UserPreferences> => {
    const res = await fetch(`${API_BASE}/preferences`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        volume_multiplier: volumeMultiplier,
        price_move_pct: priceMovePct,
        auto_notify_critical: autoNotify,
      }),
    });
    return res.json();
  },

  // Web Push Notifications
  getVapidKey: async (): Promise<{ public_key: string }> => {
    const res = await fetch(`${API_BASE}/notifications/vapid-key`);
    return res.json();
  },

  subscribePush: async (subscription: PushSubscription): Promise<{ success: boolean }> => {
    const res = await fetch(`${API_BASE}/notifications/subscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription),
    });
    return res.json();
  },

  sendTestPush: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/notifications/test`, {
      method: 'POST',
    });
    return res.json();
  },

  // Pull Research
  getResearch: async (ticker: string): Promise<PullResearch> => {
    const res = await fetch(`${API_BASE}/pull/research/${ticker}`);
    return res.json();
  },

  // Nexus Network
  getNetworkFeed: async (): Promise<NetworkContact[]> => {
    const res = await fetch(`${API_BASE}/network/feed`);
    return res.json();
  },

  toggleStarContact: async (contactId: string): Promise<{ id: string; is_starred: boolean }> => {
    const res = await fetch(`${API_BASE}/network/contacts/${contactId}/star`, {
      method: 'POST',
    });
    return res.json();
  },

  getWhoToCall: async (ticker: string): Promise<WhoToCallResponse> => {
    const res = await fetch(`${API_BASE}/network/who-to-call/${ticker}`);
    return res.json();
  },

  getSecondDegreeReach: async (
    targetPerson: string,
    targetRole?: string,
    targetCompany?: string
  ): Promise<SecondDegreePath> => {
    const params = new URLSearchParams({
      target_person: targetPerson,
      target_role: targetRole || 'Executive',
      target_company: targetCompany || 'Company',
    });
    const res = await fetch(`${API_BASE}/network/second-degree?${params.toString()}`);
    return res.json();
  },

  // On-demand Pipeline runner
  runPipeline: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/pipeline/run`, {
      method: 'POST',
    });
    return res.json();
  },
};
