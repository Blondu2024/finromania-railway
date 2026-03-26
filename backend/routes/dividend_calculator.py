"""
Dividend Calculator PRO - Calculator avansat de dividende pentru BVB
Permite utilizatorilor să-și calculeze veniturile din dividende și să simuleze scenarii
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import logging

from config.database import get_database
from routes.auth import require_auth, get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dividend-calculator", tags=["Dividend Calculator"])


# ============================================
# DATA - Dividend yields estimate 2026
# Source: TradeVille research + historical patterns
# ============================================

DIVIDEND_ESTIMATES_2026 = {
    "TLV": {
        "name": "Banca Transilvania",
        "sector": "Financiar",
        "price_estimate": 36.50,
        "dividend_per_share": 1.30,
        "dividend_yield": 3.56,
        "payout_ratio": 30,
        "ex_date_estimate": "2026-05-25",
        "payment_date_estimate": "2026-06-15",
        "dividend_growth_5y": 15.2,
        "history": [
            {"year": 2024, "dividend": 1.27, "yield": 4.5},
            {"year": 2023, "dividend": 1.00, "yield": 4.2},
            {"year": 2022, "dividend": 0.90, "yield": 3.8},
        ]
    },
    "BRD": {
        "name": "BRD Groupe Société Générale",
        "sector": "Financiar",
        "price_estimate": 21.50,
        "dividend_per_share": 1.95,
        "dividend_yield": 9.07,
        "payout_ratio": 65,
        "ex_date_estimate": "2026-04-25",
        "payment_date_estimate": "2026-05-15",
        "dividend_growth_5y": 12.5,
        "history": [
            {"year": 2024, "dividend": 1.97, "yield": 9.1},
            {"year": 2023, "dividend": 1.64, "yield": 8.5},
            {"year": 2022, "dividend": 1.75, "yield": 9.0},
        ]
    },
    "SNP": {
        "name": "OMV Petrom",
        "sector": "Energie",
        "price_estimate": 1.00,
        "dividend_per_share": 0.065,
        "dividend_yield": 6.50,
        "payout_ratio": 50,
        "ex_date_estimate": "2026-05-20",
        "payment_date_estimate": "2026-06-10",
        "dividend_growth_5y": 8.3,
        "history": [
            {"year": 2024, "dividend": 0.06, "yield": 6.0},
            {"year": 2023, "dividend": 0.06, "yield": 5.8},
            {"year": 2022, "dividend": 0.06, "yield": 5.5},
        ]
    },
    "SNN": {
        "name": "Nuclearelectrica",
        "sector": "Energie",
        "price_estimate": 62.00,
        "dividend_per_share": 4.00,
        "dividend_yield": 6.45,
        "payout_ratio": 90,
        "ex_date_estimate": "2026-06-15",
        "payment_date_estimate": "2026-07-05",
        "dividend_growth_5y": 18.7,
        "history": [
            {"year": 2024, "dividend": 3.83, "yield": 6.2},
            {"year": 2023, "dividend": 2.94, "yield": 6.0},
            {"year": 2022, "dividend": 2.29, "yield": 5.5},
        ]
    },
    "H2O": {
        "name": "Hidroelectrica",
        "sector": "Energie",
        "price_estimate": 148.00,
        "dividend_per_share": 8.20,
        "dividend_yield": 5.54,
        "payout_ratio": 90,
        "ex_date_estimate": "2026-06-10",
        "payment_date_estimate": "2026-07-01",
        "dividend_growth_5y": 0,
        "note": "IPO 2023 - First dividend 2024",
        "history": [
            {"year": 2024, "dividend": 7.54, "yield": 5.1},
        ]
    },
    "SNG": {
        "name": "Romgaz",
        "sector": "Energie",
        "price_estimate": 55.00,
        "dividend_per_share": 3.60,
        "dividend_yield": 6.55,
        "payout_ratio": 50,
        "ex_date_estimate": "2026-06-01",
        "payment_date_estimate": "2026-06-25",
        "dividend_growth_5y": 14.2,
        "history": [
            {"year": 2024, "dividend": 3.11, "yield": 5.7},
            {"year": 2023, "dividend": 2.81, "yield": 5.5},
            {"year": 2022, "dividend": 3.00, "yield": 6.2},
        ]
    },
    "TGN": {
        "name": "Transgaz",
        "sector": "Energie",
        "price_estimate": 22.00,
        "dividend_per_share": 1.10,
        "dividend_yield": 5.00,
        "payout_ratio": 90,
        "ex_date_estimate": "2026-06-20",
        "payment_date_estimate": "2026-07-10",
        "dividend_growth_5y": 3.5,
        "history": [
            {"year": 2024, "dividend": 1.08, "yield": 4.8},
            {"year": 2023, "dividend": 1.03, "yield": 4.5},
            {"year": 2022, "dividend": 1.00, "yield": 4.2},
        ]
    },
    "FP": {
        "name": "Fondul Proprietatea",
        "sector": "Financiar",
        "price_estimate": 0.55,
        "dividend_per_share": 0.035,
        "dividend_yield": 6.36,
        "payout_ratio": 100,
        "ex_date_estimate": "2026-06-15",
        "payment_date_estimate": "2026-07-05",
        "dividend_growth_5y": -5.2,
        "note": "Dividend variabil - depinde de vânzări active",
        "history": [
            {"year": 2024, "dividend": 0.033, "yield": 6.0},
            {"year": 2023, "dividend": 0.042, "yield": 7.5},
            {"year": 2022, "dividend": 0.10, "yield": 8.0},
        ]
    },
    "DIGI": {
        "name": "Digi Communications",
        "sector": "Telecom",
        "price_estimate": 52.00,
        "dividend_per_share": 2.60,
        "dividend_yield": 5.00,
        "payout_ratio": 35,
        "ex_date_estimate": "2026-05-10",
        "payment_date_estimate": "2026-05-30",
        "dividend_growth_5y": 22.5,
        "history": [
            {"year": 2024, "dividend": 2.38, "yield": 4.8},
            {"year": 2023, "dividend": 1.80, "yield": 4.0},
            {"year": 2022, "dividend": 1.25, "yield": 3.2},
        ]
    },
    "EL": {
        "name": "Electrica",
        "sector": "Energie",
        "price_estimate": 16.50,
        "dividend_per_share": 0.85,
        "dividend_yield": 5.15,
        "payout_ratio": 85,
        "ex_date_estimate": "2026-06-01",
        "payment_date_estimate": "2026-06-20",
        "dividend_growth_5y": 5.8,
        "history": [
            {"year": 2024, "dividend": 0.82, "yield": 5.0},
            {"year": 2023, "dividend": 0.81, "yield": 5.2},
            {"year": 2022, "dividend": 0.78, "yield": 5.5},
        ]
    },
    "TEL": {
        "name": "Transelectrica",
        "sector": "Energie",
        "price_estimate": 38.00,
        "dividend_per_share": 2.10,
        "dividend_yield": 5.53,
        "payout_ratio": 85,
        "ex_date_estimate": "2026-06-15",
        "payment_date_estimate": "2026-07-05",
        "dividend_growth_5y": 8.2,
        "history": [
            {"year": 2024, "dividend": 1.93, "yield": 5.2},
            {"year": 2023, "dividend": 1.85, "yield": 5.3},
            {"year": 2022, "dividend": 1.69, "yield": 5.0},
        ]
    },
    "ONE": {
        "name": "One United Properties",
        "sector": "Imobiliare",
        "price_estimate": 1.10,
        "dividend_per_share": 0.048,
        "dividend_yield": 4.36,
        "payout_ratio": 20,
        "ex_date_estimate": "2026-05-15",
        "payment_date_estimate": "2026-06-05",
        "dividend_growth_5y": 35.0,
        "note": "High growth company - low payout, reinvesting",
        "history": [
            {"year": 2024, "dividend": 0.044, "yield": 4.0},
            {"year": 2023, "dividend": 0.035, "yield": 3.5},
        ]
    },
    "WINE": {
        "name": "Purcari Wineries",
        "sector": "Consum",
        "price_estimate": 17.00,
        "dividend_per_share": 0.55,
        "dividend_yield": 3.24,
        "payout_ratio": 40,
        "ex_date_estimate": "2026-06-01",
        "payment_date_estimate": "2026-06-20",
        "dividend_growth_5y": 12.8,
        "history": [
            {"year": 2024, "dividend": 0.50, "yield": 3.0},
            {"year": 2023, "dividend": 0.45, "yield": 2.8},
            {"year": 2022, "dividend": 0.40, "yield": 2.5},
        ]
    },
    "M": {
        "name": "MedLife",
        "sector": "Sănătate",
        "price_estimate": 7.50,
        "dividend_per_share": 0.15,
        "dividend_yield": 2.00,
        "payout_ratio": 15,
        "ex_date_estimate": "2026-05-20",
        "payment_date_estimate": "2026-06-10",
        "dividend_growth_5y": 25.0,
        "note": "Growth company - low payout ratio",
        "history": [
            {"year": 2024, "dividend": 0.12, "yield": 1.8},
            {"year": 2023, "dividend": 0.10, "yield": 1.5},
        ]
    },
    "AQ": {
        "name": "Aquila Part Prod Com",
        "sector": "Distribuție",
        "price_estimate": 1.80,
        "dividend_per_share": 0.09,
        "dividend_yield": 5.00,
        "payout_ratio": 50,
        "ex_date_estimate": "2026-05-25",
        "payment_date_estimate": "2026-06-15",
        "dividend_growth_5y": 18.5,
        "history": [
            {"year": 2024, "dividend": 0.08, "yield": 4.8},
            {"year": 2023, "dividend": 0.065, "yield": 4.0},
        ]
    },
}


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class PortfolioHolding(BaseModel):
    symbol: str
    shares: int
    purchase_price: Optional[float] = None


class CalculateRequest(BaseModel):
    holdings: List[PortfolioHolding]
    reinvest_dividends: bool = False
    years_projection: int = 5
    dividend_growth_rate: Optional[float] = None  # Override annual growth


class DividendResult(BaseModel):
    symbol: str
    name: str
    shares: int
    current_price: float
    dividend_per_share: float
    dividend_yield: float
    annual_dividend: float
    tax_16_percent: float
    net_dividend: float
    ex_date: str
    payment_date: str


# ============================================
# ENDPOINTS
# ============================================

@router.get("/stocks")
async def get_dividend_stocks():
    """
    Returnează toate acțiunile BVB cu dividende estimate pentru 2026
    Sortate după dividend yield descrescător
    """
    stocks = []
    for symbol, data in DIVIDEND_ESTIMATES_2026.items():
        stocks.append({
            "symbol": symbol,
            "name": data["name"],
            "sector": data["sector"],
            "price": data["price_estimate"],
            "dividend_per_share": data["dividend_per_share"],
            "dividend_yield": data["dividend_yield"],
            "payout_ratio": data["payout_ratio"],
            "ex_date": data["ex_date_estimate"],
            "payment_date": data["payment_date_estimate"],
            "dividend_growth_5y": data.get("dividend_growth_5y", 0),
            "history": data.get("history", []),
            "note": data.get("note")
        })
    
    # Sort by yield descending
    stocks.sort(key=lambda x: x["dividend_yield"], reverse=True)
    
    return {
        "stocks": stocks,
        "count": len(stocks),
        "average_yield": round(sum(s["dividend_yield"] for s in stocks) / len(stocks), 2),
        "data_source": "TradeVille estimates 2026",
        "last_updated": "2026-03-26"
    }


@router.post("/calculate")
async def calculate_dividends(request: CalculateRequest):
    """
    Calculator avansat de dividende
    Calculează veniturile din dividende pentru un portofoliu dat
    Include: taxe, proiecții pe ani, scenarii de reinvestire
    """
    results = []
    total_investment = 0
    total_annual_dividend = 0
    total_net_dividend = 0
    
    for holding in request.holdings:
        symbol = holding.symbol.upper()
        
        if symbol not in DIVIDEND_ESTIMATES_2026:
            continue
        
        data = DIVIDEND_ESTIMATES_2026[symbol]
        shares = holding.shares
        current_price = data["price_estimate"]
        dividend_per_share = data["dividend_per_share"]
        
        # Calculate dividends
        annual_dividend = shares * dividend_per_share
        tax_amount = annual_dividend * 0.16  # 16% tax on dividends in Romania
        net_dividend = annual_dividend - tax_amount
        
        # Track totals
        investment_value = shares * current_price
        total_investment += investment_value
        total_annual_dividend += annual_dividend
        total_net_dividend += net_dividend
        
        results.append({
            "symbol": symbol,
            "name": data["name"],
            "sector": data["sector"],
            "shares": shares,
            "current_price": current_price,
            "investment_value": round(investment_value, 2),
            "dividend_per_share": dividend_per_share,
            "dividend_yield": data["dividend_yield"],
            "annual_dividend_gross": round(annual_dividend, 2),
            "tax_16_percent": round(tax_amount, 2),
            "annual_dividend_net": round(net_dividend, 2),
            "monthly_income_net": round(net_dividend / 12, 2),
            "ex_date": data["ex_date_estimate"],
            "payment_date": data["payment_date_estimate"],
        })
    
    # Calculate portfolio metrics
    portfolio_yield = (total_annual_dividend / total_investment * 100) if total_investment > 0 else 0
    
    # Generate projections
    projections = []
    current_shares = {r["symbol"]: r["shares"] for r in results}
    current_investment = total_investment
    
    growth_rate = request.dividend_growth_rate or 5.0  # Default 5% annual dividend growth
    
    for year in range(1, request.years_projection + 1):
        year_data = {"year": 2026 + year - 1}
        
        if request.reinvest_dividends and year > 1:
            # Reinvest previous year's dividends
            for r in results:
                symbol = r["symbol"]
                data = DIVIDEND_ESTIMATES_2026[symbol]
                prev_dividend = current_shares[symbol] * data["dividend_per_share"] * (1 + growth_rate/100) ** (year - 2)
                net_prev = prev_dividend * 0.84  # After 16% tax
                # Buy more shares with dividends
                new_shares = int(net_prev / data["price_estimate"])
                current_shares[symbol] += new_shares
                current_investment += net_prev
        
        year_dividend = 0
        for r in results:
            symbol = r["symbol"]
            data = DIVIDEND_ESTIMATES_2026[symbol]
            # Apply dividend growth
            projected_dividend = data["dividend_per_share"] * (1 + growth_rate/100) ** (year - 1)
            year_dividend += current_shares[symbol] * projected_dividend
        
        net_year_dividend = year_dividend * 0.84
        
        year_data["gross_dividend"] = round(year_dividend, 2)
        year_data["net_dividend"] = round(net_year_dividend, 2)
        year_data["cumulative_net"] = round(sum(p.get("net_dividend", 0) for p in projections) + net_year_dividend, 2)
        year_data["yield_on_cost"] = round(year_dividend / total_investment * 100, 2) if total_investment > 0 else 0
        
        projections.append(year_data)
    
    return {
        "holdings": results,
        "summary": {
            "total_investment": round(total_investment, 2),
            "total_annual_dividend_gross": round(total_annual_dividend, 2),
            "total_annual_dividend_net": round(total_net_dividend, 2),
            "total_monthly_income_net": round(total_net_dividend / 12, 2),
            "portfolio_yield": round(portfolio_yield, 2),
            "tax_paid_annually": round(total_annual_dividend * 0.16, 2),
        },
        "projections": projections,
        "settings": {
            "reinvest_dividends": request.reinvest_dividends,
            "dividend_growth_rate": growth_rate,
            "years_projected": request.years_projection,
            "tax_rate": 16.0,
        },
        "disclaimer": "Estimările se bazează pe date publice și proiecții TradeVille. Dividendele reale pot varia."
    }


@router.get("/stock/{symbol}")
async def get_stock_dividend_details(symbol: str):
    """
    Detalii complete despre dividendul unei acțiuni
    Include istoric, proiecții și comparații
    """
    symbol = symbol.upper()
    
    if symbol not in DIVIDEND_ESTIMATES_2026:
        raise HTTPException(status_code=404, detail=f"Acțiunea {symbol} nu are date despre dividende")
    
    data = DIVIDEND_ESTIMATES_2026[symbol]
    
    # Calculate for 100 shares example
    example_shares = 100
    annual_dividend = example_shares * data["dividend_per_share"]
    net_dividend = annual_dividend * 0.84
    
    return {
        "symbol": symbol,
        "name": data["name"],
        "sector": data["sector"],
        "current_price": data["price_estimate"],
        "dividend_2026": {
            "per_share": data["dividend_per_share"],
            "yield": data["dividend_yield"],
            "payout_ratio": data["payout_ratio"],
            "ex_date": data["ex_date_estimate"],
            "payment_date": data["payment_date_estimate"],
        },
        "history": data.get("history", []),
        "dividend_growth_5y": data.get("dividend_growth_5y", 0),
        "example_calculation": {
            "shares": example_shares,
            "investment": example_shares * data["price_estimate"],
            "annual_dividend_gross": round(annual_dividend, 2),
            "annual_dividend_net": round(net_dividend, 2),
            "monthly_income_net": round(net_dividend / 12, 2),
        },
        "note": data.get("note"),
        "data_source": "TradeVille estimates 2026"
    }


@router.get("/top-yielders")
async def get_top_dividend_yielders(limit: int = Query(default=10, ge=1, le=20)):
    """
    Top acțiuni după dividend yield
    Ideal pentru vânătorii de dividende
    """
    stocks = []
    for symbol, data in DIVIDEND_ESTIMATES_2026.items():
        stocks.append({
            "symbol": symbol,
            "name": data["name"],
            "sector": data["sector"],
            "price": data["price_estimate"],
            "dividend_yield": data["dividend_yield"],
            "dividend_per_share": data["dividend_per_share"],
            "payout_ratio": data["payout_ratio"],
            "growth_5y": data.get("dividend_growth_5y", 0),
        })
    
    # Sort by yield
    stocks.sort(key=lambda x: x["dividend_yield"], reverse=True)
    
    return {
        "top_yielders": stocks[:limit],
        "average_yield": round(sum(s["dividend_yield"] for s in stocks) / len(stocks), 2),
        "highest_yield": stocks[0] if stocks else None,
    }


@router.get("/calendar/upcoming")
async def get_upcoming_dividends():
    """
    Calendar cu dividendele estimate pentru următoarele 3 luni
    """
    from datetime import datetime, timedelta
    
    today = datetime.now(timezone.utc).date()
    three_months = today + timedelta(days=90)
    
    upcoming = []
    for symbol, data in DIVIDEND_ESTIMATES_2026.items():
        ex_date = datetime.strptime(data["ex_date_estimate"], "%Y-%m-%d").date()
        
        if today <= ex_date <= three_months:
            upcoming.append({
                "symbol": symbol,
                "name": data["name"],
                "ex_date": data["ex_date_estimate"],
                "payment_date": data["payment_date_estimate"],
                "dividend_per_share": data["dividend_per_share"],
                "dividend_yield": data["dividend_yield"],
                "days_until_ex": (ex_date - today).days,
            })
    
    # Sort by ex_date
    upcoming.sort(key=lambda x: x["ex_date"])
    
    return {
        "upcoming": upcoming,
        "count": len(upcoming),
        "period": f"{today.isoformat()} - {three_months.isoformat()}"
    }
