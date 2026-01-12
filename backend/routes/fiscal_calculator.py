"""
Calculator Fiscal România - CORECT conform legislației 2024-2025
Optimizare PF vs PFA vs SRL pentru investiții la bursă
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
# ACTUALIZATE CONFORM LEGISLAȚIEI ÎN VIGOARE
# ============================================

# Salariu minim brut pe economie 2024
SALARIU_MINIM_BRUT = 3700  # RON/lună

# Prag CASS pentru venituri din investiții
# CASS se datorează dacă venitul TOTAL din investiții > 6 salarii minime brute anuale
CASS_PRAG_MINIM = 6 * SALARIU_MINIM_BRUT  # 22.200 RON (baza minimă de calcul)
CASS_PRAG_ANUAL = 6 * SALARIU_MINIM_BRUT * 12  # ~266.400 RON (prag activare)

# === IMPOZITE BVB (Titluri listate în România) ===
# Conform Codului Fiscal actualizat 2024-2025
IMPOZIT_BVB_TERMEN_LUNG = 0.01      # 1% - deținere >= 365 zile
IMPOZIT_BVB_TERMEN_SCURT = 0.03    # 3% - deținere < 365 zile

# === IMPOZITE PIEȚE INTERNAȚIONALE ===
IMPOZIT_INTERNATIONAL = 0.10       # 10% pentru piețe străine (câștig capital)
IMPOZIT_DIVIDENDE_INTERNATIONALE = 0.10  # 10% pentru dividende străine

# === DIVIDENDE ===
IMPOZIT_DIVIDENDE_RO = 0.08        # 8% pentru dividende BVB (reținut la sursă)
IMPOZIT_DIVIDENDE_STRAINE = 0.10   # 10% pentru dividende din străinătate

# Reținere la sursă în alte țări (tratate de evitare a dublei impuneri)
RETINERE_USA = 0.15               # 15% reținere SUA (cu W-8BEN) sau 30% fără
RETINERE_EU_MEDIE = 0.15          # Media UE ~15% (variază pe țară)

# NOTĂ IMPORTANTĂ pentru dividende internaționale:
# - SUA: 15% reținut la sursă (cu W-8BEN), apoi 10% în RO, dar cu credit fiscal
# - UE: Variază, de obicei 15-25%, cu credit fiscal în RO

# === CASS ===
CASS_RATE = 0.10  # 10% CASS pe baza de calcul

# === Micro-întreprindere ===
MICRO_IMPOZIT_CU_ANGAJAT = 0.01    # 1% dacă ai angajat
MICRO_IMPOZIT_FARA_ANGAJAT = 0.03  # 3% fără angajat
MICRO_PLAFON_VENITURI_EUR = 500000  # EUR plafon pentru micro

# === PFA ===
PFA_IMPOZIT_VENIT = 0.10  # 10% impozit pe venit
PFA_CAS = 0.25            # 25% CAS (pensie) - opțional pentru investiții
PFA_CASS = 0.10           # 10% CASS (sănătate)


class TipEntitate(str, Enum):
    PF = "pf"              # Persoană Fizică
    PFA = "pfa"            # Persoană Fizică Autorizată  
    SRL_MICRO = "srl_micro"  # SRL Micro-întreprindere


class TipPiata(str, Enum):
    BVB = "bvb"                    # Bursa de Valori București
    INTERNATIONAL = "international"  # Piețe străine (US, EU, etc.)


class PerioadaDetinere(str, Enum):
    SUB_1_AN = "sub_1_an"      # < 365 zile (impozit 3% BVB)
    PESTE_1_AN = "peste_1_an"  # >= 365 zile (impozit 1% BVB)
    MIXT = "mixt"              # Mix de perioade


class CalculFiscalInput(BaseModel):
    """Input pentru calculul fiscal - adaptat pentru investiții bursiere"""
    castig_capital_anual: float = Field(default=0, ge=0, description="Câștig din vânzarea acțiunilor (RON)")
    dividende_anuale: float = Field(default=0, ge=0, description="Dividende primite (RON)")
    tip_piata: TipPiata = Field(default=TipPiata.BVB, description="BVB sau Internațional")
    perioada_detinere: PerioadaDetinere = Field(default=PerioadaDetinere.MIXT, description="Perioada medie de deținere")
    procent_termen_lung: float = Field(default=50, ge=0, le=100, description="% din câștig pe termen lung (>=1 an)")
    are_alte_venituri_cass: bool = Field(default=True, description="Are salariu sau alte venituri cu CASS plătit")
    are_angajat_srl: bool = Field(default=False, description="SRL-ul are cel puțin un angajat")


class ScenariuFiscal(BaseModel):
    """Rezultatul pentru un scenariu fiscal"""
    tip_entitate: str
    nume_entitate: str
    venit_brut: float
    impozit_castig_capital: float
    impozit_dividende: float
    cass: float
    cas: float
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
    nota_legala: str


# ============================================
# FUNCȚII DE CALCUL - CONFORM LEGISLAȚIEI
# ============================================

def calcul_pf_bvb(input_data: CalculFiscalInput) -> ScenariuFiscal:
    """
    Calculează impozitele pentru Persoană Fizică - Investiții BVB
    
    LEGISLAȚIE 2024-2025:
    - Câștig capital BVB: 1% (>=1 an) sau 3% (<1 an) - reținut la sursă
    - Dividende: 8% - reținut la sursă
    - CASS: 10% dacă venit total > 6 salarii minime și NU ai alte surse CASS
    """
    castig = input_data.castig_capital_anual
    dividende = input_data.dividende_anuale
    venit_total = castig + dividende
    
    # === IMPOZIT PE CÂȘTIG DE CAPITAL ===
    if input_data.tip_piata == TipPiata.BVB:
        if input_data.perioada_detinere == PerioadaDetinere.PESTE_1_AN:
            impozit_castig = castig * IMPOZIT_BVB_TERMEN_LUNG
            nota_castig = f"1% (deținere ≥1 an): {impozit_castig:,.0f} RON"
        elif input_data.perioada_detinere == PerioadaDetinere.SUB_1_AN:
            impozit_castig = castig * IMPOZIT_BVB_TERMEN_SCURT
            nota_castig = f"3% (deținere <1 an): {impozit_castig:,.0f} RON"
        else:  # MIXT
            castig_lung = castig * (input_data.procent_termen_lung / 100)
            castig_scurt = castig - castig_lung
            impozit_castig = (castig_lung * IMPOZIT_BVB_TERMEN_LUNG + 
                            castig_scurt * IMPOZIT_BVB_TERMEN_SCURT)
            nota_castig = f"Mixt: {castig_lung:,.0f} RON × 1% + {castig_scurt:,.0f} RON × 3% = {impozit_castig:,.0f} RON"
    else:
        # Piețe internaționale: 10%
        impozit_castig = castig * IMPOZIT_INTERNATIONAL
        nota_castig = f"10% (piețe internaționale): {impozit_castig:,.0f} RON"
    
    # === IMPOZIT PE DIVIDENDE ===
    impozit_div = dividende * IMPOZIT_DIVIDENDE_RO
    nota_div = f"8% reținut la sursă: {impozit_div:,.0f} RON"
    
    # === CASS ===
    cass = 0
    nota_cass = ""
    
    if not input_data.are_alte_venituri_cass:
        # Trebuie să plătești CASS dacă nu ai alte surse de venit
        if venit_total > CASS_PRAG_MINIM:
            # Baza de calcul CASS = minim 6 salarii minime, maxim venitul real
            baza_cass = max(CASS_PRAG_MINIM, min(venit_total, CASS_PRAG_MINIM * 4))
            cass = baza_cass * CASS_RATE
            nota_cass = f"CASS 10% pe baza de {baza_cass:,.0f} RON = {cass:,.0f} RON"
        else:
            nota_cass = f"CASS: 0 RON (venit sub pragul de {CASS_PRAG_MINIM:,.0f} RON)"
    else:
        nota_cass = "CASS: 0 RON (plătit din salariu/alte venituri)"
    
    total_taxe = impozit_castig + impozit_div + cass
    venit_net = venit_total - total_taxe
    rata_efectiva = (total_taxe / venit_total * 100) if venit_total > 0 else 0
    
    detalii = [
        f"Câștig capital: {castig:,.0f} RON",
        f"Dividende: {dividende:,.0f} RON",
        f"Impozit câștig capital: {nota_castig}",
        f"Impozit dividende: {nota_div}",
        nota_cass
    ]
    
    avantaje = [
        "✅ Impozit foarte mic pe BVB: 1-3%",
        "✅ Reținere la sursă (broker-ul plătește)",
        "✅ Fără contabilitate sau declarații complexe",
        "✅ Ideal pentru investitori pasivi"
    ]
    
    dezavantaje = [
        "❌ Nu poți compensa pierderile cu câștigurile",
        "❌ CASS obligatoriu dacă nu ai salariu",
        "❌ Nu poți deduce nicio cheltuială"
    ]
    
    return ScenariuFiscal(
        tip_entitate="pf",
        nume_entitate="Persoană Fizică (BVB)",
        venit_brut=venit_total,
        impozit_castig_capital=impozit_castig,
        impozit_dividende=impozit_div,
        cass=cass,
        cas=0,
        alte_taxe=0,
        total_taxe=total_taxe,
        venit_net=venit_net,
        rata_efectiva_impozitare=rata_efectiva,
        detalii=detalii,
        avantaje=avantaje,
        dezavantaje=dezavantaje
    )


def calcul_pf_international(input_data: CalculFiscalInput) -> ScenariuFiscal:
    """
    Calculează impozitele pentru Persoană Fizică - Investiții INTERNAȚIONALE
    
    LEGISLAȚIE 2024-2025 pentru piețe străine:
    - Câștig capital: 10% (indiferent de perioadă)
    - Dividende: 10% în România + reținere la sursă în țara emitentului
    - Pierderile se pot compensa până la 70% din câștiguri
    - CASS: 10% dacă venit total > 6 salarii minime și NU ai alte surse CASS
    - Trebuie declarat în Declarația Unică (formularul 212)
    """
    castig = input_data.castig_capital_anual
    dividende = input_data.dividende_anuale
    venit_total = castig + dividende
    
    # === IMPOZIT PE CÂȘTIG DE CAPITAL ===
    # 10% indiferent de perioada de deținere
    impozit_castig = castig * IMPOZIT_INTERNATIONAL
    nota_castig = f"10% câștig capital: {impozit_castig:,.0f} RON"
    
    # === IMPOZIT PE DIVIDENDE INTERNAȚIONALE ===
    # Reținere la sursă în țara emitentului + impozit în RO
    # Cu tratate de evitare a dublei impuneri, se acordă credit fiscal
    
    # Exemplu SUA cu W-8BEN: 15% reținut în SUA
    retinere_sursa = dividende * RETINERE_USA
    
    # În România se datorează 10%, dar se scade ce s-a plătit în străinătate (credit fiscal)
    # Dacă s-a reținut 15% în SUA, nu mai datorezi nimic în RO (15% > 10%)
    impozit_div_ro = max(0, dividende * IMPOZIT_DIVIDENDE_STRAINE - retinere_sursa)
    impozit_div_total = retinere_sursa + impozit_div_ro
    
    nota_div = f"Dividende: {retinere_sursa:,.0f} RON reținut la sursă (15% SUA)"
    if impozit_div_ro > 0:
        nota_div += f" + {impozit_div_ro:,.0f} RON în RO"
    else:
        nota_div += " (credit fiscal acoperă impozitul RO)"
    
    # === CASS ===
    cass = 0
    nota_cass = ""
    
    if not input_data.are_alte_venituri_cass:
        if venit_total > CASS_PRAG_MINIM:
            baza_cass = max(CASS_PRAG_MINIM, min(venit_total, CASS_PRAG_MINIM * 4))
            cass = baza_cass * CASS_RATE
            nota_cass = f"CASS 10% pe baza de {baza_cass:,.0f} RON = {cass:,.0f} RON"
        else:
            nota_cass = f"CASS: 0 RON (venit sub pragul de {CASS_PRAG_MINIM:,.0f} RON)"
    else:
        nota_cass = "CASS: 0 RON (plătit din salariu/alte venituri)"
    
    total_taxe = impozit_castig + impozit_div_total + cass
    venit_net = venit_total - total_taxe
    rata_efectiva = (total_taxe / venit_total * 100) if venit_total > 0 else 0
    
    detalii = [
        f"Câștig capital: {castig:,.0f} RON",
        f"Dividende brute: {dividende:,.0f} RON",
        f"Impozit câștig capital: {nota_castig}",
        nota_div,
        nota_cass,
        "📋 Trebuie completată Declarația Unică (212)"
    ]
    
    avantaje = [
        "✅ Acces la mii de companii globale",
        "✅ Diversificare geografică",
        "✅ Pierderile se pot compensa (70%)",
        "✅ ETF-uri cu costuri mici",
        "✅ Credit fiscal pentru dividende (tratate)"
    ]
    
    dezavantaje = [
        "❌ Impozit 10% vs 1-3% pe BVB",
        "❌ Trebuie să completezi Declarația Unică",
        "❌ Calcul manual al impozitului",
        "❌ Complexitate cu reținerea la sursă",
        "❌ Risc valutar (USD/EUR)"
    ]
    
    return ScenariuFiscal(
        tip_entitate="pf_international",
        nume_entitate="Persoană Fizică (Piețe Internaționale)",
        venit_brut=venit_total,
        impozit_castig_capital=impozit_castig,
        impozit_dividende=impozit_div_total,
        cass=cass,
        cas=0,
        alte_taxe=0,
        total_taxe=total_taxe,
        venit_net=venit_net,
        rata_efectiva_impozitare=rata_efectiva,
        detalii=detalii,
        avantaje=avantaje,
        dezavantaje=dezavantaje
    )


def calcul_pfa_investitii(input_data: CalculFiscalInput) -> ScenariuFiscal:
    """
    Calculează pentru PFA - NU este recomandat pentru investiții pure!
    PFA-ul are sens doar dacă faci trading activ ca activitate principală.
    """
    venit_total = input_data.castig_capital_anual + input_data.dividende_anuale
    
    # PFA plătește 10% impozit pe venit
    impozit_venit = venit_total * PFA_IMPOZIT_VENIT
    
    # CAS obligatoriu (25%) - bază minim 12 salarii minime
    baza_cas = max(12 * SALARIU_MINIM_BRUT, min(venit_total, 24 * SALARIU_MINIM_BRUT))
    cas = baza_cas * PFA_CAS
    
    # CASS obligatoriu (10%)
    baza_cass = max(6 * SALARIU_MINIM_BRUT, min(venit_total, 24 * SALARIU_MINIM_BRUT))
    cass = baza_cass * PFA_CASS
    
    # Costuri administrative
    costuri_admin = 3600  # ~300 RON/lună contabilitate
    
    total_taxe = impozit_venit + cas + cass + costuri_admin
    venit_net = venit_total - total_taxe
    rata_efectiva = (total_taxe / venit_total * 100) if venit_total > 0 else 0
    
    detalii = [
        f"Impozit venit (10%): {impozit_venit:,.0f} RON",
        f"CAS pensie (25%): {cas:,.0f} RON",
        f"CASS sănătate (10%): {cass:,.0f} RON",
        f"Costuri contabilitate: {costuri_admin:,.0f} RON/an"
    ]
    
    avantaje = [
        "✅ Contribuții la pensie (CAS)",
        "✅ Poți deduce cheltuieli (software, cursuri)",
        "✅ Stagiu de cotizare pentru pensie"
    ]
    
    dezavantaje = [
        "❌ CAS+CASS obligatorii (~35% din bază)",
        "❌ Impozit 10% vs 1-3% ca PF pe BVB",
        "❌ Contabilitate lunară obligatorie",
        "❌ NU are sens pentru investiții pasive!",
        "❌ Răspundere cu patrimoniul personal"
    ]
    
    return ScenariuFiscal(
        tip_entitate="pfa",
        nume_entitate="PFA (NU recomandat pentru investiții)",
        venit_brut=venit_total,
        impozit_castig_capital=impozit_venit,
        impozit_dividende=0,
        cass=cass,
        cas=cas,
        alte_taxe=costuri_admin,
        total_taxe=total_taxe,
        venit_net=venit_net,
        rata_efectiva_impozitare=rata_efectiva,
        detalii=detalii,
        avantaje=avantaje,
        dezavantaje=dezavantaje
    )


def calcul_srl_micro_investitii(input_data: CalculFiscalInput) -> ScenariuFiscal:
    """
    Calculează pentru SRL Micro - poate avea sens pentru sume FOARTE mari
    sau dacă vrei să reinvestești profitul fără să retragi.
    """
    venit_total = input_data.castig_capital_anual + input_data.dividende_anuale
    
    # Rata impozit micro
    if input_data.are_angajat_srl:
        rata_micro = MICRO_IMPOZIT_CU_ANGAJAT
        tip_micro = "1% (cu angajat)"
    else:
        rata_micro = MICRO_IMPOZIT_FARA_ANGAJAT
        tip_micro = "3% (fără angajat)"
    
    # Impozit pe venit micro
    impozit_micro = venit_total * rata_micro
    
    # Profit disponibil pentru dividende
    profit_dupa_impozit = venit_total - impozit_micro
    
    # Impozit dividende la retragere (8%)
    impozit_div = profit_dupa_impozit * IMPOZIT_DIVIDENDE_RO
    
    # Costuri administrative SRL
    costuri_admin = 8000  # ~650 RON/lună contabilitate + taxe diverse
    
    total_taxe = impozit_micro + impozit_div + costuri_admin
    venit_net = venit_total - total_taxe
    rata_efectiva = ((impozit_micro + impozit_div) / venit_total * 100) if venit_total > 0 else 0
    
    detalii = [
        f"Impozit micro ({tip_micro}): {impozit_micro:,.0f} RON",
        f"Profit după impozit: {profit_dupa_impozit:,.0f} RON",
        f"Impozit dividende la retragere (8%): {impozit_div:,.0f} RON",
        f"Costuri admin estimate: {costuri_admin:,.0f} RON/an",
        f"Impozitare totală: {rata_efectiva:.1f}%"
    ]
    
    avantaje = [
        "✅ Răspundere limitată la capitalul social",
        "✅ Poți lăsa profitul în firmă (fără 8%)",
        "✅ Credibilitate în business",
        "✅ Poți deduce toate cheltuielile"
    ]
    
    dezavantaje = [
        f"❌ Impozitare totală ~{rata_efectiva:.0f}% vs 1-3% ca PF",
        "❌ Costuri înființare (~2000 RON)",
        "❌ Contabilitate obligatorie lunară",
        "❌ Declarații fiscale multiple",
        "❌ NU are sens pentru investiții pe BVB!"
    ]
    
    return ScenariuFiscal(
        tip_entitate="srl_micro",
        nume_entitate=f"SRL Micro ({tip_micro})",
        venit_brut=venit_total,
        impozit_castig_capital=impozit_micro,
        impozit_dividende=impozit_div,
        cass=0,
        cas=0,
        alte_taxe=costuri_admin,
        total_taxe=total_taxe,
        venit_net=venit_net,
        rata_efectiva_impozitare=rata_efectiva,
        detalii=detalii,
        avantaje=avantaje,
        dezavantaje=dezavantaje
    )


def genereaza_recomandare(scenarii: List[ScenariuFiscal], input_data: CalculFiscalInput) -> tuple:
    """Generează recomandarea bazată pe legislația română"""
    
    venit = input_data.castig_capital_anual + input_data.dividende_anuale
    
    # Găsește cel mai avantajos
    cel_mai_bun = max(scenarii, key=lambda x: x.venit_net)
    cel_mai_rau = min(scenarii, key=lambda x: x.venit_net)
    economie = cel_mai_bun.venit_net - cel_mai_rau.venit_net
    
    # Pentru BVB, PF este APROAPE ÎNTOTDEAUNA cel mai avantajos
    if input_data.tip_piata == TipPiata.BVB:
        explicatie = f"""
