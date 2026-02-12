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
  - EODHD API (EOD+Intraday $29.99/month) - **15 minute delayed** data
  - yfinance - Crypto, commodities, forex
  - BVB scraper/mock data

## Data Delay Information
**IMPORTANT**: EODHD plan changed from $100 All-In-One to $29.99 EOD+Intraday
- All market data has **15 minute delay** (not real-time)
- UI badges updated to show "15min Delay"
- Auto-refresh intervals optimized (60s for global, 30-60s for BVB)

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

### Completed Updates (Feb 12, 2026)
- [x] Updated UI to show "15min Delay" instead of "LIVE"
- [x] Optimized refresh intervals (60s global, 30s ticker)
- [x] Updated backend comments to reflect $29.99 plan
- [x] Changed source tag from "eodhd_realtime" to "eodhd_15min_delay"

### P1 - Pending
- [ ] Full Quiz System implementation
- [ ] Mobile responsiveness fixes

### P2 - Future
- [ ] "3 Straturi" Portfolio system
- [ ] Revolut Business payment option
- [ ] PWA improvements
- [ ] Push notifications

## Data Refresh Intervals
- Ticker Bar: 30 seconds
- Global Markets: 60 seconds  
- BVB (Free): 60 seconds
- BVB (PRO): 30 seconds

## Test Coverage
- Backend: 100% (17/17 tests passing)
- Test file: `/app/backend/tests/test_live_data_cache.py`
- Latest report: `/app/test_reports/iteration_6.json`

## Known Issues
None critical. All P0 issues resolved.

## Contact
Platform URL: https://financero.preview.emergentagent.com
