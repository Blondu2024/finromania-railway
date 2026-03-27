"""
Dividend Calculator PRO - Calculator avansat de dividende pentru BVB
Permite utilizatorilor să-și calculeze veniturile din dividende și să simuleze scenarii
DATE LIVE de la EODHD + fallback verificat cu date reale BVB.ro
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import logging
import httpx
import os

from config.database import get_database
from routes.auth import require_auth, get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dividend-calculator", tags=["Dividend Calculator"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE = "https://eodhd.com/api"


# ============================================
# FALLBACK DATA - Verificat cu EODHD + BVB.ro
# SURSA: EODHD /div/{symbol}.RO — unadjustedValue
# ACTUALIZAT: Martie 2026
#
# TAX 2026: Impozit dividende = 16% (Legea 141/2025, pentru dividende distribuite din 01.01.2026)
# TAX 2025: Impozit dividende = 10% (dacă distribuite în 2025)
# CASS: 10% pe plafon 6/12/24 salarii minime, dacă venituri neosalariale > 6 SMB (~27.000 RON/an 2026)
# ============================================

SALARIU_MINIM_2026 = 4700  # RON brut estimat 2026

DIVIDEND_FALLBACK_2026 = {
    "TLV": {
        "name": "Banca Transilvania",
        "sector": "Financiar",
        "dividend_per_share": 1.73333,  # EODHD div 2025-06-13 (din profit 2024)
        "dividend_2026_est": 1.85,      # Estimare 2026 (creștere ~7%)
        "ex_date_estimate": "2026-06-12",
        "payment_date_estimate": "2026-06-26",
        "source_confirmed": "EODHD div API",
        "note": "Dividend anual din profit 2024. Suplimentar: 0.642 RON dividend interimar (nov 2025)."
    },
    "BRD": {
        "name": "BRD Groupe Société Générale",
        "sector": "Financiar",
        "dividend_per_share": 1.0752,   # CONFIRMAT MarketScreener & EODHD — ex-date 2026-05-18
        "dividend_2026_est": 1.0752,
        "ex_date_estimate": "2026-05-18",   # CONFIRMAT
        "payment_date_estimate": "2026-06-05",  # CONFIRMAT
        "source_confirmed": "Confirmat BRD/BVB 2026",
        "note": "Dividend confirmat pentru 2026 (din profit 2025). Ex-date: 18 mai 2026."
    },
    "SNP": {
        "name": "OMV Petrom",
        "sector": "Energie",
        "dividend_per_share": 0.0578,   # CONFIRMAT OMV Petrom — ex-date 2026-05-14
        "dividend_2026_est": 0.0578,
        "ex_date_estimate": "2026-05-14",   # CONFIRMAT
        "payment_date_estimate": "2026-06-08",  # CONFIRMAT
        "source_confirmed": "Confirmat OMV Petrom/BVB 2026",
        "note": "Dividend final confirmat 2026 (profit 2025). Randament ~5.7%."
    },
    "H2O": {
        "name": "Hidroelectrica",
        "sector": "Energie",
        "dividend_per_share": 8.9889,   # EODHD div 2025-06-03 (din profit 2024)
        "dividend_2026_est": 9.50,      # Estimare 2026
        "ex_date_estimate": "2026-06-05",
        "payment_date_estimate": "2026-06-25",
        "source_confirmed": "EODHD div API",
        "note": "Cel mai mare dividend pe acțiune de pe BVB. Randament ~6%."
    },
    "SNN": {
        "name": "Nuclearelectrica",
        "sector": "Energie",
        "dividend_per_share": 2.70243,  # EODHD div 2025-06-02 (din profit 2024)
        "dividend_2026_est": 2.80,      # Estimare 2026
        "ex_date_estimate": "2026-06-04",
        "payment_date_estimate": "2026-06-25",
        "source_confirmed": "EODHD div API",
        "note": "Dividend anual stabil. Randament ~4%."
    },
    "SNG": {
        "name": "Romgaz",
        "sector": "Energie",
        "dividend_per_share": 0.1568,   # CONFIRMAT EODHD + Romgaz.ro — ex-date 2025-07-03
        "dividend_2026_est": 0.1572,    # Propus CA 25 mart 2026 (supus AGA apr 2026)
        "ex_date_estimate": "2026-07-03",
        "payment_date_estimate": "2026-07-28",
        "source_confirmed": "EODHD + Romgaz.ro",
        "note": "Propunere 2026: 0.1572 RON/acț. Politică conservatoare de dividende."
    },
    "TGN": {
        "name": "Transgaz",
        "sector": "Energie",
        "dividend_per_share": 1.08,     # EODHD div 2025-06-24 (din profit 2024)
        "dividend_2026_est": 1.15,      # Estimare 2026
        "ex_date_estimate": "2026-06-24",
        "payment_date_estimate": "2026-07-10",
        "source_confirmed": "EODHD div API",
        "note": "Dividend anual regulat."
    },
    "EL": {
        "name": "Electrica",
        "sector": "Energie",
        "dividend_per_share": 0.1767,   # EODHD div 2025-06-03 (din profit 2024)
        "dividend_2026_est": 0.20,      # Estimare 2026
        "ex_date_estimate": "2026-06-03",
        "payment_date_estimate": "2026-06-20",
        "source_confirmed": "EODHD div API",
        "note": "Dividend după ajustare pentru split acțiuni."
    },
    "TEL": {
        "name": "Transelectrica",
        "sector": "Energie",
        "dividend_per_share": 2.12,     # EODHD div 2025-06-05 (dividend anual din profit 2024)
        "dividend_2026_est": 2.20,      # Estimare 2026
        "ex_date_estimate": "2026-06-05",
        "payment_date_estimate": "2026-06-20",
        "source_confirmed": "EODHD div API",
        "note": "Dividend anual + posibil dividend special separat (3.81 RON în iul 2025 - excepțional)."
    },
    "DIGI": {
        "name": "Digi Communications",
        "sector": "Telecom",
        "dividend_per_share": 1.35,     # EODHD div 2025-06-26 (din profit 2024)
        "dividend_2026_est": 1.45,      # Estimare 2026
        "ex_date_estimate": "2026-06-26",
        "payment_date_estimate": "2026-07-10",
        "source_confirmed": "EODHD div API",
        "note": "Dividend anual stabil."
    },
    "FP": {
        "name": "Fondul Proprietatea",
        "sector": "Financiar",
        "dividend_per_share": 0.0409,   # EODHD div 2025-05-27
        "dividend_2026_est": 0.035,     # Estimare 2026 (variabil)
        "ex_date_estimate": "2026-05-25",
        "payment_date_estimate": "2026-06-10",
        "source_confirmed": "EODHD div API",
        "note": "Dividend variabil — depinde de vânzări active din portofoliu."
    },
    "ONE": {
        "name": "One United Properties",
        "sector": "Imobiliare",
        "dividend_per_share": 0.36,     # EODHD div 2025-05-20 (și nov 2025 = 0.36)
        "dividend_2026_est": 0.36,      # Estimare 2026 (menținut)
        "ex_date_estimate": "2026-05-20",
        "payment_date_estimate": "2026-06-05",
        "source_confirmed": "EODHD div API",
        "note": "Dividende semestriale — 0.36 RON × 2 plăți/an."
    },
    "WINE": {
        "name": "Purcari Wineries",
        "sector": "Consum",
        "dividend_per_share": 0.65,     # EODHD div 2025-09-01
        "dividend_2026_est": 0.68,      # Estimare 2026
        "ex_date_estimate": "2026-09-01",
        "payment_date_estimate": "2026-09-20",
        "source_confirmed": "EODHD div API",
        "note": "Dividend anual din profit."
    },
    "AQ": {
        "name": "Aquila Part Prod Com",
        "sector": "Distribuție",
        "dividend_per_share": 0.0499,   # EODHD div 2025-05-20
        "dividend_2026_est": 0.055,     # Estimare 2026
        "ex_date_estimate": "2026-05-20",
        "payment_date_estimate": "2026-06-05",
        "source_confirmed": "EODHD div API",
        "note": "Dividend anual."
    },
    "M": {
        "name": "MedLife",
        "sector": "Sănătate",
        "dividend_per_share": 0,
        "dividend_2026_est": 0,
        "ex_date_estimate": None,
        "payment_date_estimate": None,
        "source_confirmed": "BVB.ro",
        "note": "EPS negativ — fără dividend așteptat în 2026."
    },
}

# All dividend-paying BVB stocks to check (expanded list)
DIVIDEND_SYMBOLS = [
    "TLV", "BRD", "SNP", "H2O", "SNN", "SNG", "TGN", "EL", "TEL",
    "DIGI", "FP", "ONE", "WINE", "AQ"
]

# ============================================
# CASS CALCULATOR 2026
# ============================================
def calculate_cass_2026(venituri_anuale_brut: float) -> dict:
    """
    Calculează contribuția CASS (sănătate) pentru venituri din dividende 2026.
    CASS = 10% aplicat pe baza de calcul plafonată (6/12/24 salarii minime brute).
    Sursa: Codul Fiscal actualizat 2026.
    """
    smb = SALARIU_MINIM_2026  # 4700 RON/lună
    plafonul_6 = 6 * smb    # 28.200 RON
    plafonul_12 = 12 * smb  # 56.400 RON
    plafonul_24 = 24 * smb  # 112.800 RON

    if venituri_anuale_brut < plafonul_6:
        return {
            "datoreaza_cass": False,
            "baza_calcul": 0,
            "cass_datorat": 0,
            "plafon_aplicat": "sub 6 SMB — CASS 0",
            "detaliu": f"Venituri < {plafonul_6:,.0f} RON → fără CASS"
        }
    elif venituri_anuale_brut < plafonul_12:
        baza = plafonul_6
        cass = baza * 0.10
        return {
            "datoreaza_cass": True,
            "baza_calcul": baza,
            "cass_datorat": round(cass, 2),
            "plafon_aplicat": "6 SMB",
            "detaliu": f"Venituri ≥ {plafonul_6:,.0f} RON → CASS pe 6 SMB = {cass:,.2f} RON/an"
        }
    elif venituri_anuale_brut < plafonul_24:
        baza = plafonul_12
        cass = baza * 0.10
        return {
            "datoreaza_cass": True,
            "baza_calcul": baza,
            "cass_datorat": round(cass, 2),
            "plafon_aplicat": "12 SMB",
            "detaliu": f"Venituri ≥ {plafonul_12:,.0f} RON → CASS pe 12 SMB = {cass:,.2f} RON/an"
        }
    else:
        baza = plafonul_24
        cass = baza * 0.10
        return {
            "datoreaza_cass": True,
            "baza_calcul": baza,
            "cass_datorat": round(cass, 2),
            "plafon_aplicat": "24 SMB (plafon maxim)",
            "detaliu": f"Venituri ≥ {plafonul_24:,.0f} RON → CASS pe 24 SMB = {cass:,.2f} RON/an (MAX)"
        }



async def fetch_live_dividend_data(symbol: str) -> Optional[Dict]:
    """Fetch dividend data from EODHD API.
    Uses SUM of all dividends in the last 12 months as the annual dividend.
    This is more accurate than just the last single payment (some companies pay multiple times).
    Falls back to fundamentals Highlights if no div history.
    """
    if not EODHD_API_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # PRIMARY: Use dividend history endpoint — sum last 12M
            from datetime import timedelta
            from_date = (datetime.now(timezone.utc) - timedelta(days=380)).strftime("%Y-%m-%d")
            div_url = f"{EODHD_BASE}/div/{symbol}.RO"
            div_r = await client.get(div_url, params={"api_token": EODHD_API_KEY, "fmt": "json", "from": from_date})

            if div_r.status_code == 200:
                div_data = div_r.json()
                if isinstance(div_data, list) and div_data:
                    valid = [d for d in div_data if float(d.get("unadjustedValue", 0)) > 0.0001]
                    if valid:
                        # Sum of all dividends paid in last 12 months = trailing annual dividend
                        trailing_annual = sum(float(d["unadjustedValue"]) for d in valid)
                        latest = valid[-1]  # for ex-date

                        # Try to get name from fundamentals
                        fund_url = f"{EODHD_BASE}/fundamentals/{symbol}.RO"
                        fund_r = await client.get(fund_url, params={"api_token": EODHD_API_KEY, "fmt": "json", "filter": "General,Highlights"})
                        name = symbol
                        sector = "Unknown"
                        div_yield = None

                        if fund_r.status_code == 200:
                            fd = fund_r.json()
                            gen = fd.get("General", {})
                            hl = fd.get("Highlights", {})
                            name = gen.get("Name", symbol)
                            sector = gen.get("Sector", "Unknown")
                            div_yield = hl.get("DividendYield")

                        return {
                            "dividend_per_share": round(trailing_annual, 4),
                            "dividend_yield": round(div_yield * 100, 2) if div_yield else None,
                            "name": name,
                            "sector": sector,
                            "ex_date": latest.get("date"),
                            "payments_last_12m": len(valid),
                            "source": "EODHD DIV HISTORY (sum 12M)"
                        }

            # FALLBACK: Fundamentals Highlights
            fund_url = f"{EODHD_BASE}/fundamentals/{symbol}.RO"
            fund_r = await client.get(fund_url, params={"api_token": EODHD_API_KEY, "fmt": "json", "filter": "General,Highlights"})
            if fund_r.status_code == 200:
                fd = fund_r.json()
                hl = fd.get("Highlights", {})
                gen = fd.get("General", {})
                dividend_share = hl.get("DividendShare", 0) or 0
                if dividend_share > 0:
                    return {
                        "dividend_per_share": float(dividend_share),
                        "dividend_yield": round(hl.get("DividendYield", 0) * 100, 2),
                        "name": gen.get("Name", symbol),
                        "sector": gen.get("Sector", "Unknown"),
                        "source": "EODHD FUNDAMENTALS"
                    }

            return None

    except Exception as e:
        logger.warning(f"Error fetching dividend data for {symbol}: {e}")
        return None


async def get_current_price(symbol: str) -> float:
    """Get current stock price from database"""
    db = await get_database()
    stock = await db.stocks_bvb.find_one({"symbol": symbol}, {"_id": 0, "price": 1})
    return stock.get("price", 0) if stock else 0


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
    Returnează toate acțiunile BVB cu dividende
    Prioritate: Date LIVE EODHD > Fallback confirmat
    """
    stocks = []
    
    for symbol in DIVIDEND_SYMBOLS:
        # Try to get LIVE data from EODHD first
        live_data = await fetch_live_dividend_data(symbol)
        current_price = await get_current_price(symbol)
        
        if live_data and live_data.get("dividend_per_share", 0) > 0:
            # Use LIVE EODHD data
            div_per_share = live_data["dividend_per_share"]
            div_yield = live_data.get("dividend_yield") or (div_per_share / current_price * 100 if current_price > 0 else 0)
            
            fallback = DIVIDEND_FALLBACK_2026.get(symbol, {})
            
            stocks.append({
                "symbol": symbol,
                "name": live_data.get("name", symbol),
                "sector": live_data.get("sector", fallback.get("sector", "Unknown")),
                "price": round(current_price, 2),
                "dividend_per_share": round(div_per_share, 4),
                "dividend_yield": round(div_yield, 2),
                "ex_date": fallback.get("ex_date_estimate"),
                "payment_date": fallback.get("payment_date_estimate"),
                "data_source": "EODHD LIVE",
                "note": fallback.get("note")
            })
        elif symbol in DIVIDEND_FALLBACK_2026:
            # Use fallback data
            fallback = DIVIDEND_FALLBACK_2026[symbol]
            div_per_share = fallback.get("dividend_per_share", 0)
            
            if div_per_share > 0:
                div_yield = (div_per_share / current_price * 100) if current_price > 0 else 0
                
                stocks.append({
                    "symbol": symbol,
                    "name": fallback["name"],
                    "sector": fallback.get("sector", "Unknown"),
                    "price": round(current_price, 2),
                    "dividend_per_share": round(div_per_share, 4),
                    "dividend_yield": round(div_yield, 2),
                    "ex_date": fallback.get("ex_date_estimate"),
                    "payment_date": fallback.get("payment_date_estimate"),
                    "data_source": "Fallback (confirmat 2024)",
                    "note": fallback.get("note")
                })
    
    # Sort by yield descending
    stocks.sort(key=lambda x: x["dividend_yield"], reverse=True)
    
    return {
        "stocks": stocks,
        "count": len(stocks),
        "average_yield": round(sum(s["dividend_yield"] for s in stocks) / len(stocks), 2) if stocks else 0,
        "data_sources": "EODHD LIVE + Fallback confirmat",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "Dividendele afișate sunt ultimele distribuite. Dividendele viitoare pot varia."
    }


