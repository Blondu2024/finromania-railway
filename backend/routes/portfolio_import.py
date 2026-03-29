"""
Portfolio Import - Parsează CSV-uri de la brokeri cu GPT-4o și calculează taxe
Suportă: XTB, Plus500, Trading 212, Interactive Brokers, Revolut, eToro, etc.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import os
import json
import logging
from routes.auth import require_auth
from utils.llm import LlmChat, UserMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio-import", tags=["portfolio-import"])

# Tax constants 2026
IMPOZIT_BVB_LUNG = 0.03
IMPOZIT_BVB_SCURT = 0.06
IMPOZIT_INTERNATIONAL = 0.16
IMPOZIT_DIVIDENDE = 0.16
CASS_RATE = 0.10
SALARIU_MINIM = 4050
CASS_PRAG_6 = 6 * SALARIU_MINIM
CASS_PRAG_12 = 12 * SALARIU_MINIM
CASS_PRAG_24 = 24 * SALARIU_MINIM

PARSE_SYSTEM_PROMPT = """Ești un parser de tranzacții bursiere. Primești un CSV sau text copiat dintr-un raport de broker.

Extrage TOATE tranzacțiile și returnează un JSON VALID (fără markdown, fără explicații, DOAR JSON):

{
  "broker": "numele brokerului detectat sau 'necunoscut'",
  "market": "bvb" sau "international",
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "symbol": "SIMBOL",
      "action": "buy" sau "sell",
      "quantity": numar,
      "price": numar,
      "currency": "RON" sau "USD" sau "EUR",
      "commission": numar sau 0,
      "profit_loss": numar sau null
    }
  ],
  "dividends": [
    {
      "date": "YYYY-MM-DD",
      "symbol": "SIMBOL",
      "amount": numar,
      "currency": "RON" sau "USD" sau "EUR",
      "withholding_tax": numar sau 0
    }
  ]
}

