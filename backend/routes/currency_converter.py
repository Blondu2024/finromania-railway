"""Currency Converter routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime, timezone
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/currency", tags=["currency"])

# Cache for exchange rates
_rates_cache = {
    "rates": {},
    "last_updated": None
}

# Supported currencies with names
CURRENCIES = {
    "RON": {"name": "Leu Românesc", "flag": "🇷🇴"},
    "EUR": {"name": "Euro", "flag": "🇪🇺"},
    "USD": {"name": "Dolar American", "flag": "🇺🇸"},
    "GBP": {"name": "Liră Sterlină", "flag": "🇬🇧"},
    "CHF": {"name": "Franc Elvețian", "flag": "🇨🇭"},
    "BGN": {"name": "Leva Bulgărească", "flag": "🇧🇬"},
    "HUF": {"name": "Forint Maghiar", "flag": "🇭🇺"},
    "PLN": {"name": "Zlot Polonez", "flag": "🇵🇱"},
    "CZK": {"name": "Coroană Cehă", "flag": "🇨🇿"},
    "RUB": {"name": "Rublă Rusească", "flag": "🇷🇺"},
    "UAH": {"name": "Grivnă Ucraineană", "flag": "🇺🇦"},
    "MDL": {"name": "Leu Moldovenesc", "flag": "🇲🇩"},
    "TRY": {"name": "Liră Turcească", "flag": "🇹🇷"},
    "JPY": {"name": "Yen Japonez", "flag": "🇯🇵"},
    "CNY": {"name": "Yuan Chinezesc", "flag": "🇨🇳"},
    "AUD": {"name": "Dolar Australian", "flag": "🇦🇺"},
    "CAD": {"name": "Dolar Canadian", "flag": "🇨🇦"},
    "SEK": {"name": "Coroană Suedeză", "flag": "🇸🇪"},
    "NOK": {"name": "Coroană Norvegiană", "flag": "🇳🇴"},
    "DKK": {"name": "Coroană Daneză", "flag": "🇩🇰"},
    "INR": {"name": "Rupie Indiană", "flag": "🇮🇳"},
    "BRL": {"name": "Real Brazilian", "flag": "🇧🇷"},
    "MXN": {"name": "Peso Mexican", "flag": "🇲🇽"},
    "ZAR": {"name": "Rand Sud-African", "flag": "🇿🇦"},
    "KRW": {"name": "Won Sud-Coreean", "flag": "🇰🇷"},
    "SGD": {"name": "Dolar Singapore", "flag": "🇸🇬"},
    "HKD": {"name": "Dolar Hong Kong", "flag": "🇭🇰"},
    "NZD": {"name": "Dolar Neo-Zeelandez", "flag": "🇳🇿"},
    "AED": {"name": "Dirham Emirate", "flag": "🇦🇪"},
    "SAR": {"name": "Rial Saudit", "flag": "🇸🇦"},
}

async def fetch_exchange_rates() -> Dict:
    """Fetch exchange rates from free API"""
    global _rates_cache
    
    # Check cache (5 minute TTL)
    if _rates_cache["last_updated"]:
        age = (datetime.now(timezone.utc) - _rates_cache["last_updated"]).total_seconds()
        if age < 300 and _rates_cache["rates"]:  # 5 minutes
            return _rates_cache["rates"]
    
    try:
        # Using exchangerate-api.com free tier (no key needed for basic)
        async with httpx.AsyncClient() as client:
            # Fetch rates based on EUR
            response = await client.get(
                "https://api.exchangerate-api.com/v4/latest/EUR",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                _rates_cache["rates"] = data.get("rates", {})
                _rates_cache["last_updated"] = datetime.now(timezone.utc)
                return _rates_cache["rates"]
    except Exception as e:
        logger.error(f"Error fetching exchange rates: {e}")
    
    # Return cached rates if available, even if stale
    if _rates_cache["rates"]:
        return _rates_cache["rates"]
    
    # Fallback rates (approximate)
    return {
        "RON": 4.97, "USD": 1.08, "GBP": 0.86, "CHF": 0.94,
        "BGN": 1.96, "HUF": 395.0, "PLN": 4.32, "CZK": 25.2,
        "RUB": 98.0, "UAH": 44.5, "MDL": 19.2, "TRY": 35.0,
        "JPY": 162.0, "CNY": 7.85, "EUR": 1.0
    }

class ConvertRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

class ConvertResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    result: float
    rate: float
    timestamp: str

@router.get("/rates")
async def get_all_rates(base: str = Query(default="RON")):
    """Get all exchange rates relative to base currency"""
    rates = await fetch_exchange_rates()
    base = base.upper()
    
    if base not in rates and base != "EUR":
        raise HTTPException(status_code=400, detail=f"Valută necunoscută: {base}")
    
    # Convert rates to requested base
    base_rate = rates.get(base, 1.0) if base != "EUR" else 1.0
    
    converted_rates = {}
    for code, rate in rates.items():
        if code in CURRENCIES:
            converted_rates[code] = {
                "code": code,
                "rate": round(rate / base_rate, 6),
                "name": CURRENCIES[code]["name"],
                "flag": CURRENCIES[code]["flag"]
            }
    
    # Add EUR if not present
    if "EUR" not in converted_rates:
        converted_rates["EUR"] = {
            "code": "EUR",
            "rate": round(1.0 / base_rate, 6),
            "name": "Euro",
            "flag": "🇪🇺"
        }
    
    return {
        "base": base,
        "rates": converted_rates,
        "last_updated": _rates_cache.get("last_updated", datetime.now(timezone.utc)).isoformat()
    }

@router.post("/convert")
async def convert_currency(request: ConvertRequest) -> ConvertResponse:
    """Convert amount between currencies"""
    rates = await fetch_exchange_rates()
    
    from_curr = request.from_currency.upper()
    to_curr = request.to_currency.upper()
    
    # Validate currencies
    all_currencies = set(CURRENCIES.keys()) | {"EUR"}
    if from_curr not in all_currencies:
        raise HTTPException(status_code=400, detail=f"Valută sursă necunoscută: {from_curr}")
    if to_curr not in all_currencies:
        raise HTTPException(status_code=400, detail=f"Valută destinație necunoscută: {to_curr}")
    
    # Get rates (relative to EUR)
    from_rate = rates.get(from_curr, 1.0) if from_curr != "EUR" else 1.0
    to_rate = rates.get(to_curr, 1.0) if to_curr != "EUR" else 1.0
    
    # Calculate conversion
    # First convert to EUR, then to target
    amount_in_eur = request.amount / from_rate
    result = amount_in_eur * to_rate
    
    # Direct rate from source to target
    direct_rate = to_rate / from_rate
    
    return ConvertResponse(
        amount=request.amount,
        from_currency=from_curr,
        to_currency=to_curr,
        result=round(result, 2),
        rate=round(direct_rate, 6),
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@router.get("/currencies")
async def list_currencies():
    """List all supported currencies"""
    return {
        "currencies": [
            {"code": code, **info}
            for code, info in CURRENCIES.items()
        ],
        "total": len(CURRENCIES)
    }

@router.get("/popular-pairs")
async def get_popular_pairs():
    """Get popular currency pairs for Romania"""
    rates = await fetch_exchange_rates()
    
    # Popular pairs for Romanian users
    pairs = [
        ("EUR", "RON"),
        ("USD", "RON"),
        ("GBP", "RON"),
        ("CHF", "RON"),
        ("EUR", "USD"),
        ("BGN", "RON"),
        ("HUF", "RON"),
        ("MDL", "RON"),
    ]
    
    result = []
    for from_curr, to_curr in pairs:
        from_rate = rates.get(from_curr, 1.0) if from_curr != "EUR" else 1.0
        to_rate = rates.get(to_curr, 1.0) if to_curr != "EUR" else 1.0
        rate = to_rate / from_rate
        
        result.append({
            "from": from_curr,
            "to": to_curr,
            "rate": round(rate, 4),
            "from_flag": CURRENCIES.get(from_curr, {}).get("flag", ""),
            "to_flag": CURRENCIES.get(to_curr, {}).get("flag", ""),
            "display": f"1 {from_curr} = {round(rate, 4)} {to_curr}"
        })
    
    return {"pairs": result}
