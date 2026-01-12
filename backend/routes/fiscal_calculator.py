"""
Calculator Fiscal România - Optimizare PF vs PFA vs SRL
Feature PRO - Diferențiator unic pentru FinRomania
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone
from enum import Enum
import logging
from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fiscal", tags=["fiscal-calculator"])

# ============================================
# CONSTANTE FISCALE ROMÂNIA 2024-2025
# ============================================

# Salariu minim brut pe economie (pentru calcul CASS)
SALARIU_MINIM_BRUT = 3700  # RON, actualizat 2024

# Praguri CASS pentru venituri din investiții (PF)
CASS_PRAG_6_SALARII = 6 * SALARIU_MINIM_BRUT * 12  # ~266,400 RON/an
CASS_PRAG_12_SALARII = 12 * SALARIU_MINIM_BRUT * 12  # ~532,800 RON/an
CASS_PRAG_24_SALARII = 24 * SALARIU_MINIM_BRUT * 12  # ~1,065,600 RON/an

# Rate de impozitare
IMPOZIT_CASTIG_CAPITAL = 0.10  # 10% pe câștiguri de capital
IMPOZIT_DIVIDENDE = 0.08  # 8% pe dividende
CASS_RATE = 0.10  # 10% CASS

# Micro-întreprindere
MICRO_IMPOZIT_CU_ANGAJAT = 0.01  # 1% dacă ai angajat
MICRO_IMPOZIT_FARA_ANGAJAT = 0.03  # 3% fără angajat
MICRO_PLAFON_VENITURI = 500000  # EUR plafon pentru micro

# PFA
PFA_IMPOZIT_VENIT = 0.10  # 10% impozit pe venit
PFA_CAS = 0.25  # 25% CAS (pensie)
PFA_CASS = 0.10  # 10% CASS (sănătate)


class TipEntitate(str, Enum):
    PF = "pf"  # Persoană Fizică
    PFA = "pfa"  # Persoană Fizică Autorizată
    SRL_MICRO = "srl_micro"  # SRL Micro-întreprindere


class TipVenit(str, Enum):
    CASTIG_CAPITAL = "castig_capital"  # Vânzare acțiuni cu profit
    DIVIDENDE = "dividende"  # Dividende primite
    MIXT = "mixt"  # Ambele


class CalculFiscalInput(BaseModel):
    """Input pentru calculul fiscal"""
    venit_brut_anual: float = Field(..., gt=0, description="Venitul brut anual din investiții (RON)")
    tip_venit: TipVenit = Field(default=TipVenit.MIXT)
    procent_dividende: float = Field(default=50, ge=0, le=100, description="% din venit care sunt dividende")
    are_alte_venituri_cass: bool = Field(default=True, description="Are alte venituri cu CASS plătit (ex: salariu)")
    are_angajat_srl: bool = Field(default=False, description="SRL-ul are cel puțin un angajat")
    cheltuieli_deductibile_pfa: float = Field(default=0, description="Cheltuieli deductibile pentru PFA")


class ScenariuFiscal(BaseModel):
    """Rezultatul pentru un scenariu fiscal"""
    tip_entitate: str
    nume_entitate: str
    venit_brut: float
    impozit_venit: float
    cass: float
    cas: float
    impozit_dividende: float
    alte_taxe: float
    total_taxe: float
    venit_net: float
    rata_efectiva_impozitare: float
    detalii: List[str]
    avantaje: List[str]
    dezavantaje: List[str]


class ComparatieFiscala(BaseModel):
    """Rezultatul comparației fiscale"""
    venit_brut_anual: float
    scenarii: List[ScenariuFiscal]
    recomandare: str
    economie_maxima: float
    cel_mai_avantajos: str
    explicatie_detaliata: str


# ============================================
# FUNCȚII DE CALCUL
# ============================================

def calcul_pf(input_data: CalculFiscalInput) -> ScenariuFiscal:
    """Calculează impozitele pentru Persoană Fizică"""
    venit = input_data.venit_brut_anual
    
    # Separare câștig capital vs dividende
    if input_data.tip_venit == TipVenit.DIVIDENDE:
        dividende = venit
        castig_capital = 0
    elif input_data.tip_venit == TipVenit.CASTIG_CAPITAL:
        dividende = 0
        castig_capital = venit
    else:
        dividende = venit * (input_data.procent_dividende / 100)
        castig_capital = venit - dividende
    
    # Impozit pe câștig de capital (10%)
    impozit_castig = castig_capital * IMPOZIT_CASTIG_CAPITAL
    
    # Impozit pe dividende (8%)
    impozit_div = dividende * IMPOZIT_DIVIDENDE
    
    # CASS - depinde de praguri și dacă ai alte venituri
    cass = 0
    detalii_cass = []
    
    if not input_data.are_alte_venituri_cass:
        # Trebuie să plătești CASS dacă nu ai alte surse
        if venit <= CASS_PRAG_6_SALARII:
            cass = 6 * SALARIU_MINIM_BRUT * CASS_RATE
            detalii_cass.append(f"CASS: plafon 6 salarii minime = {cass:,.0f} RON")
        elif venit <= CASS_PRAG_12_SALARII:
            cass = 12 * SALARIU_MINIM_BRUT * CASS_RATE
            detalii_cass.append(f"CASS: plafon 12 salarii minime = {cass:,.0f} RON")
        elif venit <= CASS_PRAG_24_SALARII:
            cass = 24 * SALARIU_MINIM_BRUT * CASS_RATE
            detalii_cass.append(f"CASS: plafon 24 salarii minime = {cass:,.0f} RON")
        else:
            cass = 24 * SALARIU_MINIM_BRUT * CASS_RATE  # Plafonat la 24 salarii
            detalii_cass.append(f"CASS: plafonat la 24 salarii minime = {cass:,.0f} RON")
    else:
        detalii_cass.append("CASS: 0 RON (plătit din alte venituri)")
    
    total_taxe = impozit_castig + impozit_div + cass
    venit_net = venit - total_taxe
    rata_efectiva = (total_taxe / venit * 100) if venit > 0 else 0
    
    detalii = [
        f"Impozit câștig capital (10%): {impozit_castig:,.0f} RON",
        f"Impozit dividende (8%): {impozit_div:,.0f} RON",
        *detalii_cass
    ]
    
    avantaje = [
        "Simplitate maximă - fără contabilitate",
        "Fără costuri administrative",
        "Ideal pentru investitori pasivi",
        "Declarație anuală simplă"
    ]
    
    dezavantaje = [
        "CASS obligatoriu dacă nu ai alte venituri",
        "Nu poți deduce cheltuieli",
        "Impozit fix, fără optimizări"
    ]
    
    return ScenariuFiscal(
        tip_entitate="pf",
        nume_entitate="Persoană Fizică",
        venit_brut=venit,
        impozit_venit=impozit_castig,
        cass=cass,
        cas=0,
        impozit_dividende=impozit_div,
        alte_taxe=0,
        total_taxe=total_taxe,
        venit_net=venit_net,
        rata_efectiva_impozitare=rata_efectiva,
        detalii=detalii,
        avantaje=avantaje,
        dezavantaje=dezavantaje
    )


def calcul_pfa(input_data: CalculFiscalInput) -> ScenariuFiscal:
    """Calculează impozitele pentru PFA"""
    venit = input_data.venit_brut_anual
    cheltuieli = input_data.cheltuieli_deductibile_pfa
    
    # Venit net = venit brut - cheltuieli deductibile
    venit_impozabil = max(0, venit - cheltuieli)
    
    # Impozit pe venit (10%)
    impozit_venit = venit_impozabil * PFA_IMPOZIT_VENIT
    
    # CAS (25%) - plafonat
    # Se calculează pe venitul ales, minim 12 salarii minime
    baza_cas = max(12 * SALARIU_MINIM_BRUT, min(venit_impozabil, 24 * SALARIU_MINIM_BRUT))
    cas = baza_cas * PFA_CAS
    
    # CASS (10%) - plafonat
    baza_cass = max(6 * SALARIU_MINIM_BRUT, min(venit_impozabil, 24 * SALARIU_MINIM_BRUT))
    cass = baza_cass * PFA_CASS
    
    total_taxe = impozit_venit + cas + cass
    venit_net = venit - total_taxe - cheltuieli
    rata_efectiva = (total_taxe / venit * 100) if venit > 0 else 0
    
    detalii = [
        f"Venit brut: {venit:,.0f} RON",
        f"Cheltuieli deductibile: {cheltuieli:,.0f} RON",
        f"Venit impozabil: {venit_impozabil:,.0f} RON",
        f"Impozit venit (10%): {impozit_venit:,.0f} RON",
        f"CAS pensie (25%): {cas:,.0f} RON",
        f"CASS sănătate (10%): {cass:,.0f} RON"
    ]
    
    avantaje = [
        "Poți deduce cheltuieli (soft, cursuri, echipamente)",
        "Contribuții la pensie (CAS)",
        "Mai multă flexibilitate decât PF",
        "Fără capital social minim"
    ]
    
    dezavantaje = [
        "CAS + CASS obligatorii (35% din bază)",
        "Necesită contabilitate",
        "Costuri administrative (~200-500 RON/lună)",
        "Răspundere nelimitată cu patrimoniul personal"
    ]
    
    return ScenariuFiscal(
        tip_entitate="pfa",
        nume_entitate="PFA (Persoană Fizică Autorizată)",
        venit_brut=venit,
        impozit_venit=impozit_venit,
        cass=cass,
        cas=cas,
        impozit_dividende=0,
        alte_taxe=0,
        total_taxe=total_taxe,
        venit_net=venit_net,
        rata_efectiva_impozitare=rata_efectiva,
        detalii=detalii,
        avantaje=avantaje,
        dezavantaje=dezavantaje
    )


def calcul_srl_micro(input_data: CalculFiscalInput) -> ScenariuFiscal:
    """Calculează impozitele pentru SRL Micro-întreprindere"""
    venit = input_data.venit_brut_anual
    
    # Rata impozit micro
    if input_data.are_angajat_srl:
        rata_micro = MICRO_IMPOZIT_CU_ANGAJAT
        tip_micro = "1% (cu angajat)"
    else:
        rata_micro = MICRO_IMPOZIT_FARA_ANGAJAT
        tip_micro = "3% (fără angajat)"
    
    # Impozit pe venit micro
    impozit_micro = venit * rata_micro
    
    # Profit disponibil pentru dividende
    profit_dupa_impozit = venit - impozit_micro
    
    # Impozit dividende la retragere (8%)
    impozit_div = profit_dupa_impozit * IMPOZIT_DIVIDENDE
    
    # Costuri administrative estimate
    costuri_admin = 6000  # ~500 RON/lună contabilitate + diverse
    
    total_taxe = impozit_micro + impozit_div
    venit_net = venit - total_taxe - costuri_admin
    rata_efectiva = (total_taxe / venit * 100) if venit > 0 else 0
    
    detalii = [
        f"Impozit micro ({tip_micro}): {impozit_micro:,.0f} RON",
        f"Profit după impozit: {profit_dupa_impozit:,.0f} RON",
        f"Impozit dividende (8%): {impozit_div:,.0f} RON",
        f"Costuri admin estimate: {costuri_admin:,.0f} RON/an",
        f"Total taxe: {total_taxe:,.0f} RON"
    ]
    
    avantaje = [
        f"Impozit mic pe venit ({tip_micro})",
        "Răspundere limitată la capitalul social",
        "Poți lăsa profitul în firmă pentru reinvestire",
        "Credibilitate mai mare în business",
        "Poți angaja și deduce salarii"
    ]
    
    dezavantaje = [
        "Costuri de înființare (~1000-2000 RON)",
        "Contabilitate obligatorie (~500 RON/lună)",
        "Declarații lunare/trimestriale",
        "Capital social minim 200 RON",
        "8% impozit suplimentar la retragerea dividendelor"
    ]
    
    return ScenariuFiscal(
        tip_entitate="srl_micro",
        nume_entitate=f"SRL Micro ({tip_micro})",
        venit_brut=venit,
        impozit_venit=impozit_micro,
        cass=0,
        cas=0,
        impozit_dividende=impozit_div,
        alte_taxe=costuri_admin,
        total_taxe=total_taxe + costuri_admin,
        venit_net=venit_net,
        rata_efectiva_impozitare=rata_efectiva,
        detalii=detalii,
        avantaje=avantaje,
        dezavantaje=dezavantaje
    )


def genereaza_recomandare(scenarii: List[ScenariuFiscal], venit: float) -> tuple:
    """Generează recomandarea și explicația"""
    
    # Găsește cel mai avantajos
    cel_mai_bun = max(scenarii, key=lambda x: x.venit_net)
    cel_mai_rau = min(scenarii, key=lambda x: x.venit_net)
    economie = cel_mai_bun.venit_net - cel_mai_rau.venit_net
    
    # Generează explicație
    if venit < 50000:
        explicatie = f"""
