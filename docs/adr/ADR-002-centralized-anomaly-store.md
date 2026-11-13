# ADR-002: Centralized SQLite (WAL Mode) Anomaly Pipeline & Store

## Status
Accepted

## Context
Market price/volume movements and exchange announcements arrive continuously throughout the trading day. Investors cannot rely on on-the-fly client computation when opening the app, as this creates high latency, misses historical anomalies, and prevents proactive push notifications when the app is inactive.

## Decision
We implement a **Centralized Background Anomaly Engine** writing to a local **SQLite database configured with Write-Ahead Logging (`PRAGMA journal_mode=WAL`)**:
1. **Central Store (`finn.db`):** Holds canonical tables for `companies`, `market_eod`, `announcements`, `concall_transcripts`, `guidance_history`, `detected_anomalies`, `user_preferences`, and `push_subscriptions`.
2. **Hybrid Metric Engine:**
   - **Quantitative Market Metrics:** Volume multiple vs 20-day SMA ($Vol / SMA_{20} \ge \text{Threshold}$), daily return deviations ($|\Delta\%| \ge \text{Threshold}$).
   - **Qualitative NLP Materiality Classifier:** Evaluates exchange announcements across the 17 standard categories and assigns a Materiality Score (1–10).
3. **User-Configurable Thresholds:** Stored in `user_preferences`, enabling investors to adjust sensitivity (e.g. volume multipliers and price % triggers) via sliders without altering backend data models.
4. **Trigger Pipeline:** Upon committing any critical anomaly to `detected_anomalies`, the engine automatically fires the Web Push Dispatcher.

## Consequences
- **Positive:** Low-latency querying for windowed digests, concurrent reader-writer operations via WAL mode, persistent anomaly audit trail, decoupled notification triggers.
- **Negative:** Requires background scheduler / worker maintenance; mitigated by APScheduler or asynchronous event loops with an on-demand trigger endpoint (`/api/pipeline/run`) for test evaluation.
