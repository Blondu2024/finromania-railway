# FinRomania 2.0 - Product Requirements Document

## Original Problem Statement
Build "FinRomania 2.0", a comprehensive financial platform for the Romanian market featuring BVB & Global market data, fiscal calculators, educational resources, AI assistant, PRO subscriptions, and daily email summaries.

## Tech Stack
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + Python
- Database: MongoDB
- Auth: Google Auth (Emergent)
- Payments: Stripe
- Email: Resend
- AI: OpenAI GPT (Emergent LLM Key)
- Market Data: **EODHD (Paid Plan - $100/month All-in-One, 300k requests/day)**
- Indices: TradingView API (free)
- Global Markets: Yahoo Finance

## What's Been Implemented

### Core Features
- Homepage with market ticker, hero section, feature cards
- BVB stocks listing and detail pages with real-time data
- Global markets pages with Yahoo Finance data
- BVB Indices via TradingView (100% accurate)
- News system (Romanian RSS + international)
- In-app notifications for price alerts
- Interactive onboarding tour

### PRO Features (NEW - March 26, 2026)
- **Screener PRO** - Advanced stock screener with:
  - RSI, MACD, Bollinger Bands, SMA/EMA (LIVE from EODHD)
  - P/E, ROE, EPS, Dividend Yield (LIVE from EODHD)
  - AI-powered Buy/Sell signals with scoring
  - 6 preset strategies (Oversold Quality, Momentum, Dividend Hunters, etc.)
  - Export to CSV
- **Calculator Dividende** - Dividend calculator with:
  - 15 BVB stocks with 2026 dividend estimates
  - Portfolio builder with custom shares
  - Tax calculation (16% withheld at source)
  - 5-20 year projections with compound growth
  - DRIP (dividend reinvestment) simulation
- **Demo Login Endpoint** for automated testing (Playwright)

### Fiscal Tools
- Fiscal Calculator (PF vs PFA vs SRL) - Updated for 2026
- Fiscal Simulator Antreprenor (multi-entity comparison)

### AI Features
- AI Assistant (FinRomania Assistant)
- AI Technical Analysis (RSI, MACD, Support/Resistance)
- Daily AI Summary (cached once/day)

### Subscription & Auth
- PRO subscription via Stripe (49 lei/month)
- FREE PRO for ALL users until June 5, 2026
- Google Auth integration

### Admin Tools
- Admin dashboard with feedback management
- Bulk upgrade users to PRO button
- Trading School / Education section with quizzes

