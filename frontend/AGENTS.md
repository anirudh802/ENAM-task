# Frontend AGENTS.md — FINN Mobile-First PWA

## Role & Responsibilities
The `frontend/` directory houses the Progressive Web Application built with React 18, Vite, and Tailwind CSS. It delivers:
1. **Pulse View:** Windowed digest bar (24h/7d/30d), top pinned dismissible critical alert banner, prioritized filings stream with routine paperwork collapsed.
2. **Alerts View:** Ranked by severity (`CRITICAL`, `HIGH`, `MEDIUM`) with pinned cards on top and interactive threshold adjustment sliders.
3. **DeepDive View:** NSE ticker search, high-density financial metrics, "Narrative vs. Numbers" guidance vs. actual comparison table, cash conversion, and bull/bear synthesis.
4. **Nexus View:** Pinned starred contacts on top, relevance-ranked network contacts with 1–2 line development summaries, and 2nd-degree connection path visualization.
5. **PWA & Push:** Service worker registration, installable app manifest, native Web Push notification opt-in button, and optional desktop phone simulator frame.

## Directory Structure
```
frontend/
├── public/              # Icons, manifest.json, sw.js
├── src/
│   ├── assets/          # Static assets & logos
│   ├── components/      # UI components (common, push, pull, network, layout)
│   ├── hooks/           # Custom React hooks (usePWA, usePushNotifications, useApi)
│   ├── services/        # API client and IndexedDB offline cache
│   ├── types/           # TypeScript interfaces
│   ├── App.tsx          # Main navigation & view switching
│   └── main.tsx         # React root
├── package.json
└── AGENTS.md
```

## Discrete Commands
```bash
# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Run TypeScript check & production build
npm run build

# Preview production build
npm run preview
```

## Guardrails & Styling Rules
1. **Mobile-First Ergonomics:** All touch targets must be at least 44x44px. The primary viewport must fit comfortably on mobile screens (375px–430px width) while offering an edge-to-edge desktop mode and a toggleable phone frame.
2. **High-Density Finance Design:** Use dark slate / financial navy palettes (`slate-900`, `slate-800`, `emerald-500` for beats, `rose-500` for misses, `amber-500` for warnings). Avoid generic conversational chat templates.
3. **PWA Service Worker:** Always handle service worker lifecycle gracefully (prompting user on updates without breaking current state).