@router.post("/calculate")
async def calculate_dividends(request: CalculateRequest):
    """
    Calculator avansat de dividende cu DATE LIVE
    Calculează veniturile din dividende pentru un portofoliu dat
    Include: taxe, proiecții pe ani, scenarii de reinvestire
    """
    results = []
    total_investment = 0
    total_annual_dividend = 0
    total_net_dividend = 0
    
    for holding in request.holdings:
        symbol = holding.symbol.upper()
        shares = holding.shares
        
        # Get LIVE data
        live_data = await fetch_live_dividend_data(symbol)
        current_price = await get_current_price(symbol)
        fallback = DIVIDEND_FALLBACK_2026.get(symbol, {})
        
        # Determine dividend per share (LIVE > Fallback)
        if live_data and live_data.get("dividend_per_share", 0) > 0:
            dividend_per_share = live_data["dividend_per_share"]
            name = live_data.get("name", symbol)
            sector = live_data.get("sector", fallback.get("sector", "Unknown"))
            data_source = "EODHD LIVE"
        elif fallback.get("dividend_per_share", 0) > 0:
            dividend_per_share = fallback["dividend_per_share"]
            name = fallback.get("name", symbol)
            sector = fallback.get("sector", "Unknown")
            data_source = "Fallback 2024"
        else:
            # No dividend data available
            continue
        
        if current_price <= 0:
            continue
        
        # ── Calculate dividends with Romanian fiscal rules ──────────────
        # 2026: 16% withholding tax (Legea 141/2025, dividende distribuite din 01.01.2026)
        TAX_RATE = 0.16
        annual_dividend = shares * dividend_per_share
        tax_amount = annual_dividend * TAX_RATE
        net_dividend = annual_dividend - tax_amount
        div_yield = (dividend_per_share / current_price * 100)
        
        # Track totals
        investment_value = shares * current_price
        total_investment += investment_value
        total_annual_dividend += annual_dividend
        total_net_dividend += net_dividend
        
        results.append({
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "shares": shares,
            "current_price": round(current_price, 2),
            "investment_value": round(investment_value, 2),
            "dividend_per_share": round(dividend_per_share, 4),
            "dividend_yield": round(div_yield, 2),
            "annual_dividend_gross": round(annual_dividend, 2),
            "tax_16_percent": round(tax_amount, 2),
            "annual_dividend_net": round(net_dividend, 2),
            "monthly_income_net": round(net_dividend / 12, 2),
            "ex_date": fallback.get("ex_date_estimate"),
            "payment_date": fallback.get("payment_date_estimate"),
            "data_source": data_source
        })
    
    # Calculate portfolio metrics
    portfolio_yield = (total_annual_dividend / total_investment * 100) if total_investment > 0 else 0
    
    # Calculate CASS (health insurance) on total dividend income
    cass_info = calculate_cass_2026(total_annual_dividend)
    cass_amount = cass_info["cass_datorat"]
    total_net_after_cass = total_net_dividend - cass_amount
    
    # Generate projections (simplified - uses average growth rate)
    projections = []
    growth_rate = request.dividend_growth_rate or 3.0  # Default 3% annual dividend growth (conservative)
    cumulative_net = 0
    
    for year in range(1, request.years_projection + 1):
        year_data = {"year": 2026 + year - 1}
        
        # Apply dividend growth to total
        year_gross = total_annual_dividend * (1 + growth_rate/100) ** (year - 1)
        year_net = year_gross * 0.84  # After 16% impozit dividende
        year_cass = calculate_cass_2026(year_gross)["cass_datorat"]
        year_net_final = year_net - year_cass
        cumulative_net += year_net_final
        
        year_data["gross_dividend"] = round(year_gross, 2)
        year_data["impozit_16pct"] = round(year_gross * 0.16, 2)
        year_data["net_dividend"] = round(year_net, 2)
        year_data["cass"] = round(year_cass, 2)
        year_data["net_final_dupa_cass"] = round(year_net_final, 2)
        year_data["cumulative_net"] = round(cumulative_net, 2)
        year_data["yield_on_cost"] = round(year_gross / total_investment * 100, 2) if total_investment > 0 else 0
        
        projections.append(year_data)
    
    return {
        "holdings": results,
        "summary": {
            "total_investment": round(total_investment, 2),
            "total_annual_dividend_gross": round(total_annual_dividend, 2),
            "impozit_dividende_16pct": round(total_annual_dividend * 0.16, 2),
            "total_annual_dividend_net": round(total_net_dividend, 2),
            "cass": {
                "datorat": cass_info["datoreaza_cass"],
                "plafon": cass_info["plafon_aplicat"],
                "suma": cass_amount,
                "detaliu": cass_info["detaliu"],
            },
            "total_net_dupa_cass": round(total_net_after_cass, 2),
            "total_monthly_income_net": round(total_net_after_cass / 12, 2),
            "portfolio_yield": round(portfolio_yield, 2),
        },
        "projections": projections,
        "settings": {
            "reinvest_dividends": request.reinvest_dividends,
            "dividend_growth_rate": growth_rate,
            "years_projected": request.years_projection,
            "tax_rate_2026": 16.0,
            "cass_rate_2026": 10.0,
            "salariu_minim_2026": SALARIU_MINIM_2026,
        },
        "tax_info": {
            "impozit_dividende": "16% (reținut la sursă din 01.01.2026 — Legea 141/2025)",
            "cass": f"10% pe plafon {cass_info['plafon_aplicat']} dacă venituri ≥ {6*SALARIU_MINIM_2026:,.0f} RON/an",
            "baza_legala": "Codul Fiscal 2026 — art. 97 (impozit dividende) + art. 156 (CASS)"
        },
        "data_source": "EODHD Dividend History + Fallback confirmat BVB 2026",
        "disclaimer": "Dividendele afișate sunt ultimele distribuite. Dividendele viitoare pot varia și depind de deciziile AGA."
    }


