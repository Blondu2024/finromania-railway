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
- Market Data: **EODHD 100% (Paid Plan - $100/month All-in-One)** - NO yfinance
- Global Markets: 100% EODHD (removed yfinance March 2026)

## What's Been Implemented

### Core Features
- Homepage with market ticker, hero section, feature cards
- BVB stocks listing and detail pages with real-time data
- **Global markets 100% EODHD** (removed yfinance March 2026):
  - Gold = XAUUSD.FOREX real spot price (~$4,421/oz, NOT ETF price)
  - Silver = XAGUSD.FOREX real spot price (~$68/oz)
  - Oil/Gas = ETF proxies clearly labeled (USO ETF, UNG ETF)
  - NASDAQ 100 (NDX.INDX) replaces old NASDAQ Composite
  - FTSE 100 via DB fallback (^FTSE from yfinance, updated by EODHD scheduler)
  - Scheduler (update_global_indices) uses 100% EODHD
  - **Market Status Panel** (March 27, 2026): 7 burse cu DESCHISĂ/ÎNCHISĂ, countdown, BVB DST auto
    (NYSE/NASDAQ, LSE, XETRA/Euronext, TSE, HKEX, BVB, Crypto 24/7)
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

## Completed Bug Fixes (This Session - March 27, 2026)
- [x] **Pagina educațională CFD-uri vs Acțiuni Reale** (/educatie-cfd-vs-actiuni):
  - Hero cu badge avertizare + text explicativ
  - Banner 74-89% ESMA warning
  - Tabel comparativ 10 rânduri
  - Explicație levier + exemple concrete
  - Secțiune brokeri autorizați BVB
  - FAQ expandabil (6 întrebări)
  - CTA spre acțiuni BVB și calculator dividende
  - Link în meniu Academia + footer
- [x] **Toggle Email Rezumat Zilnic** în /notifications:
  - Secțiune vizuală nouă "Email Zilnic — Rezumatul Bursei"
  - Switch conectat la `POST /api/daily-summary/toggle-subscription`
  - Afișare status actual (activ/dezactivat cu emailul userului)
  - Banner verde de confirmare + badge "Salvat!"
  - Endpoint nou `GET /api/daily-summary/my-subscription`
  - Endpoint nou `POST /api/daily-summary/toggle-subscription`
- [x] **Export CSV Screener PRO** - îmbunătățit cu UTF-8 BOM și ghilimele pentru câmpuri
- [x] **Export CSV Portofoliu BVB** - buton nou în headerul "Poziții Active", descarcă toate pozițiile
- [x] **Fix MAJOR: Screener PRO scan timeout (502)** - implementat sistem de caching:
  - Scan rulează în background și cache-uiește în MongoDB (`screener_pro_cache`)
  - `/scan` returnează din cache instant (<0.3s vs 60+s anterior)
  - Job scheduler la 45 min pentru refresh automat al cache-ului
  - Frontend gestionează starea `cache_refreshing` cu mesaj informativ
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

## Completed (March 27, 2026 — Acuratețe Date Financiare Screener PRO)
- [x] **MAJOR: Date financiare 100% reale, fără estimări (Screener PRO)**
  - Dividend Yield: STRICT din dividende confirmate BVB.ro (nu EODHD estimate)
    - Badge "BVB.ro" verde în UI, tooltip "Confirmat BVB.ro (dividende reale)"
    - 41/87 acțiuni cu yield confirmat, 46 afișează N/A
  - P/E: null automat dacă EPS ≤ 0 (companie cu pierderi → P/E invalid)
    - DIGI: EPS=-1.77 → P/E=null (afișat '-' în UI)
    - M: EPS=-0.02 (manual override) → P/E=null
  - ROE: STRICT valoarea raportată EODHD (include și negative), fără estimări din profit_margin
    - 18/87 acțiuni cu ROE negativ (raportat corect, nu eliminat)
  - Debt/Equity: calculat din bilanțul EODHD (shortLongTermDebtTotal / totalStockholderEquity)
    - TLV=8.97, SNP=0.59, BRD=8.27, SNG=0.21 - exact cu datele oficiale
    - 61/87 acțiuni cu D/E disponibil
  - Coloană D/E nouă în tabelul Screener PRO (sortabilă, culoare portocalie dacă > 2)
  - Cache zilnic fundamentale: MongoDB `fundamentals_daily_cache` (83 documente)
    - Job nou în scheduler la 8:00 AM Bucharest: refresh P/E, ROE, EPS, D/E
    - Screener scan folosește cache zilnic → nu mai apelează EODHD live pentru fundamentale
  - Endpoint nou: POST /api/screener-pro/refresh-fundamentals (trigger manual)
  - Filter /api/screener-pro/filter funcționează corect cu max_debt_equity

## Completed (March 27, 2026 — BVB.ro Scraping + Istoric Dividende PRO)
- [x] **MAJOR: BVB.ro Dividend Scraping** — Official dividend data from BVB.ro replaces hardcoded/estimated data
  - Scraper: `/app/backend/scrapers/bvb_dividend_scraper.py`
  - 99 dividend records + 1,411 calendar events from BVB.ro
  - Rate limiting (3-5s between requests), realistic User-Agent
  - MongoDB caching (`bvb_dividends_scraped`, `bvb_calendar_scraped`, `bvb_scrape_meta`)
  - Automatic daily scrape at 7:00 AM Bucharest time + startup warmup
  - New API: `/api/bvb-dividends/*` (all, latest, upcoming, trailing, history, calendar, refresh, status)
- [x] **Updated Dividend Calculator** — Now uses BVB.ro > EODHD > Fallback priority chain
  - 42 stocks with official BVB.ro dividend data
  - "BVB.ro (oficial)" data source shown on UI