## Completed Bug Fixes (This Session - March 2026)
- [x] Fixed blue gradient overlay on homepage (HeroSection + InteractiveTour welcome screen) → bg-black solid
- [x] Email date now in Romanian ("18 martie 2026" instead of "18 March 2026")
- [x] AI summary uses exact numbers (no vague words like "semnificativ")
- [x] Fixed AI LLM integration import (was using old `chat()` function, now uses `LlmChat` class correctly)
- [x] Added personalized watchlist section to daily email (shows user's tracked stocks with % change)
- [x] Created "/rezumat-zilnic" page with full daily summary + navbar button
- [x] Changed PRO from "first 100 users" to "FREE for ALL until June 5, 2026"
- [x] Hidden PRO upsell banners/cards for PRO users (EarlyAdopterBanner + homepage CTA)
- [x] Added subscription_level to UserResponse model for frontend awareness
- [x] Fixed CASS calculation bug: now applies to employees too (was showing 0 CASS for salaried investors)
- [x] Added 24 minimum salary threshold for CASS (was missing)
- [x] Fixed quiz/lesson submission error ("Eroare de conexiune") — removed conflicting `credentials: 'include'` from 8 pages
- [x] Fixed stock detail pages not loading (SNP, TLV, BRD, etc.) — fallback to DB data when EODHD fails
- [x] Fixed daily email not sending: 0 subscribers + wrong timezone → enabled all users + Europe/Bucharest
- [x] Added 95/day email limit for Resend free plan
- [x] **MAJOR: Updated entire Fiscal Calculator from 2025 to 2026 legislation:**
  - Capital gains BVB: 1%→3% (>1yr), 3%→6% (<1yr)
  - Dividends: 10%→16%
  - International: 10%→16%
  - SRL dividends: 8%→16%
  - All UI/SEO references updated to 2026
  - Fixed preview endpoint to accept period/percentage params
- [x] Added admin "Upgrade All to PRO" button in dashboard
- [x] **EODHD INTEGRATION COMPLETE (March 20, 2026):**
  - Removed temporary web scraper (bvb_scraper.py)
  - Using paid EODHD plan with .RO suffix for BVB stocks
  - Real-time quotes + historical data working
  - Charts now show real candlestick data
  - Removed beautifulsoup4 dependency
- [x] **Fixed "+%" bug on Daily Summary page** - percentages now display correctly (was using wrong field name)
- [x] **MAJOR: Indicii BVB acum 100% CORECȚI (March 20, 2026):**
  - Implementat TradingView API Client pentru indicii BVB (gratuit, date exacte!)
  - Toate valorile sunt IDENTICE cu bvb.ro
  - BET: 28,036.31 (+0.16%) - LIVE ✅
  - BET-FI: 100,481.52 (-0.44%) - LIVE ✅
  - BET-NG: 2,075.20 (+0.27%) - LIVE ✅
  - Fișier nou: /app/backend/apis/tradingview_client.py
- [x] **Fix grafice Global (AAPL, etc):** Corectat period mapping (1m -> 1mo pentru yfinance)
- [x] **Fix API Global details:** Adăugat price, change, change_percent în răspuns
- [x] **CACHING Rezumat Zilnic (March 20, 2026):**
  - Rezumatul se generează O SINGURĂ DATĂ pe zi (la 18:10 după închiderea BVB)
  - Se salvează în MongoDB colecția `daily_summaries`
  - Toți utilizatorii primesc același rezumat din cache (rapid, fără AI la fiecare request)
  - Endpoint nou: POST /api/daily-summary/generate pentru forțare manuală
  - Emailurile folosesc rezumatul salvat (nu regenerează AI pentru fiecare abonat)

## Pending Issues
- [x] ~~P0: EODHD integration - scraper removal~~ ✅ DONE
- [x] ~~P1: Charts not loading on BVB stock pages~~ ✅ DONE (real historical data)
- [x] ~~P1: Charts not loading on Global stock pages~~ ✅ DONE (fixed period mapping)
- [x] ~~P1: "Failed to fetch" error on Fiscal Simulator page~~ ✅ WORKS (tested)
- [ ] P2: Mobile responsiveness issues
- [ ] P2: Slow page load times

## Completed (March 26, 2026 Session)
- [x] **Screener PRO** with LIVE technical indicators + fundamentals from EODHD
- [x] **Calculator Dividende** with 2026 estimates and projections
- [x] **Demo Login Endpoint** for automated testing (Playwright)
- [x] Upgraded to EODHD All-in-One plan ($100/month) for full fundamentals access

## Upcoming Tasks
- [ ] P1: Add "Subscribe to Daily Summary" UI checkbox in user settings
- [ ] P1: Verify Resend domain (pending user DNS records)
- [ ] P1: PRO Live Chat (community feature)
- [ ] P2: Get expert feedback on Fiscal Simulator

## Future/Backlog
- [ ] Hot Stocks section on homepage
- [ ] "3 Straturi" portfolio strategy feature
- [ ] Expiration notification emails
- [ ] Native mobile app
- [ ] Heatmap BVB
- [ ] Earnings Calendar

## Key API Endpoints - NEW
- GET /api/screener-pro/scan - Full BVB scan with technicals + fundamentals
- POST /api/screener-pro/filter - Filter by RSI, MACD, P/E, etc.
- GET /api/screener-pro/presets - 6 preset strategies
- GET /api/dividend-calculator/stocks - All dividend-paying BVB stocks
- POST /api/dividend-calculator/calculate - Calculate dividends for portfolio
- GET /api/auth/demo-login?secret=xxx - Demo login for automated testing

## Key Files - NEW
- /app/backend/routes/screener_pro.py - Screener PRO API
- /app/backend/routes/dividend_calculator.py - Dividend Calculator API  
- /app/frontend/src/pages/ScreenerProPage.jsx - Screener PRO UI
- /app/frontend/src/pages/DividendCalculatorPage.jsx - Dividend Calculator UI
- /app/frontend/src/pages/FiscalSimulatorPage.jsx
- /app/backend/services/daily_summary_service.py
- /app/backend/services/notification_service.py
