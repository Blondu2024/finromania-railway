"""
Simulator Fiscal Antreprenor - EDUCATIV
Ajută antreprenorii să înțeleagă regulile fiscale pentru multiple entități
DISCLAIMER: Informații educative, NU consiliere fiscală!
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fiscal-simulator", tags=["fiscal-simulator-antreprenor"])

# ============================================
# CONSTANTE FISCALE ROMÂNIA 2026
# ACTUALIZAT CONFORM OUG 89/2025, Legea 239/2025, OUG 8/2026
# SCOP EDUCATIV
# ============================================

# Praguri importante
PRAG_TVA = 395000  # RON - prag înregistrare TVA obligatorie (modificat 2026!)
PRAG_MICRO_EUR = 100000  # EUR - prag maxim venituri micro (redus de la 500k!)
PRAG_DETINERE_AGREGARE = 25  # % - dacă deții >25% în mai multe firme, veniturile se agregă

# Curs EUR aproximativ (31.12.2025)
CURS_EUR = 5.10  # RON/EUR

# Impozite micro - COTĂ UNICĂ din 2026!
IMPOZIT_MICRO = 1  # % - cotă unică indiferent de angajați

# Impozit profit standard
IMPOZIT_PROFIT = 16  # %

# Impozit dividende - MAJORAT în 2026!
IMPOZIT_DIVIDENDE = 16  # % (de la 8% în 2025!)

# PFA
PFA_IMPOZIT = 10  # %
PFA_CASS = 10  # %
PFA_CAS = 25  # % (opțional)

# CASS - MODIFICĂRI 2026
SALARIU_MINIM_S1 = 4050  # RON (ianuarie-iunie 2026)
SALARIU_MINIM_S2 = 4325  # RON (iulie-decembrie 2026)
SALARIU_MINIM = 4050  # RON - folosim cel de la început de an
CASS_BAZA_MINIMA = 6 * SALARIU_MINIM  # 24,300 RON
CASS_BAZA_MAXIMA = 72 * SALARIU_MINIM  # MAJORAT de la 60 la 72 salarii minime!

# Coduri CAEN cu regim special
CAEN_SCUTIRI = {
    # IT - Scutit impozit profit (condiții speciale)
    "6201": {"nume": "Activități de realizare a soft-ului la comandă", "scutire_profit": True, "conditii": "Minim 80% venituri din IT, angajați cu studii superioare IT"},
    "6202": {"nume": "Activități de consultanță în tehnologia informației", "scutire_profit": True, "conditii": "Minim 80% venituri din IT"},
    "6209": {"nume": "Alte activități de servicii IT", "scutire_profit": True, "conditii": "Minim 80% venituri din IT"},
    "6311": {"nume": "Prelucrarea datelor, administrarea paginilor web", "scutire_profit": True, "conditii": "Minim 80% venituri din IT"},
    "6312": {"nume": "Activități ale portalurilor web", "scutire_profit": True, "conditii": "Minim 80% venituri din IT"},
    # Medical - TVA scutit
    "8621": {"nume": "Activități de asistență medicală generală", "scutire_tva": True, "conditii": "Servicii medicale"},
    "8622": {"nume": "Activități de asistență medicală specializată", "scutire_tva": True, "conditii": "Servicii medicale"},
    # Educație - TVA scutit
    "8510": {"nume": "Învățământ preșcolar", "scutire_tva": True, "conditii": "Educație"},
    "8520": {"nume": "Învățământ primar", "scutire_tva": True, "conditii": "Educație"},
    "8559": {"nume": "Alte forme de învățământ", "scutire_tva": True, "conditii": "Educație, cursuri"},
    # Agricultură - regim special TVA
    "0111": {"nume": "Cultivarea cerealelor", "regim_special_tva": True, "conditii": "Agricultură"},
    "0113": {"nume": "Cultivarea legumelor", "regim_special_tva": True, "conditii": "Agricultură"},
}

# ============================================
# MODELE DE DATE
# ============================================

class TipEntitate(str, Enum):
    PF = "pf"
    PFA_NORMA = "pfa_norma"
    PFA_REAL = "pfa_real"
    PFI = "pfi"
    SRL_MICRO = "srl_micro"
    SRL_PROFIT = "srl_profit"

class EntitateInput(BaseModel):
    """O entitate din portofoliul antreprenorului"""
    tip: TipEntitate
    nume: str = Field(default="", description="Nume opțional pentru identificare")
    cod_caen: Optional[str] = Field(default=None, description="Cod CAEN principal")
    venit_anual_estimat: float = Field(default=0, ge=0, description="Venit anual estimat RON")
    procent_detinere: float = Field(default=100, ge=0, le=100, description="% deținere în entitate")
    are_angajati: bool = Field(default=False, description="Are cel puțin un angajat")
    platitor_tva: bool = Field(default=False, description="Este plătitor de TVA")
    # CÂMPURI NOI
    norma_venit_anuala: Optional[float] = Field(default=None, description="Norma de venit ANAF pentru PFA normă")
    an_infiintare: Optional[int] = Field(default=None, description="Anul înființării firmei")
    marja_profit: Optional[float] = Field(default=20, ge=1, le=90, description="Marjă profit % pentru SRL Profit")
    
class SimulatorInput(BaseModel):
    """Input pentru simulatorul fiscal"""
    entitati: List[EntitateInput] = Field(default=[], description="Lista entităților")
    are_salariu: bool = Field(default=False, description="Are salariu cu CASS plătit")
    salariu_brut_lunar: float = Field(default=0, ge=0, description="Salariu brut lunar RON")
    # CÂMP NOU - pentru verificare asocieri
    alte_asocieri_peste_25: bool = Field(default=False, description="Asociat/admin în alte firme cu >25% deținere (neincluse în listă)")

class PasCalcul(BaseModel):
    """Un pas din explicația calculului"""
    descriere: str
    formula: Optional[str] = None
    rezultat: Optional[str] = None

class AvertismentFiscal(BaseModel):
    """Un avertisment despre situația fiscală"""
    tip: str  # "info", "warning", "danger"
    titlu: str
    descriere: str
    actiune_recomandata: Optional[str] = None

class ComparatieAlternativa(BaseModel):
    """Comparație cu o alternativă fiscală"""
    alternativa: str
    impozit_alternativ: float
    diferenta: float
    recomandare: str

class RezultatEntitate(BaseModel):
    """Rezultatul pentru o entitate"""
    nume: str
    tip: str
    venit: float
    impozit_estimat: float
    rata_impozitare: float
    regim_tva: str
    scutiri_active: List[str]
    observatii: List[str]
    # CÂMPURI NOI
    pasi_calcul: List[PasCalcul] = Field(default=[])
    comparatii: List[ComparatieAlternativa] = Field(default=[])

class SimulatorOutput(BaseModel):
    """Output-ul simulatorului"""
    entitati: List[RezultatEntitate]
    total_venituri: float
    total_impozite_estimate: float
    rata_efectiva_globala: float
    avertismente: List[AvertismentFiscal]
    # CÂMPURI NOI
    sumar_comparativ: Optional[Dict] = None
    explicatie_ai: Optional[str] = None
    disclaimer: str

# ============================================
# LOGICA DE CALCUL
# ============================================

def verifica_scutiri_caen(cod_caen: str) -> Dict:
    """Verifică dacă un cod CAEN are scutiri speciale"""
    if cod_caen in CAEN_SCUTIRI:
        return CAEN_SCUTIRI[cod_caen]
    return {}

def calculeaza_impozit_entitate(entitate: EntitateInput, an_curent: int = 2026) -> RezultatEntitate:
    """Calculează impozitul estimat pentru o entitate cu explicații detaliate"""
    venit = entitate.venit_anual_estimat
    scutiri = []
    observatii = []
    pasi_calcul = []
    comparatii = []
    impozit = 0
    rata = 0
    regim_tva = "Neînregistrat TVA"
    
    # Verifică scutiri CAEN (tratăm "none" ca None)
    cod_caen = entitate.cod_caen if entitate.cod_caen and entitate.cod_caen != "none" else None
    info_caen = verifica_scutiri_caen(cod_caen) if cod_caen else {}
    
    # Verifică dacă e primul an de activitate
    este_primul_an = entitate.an_infiintare and entitate.an_infiintare == an_curent
    
    if entitate.tip == TipEntitate.PF:
        observatii.append("Ca PF, veniturile din activități economice trebuie declarate prin PFA/PFI sau SRL")
        rata = 0
        impozit = 0
        pasi_calcul.append(PasCalcul(
            descriere="Persoană fizică nu poate desfășura direct activități economice",
            rezultat="Trebuie să alegi PFA, PFI sau SRL"
        ))
        
    elif entitate.tip == TipEntitate.PFA_NORMA:
        # PFA Normă de venit
        norma = entitate.norma_venit_anuala or venit  # Folosim norma dacă e specificată
        rata = PFA_IMPOZIT
        impozit = norma * rata / 100
        
        pasi_calcul.append(PasCalcul(
            descriere="Pas 1: Identificare normă de venit ANAF",
            formula=f"Norma = {norma:,.0f} RON (stabilită de ANAF pentru activitate)",
            rezultat=f"{norma:,.0f} RON"
        ))
        pasi_calcul.append(PasCalcul(
            descriere="Pas 2: Calcul impozit pe venit",
            formula=f"{norma:,.0f} × {rata}% = {impozit:,.0f} RON",
            rezultat=f"Impozit: {impozit:,.0f} RON"
        ))
        
        observatii.append(f"PFA Normă de venit - impozit {rata}% aplicat la norma ANAF, NU la venitul real")
        observatii.append("Avantaj: dacă câștigi mai mult decât norma, nu plătești impozit suplimentar")
        
        # Comparație cu SRL
        impozit_srl = venit * IMPOZIT_MICRO / 100
        comparatii.append(ComparatieAlternativa(
            alternativa="SRL Micro",
            impozit_alternativ=impozit_srl,
            diferenta=impozit_srl - impozit,
            recomandare=f"{'SRL ar fi mai avantajos' if impozit_srl < impozit else 'PFA Normă e mai avantajos'} cu {abs(impozit_srl - impozit):,.0f} RON"
        ))
        
    elif entitate.tip == TipEntitate.PFA_REAL:
        rata = PFA_IMPOZIT
        cheltuieli_estimate = venit * 0.30  # Estimăm 30% cheltuieli
        venit_net = venit - cheltuieli_estimate
        impozit = venit_net * rata / 100
        
        pasi_calcul.append(PasCalcul(
            descriere="Pas 1: Calcul venit net (venit - cheltuieli deductibile)",
            formula=f"{venit:,.0f} - {cheltuieli_estimate:,.0f} (est. 30%) = {venit_net:,.0f} RON",
            rezultat=f"Venit net: {venit_net:,.0f} RON"
        ))
        pasi_calcul.append(PasCalcul(
            descriere="Pas 2: Calcul impozit pe venit net",
            formula=f"{venit_net:,.0f} × {rata}% = {impozit:,.0f} RON",
            rezultat=f"Impozit: {impozit:,.0f} RON"
        ))
        
        observatii.append("PFA Sistem Real - plătești impozit pe venitul NET (după cheltuieli)")
        observatii.append("CASS 10% datorat dacă veniturile depășesc 6 salarii minime/an")
        
        # Comparație cu normă
        norma_estimata = venit * 0.5
        impozit_norma = norma_estimata * rata / 100
        comparatii.append(ComparatieAlternativa(
            alternativa="PFA Normă (dacă norma e ~50% din venit)",
            impozit_alternativ=impozit_norma,
            diferenta=impozit_norma - impozit,
            recomandare="Verifică norma ANAF pentru activitatea ta"
        ))
        
    elif entitate.tip == TipEntitate.PFI:
        rata = PFA_IMPOZIT
        impozit = venit * rata / 100
        
        pasi_calcul.append(PasCalcul(
            descriere="Pas 1: Baza de impozitare = venitul brut",
            formula=f"Venit: {venit:,.0f} RON",
            rezultat=f"{venit:,.0f} RON"
        ))
        pasi_calcul.append(PasCalcul(
            descriere="Pas 2: Calcul impozit",
            formula=f"{venit:,.0f} × {rata}% = {impozit:,.0f} RON",
            rezultat=f"Impozit: {impozit:,.0f} RON"
        ))
        
        observatii.append("PFI (Profesie liberală) - 10% impozit + CASS 10%")
        
    elif entitate.tip == TipEntitate.SRL_MICRO:
        prag_ron = PRAG_MICRO_EUR * CURS_EUR
        
        if info_caen.get("scutire_profit"):
            scutiri.append(f"Scutire impozit profit - {info_caen.get('conditii', '')}")
            rata = 0
            impozit = 0
            pasi_calcul.append(PasCalcul(
                descriere="Cod CAEN cu scutire de impozit",
                formula=f"Scutire: {info_caen.get('conditii', '')}",
                rezultat="Impozit: 0 RON (dacă îndeplinești condițiile)"
            ))
            observatii.append("ATENȚIE: Scutirea se aplică doar dacă îndeplinești TOATE condițiile!")
        else:
            rata = IMPOZIT_MICRO
            impozit_micro = venit * rata / 100
            # Impozit dividende pe profitul net distribuit
            profit_net_micro = venit - impozit_micro
            impozit_div_micro = profit_net_micro * IMPOZIT_DIVIDENDE / 100
            impozit = impozit_micro + impozit_div_micro

            pasi_calcul.append(PasCalcul(
                descriere="Pas 1: Verificare eligibilitate micro",
                formula=f"Venit {venit:,.0f} RON < Prag {prag_ron:,.0f} RON?",
                rezultat="DA - eligibil micro" if venit <= prag_ron else "NU - depășit prag!"
            ))
            pasi_calcul.append(PasCalcul(
                descriere="Pas 2: Calcul impozit micro (cotă unică 2026)",
                formula=f"{venit:,.0f} × {rata}% = {impozit_micro:,.0f} RON",
                rezultat=f"Impozit micro: {impozit_micro:,.0f} RON"
            ))
            pasi_calcul.append(PasCalcul(
                descriere=f"Pas 3: Impozit dividende ({IMPOZIT_DIVIDENDE}%) pe profitul net",
                formula=f"({venit:,.0f} - {impozit_micro:,.0f}) × {IMPOZIT_DIVIDENDE}% = {impozit_div_micro:,.0f} RON",
                rezultat=f"Impozit dividende: {impozit_div_micro:,.0f} RON"
            ))

            observatii.append(f"Micro {IMPOZIT_MICRO}% + {IMPOZIT_DIVIDENDE}% dividende (cotă unică din 2026)")
            
            if este_primul_an:
                observatii.append("✅ Primul an de activitate - poți alege micro indiferent de estimări")
            
        if venit > prag_ron:
            observatii.append(f"⚠️ ATENȚIE: Depășești pragul micro de {PRAG_MICRO_EUR:,} EUR!")
            observatii.append("Trebuie să treci la impozit pe profit 16%!")
            
            # Recalculăm ca SRL profit (marjă 20% default)
            profit_est = venit * 0.20
            imp_profit = profit_est * IMPOZIT_PROFIT / 100
            imp_div = (profit_est - imp_profit) * IMPOZIT_DIVIDENDE / 100
            total_profit = imp_profit + imp_div
            comparatii.append(ComparatieAlternativa(
                alternativa="SRL Profit (obligatoriu la depășire)",
                impozit_alternativ=total_profit,
                diferenta=total_profit - impozit,
                recomandare=f"La depășirea pragului: ~{total_profit:,.0f} RON (16% profit + 16% dividende)"
            ))
            
    elif entitate.tip == TipEntitate.SRL_PROFIT:
        marja = (entitate.marja_profit or 20) / 100
        profit_estimat = venit * marja

        if info_caen.get("scutire_profit"):
            scutiri.append(f"Scutire impozit profit - {info_caen.get('conditii', '')}")
            rata = 0
            impozit = 0
        else:
            rata = IMPOZIT_PROFIT
            impozit_profit = profit_estimat * rata / 100
            # Impozit dividende pe profitul net distribuit
            profit_net = profit_estimat - impozit_profit
            impozit_div = profit_net * IMPOZIT_DIVIDENDE / 100
            impozit = impozit_profit + impozit_div

            pasi_calcul.append(PasCalcul(
                descriere=f"Pas 1: Estimare profit (marjă {entitate.marja_profit or 20}%)",
                formula=f"{venit:,.0f} × {entitate.marja_profit or 20}% = {profit_estimat:,.0f} RON",
                rezultat=f"Profit estimat: {profit_estimat:,.0f} RON"
            ))
            pasi_calcul.append(PasCalcul(
                descriere="Pas 2: Impozit pe profit",
                formula=f"{profit_estimat:,.0f} × {rata}% = {impozit_profit:,.0f} RON",
                rezultat=f"Impozit profit: {impozit_profit:,.0f} RON"
            ))
            pasi_calcul.append(PasCalcul(
                descriere=f"Pas 3: Impozit dividende ({IMPOZIT_DIVIDENDE}%) pe profitul net distribuit",
                formula=f"({profit_estimat:,.0f} - {impozit_profit:,.0f}) × {IMPOZIT_DIVIDENDE}% = {impozit_div:,.0f} RON",
                rezultat=f"Impozit dividende: {impozit_div:,.0f} RON"
            ))
            pasi_calcul.append(PasCalcul(
                descriere="Total taxe SRL Profit",
                formula=f"{impozit_profit:,.0f} + {impozit_div:,.0f} = {impozit:,.0f} RON",
                rezultat=f"Total: {impozit:,.0f} RON"
            ))

            observatii.append(f"{rata}% impozit profit + {IMPOZIT_DIVIDENDE}% impozit dividende (marjă {entitate.marja_profit or 20}%)")
            observatii.append("Poți ajusta marja de profit în funcție de activitatea ta")

        # Comparație cu micro (dacă ar fi eligibil)
        if venit <= PRAG_MICRO_EUR * CURS_EUR:
            impozit_micro = venit * IMPOZIT_MICRO / 100
            profit_micro_net = venit - impozit_micro
            div_micro = profit_micro_net * IMPOZIT_DIVIDENDE / 100
            total_micro = impozit_micro + div_micro
            comparatii.append(ComparatieAlternativa(
                alternativa=f"SRL Micro (1% + {IMPOZIT_DIVIDENDE}% dividende)",
                impozit_alternativ=total_micro,
                diferenta=total_micro - impozit,
                recomandare=f"{'Micro ar fi mai avantajos' if total_micro < impozit else 'Profit e mai avantajos'}"
            ))
    
    # Verifică TVA
    if entitate.platitor_tva:
        regim_tva = "Plătitor TVA"
    elif info_caen.get("scutire_tva"):
        regim_tva = "Scutit TVA (activitate scutită)"
        scutiri.append("TVA scutit conform Cod Fiscal")
    elif venit > PRAG_TVA:
        regim_tva = "⚠️ Trebuie înregistrat TVA (depășit prag)"
        observatii.append(f"Venitul depășește pragul TVA de {PRAG_TVA:,} RON!")
    
    return RezultatEntitate(
        nume=entitate.nume or f"{entitate.tip.value.upper()}",
        tip=entitate.tip.value,
        venit=venit,
        impozit_estimat=round(impozit, 2),
        rata_impozitare=rata,
        regim_tva=regim_tva,
        scutiri_active=scutiri,
        observatii=observatii,
        pasi_calcul=pasi_calcul,
        comparatii=comparatii
    )

def verifica_agregare_micro(entitati: List[EntitateInput], alte_asocieri: bool = False) -> List[AvertismentFiscal]:
    """Verifică regula agregării veniturilor pentru micro"""
    avertismente = []
    
    # Găsește SRL-uri micro cu deținere >25%
    srl_micro_relevante = [
        e for e in entitati 
        if e.tip == TipEntitate.SRL_MICRO and e.procent_detinere > PRAG_DETINERE_AGREGARE
    ]
    
    # Avertizare dacă are alte asocieri nedeclarate
    if alte_asocieri:
        avertismente.append(AvertismentFiscal(
            tip="danger",
            titlu="⚠️ Asocieri suplimentare cu >25% deținere!",
            descriere="Ai indicat că ești asociat/administrator în ALTE firme cu peste 25% deținere care NU sunt incluse în această simulare.",
            actiune_recomandata="IMPORTANT: Veniturile din TOATE firmele cu >25% deținere se agregă pentru pragul micro! Adaugă toate firmele sau consultă un contabil."
        ))
    
    if len(srl_micro_relevante) >= 1 and alte_asocieri:
        avertismente.append(AvertismentFiscal(
            tip="warning",
            titlu="Risc de depășire prag micro",
            descriere="Având asocieri în alte firme, veniturile totale agregate pot depăși pragul de 100.000 EUR!",
            actiune_recomandata="Verifică suma tuturor veniturilor din firmele unde deții >25%."
        ))
    
    if len(srl_micro_relevante) > 1:
        total_venituri = sum(e.venit_anual_estimat for e in srl_micro_relevante)
        prag_micro_ron = PRAG_MICRO_EUR * CURS_EUR
        
        avertismente.append(AvertismentFiscal(
            tip="warning",
            titlu="Agregare venituri micro-întreprinderi",
            descriere=f"Deții >25% în {len(srl_micro_relevante)} SRL-uri micro. Conform legii, veniturile se AGREGĂ pentru verificarea pragului de {PRAG_MICRO_EUR:,} EUR.",
            actiune_recomandata=f"Total agregat: {total_venituri:,.0f} RON. Pragul este {prag_micro_ron:,.0f} RON ({PRAG_MICRO_EUR:,} EUR)."
        ))
        
        if total_venituri > prag_micro_ron:
            avertismente.append(AvertismentFiscal(
                tip="danger",
                titlu="⚠️ Depășire prag micro prin agregare!",
                descriere=f"Veniturile agregate ({total_venituri:,.0f} RON) depășesc pragul micro de {PRAG_MICRO_EUR:,} EUR!",
                actiune_recomandata="Una sau mai multe firme trebuie să treacă la impozit pe profit 16%. Consultă un expert contabil URGENT!"
            ))
    
    return avertismente

def verifica_tva_global(entitati: List[EntitateInput]) -> List[AvertismentFiscal]:
    """Verifică situația TVA pentru toate entitățile"""
    avertismente = []
    
    for e in entitati:
        if e.venit_anual_estimat > PRAG_TVA and not e.platitor_tva:
            info_caen = verifica_scutiri_caen(e.cod_caen) if e.cod_caen else {}
            if not info_caen.get("scutire_tva"):
                avertismente.append(AvertismentFiscal(
                    tip="danger",
                    titlu=f"Înregistrare TVA obligatorie - {e.nume or e.tip.value}",
                    descriere=f"Venitul de {e.venit_anual_estimat:,.0f} RON depășește pragul TVA de {PRAG_TVA:,} RON.",
                    actiune_recomandata="Trebuie să te înregistrezi în scopuri de TVA la ANAF în max 10 zile de la depășire!"
                ))
    
    return avertismente

# ============================================
# ENDPOINTS
# ============================================

@router.get("/caen-codes")
async def get_caen_codes():
    """Returnează lista codurilor CAEN cu regim special"""
    return {
        "success": True,
        "caen_codes": CAEN_SCUTIRI,
        "disclaimer": "Lista include doar codurile CAEN cu scutiri/regim special. Pentru lista completă, consultați clasificarea oficială CAEN Rev.2."
    }

@router.get("/praguri")
async def get_praguri_fiscale():
    """Returnează pragurile fiscale actuale"""
    return {
        "success": True,
        "praguri": {
            "tva": {
                "valoare": PRAG_TVA,
                "moneda": "RON",
                "descriere": "Prag pentru înregistrare obligatorie TVA (MAJORAT în 2026!)"
            },
            "micro": {
                "valoare": PRAG_MICRO_EUR,
                "moneda": "EUR",
                "valoare_ron": int(PRAG_MICRO_EUR * CURS_EUR),
                "descriere": "Plafon maxim venituri pentru regim micro-întreprindere (REDUS de la 500k în 2026!)"
            },
            "impozit_micro": {
                "valoare": IMPOZIT_MICRO,
                "unitate": "%",
                "descriere": "Cotă unică micro din 2026 (elimină diferența 1%/3%)"
            },
            "impozit_dividende": {
                "valoare": IMPOZIT_DIVIDENDE,
                "unitate": "%",
                "descriere": "Impozit dividende (MAJORAT de la 8% în 2026!)"
            },
            "agregare": {
                "valoare": PRAG_DETINERE_AGREGARE,
                "unitate": "%",
                "descriere": "Prag deținere pentru agregare venituri micro (asociat în multiple SRL-uri)"
            },
            "cass_minim": {
                "valoare": CASS_BAZA_MINIMA,
                "moneda": "RON",
                "descriere": "Baza minimă anuală pentru calculul CASS (6 salarii minime)"
            },
            "cass_maxim": {
                "valoare": int(CASS_BAZA_MAXIMA),
                "moneda": "RON",
                "descriere": "Baza maximă anuală CASS (72 salarii minime - MAJORAT de la 60!)"
            },
            "salariu_minim": {
                "s1_2026": SALARIU_MINIM_S1,
                "s2_2026": SALARIU_MINIM_S2,
                "moneda": "RON",
                "descriere": "Salariu minim brut: 4.050 lei (ian-iun), 4.325 lei (iul-dec)"
            }
        },
        "actualizat": "2026 (conform OUG 89/2025, Legea 239/2025, OUG 8/2026)",
        "disclaimer": "Valorile pot suferi modificări legislative. Verificați sursele oficiale ANAF/MFP."
    }

@router.post("/simuleaza", response_model=SimulatorOutput)
async def simuleaza_situatie_fiscala(input_data: SimulatorInput):
    """
    Simulează situația fiscală pentru un portofoliu de entități.
    SCOP EDUCATIV - NU reprezintă consiliere fiscală!
    """
    try:
        rezultate_entitati = []
        avertismente = []
        
        # Calculează pentru fiecare entitate
        for entitate in input_data.entitati:
            rezultat = calculeaza_impozit_entitate(entitate)
            rezultate_entitati.append(rezultat)
        
        # Verifică reguli de agregare (inclusiv alte asocieri)
        avertismente.extend(verifica_agregare_micro(
            input_data.entitati, 
            alte_asocieri=input_data.alte_asocieri_peste_25
        ))
        
        # Verifică TVA
        avertismente.extend(verifica_tva_global(input_data.entitati))
        
        # Verifică CASS - se aplică pe TOATE veniturile din investiții/activități independente
        # Inclusiv dividende SRL dacă nu ai salariu!
        total_venituri_pfa = sum(
            e.venit_anual_estimat for e in input_data.entitati
            if e.tip in [TipEntitate.PFA_NORMA, TipEntitate.PFA_REAL, TipEntitate.PFI]
        )
        # Dividendele din SRL intră în baza CASS
        total_dividende_srl = sum(
            e.venit_anual_estimat * (1 - IMPOZIT_MICRO / 100) * (1 - IMPOZIT_DIVIDENDE / 100)
            if e.tip == TipEntitate.SRL_MICRO else
            e.venit_anual_estimat * ((e.marja_profit or 20) / 100) * (1 - IMPOZIT_PROFIT / 100) * (1 - IMPOZIT_DIVIDENDE / 100)
            if e.tip == TipEntitate.SRL_PROFIT else 0
            for e in input_data.entitati
        )
        total_baza_cass = total_venituri_pfa + total_dividende_srl

        if total_baza_cass > CASS_BAZA_MINIMA:
            cass_estimat = min(total_baza_cass, CASS_BAZA_MAXIMA) * 0.10
            surse = []
            if total_venituri_pfa > 0:
                surse.append(f"PFA/PFI: {total_venituri_pfa:,.0f} RON")
            if total_dividende_srl > 0:
                surse.append(f"Dividende SRL: {total_dividende_srl:,.0f} RON")
            if input_data.are_salariu:
                avertismente.append(AvertismentFiscal(
                    tip="info",
                    titlu="CASS suplimentar posibil",
                    descriere=f"Veniturile din investiții/activități ({' + '.join(surse)}) depășesc {CASS_BAZA_MINIMA:,} RON. Chiar și cu salariu, datorezi CASS 10% suplimentar.",
                    actiune_recomandata=f"CASS estimat suplimentar: {cass_estimat:,.0f} RON/an"
                ))
            else:
                avertismente.append(AvertismentFiscal(
                    tip="warning",
                    titlu="CASS datorat din venituri independente",
                    descriere=f"Veniturile totale ({' + '.join(surse)}) depășesc {CASS_BAZA_MINIMA:,} RON. Datorezi CASS 10%.",
                    actiune_recomandata=f"CASS estimat: {cass_estimat:,.0f} RON/an (bază plafonată la {CASS_BAZA_MAXIMA:,.0f} RON)"
                ))
        
        # Calculează totaluri
        total_venituri = sum(r.venit for r in rezultate_entitati)
        total_impozite = sum(r.impozit_estimat for r in rezultate_entitati)
        rata_efectiva = (total_impozite / total_venituri * 100) if total_venituri > 0 else 0
        
        # Sumar comparativ global (inclusiv dividende)
        total_venit_all = sum(e.venit_anual_estimat for e in input_data.entitati)
        micro_tax = total_venit_all * IMPOZIT_MICRO / 100
        micro_div = (total_venit_all - micro_tax) * IMPOZIT_DIVIDENDE / 100
        profit_est = total_venit_all * 0.20
        profit_tax = profit_est * IMPOZIT_PROFIT / 100
        profit_div = (profit_est - profit_tax) * IMPOZIT_DIVIDENDE / 100
        sumar_comparativ = {
            "total_ca_micro": round(micro_tax + micro_div, 0),
            "total_ca_profit": round(profit_tax + profit_div, 0),
            "total_ca_pfa": round(total_venit_all * PFA_IMPOZIT / 100, 0),
            "economie_vs_profit": round((profit_tax + profit_div) - total_impozite, 0)
        }
        
        return SimulatorOutput(
            entitati=rezultate_entitati,
            total_venituri=round(total_venituri, 2),
            total_impozite_estimate=round(total_impozite, 2),
            rata_efectiva_globala=round(rata_efectiva, 2),
            avertismente=avertismente,
            sumar_comparativ=sumar_comparativ,
            explicatie_ai=None,
            disclaimer="""