@router.get("/stock/{symbol}")
async def get_stock_dividend_details(symbol: str):
    """
    Detalii complete despre dividendul unei acțiuni cu DATE LIVE
    """
    symbol = symbol.upper()
    
    # Get LIVE data
    live_data = await fetch_live_dividend_data(symbol)
    current_price = await get_current_price(symbol)
    fallback = DIVIDEND_FALLBACK_2026.get(symbol, {})
    
    # Determine dividend data
    if live_data and live_data.get("dividend_per_share", 0) > 0:
        dividend_per_share = live_data["dividend_per_share"]
        name = live_data.get("name", symbol)
        sector = live_data.get("sector", fallback.get("sector", "Unknown"))
        data_source = "EODHD LIVE"
    elif fallback.get("dividend_per_share", 0) > 0:
        dividend_per_share = fallback["dividend_per_share"]
        name = fallback.get("name", symbol)
        sector = fallback.get("sector", "Unknown")
        data_source = "Fallback (confirmat 2024)"
    else:
        raise HTTPException(status_code=404, detail=f"Acțiunea {symbol} nu are date despre dividende")
    
    if current_price <= 0:
        raise HTTPException(status_code=404, detail=f"Nu am putut obține prețul pentru {symbol}")
    
    div_yield = (dividend_per_share / current_price * 100)
    
    # Calculate for 100 shares example
    example_shares = 100
    annual_dividend = example_shares * dividend_per_share
    net_dividend = annual_dividend * 0.84
    
    return {
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "current_price": round(current_price, 2),
        "dividend_data": {
            "per_share": round(dividend_per_share, 4),
            "yield": round(div_yield, 2),
            "ex_date": fallback.get("ex_date_estimate"),
            "payment_date": fallback.get("payment_date_estimate"),
        },
        "example_calculation": {
            "shares": example_shares,
            "investment": round(example_shares * current_price, 2),
            "annual_dividend_gross": round(annual_dividend, 2),
            "annual_dividend_net": round(net_dividend, 2),
            "monthly_income_net": round(net_dividend / 12, 2),
        },
        "note": fallback.get("note"),
        "data_source": data_source
    }


