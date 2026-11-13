# Root AGENTS.md — FINN Financial Investment Agent

## Project Mission
FINN is a mobile-first, installable Progressive Web Application (PWA) built for high-conviction public-market investors at ENAM Holdings. It solves information overload through intelligent filtering and materiality classification, surfaces primary-source company research ("Narrative vs. Numbers"), and activates the investor's latent personal network with privacy-preserving graph intelligence.

## Repository Layout
- `backend/`: FastAPI Python application, centralized SQLite WAL store, anomaly detector, NetworkX graph engine, LLM router.
- `frontend/`: React 18 + Vite + Tailwind CSS PWA, service worker, Web Push integration.
- `data/`: Seed data definitions, primary source financial disclosures, mock network graphs.
- `docs/adr/`: Architecture Decision Records.

## Discrete Commands
```bash
# Backend Setup & Run
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.data.seed_data       # Seeds the SQLite WAL database
uvicorn app.main:app --reload --port 8000

# Backend Testing
cd backend
pytest tests/ -v

# Frontend Setup & Run
cd frontend
npm install
npm run dev                         # Starts Vite dev server on port 5173
npm run build                       # Verifies production build & PWA manifest

# Fullstack Verification
curl http://localhost:8000/api/health
```

## Global Guardrails for Agents
1. **Strict Primary-Source Grounding:** NEVER perform external web searches or use hallucinated LLM training knowledge for company fundamentals. All Pull research must strictly use primary sources (concalls, annual reports, screener filings).
2. **Privacy First:** Never log, expose, or mix the private investor network with public market data. Tenant boundaries must be respected.
3. **High Financial Density ("No AI Slop"):** UI and AI responses must be concise, bulleted, quantified (in bps, YoY/QoQ %, D/E, Cash Conversion), and designed for hedge-fund professionals.
4. **Git Hygiene:** Maintain clean, atomic commits for every completed sub-phase. Never commit `.env`, credentials, or raw cache files.
