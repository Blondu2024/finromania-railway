# FinRomania 2.0 - Product Requirements Document

## Overview
FinRomania 2.0 is a comprehensive financial platform for the Romanian market, providing real-time market data, fiscal calculators, educational resources, and AI-powered trading assistance.

## Original Problem Statement
Build a professional financial platform that:
1. Provides market data from BVB (Bucharest Stock Exchange) and global markets
2. Offers a fiscal calculator for tax optimization (PF vs. SRL)
3. Implements a PRO subscription model with Stripe
4. Features an AI advisor with usage limits
5. Includes admin dashboard for user management
6. Achieves good SEO for Romanian financial terms

## Tech Stack
- **Frontend**: React 18, TailwindCSS, Shadcn/UI, Framer Motion, Recharts
- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB
- **Auth**: Firebase Authentication
- **Payments**: Stripe (LIVE keys configured)
- **Data Sources**: 
  - EODHD API (EOD+Intraday $29.99/month)
  - yfinance - Crypto, commodities, forex
  - BVB scraper/mock data
- **News Sources**:
  - Romanian: ZF, Profit.ro, Capital, Economica
  - International: Yahoo Finance, CNBC, Reuters, Bloomberg, MarketWatch, Financial Times, Investing.com

## Core Features

### Implemented (100%)
- [x] Homepage with navigation and feature showcase
- [x] Global Markets Page (/global) with live heatmap, sentiment gauge, market status
- [x] BVB Stocks Page (/stocks) with Market Pulse, indices, heatmap, stock table
- [x] Ticker Bar with auto-refresh (30s)
- [x] User authentication (Firebase)
- [x] PRO subscription with Stripe (monthly/annual)
- [x] Admin Dashboard with user management
- [x] AI Advisor with query limits (5/day free, unlimited PRO)
- [x] Fiscal Calculator (PRO feature)
- [x] SEO optimization (sitemap, robots.txt, meta tags)

### Completed Updates (Mar 6, 2026)
- [x] **Early Adopter Program** - Primii 100 useri primesc PRO gratuit pentru 3 luni
- [x] Counter live pe Homepage și Pricing: "100/100 locuri disponibile"
- [x] Auto-upgrade la înregistrare pentru primii 100 useri
- [x] API endpoints: `/api/early-adopter/status`, `/api/early-adopter/claim`
- [x] Banner atractiv cu gradient orange/roșu și urgency messages
- [x] Beneficii afișate: AI nelimitat, toate nivelurile, Calculator Fiscal PRO
- [x] **Sistem de Notificări pentru Expirare**:
  - Job zilnic la 9:00 AM verifică expirările
  - Notificări la 7 zile, 3 zile, 1 zi înainte de expirare
  - Auto-downgrade la FREE când expiră
  - NotificationBell în header pentru utilizatori logați
  - CriticalNotificationBanner pentru alerte urgente
  - API: `/api/notifications`, `/api/notifications/count`
- [x] **SEO & Sitemap Dinamic**:
  - Sitemap generat automat: `/api/sitemap.xml` cu 271+ URL-uri
  - Include: pagini statice, acțiuni BVB, indici globali, știri, lecții
  - robots.txt actualizat pentru Google
  - Structured Data (Schema.org) pentru toate tipurile de pagini
  - Domeniu actualizat la finromania.ro

### Completed Updates (Feb 21, 2026)
- [x] **News System cu 2 taburi** - România & BVB + Internațional
- [x] Surse internaționale adăugate: Yahoo Finance, CNBC, Reuters, Bloomberg, MarketWatch, Financial Times, Investing.com
- [x] **UI Update** - Badge "Live" în loc de "15min Delay"
- [x] Scheduler actualizat pentru știri internaționale (every 15 min)
- [x] **HomePage actualizată** - arată 2 coloane de știri (România + Internațional)
- [x] **Articole se deschid pe platformă** - nu mai redirecționează pe site-urile externe
- [x] Sursa originală afișată în josul fiecărui articol cu link către sursa externă
- [x] **Scraping pentru articole internaționale** - conținut complet extras de la CNBC, Yahoo Finance, etc.
- [x] Configurații de scraping pentru: CNBC, Yahoo Finance, Reuters, Bloomberg, MarketWatch, Investing.com, Financial Times

### P1 - Pending
- [ ] Full Quiz System implementation
- [ ] Mobile responsiveness fixes

### P2 - Future
- [ ] "3 Straturi" Portfolio system
- [ ] Revolut Business payment option
- [ ] PWA improvements
- [ ] Push notifications

## API Endpoints

### News
- `GET /api/news?news_type=all|romania|international` - Știri combinate sau separate
- `GET /api/news/romania` - Știri românești (ZF, Profit.ro, etc.)
- `GET /api/news/international` - Știri internaționale (Yahoo, CNBC, Reuters, etc.)

### Market Data
- `GET /api/global/overview` - Complete global market data
- `GET /api/stocks/bvb` - All BVB stocks
- `GET /api/stocks/global` - Global indices for ticker
- `GET /api/bvb/indices` - BVB indices (BET, BETTR, etc.)

## Data Refresh Intervals
- Ticker Bar: 30 seconds
- Global Markets: 60 seconds  
- BVB: 60 seconds (FREE) / 30 seconds (PRO)
- News: 15 minutes

## Files Created/Modified
- `/app/backend/apis/international_rss_client.py` - NEW: Client RSS internațional
- `/app/backend/services/news_service.py` - MODIFIED: Suport pentru știri internaționale
- `/app/backend/jobs/scheduler.py` - MODIFIED: Job nou pentru știri internaționale
- `/app/frontend/src/pages/NewsPage.jsx` - MODIFIED: UI cu 2 taburi

## Contact
Platform URL: https://finromania-beta.preview.emergentagent.com
