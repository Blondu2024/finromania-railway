"""
Calculator Fiscal Romania - CORECT conform legislatiei 2026
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
# CONSTANTE FISCALE ROMANIA 2026
# ACTUALIZATE CONFORM LEGISLATIEI IN VIGOARE
# Surse: Cod Fiscal 2026, ANAF, goldring.ro
# ============================================

# Salariu minim brut pe economie 2026
# Ian-Iun 2026: 4.050 RON, Iul-Dec 2026: 4.325 RON
# Folosim 4.050 RON ca baza pentru CASS (prima jumatate a anului)
SALARIU_MINIM_BRUT = 4050  # RON/luna (ianuarie-iunie 2026)

# Prag CASS pentru venituri din investitii
# CASS se datoreaza daca venitul TOTAL din investitii > 6 salarii minime brute
# Praguri: 6, 12, 24 salarii minime (baze de calcul CASS)
CASS_PRAG_6 = 6 * SALARIU_MINIM_BRUT   # 24.300 RON
CASS_PRAG_12 = 12 * SALARIU_MINIM_BRUT  # 48.600 RON
CASS_PRAG_24 = 24 * SALARIU_MINIM_BRUT  # 97.200 RON

# === IMPOZITE BVB (Titluri listate in Romania prin brokeri romani) ===
# Conform Codului Fiscal 2026 (in vigoare de la 1 ianuarie 2026)
# Impozitul se retine la sursa de catre broker, per tranzactie
# Pierderile NU se compenseaza cu castigurile
IMPOZIT_BVB_TERMEN_LUNG = 0.03      # 3% - detinere >= 365 zile (2026)
IMPOZIT_BVB_TERMEN_SCURT = 0.06     # 6% - detinere < 365 zile (2026)

# === IMPOZITE PIETE INTERNATIONALE (brokeri nerezidenti) ===
# eToro, Interactive Brokers, etc. - 16% pe castig NET anual
# Castiguri minus pierderi, declarat prin Declaratia Unica
IMPOZIT_INTERNATIONAL = 0.16       # 16% pentru piete straine (2026)

# === DIVIDENDE ===
# Impozit pe dividende 2026: 16% (crescut de la 10% in 2025)
# Retinut la sursa de catre societate
IMPOZIT_DIVIDENDE_RO = 0.16        # 16% pentru dividende romanesti (2026)
IMPOZIT_DIVIDENDE_STRAINE = 0.16   # 16% pentru dividende din strainatate (2026)

# Reținere la sursă în alte țări (tratate de evitare a dublei impuneri)
RETINERE_USA = 0.15               # 15% reținere SUA (cu W-8BEN) sau 30% fără
RETINERE_EU_MEDIE = 0.15          # Media UE ~15% (variază pe țară)

# === CASS ===
CASS_RATE = 0.10  # 10% CASS pe baza de calcul

# === Micro-intreprindere (2026) ===
# Din 2026: 1% pentru toate micro-intreprinderile (cifra afaceri sub 100.000 EUR)
MICRO_IMPOZIT = 0.01                # 1% impozit pe venit
MICRO_PLAFON_VENITURI_EUR = 100000  # EUR plafon pentru micro (2026, redus de la 500.000)

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
    SUB_1_AN = "sub_1_an"      # < 365 zile (impozit 6% BVB 2026)
    PESTE_1_AN = "peste_1_an"  # >= 365 zile (impozit 3% BVB 2026)
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
    Calculeaza impozitele pentru Persoana Fizica - Investitii BVB
    
    LEGISLATIE 2026:
    - Castig capital BVB: 3% (>=1 an) sau 6% (<1 an) - retinut la sursa de broker
    - Dividende: 16% - retinut la sursa
    - CASS: 10% daca venit total > 6 salarii minime (se aplica si salariatilor)
    - Pierderile NU se compenseaza cu castigurile
    """
    castig = input_data.castig_capital_anual
    dividende = input_data.dividende_anuale
    venit_total = castig + dividende
    
    # === IMPOZIT PE CASTIG DE CAPITAL ===
    if input_data.tip_piata == TipPiata.BVB:
        if input_data.perioada_detinere == PerioadaDetinere.PESTE_1_AN:
            impozit_castig = castig * IMPOZIT_BVB_TERMEN_LUNG
            nota_castig = f"3% (detinere >=1 an): {impozit_castig:,.0f} RON"
        elif input_data.perioada_detinere == PerioadaDetinere.SUB_1_AN:
            impozit_castig = castig * IMPOZIT_BVB_TERMEN_SCURT
            nota_castig = f"6% (detinere <1 an): {impozit_castig:,.0f} RON"
        else:  # MIXT
            castig_lung = castig * (input_data.procent_termen_lung / 100)
            castig_scurt = castig - castig_lung
            impozit_castig = (castig_lung * IMPOZIT_BVB_TERMEN_LUNG + 
                            castig_scurt * IMPOZIT_BVB_TERMEN_SCURT)
            nota_castig = f"Mixt: {castig_lung:,.0f} RON x 3% + {castig_scurt:,.0f} RON x 6% = {impozit_castig:,.0f} RON"
    else:
        # Piete internationale: 16% pe castig NET anual
        impozit_castig = castig * IMPOZIT_INTERNATIONAL
        nota_castig = f"16% (piete internationale, castig net anual): {impozit_castig:,.0f} RON"
    
    # === IMPOZIT PE DIVIDENDE ===
    impozit_div = dividende * IMPOZIT_DIVIDENDE_RO
    nota_div = f"16% retinut la sursa (2026): {impozit_div:,.0f} RON"
    
    # === CASS ===
    # CASS se aplica TUTUROR investitorilor (inclusiv salariatilor) pe veniturile din investitii
    # Praguri 2026: 6, 12, 24 salarii minime brute
    cass = 0
    nota_cass = ""
    
    if venit_total <= CASS_PRAG_6:
        nota_cass = f"CASS: 0 RON (venit {venit_total:,.0f} RON sub pragul de {CASS_PRAG_6:,.0f} RON = 6 salarii minime)"
    elif venit_total <= CASS_PRAG_12:
        baza_cass = CASS_PRAG_6
        cass = baza_cass * CASS_RATE
        nota_cass = f"CASS 10% x {baza_cass:,.0f} RON (6 salarii minime) = {cass:,.0f} RON"
    elif venit_total <= CASS_PRAG_24:
        baza_cass = CASS_PRAG_12
        cass = baza_cass * CASS_RATE
        nota_cass = f"CASS 10% x {baza_cass:,.0f} RON (12 salarii minime) = {cass:,.0f} RON"
    else:
        baza_cass = CASS_PRAG_24
        cass = baza_cass * CASS_RATE
        nota_cass = f"CASS 10% x {baza_cass:,.0f} RON (24 salarii minime, plafonat) = {cass:,.0f} RON"
    
    total_taxe = impozit_castig + impozit_div + cass
    venit_net = venit_total - total_taxe
    rata_efectiva = (total_taxe / venit_total * 100) if venit_total > 0 else 0
    
    detalii = [
        f"Castig capital: {castig:,.0f} RON",
        f"Dividende: {dividende:,.0f} RON",
        f"Impozit castig capital: {nota_castig}",
        f"Impozit dividende: {nota_div}",
        nota_cass
    ]
    
    avantaje = [
        "Impozit redus pe BVB: 3% (>1 an) sau 6% (<1 an)",
        "Retinere la sursa (brokerul plateste automat)",
        "Fara contabilitate sau declaratii complexe",
        "Ideal pentru investitori pasivi",
        "NOU 2026: Deducere pana la 400 EUR/an pentru investitii"
    ]
    
    dezavantaje = [
        "Nu poti compensa pierderile cu castigurile",
        "CASS obligatoriu peste 24.300 RON/an (inclusiv salariati)",
        "Nu poti deduce nicio cheltuiala",
        "Impozit pe tranzactie, nu pe profit net anual"
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
    Calculeaza impozitele pentru Persoana Fizica - Investitii INTERNATIONALE
    
    LEGISLATIE 2026 pentru piete straine (brokeri nerezidenti):
    - Castig capital: 16% pe castig NET anual (castiguri minus pierderi)
    - Dividende: 16% in Romania + retinere la sursa in tara emitentului
    - Pierderile se pot compensa cu castigurile
    - CASS: 10% daca venit total > 6 salarii minime
    - Trebuie declarat in Declaratia Unica (formularul 212)
    """
    castig = input_data.castig_capital_anual
    dividende = input_data.dividende_anuale
    venit_total = castig + dividende
    
    # === IMPOZIT PE CASTIG DE CAPITAL ===
    # 16% pe castig NET anual (brokeri nerezidenti)
    impozit_castig = castig * IMPOZIT_INTERNATIONAL
    nota_castig = f"16% castig capital net: {impozit_castig:,.0f} RON"
    
    # === IMPOZIT PE DIVIDENDE INTERNATIONALE ===
    # Retinere la sursa in tara emitentului + impozit in RO
    # Cu tratate de evitare a dublei impuneri, se acorda credit fiscal
    
    # Exemplu SUA cu W-8BEN: 15% retinut in SUA
    retinere_sursa = dividende * RETINERE_USA
    
    # In Romania se datoreaza 16%, dar se scade ce s-a platit in strainatate (credit fiscal)
    # Daca s-a retinut 15% in SUA, mai datorezi 1% in RO (16% - 15%)
    impozit_div_ro = max(0, dividende * IMPOZIT_DIVIDENDE_STRAINE - retinere_sursa)
    impozit_div_total = retinere_sursa + impozit_div_ro
    
    nota_div = f"Dividende: {retinere_sursa:,.0f} RON retinut la sursa (15% SUA)"
    if impozit_div_ro > 0:
        nota_div += f" + {impozit_div_ro:,.0f} RON in RO (diferenta pana la 16%)"
    else:
        nota_div += " (credit fiscal acopera impozitul RO)"
    
    # === CASS ===
    # CASS se aplică TUTUROR investitorilor pe veniturile din investiții
    cass = 0
    nota_cass = ""
    
    if venit_total <= CASS_PRAG_6:
        nota_cass = f"CASS: 0 RON (venit {venit_total:,.0f} RON sub pragul de {CASS_PRAG_6:,.0f} RON = 6 salarii minime)"
    elif venit_total <= CASS_PRAG_12:
        baza_cass = CASS_PRAG_6
        cass = baza_cass * CASS_RATE
        nota_cass = f"CASS 10% × {baza_cass:,.0f} RON (6 salarii minime) = {cass:,.0f} RON"
    elif venit_total <= CASS_PRAG_24:
        baza_cass = CASS_PRAG_12
        cass = baza_cass * CASS_RATE
        nota_cass = f"CASS 10% × {baza_cass:,.0f} RON (12 salarii minime) = {cass:,.0f} RON"
    else:
        baza_cass = CASS_PRAG_24
        cass = baza_cass * CASS_RATE
        nota_cass = f"CASS 10% × {baza_cass:,.0f} RON (24 salarii minime, plafonat) = {cass:,.0f} RON"
    
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
        "Acces la mii de companii globale",
        "Diversificare geografica",
        "Pierderile se compenseaza cu castigurile",
        "ETF-uri cu costuri mici",
        "Credit fiscal pentru dividende (tratate)"
    ]
    
    dezavantaje = [
        "Impozit 16% vs 3-6% pe BVB",
        "Trebuie sa completezi Declaratia Unica",
        "Calcul manual al impozitului",
        "Complexitate cu retinerea la sursa",
        "Risc valutar (USD/EUR)"
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
        "Impozit 16% vs 3-6% ca PF pe BVB",
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
    
    # Rata impozit micro 2026: 1% pentru toate micro (cifra afaceri < 100.000 EUR)
    rata_micro = MICRO_IMPOZIT
    tip_micro = "1% micro (2026)"
    
    # Impozit pe venit micro
    impozit_micro = venit_total * rata_micro
    
    # Profit disponibil pentru dividende
    profit_dupa_impozit = venit_total - impozit_micro
    
    # Impozit dividende la retragere (16% din 2026)
    impozit_div = profit_dupa_impozit * IMPOZIT_DIVIDENDE_RO
    
    # Costuri administrative SRL
    costuri_admin = 8000  # ~650 RON/luna contabilitate + taxe diverse
    
    total_taxe = impozit_micro + impozit_div + costuri_admin
    venit_net = venit_total - total_taxe
    rata_efectiva = ((impozit_micro + impozit_div) / venit_total * 100) if venit_total > 0 else 0
    
    detalii = [
        f"Impozit micro (1%): {impozit_micro:,.0f} RON",
        f"Profit dupa impozit: {profit_dupa_impozit:,.0f} RON",
        f"Impozit dividende la retragere (16%): {impozit_div:,.0f} RON",
        f"Costuri admin estimate: {costuri_admin:,.0f} RON/an",
        f"Impozitare totala (fara admin): {rata_efectiva:.1f}%"
    ]
    
    avantaje = [
        "Raspundere limitata la capitalul social",
        "Poti lasa profitul in firma (fara 16%)",
        "Credibilitate in business",
        "Poti deduce toate cheltuielile"
    ]
    
    dezavantaje = [
        f"Impozitare totala ~{rata_efectiva:.0f}% vs 3-6% ca PF pe BVB",
        "Costuri infiintare (~2000 RON)",
        "Contabilitate obligatorie lunara",
        "Declaratii fiscale multiple",
        "NU are sens pentru investitii pe BVB!"
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
### CONCLUZIE PENTRU INVESTITII PE BVB (2026):

**Persoana Fizica este aproape intotdeauna cea mai buna optiune!**

De ce? Legislatia romana ofera un regim fiscal avantajos pentru investitorii pe BVB:

| Situatie | Impozit 2026 |
|----------|------------|
| Detinere >= 1 an | **3%** |
| Detinere < 1 an | **6%** |
| Dividende | **16%** |

**Comparativ:**
- PFA: ~35-45% (impozit + CAS + CASS)
- SRL Micro: ~19-20% + costuri administrative

**Economie folosind PF:** pana la **{economie:,.0f} RON/an**

**CASS**: Daca castigurile din investitii depasesc {CASS_PRAG_6:,.0f} RON/an (6 salarii minime),
vei datora CASS (10% din baza de calcul: 6, 12 sau 24 salarii minime). Se aplica si salariatilor!

**Ce trebuie sa faci:**
1. Brokerul retine automat impozitul pe castig (3% sau 6%)
2. Companiile retin 16% din dividende
3. Completezi Declaratia Unica (212) pana in mai pentru CASS (daca e cazul)
"""
    else:  # INTERNATIONAL
        # Comparatie BVB vs International
        pf_bvb_ipotetic = input_data.castig_capital_anual * 0.045  # Media 4.5% pentru BVB (mixt 3-6%)
        pf_int = input_data.castig_capital_anual * 0.16  # 16% international
        diferenta_bvb_int = pf_int - pf_bvb_ipotetic
        
        explicatie = f"""
### CONCLUZIE PENTRU INVESTITII INTERNATIONALE (2026):

**Impozitarea este semnificativ mai mare decat pe BVB.**

| Piata | Impozit Castig 2026 | Dividende 2026 |
|-------|---------------------|----------------|
| BVB | **3-6%** | 16% |
| USA/UE (brokeri straini) | **16%** | 15% retinut + 1% RO |

**Calculul tau (2026):**
- Castig capital: {input_data.castig_capital_anual:,.0f} RON x 16% = **{input_data.castig_capital_anual * 0.16:,.0f} RON**
- Dividende: {input_data.dividende_anuale:,.0f} RON x ~16% = **{input_data.dividende_anuale * 0.16:,.0f} RON**

**Comparatie cu BVB:**
Daca ai investi aceeasi suma pe BVB, ai plati ~**{diferenta_bvb_int:,.0f} RON mai putin** impozit pe castiguri!

**Ce trebuie sa faci:**
1. Completeaza formularul **W-8BEN** la broker (reduce impozitul SUA de la 30% la 15%)
2. Depune **Declaratia Unica (212)** pana in mai
3. Calculeaza si plateste diferenta de impozit (16% - credit fiscal)
4. Pastreaza toate rapoartele de la broker

**CASS**: Se aplica la fel ca pentru BVB (prag {CASS_PRAG_6:,.0f} RON, inclusiv salariati).
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
    DOAR PENTRU UTILIZATORI PRO!
    ACTUALIZAT conform legislatiei romane 2026.
    """
    db = await get_database()
    
    # Verifică dacă user-ul are PRO
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    subscription_level = user_data.get("subscription_level", "free") if user_data else "free"
    
    if subscription_level != "pro":
        raise HTTPException(
            status_code=403, 
            detail={
                "error": "pro_required",
                "message": "Calculatorul Fiscal este disponibil doar pentru utilizatorii PRO.",
                "upgrade_url": "/pricing"
            }
        )
    
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
    """Returneaza constantele fiscale actuale pentru BVB (public) - ACTUALIZAT 2026"""
    return {
        "an_fiscal": "2026",
        "ultima_actualizare": "Ianuarie 2026",
        "salariu_minim_brut": SALARIU_MINIM_BRUT,
        "bvb": {
            "castig_capital_termen_lung": "3% (detinere >= 365 zile)",
            "castig_capital_termen_scurt": "6% (detinere < 365 zile)",
            "dividende": "16% (retinut la sursa)",
            "nota": "Impozitul este retinut automat de broker. Pierderile NU se compenseaza."
        },
        "international": {
            "castig_capital": "16% (pe castig net anual)",
            "dividende_sua": "15% retinut la sursa (cu W-8BEN) + 1% diferenta in RO",
            "dividende_ue": "10-25% (variaza pe tara)",
            "credit_fiscal": "Se scade impozitul platit in strainatate (max 16%)",
            "nota": "Trebuie declarat in Declaratia Unica (212). Pierderile SE compenseaza."
        },
        "cass": {
            "rata": "10%",
            "prag_6_salarii": f"{CASS_PRAG_6:,} RON/an (6 x salariu minim 2026)",
            "prag_12_salarii": f"{CASS_PRAG_12:,} RON/an (12 x salariu minim 2026)",
            "prag_24_salarii": f"{CASS_PRAG_24:,} RON/an (24 x salariu minim 2026, plafon maxim)",
            "nota": "CASS se aplica TUTUROR investitorilor (inclusiv salariatilor) pe veniturile din investitii peste pragul de 6 salarii minime"
        },
        "micro_srl": {
            "impozit_micro": "1%",
            "dividende_la_retragere": "16%",
            "plafon_venituri_eur": MICRO_PLAFON_VENITURI_EUR,
            "nota": "1% pe venit pentru cifra de afaceri sub 100.000 EUR (2026)"
        },
        "pfa": {
            "impozit_venit": "10%",
            "cas": "25%",
            "cass": "10%"
        },
        "disclaimer": "Valorile sunt orientative conform legislatiei in vigoare in 2026 (Cod Fiscal actualizat). Consultati un contabil CECCAR pentru situatia dumneavoastra specifica."
    }


@router.get("/preview")
async def get_preview_calcul(
    castig: float = 50000,
    dividende: float = 10000,
    are_salariu: bool = True,
    piata: str = "bvb",
    perioada: str = "mixt",
    procent_lung: int = 50
):
    """
    Preview rapid pentru homepage (public)
    Arata economiile posibile intre PF si alte forme
    Suporta atat BVB cat si piete internationale
    """
    tip_piata = TipPiata.INTERNATIONAL if piata == "international" else TipPiata.BVB
    
    # Map perioada
    if perioada == "peste_1_an":
        per = PerioadaDetinere.PESTE_1_AN
        pct_lung = 100
    elif perioada == "sub_1_an":
        per = PerioadaDetinere.SUB_1_AN
        pct_lung = 0
    else:
        per = PerioadaDetinere.MIXT
        pct_lung = max(0, min(100, procent_lung))
    
    input_data = CalculFiscalInput(
        castig_capital_anual=castig,
        dividende_anuale=dividende,
        tip_piata=tip_piata,
        perioada_detinere=per,
        procent_termen_lung=pct_lung,
        are_alte_venituri_cass=are_salariu,
        are_angajat_srl=False
    )
    
    if tip_piata == TipPiata.BVB:
        pf = calcul_pf_bvb(input_data)
        srl = calcul_srl_micro_investitii(input_data)
        economie = pf.venit_net - srl.venit_net
        
        # Comparație cu international
        input_int = CalculFiscalInput(
            castig_capital_anual=castig,
            dividende_anuale=dividende,
            tip_piata=TipPiata.INTERNATIONAL,
            perioada_detinere=PerioadaDetinere.MIXT,
            procent_termen_lung=50,
            are_alte_venituri_cass=are_salariu,
            are_angajat_srl=False
        )
        pf_int = calcul_pf_international(input_int)
        diferenta_bvb_vs_int = pf.venit_net - pf_int.venit_net
        
        return {
            "piata": "BVB",
            "castig_capital": castig,
            "dividende": dividende,
            "venit_total": castig + dividende,
            "comparatie": {
                "pf_bvb": {
                    "venit_net": round(pf.venit_net),
                    "total_taxe": round(pf.total_taxe),
                    "rata_impozitare": f"{pf.rata_efectiva_impozitare:.1f}%",
                    "detalii": "3-6% castig + 16% dividende (2026)"
                },
                "pf_international": {
                    "venit_net": round(pf_int.venit_net),
                    "total_taxe": round(pf_int.total_taxe),
                    "rata_impozitare": f"{pf_int.rata_efectiva_impozitare:.1f}%",
                    "detalii": "16% castig + 16% dividende (2026)"
                },
                "srl_micro": {
                    "venit_net": round(srl.venit_net),
                    "total_taxe": round(srl.total_taxe),
                    "rata_impozitare": f"{srl.rata_efectiva_impozitare:.1f}%",
                    "detalii": "1% micro + 16% dividende + costuri admin (2026)"
                }
            },
            "economie_pf_vs_srl": round(economie) if economie > 0 else 0,
            "economie_bvb_vs_international": round(diferenta_bvb_vs_int) if diferenta_bvb_vs_int > 0 else 0,
            "concluzie": "Pentru investiții pe BVB, Persoana Fizică este aproape întotdeauna mai avantajoasă!",
            "mesaj_principal": f"🇷🇴 BVB: doar {pf.rata_efectiva_impozitare:.1f}% taxe vs 🌍 International: {pf_int.rata_efectiva_impozitare:.1f}%",
            "bonus_bvb": f"Economisești {diferenta_bvb_vs_int:,.0f} RON investind pe BVB în loc de SUA!",
            "is_preview": True
        }
    else:  # INTERNATIONAL
        pf_int = calcul_pf_international(input_data)
        srl = calcul_srl_micro_investitii(input_data)
        economie = pf_int.venit_net - srl.venit_net
        
        # Comparație cu BVB
        input_bvb = CalculFiscalInput(
            castig_capital_anual=castig,
            dividende_anuale=dividende,
            tip_piata=TipPiata.BVB,
            perioada_detinere=PerioadaDetinere.MIXT,
            procent_termen_lung=50,
            are_alte_venituri_cass=are_salariu,
            are_angajat_srl=False
        )
        pf_bvb = calcul_pf_bvb(input_bvb)
        diferenta_int_vs_bvb = pf_bvb.venit_net - pf_int.venit_net
        
        return {
            "piata": "Internațional",
            "castig_capital": castig,
            "dividende": dividende,
            "venit_total": castig + dividende,
            "comparatie": {
                "pf_international": {
                    "venit_net": round(pf_int.venit_net),
                    "total_taxe": round(pf_int.total_taxe),
                    "rata_impozitare": f"{pf_int.rata_efectiva_impozitare:.1f}%",
                    "detalii": "16% castig + 16% dividende (2026)"
                },
                "pf_bvb": {
                    "venit_net": round(pf_bvb.venit_net),
                    "total_taxe": round(pf_bvb.total_taxe),
                    "rata_impozitare": f"{pf_bvb.rata_efectiva_impozitare:.1f}%",
                    "detalii": "3-6% castig + 16% dividende (2026)"
                },
                "srl_micro": {
                    "venit_net": round(srl.venit_net),
                    "total_taxe": round(srl.total_taxe),
                    "rata_impozitare": f"{srl.rata_efectiva_impozitare:.1f}%",
                    "detalii": "1% micro + 16% dividende + costuri admin (2026)"
                }
            },
            "economie_pf_vs_srl": round(economie) if economie > 0 else 0,
            "cost_vs_bvb": round(diferenta_int_vs_bvb) if diferenta_int_vs_bvb > 0 else 0,
            "concluzie": "Piețele internaționale au impozit mai mare, dar oferă diversificare globală.",
            "mesaj_principal": f"🌍 International: {pf_int.rata_efectiva_impozitare:.1f}% taxe (vs 🇷🇴 BVB: {pf_bvb.rata_efectiva_impozitare:.1f}%)",
            "nota_bvb": f"Ai plăti cu {diferenta_int_vs_bvb:,.0f} RON mai puțin pe BVB",
            "is_preview": True
        }