**Pentru venituri sub 50.000 RON/an:**

Recomandăm **Persoana Fizică** pentru simplitate. La acest nivel de venituri, 
costurile administrative ale unui SRL sau PFA nu se justifică.

Economie față de varianta cea mai scumpă: **{economie:,.0f} RON/an**
"""
    elif venit < 200000:
        explicatie = f"""
**Pentru venituri între 50.000 - 200.000 RON/an:**

Situația depinde de circumstanțele tale:
- **Dacă ai salariu** și plătești deja CASS → PF este simplu și eficient
- **Dacă vrei să deduci cheltuieli** → PFA poate fi avantajos
- **Dacă vrei protecție juridică** → SRL oferă răspundere limitată

Economie maximă posibilă: **{economie:,.0f} RON/an**
"""
    else:
        explicatie = f"""
**Pentru venituri peste 200.000 RON/an:**

La acest nivel, **SRL Micro cu angajat (1%)** devine foarte atractiv:
- Impozit pe venit: doar 1%
- Poți lăsa profitul în firmă pentru reinvestire
- Total impozitare la retragere: ~9% (1% + 8% dividende)

Economie față de PF: **{economie:,.0f} RON/an**

⚠️ Consultă un contabil pentru situația ta specifică!
"""
    
    return cel_mai_bun.tip_entitate, economie, explicatie


# ============================================
# ENDPOINTS
# ============================================

@router.post("/calculeaza", response_model=ComparatieFiscala)
async def calculeaza_impozite(
    input_data: CalculFiscalInput,
    user: dict = Depends(require_auth)
):
    """
    Calculează și compară scenariile fiscale.
    Disponibil DOAR pentru utilizatori PRO.
    """
    db = await get_database()
    
    # Verifică dacă user-ul are PRO
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    subscription_level = user_data.get("subscription_level", "free") if user_data else "free"
    
    # Pentru demo, permitem accesul - în producție, decomentează:
    # if subscription_level != "pro":
    #     raise HTTPException(
    #         status_code=403,
    #         detail={
    #             "error": "pro_required",
    #             "message": "Calculatorul Fiscal este disponibil doar pentru utilizatorii PRO.",
    #             "upgrade_url": "/pricing"
    #         }
    #     )
    
    # Calculează toate scenariile
    scenarii = [
        calcul_pf(input_data),
        calcul_pfa(input_data),
        calcul_srl_micro(input_data)
    ]
    
    # Generează recomandare
    cel_mai_bun, economie, explicatie = genereaza_recomandare(scenarii, input_data.venit_brut_anual)
    
    # Salvează în istoric pentru analytics
    await db.fiscal_calculations.insert_one({
        "user_id": user["user_id"],
        "venit_brut": input_data.venit_brut_anual,
        "tip_venit": input_data.tip_venit,
        "recomandare": cel_mai_bun,
        "economie": economie,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return ComparatieFiscala(
        venit_brut_anual=input_data.venit_brut_anual,
        scenarii=scenarii,
        recomandare=f"Pentru situația ta, {cel_mai_bun.upper()} pare cel mai avantajos.",
        economie_maxima=economie,
        cel_mai_avantajos=cel_mai_bun,
        explicatie_detaliata=explicatie
    )


@router.get("/constante")
async def get_constante_fiscale():
    """Returnează constantele fiscale actuale (public)"""
    return {
        "an_fiscal": 2024,
        "salariu_minim_brut": SALARIU_MINIM_BRUT,
        "impozite": {
            "castig_capital": f"{IMPOZIT_CASTIG_CAPITAL * 100}%",
            "dividende": f"{IMPOZIT_DIVIDENDE * 100}%",
            "cass": f"{CASS_RATE * 100}%"
        },
        "praguri_cass": {
            "6_salarii": CASS_PRAG_6_SALARII,
            "12_salarii": CASS_PRAG_12_SALARII,
            "24_salarii": CASS_PRAG_24_SALARII
        },
        "micro_srl": {
            "cu_angajat": f"{MICRO_IMPOZIT_CU_ANGAJAT * 100}%",
            "fara_angajat": f"{MICRO_IMPOZIT_FARA_ANGAJAT * 100}%",
            "plafon_venituri_eur": MICRO_PLAFON_VENITURI
        },
        "pfa": {
            "impozit_venit": f"{PFA_IMPOZIT_VENIT * 100}%",
            "cas": f"{PFA_CAS * 100}%",
            "cass": f"{PFA_CASS * 100}%"
        },
        "nota": "Valorile sunt orientative. Consultați un contabil pentru situația dumneavoastră specifică."
    }


@router.get("/preview")
async def get_preview_calcul(venit: float = 100000):
    """
    Preview rapid pentru non-utilizatori (simplificat)
    Afișează doar rezultatele, fără detalii complete
    """
    input_data = CalculFiscalInput(
        venit_brut_anual=venit,
        tip_venit=TipVenit.MIXT,
        procent_dividende=50,
        are_alte_venituri_cass=True,
        are_angajat_srl=False
    )
    
    pf = calcul_pf(input_data)
    srl = calcul_srl_micro(input_data)
    
    economie = srl.venit_net - pf.venit_net
    
    return {
        "venit_anual": venit,
        "comparatie_rapida": {
            "pf": {
                "venit_net": round(pf.venit_net),
                "rata_impozitare": f"{pf.rata_efectiva_impozitare:.1f}%"
            },
            "srl_micro": {
                "venit_net": round(srl.venit_net),
                "rata_impozitare": f"{srl.rata_efectiva_impozitare:.1f}%"
            }
        },
        "economie_potentiala": round(economie) if economie > 0 else 0,
        "mesaj": f"Poți economisi până la {abs(economie):,.0f} RON/an cu structura fiscală potrivită!",
        "cta": "Creează cont PRO pentru analiza completă",
        "is_preview": True
    }