- [x] **Updated Dividend Calendar** — Official BVB.ro data instead of hardcoded estimates
  - Dividend Kings, CSV export all use BVB.ro data
  - Calendar events from BVB.ro financial calendar
- [x] **NEW: Istoric Dividende PRO** — Tab nou în Calculator Dividende (PRO-only)
  - Dividend Score (0-100) cu breakdown: Stabilitate 40% + Creștere 30% + Randament 30%
  - CAGR pe 5-8 ani de date (BVB.ro + EODHD deep history)
  - Clasament complet 43 acțiuni BVB sortate după Dividend Score
  - Analiză detaliată per acțiune cu grafic bar chart pe ani (Recharts)
  - Score badges cu culori gradient (verde=Excelent, albastru=FoarteBun, etc.)
  - MongoDB cache pentru clasament (se actualizează la fiecare 6h)
  - PRO paywall cu "Upgrade la PRO" pentru utilizatori free
- [x] **NEW: Comparație Dividende Side-by-Side** — Compară 2-4 acțiuni BVB
  - Checkboxes în tabelul de clasament + sticky bar "Compară"
  - Grouped bar chart cu culori diferite per acțiune (albastru, verde, amber, rosu)
  - Summary cards cu Score, Yield, CAGR, Preț pentru fiecare acțiune
  - Tabel comparativ expandabil an-cu-an
  - API: `/api/bvb-dividends/compare?symbols=TLV,BRD,SNP`

## Completed (March 26, 2026 Session)
- [x] **Screener PRO** with LIVE technical indicators + fundamentals from EODHD
- [x] **Calculator Dividende** with 2026 estimates and projections
- [x] **Demo Login Endpoint** for automated testing (Playwright)
- [x] Upgraded to EODHD All-in-One plan ($100/month) for full fundamentals access
- [x] **MAJOR: Fixed backend startup blocking issue** - removed immediate job execution that was blocking uvicorn startup
- [x] **NEW: Stock Comparison Tool** (`/api/stocks/compare`) - Compare 2-4 BVB stocks side-by-side with P/E, RSI, dividend yield, 52W high/low
- [x] **NEW: Unusual Volume Alerts** (`/api/stocks/unusual-volume`) - Shows stocks with 2x+ average volume with severity badges
- [x] **NEW: 52 Week Extremes** (`/api/stocks/52-week-extremes`) - Stocks near 52 week high/low
- [x] **NEW: Sector Filter** on StocksPage - Dropdown to filter stocks by sector (data pending)
- [x] **NEW: Stock Compare UI** on StocksPage - Checkbox selection + "Compară" button for side-by-side comparison
- [x] **NEW: Market Signals Widget** on Homepage - Shows unusual volume and 52 week extremes in real-time
- [x] **Email Notifications for Price Alerts** - Price alerts now send email via Resend ($20 plan)
- [x] **Daily Summary at 18:05** - Changed from 18:10 to 18:05 (right after BVB closes at 18:00)
- [x] **Increased Email Limit** - From 95/day to 500/day (Resend $20 plan = 10k/month)

## Upcoming Tasks
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
- GET /api/dividend-calculator/stocks - All dividend-paying BVB stocks (BVB.ro source)
- POST /api/dividend-calculator/calculate - Calculate dividends for portfolio
- GET /api/auth/demo-login?secret=xxx - Demo login for automated testing
- **GET /api/bvb-dividends/analysis/{symbol}** - Full dividend analysis with Score, CAGR, chart data
- **GET /api/bvb-dividends/rankings** - All stocks ranked by Dividend Score (cached)
- **GET /api/bvb-dividends/all** - All scraped BVB.ro dividend records
- **GET /api/bvb-dividends/latest** - Latest dividend per symbol
- **GET /api/bvb-dividends/upcoming** - Upcoming dividends (ex_date >= today)
- **GET /api/bvb-dividends/trailing/{symbol}** - Trailing 12M dividend for a symbol
- **GET /api/bvb-dividends/history/{symbol}** - Full dividend history for a symbol
- **GET /api/bvb-dividends/calendar** - BVB.ro financial calendar events
- **POST /api/bvb-dividends/refresh** - Trigger manual BVB.ro scrape
- **GET /api/bvb-dividends/status** - Scrape status and timestamps
- GET /api/stocks/compare?symbols=TLV,SNP,BRD - Compare 2-4 stocks side-by-side
- GET /api/stocks/unusual-volume - Stocks with abnormal trading volume
- GET /api/stocks/52-week-extremes - Stocks near 52 week high/low

## Key Files - NEW
- /app/backend/scrapers/bvb_dividend_scraper.py - BVB.ro dividend & calendar scraper
- /app/backend/routes/bvb_dividends.py - BVB.ro scraped data API
- /app/backend/routes/screener_pro.py - Screener PRO API
- /app/backend/routes/dividend_calculator.py - Dividend Calculator API (uses BVB.ro)
- /app/backend/routes/dividend_calendar.py - Dividend Calendar API (uses BVB.ro)
- /app/backend/routes/stock_compare.py - Stock comparison, 52W extremes, unusual volume API
- /app/frontend/src/pages/ScreenerProPage.jsx - Screener PRO UI
- /app/frontend/src/pages/DividendCalculatorPage.jsx - Dividend Calculator UI
- /app/frontend/src/pages/DividendCalendarPage.jsx - Dividend Calendar UI
- /app/frontend/src/pages/FiscalSimulatorPage.jsx
- /app/frontend/src/components/StockCompare.jsx - Stock comparison modal component
- /app/frontend/src/components/MarketSignals.jsx - 52 Week Extremes + Unusual Volume widgets
- /app/backend/services/daily_summary_service.py
- /app/backend/services/notification_service.py
