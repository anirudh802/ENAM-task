# ADR-001: Installable Progressive Web Application (PWA) with Web Push

## Status
Accepted

## Context
The build challenge brief specifies a "mobile-first working prototype" for high-conviction investment managers. Public-market investors need timely alerts while away from their desks, but native app store review cycles (App Store / Google Play) introduce friction for rapid evaluation, continuous deployment, and testing. Additionally, standard in-app-only alerts fail to notify investors when the application is not actively focused.

## Decision
We adopt an **Installable Progressive Web Application (PWA)** built with React, Vite, Tailwind CSS, and `vite-plugin-pwa`:
1. **Zero-Friction Distribution:** Accessible immediately on any mobile or desktop browser via a deployed URL or tunnel link.
2. **Native Mobile Shell:** Supports "Add to Home Screen" on iOS and "Install App" on Android with standalone display mode, application icons, and splash screens.
3. **Background Push Notifications:** Integrates the standard Web Push API and Service Workers with VAPID key pairs to dispatch OS-level system notifications on critical anomalies even when the browser is minimized or closed.
4. **Desktop Evaluator Ergonomics:** Provides an optional toggleable "Phone Viewport Simulator" on desktop displays so evaluators can inspect mobile responsiveness without switching devices.

## Consequences
- **Positive:** Single cross-platform codebase, instant deployment, zero app-store friction, native push notification capability.
- **Negative:** iOS Safari requires user interaction ("Add to Home Screen" and explicit notification permission) to enable Web Push. A clear prompt and in-app fallback stream mitigates this.
