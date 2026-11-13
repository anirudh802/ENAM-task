#!/bin/bash
# FINN - Fullstack Local Launcher
# Starts FastAPI backend (port 8000) and Vite PWA frontend (port 5173)

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo " Starting FINN - Financial Investment Agent"
echo " Mobile-First PWA + SQLite WAL Backend Engine"
echo "=========================================================="

# 1. Start Backend
echo "[1/2] Launching Backend Engine on http://localhost:8000..."
cd "$DIR/backend"
if [ ! -d "venv" ]; then
    echo "Creating python venv..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
    ./venv/bin/python -m app.data.seed_data
fi

./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Trap kill signal
cleanup() {
    echo ""
    echo "Shutting down FINN services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Wait for backend health
echo "Waiting for backend health check..."
until curl -s http://localhost:8000/api/health >/dev/null; do
    sleep 0.5
done
echo "Backend is live at http://localhost:8000 (Swagger docs at /docs)"

# 2. Start Frontend
echo "[2/2] Launching Frontend PWA on http://localhost:5173..."
cd "$DIR/frontend"
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo "=========================================================="
echo " FINN is ready!"
echo " Mobile PWA App: http://localhost:5173"
echo " Backend API:    http://localhost:8000"
echo " Health Check:   http://localhost:8000/api/health"
echo "=========================================================="

wait