### 🏆 CONCLUZIE PENTRU INVESTIȚII PE BVB:

**Persoană Fizică este aproape întotdeauna cea mai bună opțiune!**

De ce? Legislația română oferă un regim fiscal FOARTE avantajos pentru investitorii pe BVB:

| Situație | Impozit |
|----------|---------|
| Deținere ≥ 1 an | **1%** |
| Deținere < 1 an | **3%** |
| Dividende | **8%** (reținut la sursă) |

**Comparativ:**
- PFA: ~35-45% (impozit + CAS + CASS)
- SRL Micro: ~9-11% + costuri administrative

**Economie folosind PF:** până la **{economie:,.0f} RON/an**

⚠️ **CASS**: Dacă NU ai salariu și câștigurile depășesc {CASS_PRAG_MINIM:,.0f} RON/an, 
vei datora CASS (10% din baza de calcul).

📋 **Ce trebuie să faci:**
1. Broker-ul reține automat impozitul pe câștig (1% sau 3%)
2. Companiile rețin 8% din dividende
3. Completezi Declarația Unică (212) până în mai pentru CASS (dacă e cazul)
"""
    else:  # INTERNATIONAL
        # Comparație BVB vs International
        pf_bvb_ipotetic = input_data.castig_capital_anual * 0.02  # Media 2% pentru BVB
        pf_int = input_data.castig_capital_anual * 0.10  # 10% international
        diferenta_bvb_int = pf_int - pf_bvb_ipotetic
        
        explicatie = f"""
