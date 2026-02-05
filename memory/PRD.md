# FinRomania 2.0 - Product Requirements Document

## Overview
FinRomania 2.0 is a comprehensive financial platform for the Romanian market, providing real-time market data, fiscal calculators, educational resources, and AI-powered trading assistance.

## Original Problem Statement
Build a professional financial platform that:
1. Provides LIVE market data from BVB (Bucharest Stock Exchange) and global markets
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
  - EODHD API ($100/month) - Real-time US indices
  - yfinance - Crypto, commodities, forex
  - BVB scraper/mock data

## Core Features

### Implemented (100%)
- [x] Homepage with navigation and feature showcase
- [x] Global Markets Page (/global) with live heatmap, sentiment gauge, market status
- [x] BVB Stocks Page (/stocks) with Market Pulse, indices, heatmap, stock table
- [x] Ticker Bar with auto-refresh (10s)
- [x] User authentication (Firebase)
- [x] PRO subscription with Stripe (monthly/annual)
- [x] Admin Dashboard with user management
- [x] AI Advisor with query limits (5/day free, unlimited PRO)
- [x] Fiscal Calculator (PRO feature)
- [x] SEO optimization (sitemap, robots.txt, meta tags)

### P0 - LIVE Data Fix (COMPLETED - Feb 5, 2026)
- [x] Removed frontend caching that prevented live data display
- [x] Added cache-busting timestamps to all fetch requests
- [x] Added no-cache headers to all live data APIs
- [x] Auto-refresh working at configured intervals
- [x] All 17 backend tests passing (100%)

### P1 - Pending
- [ ] Full Quiz System implementation
- [ ] Mobile responsiveness fixes

### P2 - Future
- [ ] "3 Straturi" Portfolio system
- [ ] Revolut Business payment option
- [ ] PWA improvements
- [ ] Push notifications

## API Endpoints

### Live Data (with no-cache headers)
- `GET /api/global/overview` - Complete global market data
- `GET /api/stocks/bvb` - All BVB stocks
- `GET /api/stocks/global` - Global indices for ticker
- `GET /api/bvb/indices` - BVB indices (BET, BETTR, etc.)
- `GET /api/bvb/top-movers` - Gainers, losers, most traded

### User & Subscription
- `POST /api/auth/login` - User login
- `GET /api/subscriptions/status` - Check PRO status
- `POST /api/stripe/create-checkout-session` - Start payment

## Data Refresh Intervals
- Ticker Bar: 10 seconds
- Global Markets: 10 seconds  
- BVB (Free): 60 seconds
- BVB (PRO): 15 seconds

## Test Coverage
- Backend: 100% (17/17 tests passing)
- Test file: `/app/backend/tests/test_live_data_cache.py`
- Latest report: `/app/test_reports/iteration_6.json`

## Known Issues
None critical. All P0 issues resolved.

## Contact
Platform URL: https://financero.preview.emergentagent.com
