# FinRomania 2.0 - Product Requirements Document

## Original Problem Statement
Build "FinRomania 2.0", a comprehensive financial platform for the Romanian market featuring BVB & Global market data, fiscal calculators, educational resources, AI assistant, PRO subscriptions, and daily email summaries.

## Tech Stack
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + Python
- Database: MongoDB
- Auth: Firebase (Google Auth)
- Payments: Stripe
- Email: Resend
- AI: OpenAI GPT (Emergent LLM Key)
- Market Data: EODHD (Free Plan)

## What's Been Implemented
- Homepage with market ticker, hero section, feature cards
- BVB stocks listing and detail pages
- Global markets pages
- Fiscal Calculator (PF vs PFA vs SRL)
- Fiscal Simulator Antreprenor (2026 tax rules) - NEW
- AI Assistant (FinRomania Assistant)
- AI Technical Analysis (FAVORABIL/RISCANT terminology)
- PRO subscription via Stripe
- Early Adopter program (first 100 users, 3 months free PRO)
- Admin dashboard with feedback management
- News system (Romanian + international)
- In-app notifications for price alerts
- Daily BVB summary email via Resend (backend complete)
- Interactive onboarding tour
- Trading School / Education section

## Completed Bug Fixes (This Session - March 2026)
- [x] Fixed blue gradient overlay on homepage (HeroSection + InteractiveTour welcome screen)

## Pending Issues
- [ ] P1: Charts not loading on BVB stock pages (EODHD free plan limitation)
- [ ] P1: "Failed to fetch" error on Fiscal Simulator page
- [ ] P2: Mobile responsiveness issues
- [ ] P2: Slow page load times

## Upcoming Tasks
- [ ] P1: Add "Subscribe to Daily Summary" UI checkbox in user settings
- [ ] P1: Verify Resend domain (pending user DNS records)
- [ ] P2: Get expert feedback on Fiscal Simulator

## Future/Backlog
- [ ] Hot Stocks section on homepage
- [ ] "3 Straturi" portfolio strategy feature
- [ ] Expiration notification emails
- [ ] Native mobile app

## Key API Endpoints
- POST /api/fiscal-simulator/simulate
- GET /api/fiscal-simulator/praguri
- POST /api/daily-summary/subscribe
- POST /api/daily-summary/unsubscribe
- GET /api/daily-summary/preview
- POST /api/notifications/check-price-alerts

## Key Files
- /app/frontend/src/pages/HomePage.jsx
- /app/frontend/src/components/InteractiveTour.jsx
- /app/backend/routes/fiscal_simulator_antreprenor.py
- /app/frontend/src/pages/FiscalSimulatorPage.jsx
- /app/backend/services/daily_summary_service.py
- /app/backend/services/notification_service.py