### 🌍 CONCLUZIE PENTRU INVESTIȚII INTERNAȚIONALE:

**Impozitarea este mai mare decât pe BVB, dar încă rezonabilă.**

| Piață | Impozit Câștig | Impozit Dividende |
|-------|----------------|-------------------|
| 🇷🇴 BVB | **1-3%** | 8% |
| 🇺🇸 USA | **10%** | 15% (reținut) + credit fiscal |
| 🇪🇺 UE | **10%** | 10-25% (variază) |

**Calculul tău:**
- Câștig capital: {input_data.castig_capital_anual:,.0f} RON × 10% = **{input_data.castig_capital_anual * 0.10:,.0f} RON**
- Dividende: {input_data.dividende_anuale:,.0f} RON × ~15% = **{input_data.dividende_anuale * 0.15:,.0f} RON** (reținut în SUA)

**💡 Comparație cu BVB:**
Dacă ai investi aceeași sumă pe BVB, ai plăti ~**{diferenta_bvb_int:,.0f} RON mai puțin** impozit pe câștiguri!

📋 **Ce trebuie să faci:**
1. Completează formularul **W-8BEN** la broker (reduce impozitul SUA de la 30% la 15%)
2. Depune **Declarația Unică (212)** până în mai
3. Calculează și plătește diferența de impozit
4. Păstrează toate rapoartele de la broker