Reguli:
- Dacă brokerul raportează P/L direct, pune-l în profit_loss
- Dacă nu, lasă profit_loss: null (se va calcula din buy/sell)
- Detectează automat brokerul din format (XTB, Plus500, Trading 212, IBKR, Revolut, eToro, Tradeville)
- BVB stocks: simboluri ca TLV, BRD, SNP, SNG, H2O → market: "bvb"
- International stocks: AAPL, MSFT, TSLA, etc. → market: "international"
- Returnează DOAR JSON valid, nimic altceva"""


class PortfolioImportInput(BaseModel):
    csv_text: str = Field(..., description="CSV sau text copiat din raportul brokerului")
    year: int = Field(default=2025, description="Anul fiscal pentru calcul")
    has_salary: bool = Field(default=True, description="Are salariu cu CASS plătit")


class TaxReport(BaseModel):
    broker: str
    market: str
    year: int
    # Tranzacții parsate
    total_transactions: int
    total_dividends: int
    # Câștiguri/pierderi
    total_gains: float
    total_losses: float
    net_gain: float
    total_dividend_income: float
    # Taxe calculate
    capital_gains_tax: float
    dividend_tax: float
    cass_amount: float
    total_tax: float
    effective_rate: float
    # Detalii
    tax_breakdown: List[dict]
    recommendations: List[str]
    ai_summary: str
    disclaimer: str


def calculate_taxes(parsed_data: dict, year: int, has_salary: bool) -> dict:
    """Calculează taxele pe baza tranzacțiilor parsate"""
    market = parsed_data.get("market", "international")
    transactions = parsed_data.get("transactions", [])
    dividends = parsed_data.get("dividends", [])

    # Calculate capital gains
    total_gains = 0
    total_losses = 0
    breakdown = []

    # If broker provides P/L directly
    for tx in transactions:
        if tx.get("action") == "sell" and tx.get("profit_loss") is not None:
            pl = tx["profit_loss"]
            if pl >= 0:
                total_gains += pl
            else:
                total_losses += abs(pl)
            breakdown.append({
                "date": tx.get("date"),
                "symbol": tx.get("symbol"),
                "type": "sell",
                "profit_loss": pl,
            })

    # If no P/L provided, try to match buy/sell pairs
    if not any(tx.get("profit_loss") is not None for tx in transactions if tx.get("action") == "sell"):
        # Simple FIFO matching
        buys = {}
        for tx in sorted(transactions, key=lambda x: x.get("date", "")):
            sym = tx.get("symbol")
            if tx.get("action") == "buy":
                if sym not in buys:
                    buys[sym] = []
                buys[sym].append(tx)
            elif tx.get("action") == "sell" and sym in buys and buys[sym]:
                buy = buys[sym].pop(0)
                pl = (tx["price"] - buy["price"]) * tx["quantity"] - (tx.get("commission", 0) + buy.get("commission", 0))
                if pl >= 0:
                    total_gains += pl
                else:
                    total_losses += abs(pl)
                breakdown.append({
                    "date": tx.get("date"),
                    "symbol": sym,
                    "type": "sell",
                    "buy_price": buy["price"],
                    "sell_price": tx["price"],
                    "quantity": tx["quantity"],
                    "profit_loss": round(pl, 2),
                })

    net_gain = total_gains - total_losses

    # Capital gains tax
    if market == "bvb":
        # BVB: per transaction, no loss compensation
        # Simplified: assume mix of long/short term
        capital_gains_tax = total_gains * 0.045  # Average 4.5% (mix 3%/6%)
    else:
        # International: 16% on net gain, losses compensable up to 70%
        compensable_loss = min(total_losses, total_gains * 0.70)
        taxable_gain = max(0, total_gains - compensable_loss)
        capital_gains_tax = taxable_gain * IMPOZIT_INTERNATIONAL

    # Dividends
    total_dividend_income = sum(d.get("amount", 0) for d in dividends)
    foreign_tax_paid = sum(d.get("withholding_tax", 0) for d in dividends)

    if market == "bvb":
        dividend_tax = total_dividend_income * IMPOZIT_DIVIDENDE
    else:
        # Credit fiscal - reduce Romanian tax by foreign tax paid
        ro_tax_due = total_dividend_income * IMPOZIT_DIVIDENDE
        dividend_tax = max(0, ro_tax_due - foreign_tax_paid)

    for d in dividends:
        breakdown.append({
            "date": d.get("date"),
            "symbol": d.get("symbol"),
            "type": "dividend",
            "amount": d.get("amount"),
            "withholding_tax": d.get("withholding_tax", 0),
        })

    # CASS
    total_investment_income = max(0, net_gain) + total_dividend_income
    cass_amount = 0
    if total_investment_income > CASS_PRAG_6:
        if total_investment_income <= CASS_PRAG_12:
            cass_base = CASS_PRAG_6
        elif total_investment_income <= CASS_PRAG_24:
            cass_base = CASS_PRAG_12
        else:
            cass_base = CASS_PRAG_24
        cass_amount = cass_base * CASS_RATE

    total_tax = round(capital_gains_tax + dividend_tax + cass_amount, 2)
    effective_rate = round(total_tax / total_investment_income * 100, 2) if total_investment_income > 0 else 0

    # Recommendations
    recommendations = []
    if market == "international" and total_losses > 0:
        compensated = min(total_losses, total_gains * 0.70)
        if compensated > 0:
            saved = compensated * IMPOZIT_INTERNATIONAL
            recommendations.append(f"Ai compensat pierderi de {compensated:,.0f} RON cu câștiguri, economisind {saved:,.0f} RON impozit")
        remaining = total_losses - compensated
        if remaining > 0:
            recommendations.append(f"Ai {remaining:,.0f} RON pierderi necompensate - se pot reporta 7 ani")
    if market == "bvb":
        recommendations.append("Pe BVB, brokerul reține impozitul automat. NU trebuie Declarație Unică pentru câștiguri")
    if market == "international":
        recommendations.append("Trebuie să depui Declarația Unică până pe 25 mai pentru câștiguri internaționale")
    if cass_amount > 0:
        recommendations.append(f"Datorezi CASS {cass_amount:,.0f} RON (10% pe baza plafonată). Se declară prin Declarația Unică")
    if total_dividend_income > 0 and market == "international" and foreign_tax_paid > 0:
        recommendations.append(f"Ai beneficiat de credit fiscal de {foreign_tax_paid:,.0f} RON (impozit reținut în străinătate)")

    return {
        "broker": parsed_data.get("broker", "necunoscut"),
        "market": market,
        "year": year,
        "total_transactions": len([t for t in transactions if t.get("action") == "sell"]),
        "total_dividends": len(dividends),
        "total_gains": round(total_gains, 2),
        "total_losses": round(total_losses, 2),
        "net_gain": round(net_gain, 2),
        "total_dividend_income": round(total_dividend_income, 2),
        "capital_gains_tax": round(capital_gains_tax, 2),
        "dividend_tax": round(dividend_tax, 2),
        "cass_amount": round(cass_amount, 2),
        "total_tax": total_tax,
        "effective_rate": effective_rate,
        "tax_breakdown": sorted(breakdown, key=lambda x: x.get("date", "")),
        "recommendations": recommendations,
    }


@router.post("/analyze")
async def analyze_portfolio(data: PortfolioImportInput, user: dict = Depends(require_auth)):
    """
    Parsează CSV de la broker cu GPT-4o și calculează taxele.
    PRO feature.
    """
    if not data.csv_text or len(data.csv_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="CSV-ul este prea scurt sau gol")

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_UNIVERSAL_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Serviciul AI nu este configurat")

    try:
        # Step 1: GPT-4o parsează CSV-ul
        chat = LlmChat(
            api_key=api_key,
            system_message=PARSE_SYSTEM_PROMPT
        ).with_model("openai", "gpt-4o")

        raw_response = await chat.send_message(UserMessage(
            text=f"Parsează acest raport de tranzacții pentru anul {data.year}:\n\n{data.csv_text[:8000]}"
        ))

        # Clean response - remove markdown code blocks if present
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

        parsed_data = json.loads(cleaned)

        # Step 2: Python calculează taxele (deterministic, fără AI)
        tax_result = calculate_taxes(parsed_data, data.year, data.has_salary)

        # Step 3: GPT-4o explică rezultatele
        explain_chat = LlmChat(
            api_key=api_key,
            system_message="Ești un consultant fiscal virtual. Explică în română, simplu și clar, rezultatele fiscale. Max 200 cuvinte. Nu da sfaturi specifice - direcționează către contabil pentru sume mari."
        ).with_model("openai", "gpt-4o")

        summary_prompt = f"""Explică aceste rezultate fiscale pentru anul {data.year}:
- Broker: {tax_result['broker']}
- Piață: {'BVB' if tax_result['market'] == 'bvb' else 'Internațională'}
- Câștiguri: {tax_result['total_gains']:,.0f} RON, Pierderi: {tax_result['total_losses']:,.0f} RON
- Dividende: {tax_result['total_dividend_income']:,.0f} RON
- Impozit câștiguri: {tax_result['capital_gains_tax']:,.0f} RON
- Impozit dividende: {tax_result['dividend_tax']:,.0f} RON
- CASS: {tax_result['cass_amount']:,.0f} RON
- Total taxe: {tax_result['total_tax']:,.0f} RON ({tax_result['effective_rate']:.1f}% rată efectivă)"""

        ai_summary = await explain_chat.send_message(UserMessage(text=summary_prompt))

        tax_result["ai_summary"] = ai_summary
        tax_result["disclaimer"] = "Calculele sunt estimative. Legislația fiscală 2026. Consultă un contabil CECCAR pentru situația ta specifică."

        return {"success": True, "report": tax_result}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise HTTPException(status_code=422, detail="Nu am reușit să parsez raportul. Verifică formatul CSV-ului.")
    except Exception as e:
        logger.error(f"Portfolio import error: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la analiză: {str(e)}")