⚠️ DISCLAIMER IMPORTANT:
Acest simulator are SCOP EXCLUSIV EDUCATIV și informativ.
NU reprezintă consiliere fiscală, contabilă sau juridică.
Calculele sunt ESTIMATIVE și simplificate.
Pentru situația ta reală, consultă OBLIGATORIU un expert contabil autorizat!
Legislația fiscală se poate modifica. Verifică întotdeauna sursele oficiale ANAF.
            """.strip()
        )
        
    except Exception as e:
        logger.error(f"Eroare în simulare: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la simulare: {str(e)}")

@router.post("/explica-ai")
async def explica_situatie_cu_ai(input_data: SimulatorInput):
    """
    Folosește AI pentru a explica situația fiscală în limbaj simplu.
    Necesită integrare cu LLM.
    """
    # Întâi simulăm
    rezultat = await simuleaza_situatie_fiscala(input_data)
    
    # Construim prompt pentru AI
    context = f"""
Situația utilizatorului:
- Total entități: {len(rezultat.entitati)}
- Venituri totale estimate: {rezultat.total_venituri:,.0f} RON
- Impozite totale estimate: {rezultat.total_impozite_estimate:,.0f} RON
- Rata efectivă de impozitare: {rezultat.rata_efectiva_globala:.1f}%

