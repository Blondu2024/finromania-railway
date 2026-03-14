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
# CONSTANTE FISCALE ROMÂNIA 2025
# SCOP EDUCATIV - ACTUALIZAT IANUARIE 2025
# ============================================

# Praguri importante
PRAG_TVA = 300000  # RON - prag înregistrare TVA obligatorie
PRAG_MICRO_EUR = 500000  # EUR - prag maxim venituri micro
PRAG_DETINERE_AGREGARE = 25  # % - dacă deții >25% în mai multe firme, veniturile se agregă

# Curs EUR aproximativ
CURS_EUR = 5.0  # RON/EUR

# Impozite micro
MICRO_CU_ANGAJAT = 1  # %
MICRO_FARA_ANGAJAT = 3  # %

# Impozit profit standard
IMPOZIT_PROFIT = 16  # %

# PFA
PFA_IMPOZIT = 10  # %
PFA_CASS = 10  # %
PFA_CAS = 25  # % (opțional)

# CASS
SALARIU_MINIM = 4050  # RON 2025
CASS_BAZA_MINIMA = 6 * SALARIU_MINIM  # 24,300 RON
CASS_BAZA_MAXIMA = 60 * SALARIU_MINIM  # 243,000 RON

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

class SimulatorInput(BaseModel):
    """Input pentru simulatorul fiscal"""
    entitati: List[EntitateInput] = Field(default=[], description="Lista entităților")
    are_salariu: bool = Field(default=False, description="Are salariu cu CASS plătit")
    salariu_brut_lunar: float = Field(default=0, ge=0, description="Salariu brut lunar RON")

class AvertismentFiscal(BaseModel):
    """Un avertisment despre situația fiscală"""
    tip: str  # "info", "warning", "danger"
    titlu: str
    descriere: str
    actiune_recomandata: Optional[str] = None

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

class SimulatorOutput(BaseModel):
    """Output-ul simulatorului"""
    entitati: List[RezultatEntitate]
    total_venituri: float
    total_impozite_estimate: float
    rata_efectiva_globala: float
    avertismente: List[AvertismentFiscal]
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

def calculeaza_impozit_entitate(entitate: EntitateInput) -> RezultatEntitate:
    """Calculează impozitul estimat pentru o entitate"""
    venit = entitate.venit_anual_estimat
    scutiri = []
    observatii = []
    impozit = 0
    rata = 0
    regim_tva = "Neînregistrat TVA"
    
    # Verifică scutiri CAEN (tratăm "none" ca None)
    cod_caen = entitate.cod_caen if entitate.cod_caen and entitate.cod_caen != "none" else None
    info_caen = verifica_scutiri_caen(cod_caen) if cod_caen else {}
    
    if entitate.tip == TipEntitate.PF:
        # Persoană fizică - nu plătește impozite pe activitate economică direct
        observatii.append("Ca PF, veniturile din activități economice trebuie declarate prin PFA/PFI sau SRL")
        rata = 0
        impozit = 0
        
    elif entitate.tip in [TipEntitate.PFA_NORMA, TipEntitate.PFA_REAL]:
        rata = PFA_IMPOZIT
        if entitate.tip == TipEntitate.PFA_NORMA:
            observatii.append("PFA Normă de venit - impozit fix pe norma stabilită de ANAF pentru activitate")
            # La norma, impozitul e pe norma, nu pe venit real
            impozit = venit * 0.10  # Simplificat pentru educativ
        else:
            observatii.append("PFA Sistem Real - 10% pe venitul net (venit - cheltuieli)")
            impozit = venit * 0.10
        observatii.append("CASS 10% datorat dacă veniturile depășesc 6 salarii minime/an")
        
    elif entitate.tip == TipEntitate.PFI:
        rata = PFA_IMPOZIT
        impozit = venit * rata / 100
        observatii.append("PFI (Profesie liberală) - 10% impozit + CASS 10%")
        
    elif entitate.tip == TipEntitate.SRL_MICRO:
        if info_caen.get("scutire_profit"):
            scutiri.append(f"Scutire impozit profit - {info_caen.get('conditii', '')}")
            rata = 0
            impozit = 0
            observatii.append("ATENȚIE: Scutirea se aplică doar dacă îndeplinești toate condițiile!")
        else:
            rata = MICRO_CU_ANGAJAT if entitate.are_angajati else MICRO_FARA_ANGAJAT
            impozit = venit * rata / 100
            observatii.append(f"Micro {'1%' if entitate.are_angajati else '3%'} pe cifra de afaceri")
            
    elif entitate.tip == TipEntitate.SRL_PROFIT:
        if info_caen.get("scutire_profit"):
            scutiri.append(f"Scutire impozit profit - {info_caen.get('conditii', '')}")
            rata = 0
            impozit = 0
        else:
            rata = IMPOZIT_PROFIT
            impozit = venit * 0.20 * rata / 100  # Presupunem 20% profit din venit
            observatii.append("16% impozit pe profit (estimat 20% marjă de profit)")
    
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
        observatii=observatii
    )