@router.get("/top-yielders")
async def get_top_dividend_yielders(limit: int = Query(default=10, ge=1, le=20)):
    """
    Top acțiuni după dividend yield cu DATE LIVE
    """
    # Reuse the /stocks endpoint logic
    all_stocks = await get_dividend_stocks()
    stocks = all_stocks.get("stocks", [])
    
    return {
        "top_yielders": stocks[:limit],
        "average_yield": round(sum(s["dividend_yield"] for s in stocks) / len(stocks), 2) if stocks else 0,
        "highest_yield": stocks[0] if stocks else None,
        "data_source": "EODHD LIVE + Fallback"
    }


@router.get("/calendar/upcoming")
async def get_upcoming_dividends():
    """
    Calendar cu dividendele estimate pentru următoarele 3 luni
    """
    from datetime import timedelta
    
    today = datetime.now(timezone.utc).date()
    three_months = today + timedelta(days=90)
    
    upcoming = []
    
    for symbol in DIVIDEND_SYMBOLS:
        fallback = DIVIDEND_FALLBACK_2026.get(symbol, {})
        ex_date_str = fallback.get("ex_date_estimate")
        
        if not ex_date_str:
            continue
        
        try:
            ex_date = datetime.strptime(ex_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        
        if today <= ex_date <= three_months:
            # Get live data
            live_data = await fetch_live_dividend_data(symbol)
            current_price = await get_current_price(symbol)
            
            if live_data and live_data.get("dividend_per_share", 0) > 0:
                div_per_share = live_data["dividend_per_share"]
                div_yield = (div_per_share / current_price * 100) if current_price > 0 else 0
            elif fallback.get("dividend_per_share", 0) > 0:
                div_per_share = fallback["dividend_per_share"]
                div_yield = (div_per_share / current_price * 100) if current_price > 0 else 0
            else:
                continue
            
            upcoming.append({
                "symbol": symbol,
                "name": fallback.get("name", symbol),
                "ex_date": ex_date_str,
                "payment_date": fallback.get("payment_date_estimate"),
                "dividend_per_share": round(div_per_share, 4),
                "dividend_yield": round(div_yield, 2),
                "days_until_ex": (ex_date - today).days,
            })
    
    # Sort by ex_date
    upcoming.sort(key=lambda x: x["ex_date"])
    
    return {
        "upcoming": upcoming,
        "count": len(upcoming),
        "period": f"{today.isoformat()} - {three_months.isoformat()}",
        "data_source": "EODHD LIVE + Fallback"
    }