Detalii pe entități:
"""
    for e in rezultat.entitati:
        context += f"\n- {e.nume} ({e.tip}): {e.venit:,.0f} RON, impozit {e.impozit_estimat:,.0f} RON ({e.rata_impozitare}%)"
        if e.scutiri_active:
            context += f" - Scutiri: {', '.join(e.scutiri_active)}"
    
    if rezultat.avertismente:
        context += "\n\nAvertismente importante:"
        for a in rezultat.avertismente:
            context += f"\n- [{a.tip.upper()}] {a.titlu}: {a.descriere}"
    
    # Pentru moment, returnăm contextul pregătit pentru AI
    # Integrarea efectivă cu LLM se poate face ulterior
    return {
        "success": True,
        "simulare": rezultat.dict(),
        "context_pentru_ai": context,
        "nota": "Integrare AI disponibilă în versiunea PRO"
    }

# ============================================
# CALCULATOR COST SALARIAL 2026
# ============================================

class SectorSalariu(str, Enum):
    NORMAL = "normal"
    CONSTRUCTII = "constructii"
    IT = "it"
    AGRICULTURA = "agricultura"
    ALIMENTAR = "alimentar"

class TipCalculSalariu(str, Enum):
    BRUT_LA_NET = "brut_la_net"
    NET_LA_BRUT = "net_la_brut"

class SalariuInput(BaseModel):
    """Input pentru calculul salarial"""
    suma: float = Field(ge=0, description="Salariu brut SAU net (RON)")
    tip_calcul: TipCalculSalariu = Field(default=TipCalculSalariu.BRUT_LA_NET)
    numar_persoane_intretinere: int = Field(default=0, ge=0, le=4)
    sector: SectorSalariu = Field(default=SectorSalariu.NORMAL)
    tip_contract: str = Field(default="full_time")  # full_time / part_time

class SalariuOutput(BaseModel):
    """Output detaliat calcul salarial"""
    salariu_brut: float
    cas_angajat: float
    cas_procent: float
    cass_angajat: float
    cass_procent: float
    deducere_personala: float
    baza_impozabila: float
    impozit_venit: float
    impozit_procent: float
    salariu_net: float
    cam_angajator: float
    cam_procent: float
    cost_total_angajator: float
    sector: str
    scutiri_aplicate: List[str]
    pasi_calcul: List[Dict]
    comparatie_sectoare: List[Dict]


def calculeaza_deducere_personala(brut: float, nr_persoane: int = 0) -> float:
    """
    Deducere personală 2026:
    - Brut <= 2,000: 300 RON
    - 2,001 - 4,050: descrescător proporțional
    - Peste 4,050: 0 RON
    - +100 RON/persoană în întreținere (max 4)
    """
    if brut <= 2000:
        deducere_baza = 300
    elif brut <= 4050:
        # Interpolare liniară descrescătoare: 300 → 0 între 2000 și 4050
        deducere_baza = 300 * (4050 - brut) / (4050 - 2000)
    else:
        deducere_baza = 0

    # Bonus persoane în întreținere (max 4)
    persoane = min(nr_persoane, 4)
    deducere_persoane = persoane * 100

    # Deducerea pentru persoane se aplică doar dacă brut <= 4050
    if brut <= 4050:
        return round(deducere_baza + deducere_persoane, 2)
    else:
        return 0


def calculeaza_salariu_din_brut(
    brut: float,
    sector: SectorSalariu,
    nr_persoane: int = 0
) -> Dict:
    """Calculează net din brut, cu toate contribuțiile"""
    scutiri = []

    # Determinăm contribuțiile pe sector
    if sector == SectorSalariu.CONSTRUCTII:
        cas_procent = 25.0  # CAS standard (angajatul plătește)
        cass_procent = 10.0
        impozit_scutit = True
        scutiri.append("Scutire impozit venit (sector construcții)")
        scutiri.append("Condiție: salariu brut >= 4,050 RON și activitate CAEN 41-43")
    elif sector == SectorSalariu.IT:
        cas_procent = 25.0
        cass_procent = 10.0
        impozit_scutit = True
        scutiri.append("Scutire impozit venit (sector IT)")
        scutiri.append("Condiții: studii superioare IT, firma cu 80%+ venituri IT, brut >= 10,000 RON")
    elif sector == SectorSalariu.AGRICULTURA:
        cas_procent = 25.0
        cass_procent = 10.0
        impozit_scutit = True
        scutiri.append("Scutire impozit venit (sector agricultură)")
        scutiri.append("Condiție: activitate agricolă conform Cod Fiscal")
    elif sector == SectorSalariu.ALIMENTAR:
        cas_procent = 25.0
        cass_procent = 10.0
        impozit_scutit = True
        scutiri.append("Scutire impozit venit (sector alimentar)")
        scutiri.append("Condiție: activitate industrie alimentară conform OUG")
    else:
        cas_procent = 25.0
        cass_procent = 10.0
        impozit_scutit = False

    # Pas 1: CAS angajat
    cas_angajat = round(brut * cas_procent / 100, 2)

    # Pas 2: CASS angajat
    cass_angajat = round(brut * cass_procent / 100, 2)

    # Pas 3: Deducere personală
    deducere = calculeaza_deducere_personala(brut, nr_persoane)

    # Pas 4: Baza impozabilă
    baza_impozabila = max(brut - cas_angajat - cass_angajat - deducere, 0)

    # Pas 5: Impozit venit
    if impozit_scutit:
        impozit_venit = 0
        impozit_procent = 0
    else:
        impozit_procent = 10.0
        impozit_venit = round(baza_impozabila * impozit_procent / 100, 2)

    # Pas 6: Net
    salariu_net = round(brut - cas_angajat - cass_angajat - impozit_venit, 2)

    # Pas 7: CAM angajator
    cam_procent = 2.25
    cam_angajator = round(brut * cam_procent / 100, 2)

    # Cost total angajator
    cost_total = round(brut + cam_angajator, 2)

    # Pași de calcul pentru afișare
    pasi = [
        {"descriere": "Salariu brut", "formula": "", "valoare": brut, "semn": ""},
        {"descriere": f"CAS angajat ({cas_procent}%)", "formula": f"{brut:,.0f} × {cas_procent}%", "valoare": cas_angajat, "semn": "-"},
        {"descriere": f"CASS angajat ({cass_procent}%)", "formula": f"{brut:,.0f} × {cass_procent}%", "valoare": cass_angajat, "semn": "-"},
    ]
    if deducere > 0:
        pasi.append({"descriere": f"Deducere personală ({nr_persoane} pers.)", "formula": "", "valoare": deducere, "semn": "info"})
    pasi.append({"descriere": "Bază impozabilă", "formula": f"{brut:,.0f} - {cas_angajat:,.0f} - {cass_angajat:,.0f} - {deducere:,.0f}", "valoare": baza_impozabila, "semn": "="})

    if impozit_scutit:
        pasi.append({"descriere": "Impozit venit (SCUTIT)", "formula": "Sector cu scutire", "valoare": 0, "semn": "-"})
    else:
        pasi.append({"descriere": f"Impozit venit ({impozit_procent}%)", "formula": f"{baza_impozabila:,.0f} × {impozit_procent}%", "valoare": impozit_venit, "semn": "-"})

    pasi.append({"descriere": "SALARIU NET", "formula": "", "valoare": salariu_net, "semn": "="})
    pasi.append({"descriere": f"CAM angajator ({cam_procent}%)", "formula": f"{brut:,.0f} × {cam_procent}%", "valoare": cam_angajator, "semn": "+"})
    pasi.append({"descriere": "COST TOTAL ANGAJATOR", "formula": f"{brut:,.0f} + {cam_angajator:,.0f}", "valoare": cost_total, "semn": "="})

    return {
        "salariu_brut": brut,
        "cas_angajat": cas_angajat,
        "cas_procent": cas_procent,
        "cass_angajat": cass_angajat,
        "cass_procent": cass_procent,
        "deducere_personala": deducere,
        "baza_impozabila": baza_impozabila,
        "impozit_venit": impozit_venit,
        "impozit_procent": impozit_procent,
        "salariu_net": salariu_net,
        "cam_angajator": cam_angajator,
        "cam_procent": cam_procent,
        "cost_total_angajator": cost_total,
        "sector": sector.value,
        "scutiri_aplicate": scutiri,
        "pasi_calcul": pasi,
    }


def calculeaza_brut_din_net(
    net_dorit: float,
    sector: SectorSalariu,
    nr_persoane: int = 0
) -> Dict:
    """Calcul invers: din net dorit găsește brutul necesar (iterativ)"""
    # Estimare inițială
    brut_estimat = net_dorit * 1.45  # Aproximare inițială

    for _ in range(50):  # Max 50 iterații
        rezultat = calculeaza_salariu_din_brut(brut_estimat, sector, nr_persoane)
        diferenta = net_dorit - rezultat["salariu_net"]

        if abs(diferenta) < 0.5:  # Precizie sub 1 RON
            break

        brut_estimat += diferenta * 0.8  # Factor de convergență

    # Recalculăm cu brutul final rotunjit
    brut_final = round(brut_estimat, 0)
    return calculeaza_salariu_din_brut(brut_final, sector, nr_persoane)


@router.post("/calcul-salariu")
async def calculeaza_cost_salarial(input_data: SalariuInput):
    """
    Calculator cost salarial complet 2026.
    Calculează brut→net sau net→brut, cu toate contribuțiile.
    Include comparație între sectoare (normal, IT, construcții, agricultură, alimentar).
    SCOP EDUCATIV!
    """
    try:
        # Calcul principal
        if input_data.tip_calcul == TipCalculSalariu.NET_LA_BRUT:
            rezultat = calculeaza_brut_din_net(
                input_data.suma,
                input_data.sector,
                input_data.numar_persoane_intretinere
            )
        else:
            rezultat = calculeaza_salariu_din_brut(
                input_data.suma,
                input_data.sector,
                input_data.numar_persoane_intretinere
            )

        brut_pentru_comparatie = rezultat["salariu_brut"]

        # Comparație între toate sectoarele
        comparatie_sectoare = []
        for sec in SectorSalariu:
            comp = calculeaza_salariu_din_brut(
                brut_pentru_comparatie,
                sec,
                input_data.numar_persoane_intretinere
            )
            comparatie_sectoare.append({
                "sector": sec.value,
                "brut": comp["salariu_brut"],
                "net": comp["salariu_net"],
                "impozit": comp["impozit_venit"],
                "cas": comp["cas_angajat"],
                "cass": comp["cass_angajat"],
                "cam": comp["cam_angajator"],
                "cost_angajator": comp["cost_total_angajator"],
                "scutiri": comp["scutiri_aplicate"],
            })

        rezultat["comparatie_sectoare"] = comparatie_sectoare

        return {
            "success": True,
            **rezultat,
            "disclaimer": "Calculator educativ. Consultați un expert contabil pentru situația dumneavoastră reală."
        }

    except Exception as e:
        logger.error(f"Eroare calcul salariu: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la calcul: {str(e)}")