⚠️ **CASS**: Se aplică la fel ca pentru BVB dacă nu ai salariu.
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
    Calculează și compară scenariile fiscale pentru investiții.
    ACTUALIZAT conform legislației române 2024-2025.
    """
    db = await get_database()
    
    # Verifică dacă user-ul are PRO (comentat pentru testare)
    # user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    # subscription_level = user_data.get("subscription_level", "free") if user_data else "free"
    # if subscription_level != "pro":
    #     raise HTTPException(status_code=403, detail="PRO required")
    
    # Calculează scenariile bazate pe piața selectată
    if input_data.tip_piata == TipPiata.BVB:
        scenarii = [
            calcul_pf_bvb(input_data),
            calcul_pfa_investitii(input_data),
            calcul_srl_micro_investitii(input_data)
        ]
    else:  # INTERNATIONAL
        scenarii = [
            calcul_pf_international(input_data),
            calcul_pfa_investitii(input_data),
            calcul_srl_micro_investitii(input_data)
        ]
    
    # Generează recomandare
    cel_mai_bun, economie, explicatie = genereaza_recomandare(scenarii, input_data)
    
    venit_total = input_data.castig_capital_anual + input_data.dividende_anuale
    
    # Salvează în istoric
    await db.fiscal_calculations.insert_one({
        "user_id": user["user_id"],
        "castig_capital": input_data.castig_capital_anual,
        "dividende": input_data.dividende_anuale,
        "tip_piata": input_data.tip_piata,
        "recomandare": cel_mai_bun,
        "economie": economie,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return ComparatieFiscala(
        venit_brut_anual=venit_total,
        scenarii=scenarii,
        recomandare=f"Pentru investiții pe BVB, {cel_mai_bun.upper()} este recomandat.",
        economie_maxima=economie,
        cel_mai_avantajos=cel_mai_bun,
        explicatie_detaliata=explicatie,
        nota_legala="⚠️ Aceste calcule sunt orientative. Legislația fiscală se poate modifica. Consultă un contabil autorizat pentru situația ta specifică."
    )


@router.get("/constante")
async def get_constante_fiscale():
    """Returnează constantele fiscale actuale pentru BVB (public)"""
    return {
        "an_fiscal": "2024-2025",
        "ultima_actualizare": "Ianuarie 2025",
        "salariu_minim_brut": SALARIU_MINIM_BRUT,
        "bvb": {
            "castig_capital_termen_lung": "1% (deținere ≥ 365 zile)",
            "castig_capital_termen_scurt": "3% (deținere < 365 zile)",
            "dividende": "8% (reținut la sursă)",
            "nota": "Impozitul este reținut automat de broker"
        },
        "international": {
            "castig_capital": "10%",
            "nota": "Trebuie declarat în Declarația Unică"
        },
        "cass": {
            "rata": "10%",
            "prag_activare": f"{CASS_PRAG_MINIM:,} RON/an",
            "nota": "Se datorează doar dacă NU ai alte venituri cu CASS (ex: salariu)"
        },
        "micro_srl": {
            "cu_angajat": "1%",
            "fara_angajat": "3%",
            "plafon_venituri_eur": MICRO_PLAFON_VENITURI_EUR
        },
        "pfa": {
            "impozit_venit": "10%",
            "cas": "25%",
            "cass": "10%"
        },
        "disclaimer": "Valorile sunt orientative conform legislației în vigoare. Consultați un contabil pentru situația dumneavoastră specifică."
    }


@router.get("/preview")
async def get_preview_calcul(
    castig: float = 50000,
    dividende: float = 10000,
    are_salariu: bool = True
):
    """
    Preview rapid pentru homepage (public)
    Arată economiile posibile între PF și alte forme
    """
    input_data = CalculFiscalInput(
        castig_capital_anual=castig,
        dividende_anuale=dividende,
        tip_piata=TipPiata.BVB,
        perioada_detinere=PerioadaDetinere.MIXT,
        procent_termen_lung=50,
        are_alte_venituri_cass=are_salariu,
        are_angajat_srl=False
    )
    
    pf = calcul_pf_bvb(input_data)
    srl = calcul_srl_micro_investitii(input_data)
    
    economie = pf.venit_net - srl.venit_net
    
    return {
        "castig_capital": castig,
        "dividende": dividende,
        "venit_total": castig + dividende,
        "comparatie": {
            "pf_bvb": {
                "venit_net": round(pf.venit_net),
                "total_taxe": round(pf.total_taxe),
                "rata_impozitare": f"{pf.rata_efectiva_impozitare:.1f}%",
                "detalii": "1-3% câștig + 8% dividende"
            },
            "srl_micro": {
                "venit_net": round(srl.venit_net),
                "total_taxe": round(srl.total_taxe),
                "rata_impozitare": f"{srl.rata_efectiva_impozitare:.1f}%",
                "detalii": "3% micro + 8% dividende + costuri admin"
            }
        },
        "economie_pf_vs_srl": round(economie) if economie > 0 else 0,
        "concluzie": "Pentru investiții pe BVB, Persoana Fizică este aproape întotdeauna mai avantajoasă!",
        "mesaj_principal": f"Ca PF, plătești doar {pf.rata_efectiva_impozitare:.1f}% taxe pe BVB!",
        "is_preview": True
    }