def verifica_agregare_micro(entitati: List[EntitateInput]) -> List[AvertismentFiscal]:
    """Verifică regula agregării veniturilor pentru micro"""
    avertismente = []
    
    # Găsește SRL-uri micro cu deținere >25%
    srl_micro_relevante = [
        e for e in entitati 
        if e.tip == TipEntitate.SRL_MICRO and e.procent_detinere > PRAG_DETINERE_AGREGARE
    ]
    
    if len(srl_micro_relevante) > 1:
        total_venituri = sum(e.venit_anual_estimat for e in srl_micro_relevante)
        prag_micro_ron = PRAG_MICRO_EUR * CURS_EUR
        
        avertismente.append(AvertismentFiscal(
            tip="warning",
            titlu="Agregare venituri micro-întreprinderi",
            descriere=f"Deții >25% în {len(srl_micro_relevante)} SRL-uri micro. Conform legii, veniturile se AGREGĂ pentru verificarea pragului de 500.000 EUR.",
            actiune_recomandata=f"Total agregat: {total_venituri:,.0f} RON. Pragul este {prag_micro_ron:,.0f} RON ({PRAG_MICRO_EUR:,} EUR)."
        ))
        
        if total_venituri > prag_micro_ron:
            avertismente.append(AvertismentFiscal(
                tip="danger",
                titlu="⚠️ Depășire prag micro prin agregare!",
                descriere=f"Veniturile agregate ({total_venituri:,.0f} RON) depășesc pragul micro!",
                actiune_recomandata="Una sau mai multe firme trebuie să treacă la impozit pe profit 16%. Consultă un expert contabil!"
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
                "descriere": "Prag pentru înregistrare obligatorie TVA"
            },
            "micro": {
                "valoare": PRAG_MICRO_EUR,
                "moneda": "EUR",
                "descriere": "Plafon maxim venituri pentru regim micro-întreprindere"
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
            }
        },
        "actualizat": "Ianuarie 2025",
        "disclaimer": "Valorile pot suferi modificări legislative. Verificați sursele oficiale ANAF."
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
        
        # Verifică reguli de agregare
        avertismente.extend(verifica_agregare_micro(input_data.entitati))
        
        # Verifică TVA
        avertismente.extend(verifica_tva_global(input_data.entitati))
        
        # Verifică CASS
        if not input_data.are_salariu:
            total_venituri_pfa = sum(
                e.venit_anual_estimat for e in input_data.entitati 
                if e.tip in [TipEntitate.PFA_NORMA, TipEntitate.PFA_REAL, TipEntitate.PFI]
            )
            if total_venituri_pfa > CASS_BAZA_MINIMA:
                avertismente.append(AvertismentFiscal(
                    tip="info",
                    titlu="CASS datorat din PFA/PFI",
                    descriere=f"Veniturile din PFA/PFI depășesc {CASS_BAZA_MINIMA:,} RON. Datorezi CASS 10%.",
                    actiune_recomandata=f"CASS estimat: {min(total_venituri_pfa, CASS_BAZA_MAXIMA) * 0.10:,.0f} RON/an"
                ))
        
        # Calculează totaluri
        total_venituri = sum(r.venit for r in rezultate_entitati)
        total_impozite = sum(r.impozit_estimat for r in rezultate_entitati)
        rata_efectiva = (total_impozite / total_venituri * 100) if total_venituri > 0 else 0
        
        return SimulatorOutput(
            entitati=rezultate_entitati,
            total_venituri=round(total_venituri, 2),
            total_impozite_estimate=round(total_impozite, 2),
            rata_efectiva_globala=round(rata_efectiva, 2),
            avertismente=avertismente,
            explicatie_ai=None,  # Va fi populat separat dacă user-ul cere
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
