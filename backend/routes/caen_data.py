"""
Baza de date CAEN Rev.2 — cele mai comune ~80 coduri pentru antreprenori români.
Grupate pe categorii, cu regimuri fiscale speciale marcate.
SCOP EDUCATIV — verifică mereu clasificarea oficială CAEN.
"""
from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/caen", tags=["caen-database"])

# ============================================
# CAEN DATABASE — ~80 CODURI COMUNE
# ============================================

CAEN_DATABASE = {
    # ===== IT & COMUNICAȚII =====
    "6201": {"nume": "Activități de realizare a software-ului la comandă", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT, angajați cu studii superioare IT, brut ≥ 10.000 RON"},
    "6202": {"nume": "Activități de consultanță în tehnologia informației", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT"},
    "6203": {"nume": "Activități de management al mijloacelor de calcul", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT"},
    "6209": {"nume": "Alte activități de servicii privind tehnologia informației", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT"},
    "6311": {"nume": "Prelucrarea datelor, administrarea paginilor web", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT"},
    "6312": {"nume": "Activități ale portalurilor web", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT"},
    "6110": {"nume": "Activități de telecomunicații prin cablu", "categorie": "IT", "scutire_impozit_venit": False},
    "6120": {"nume": "Activități de telecomunicații prin wireless", "categorie": "IT", "scutire_impozit_venit": False},
    "5821": {"nume": "Activități de editare a jocurilor de calculator", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT"},
    "5829": {"nume": "Activități de editare a altor programe", "categorie": "IT", "scutire_impozit_venit": True, "scutire_profit": True, "conditii": "80%+ venituri IT"},

    # ===== CONSTRUCȚII =====
    "4110": {"nume": "Dezvoltare (promovare) imobiliară", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați, brut ≥ 4.050 RON"},
    "4120": {"nume": "Lucrări de construcții a clădirilor rezidențiale și nerezidențiale", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4211": {"nume": "Lucrări de construcții a drumurilor și autostrăzilor", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4221": {"nume": "Lucrări de construcții a proiectelor utilitare pentru fluide", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4299": {"nume": "Lucrări de construcții a altor proiecte inginerești", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4311": {"nume": "Lucrări de demolare a construcțiilor", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4321": {"nume": "Lucrări de instalații electrice", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4322": {"nume": "Lucrări de instalații sanitare, de încălzire și de aer condiționat", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4331": {"nume": "Lucrări de tencuire", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4332": {"nume": "Lucrări de tâmplărie și dulgherie", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4333": {"nume": "Lucrări de pardosire și placare a pereților", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4334": {"nume": "Lucrări de vopsitorie, zugrăveli și montări de geamuri", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4339": {"nume": "Alte lucrări de finisare", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4391": {"nume": "Lucrări de învelitori, șarpante și terase la construcții", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},
    "4399": {"nume": "Alte lucrări speciale de construcții n.c.a.", "categorie": "Construcții", "regim_special_salarii": True, "conditii": "Scutire impozit venit angajați"},

    # ===== COMERȚ =====
    "4711": {"nume": "Comerț cu amănuntul în magazine nespecializate, cu vânzare predominantă de produse alimentare", "categorie": "Comerț"},
    "4719": {"nume": "Comerț cu amănuntul în magazine nespecializate, cu vânzare predominantă de produse nealimentare", "categorie": "Comerț"},
    "4721": {"nume": "Comerț cu amănuntul al fructelor și legumelor proaspete", "categorie": "Comerț"},
    "4741": {"nume": "Comerț cu amănuntul al calculatoarelor, echipamentelor periferice și software-ului", "categorie": "Comerț"},
    "4751": {"nume": "Comerț cu amănuntul al textilelor", "categorie": "Comerț"},
    "4771": {"nume": "Comerț cu amănuntul al îmbrăcămintei", "categorie": "Comerț"},
    "4773": {"nume": "Comerț cu amănuntul al produselor farmaceutice (farmacie)", "categorie": "Comerț"},
    "4791": {"nume": "Comerț cu amănuntul prin intermediul caselor de comenzi sau prin Internet", "categorie": "Comerț"},
    "4690": {"nume": "Comerț cu ridicata nespecializat", "categorie": "Comerț"},
    "4619": {"nume": "Intermedieri în comerțul cu produse diverse", "categorie": "Comerț"},

    # ===== HoReCa =====
    "5510": {"nume": "Hoteluri și alte facilități de cazare similare", "categorie": "HoReCa"},
    "5520": {"nume": "Facilități de cazare pentru vacanțe și alte locuințe de scurtă durată", "categorie": "HoReCa"},
    "5590": {"nume": "Alte servicii de cazare", "categorie": "HoReCa"},
    "5610": {"nume": "Restaurante (activități de alimentație)", "categorie": "HoReCa"},
    "5621": {"nume": "Activități de alimentație (catering) pentru evenimente", "categorie": "HoReCa"},
    "5630": {"nume": "Baruri și alte activități de servire a băuturilor", "categorie": "HoReCa"},

    # ===== TRANSPORT =====
    "4931": {"nume": "Transporturi urbane, suburbane și metropolitane de călători", "categorie": "Transport"},
    "4932": {"nume": "Transporturi cu taxiuri", "categorie": "Transport"},
    "4939": {"nume": "Alte transporturi terestre de călători n.c.a.", "categorie": "Transport"},
    "4941": {"nume": "Transporturi rutiere de mărfuri", "categorie": "Transport"},
    "5210": {"nume": "Depozitări", "categorie": "Transport"},
    "5310": {"nume": "Activități poștale desfășurate sub obligativitatea serviciului universal", "categorie": "Transport"},
    "5320": {"nume": "Alte activități poștale și de curier", "categorie": "Transport"},

    # ===== SĂNĂTATE =====
    "8610": {"nume": "Activități de asistență spitalicească", "categorie": "Sănătate", "scutire_tva": True, "conditii": "Servicii medicale scutite TVA"},
    "8621": {"nume": "Activități de asistență medicală generală", "categorie": "Sănătate", "scutire_tva": True, "conditii": "Servicii medicale scutite TVA"},
    "8622": {"nume": "Activități de asistență medicală specializată", "categorie": "Sănătate", "scutire_tva": True, "conditii": "Servicii medicale scutite TVA"},
    "8623": {"nume": "Activități de asistență stomatologică", "categorie": "Sănătate", "scutire_tva": True, "conditii": "Servicii medicale scutite TVA"},
    "8690": {"nume": "Alte activități referitoare la sănătatea umană", "categorie": "Sănătate", "scutire_tva": True, "conditii": "Servicii medicale scutite TVA"},

    # ===== EDUCAȚIE =====
    "8510": {"nume": "Învățământ preșcolar", "categorie": "Educație", "scutire_tva": True, "conditii": "Educație scutită TVA"},
    "8520": {"nume": "Învățământ primar", "categorie": "Educație", "scutire_tva": True, "conditii": "Educație scutită TVA"},
    "8531": {"nume": "Învățământ secundar general", "categorie": "Educație", "scutire_tva": True, "conditii": "Educație scutită TVA"},
    "8541": {"nume": "Învățământ superior non-universitar", "categorie": "Educație", "scutire_tva": True, "conditii": "Educație scutită TVA"},
    "8551": {"nume": "Învățământ în domeniul sportiv și recreativ", "categorie": "Educație", "scutire_tva": True, "conditii": "Educație scutită TVA"},
    "8552": {"nume": "Învățământ în domeniul cultural (arte, muzică)", "categorie": "Educație", "scutire_tva": True, "conditii": "Educație scutită TVA"},
    "8559": {"nume": "Alte forme de învățământ n.c.a.", "categorie": "Educație", "scutire_tva": True, "conditii": "Cursuri, training-uri scutite TVA"},

    # ===== AGRICULTURĂ =====
    "0111": {"nume": "Cultivarea cerealelor (exclusiv orez), plantelor leguminoase", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},
    "0113": {"nume": "Cultivarea legumelor și a pepenilor, a rădăcinoaselor", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},
    "0121": {"nume": "Cultivarea strugurilor", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},
    "0141": {"nume": "Creșterea bovinelor de lapte", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},
    "0145": {"nume": "Creșterea ovinelor și caprinelor", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},
    "0150": {"nume": "Activități în ferme mixte (cultură vegetală combinată cu creșterea animalelor)", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},
    "0161": {"nume": "Activități auxiliare pentru producția vegetală", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},
    "0322": {"nume": "Acvacultură în ape dulci", "categorie": "Agricultură", "regim_special_tva": True, "conditii": "Regim special TVA agricultură"},

    # ===== SERVICII PROFESIONALE =====
    "6910": {"nume": "Activități juridice (avocatură)", "categorie": "Servicii Profesionale"},
    "6920": {"nume": "Activități de contabilitate și audit financiar; consultanță fiscală", "categorie": "Servicii Profesionale"},
    "7010": {"nume": "Activități ale direcțiilor (centralelor), birourilor administrative centralizate", "categorie": "Servicii Profesionale"},
    "7021": {"nume": "Activități de consultanță în domeniul relațiilor publice și al comunicării", "categorie": "Servicii Profesionale"},
    "7022": {"nume": "Activități de consultanță pentru afaceri și management", "categorie": "Servicii Profesionale"},
    "7111": {"nume": "Activități de arhitectură", "categorie": "Servicii Profesionale"},
    "7112": {"nume": "Activități de inginerie și consultanță tehnică legate de acestea", "categorie": "Servicii Profesionale"},
    "7311": {"nume": "Activități ale agențiilor de publicitate", "categorie": "Servicii Profesionale"},
    "7312": {"nume": "Servicii de reprezentare media", "categorie": "Servicii Profesionale"},
    "7320": {"nume": "Activități de studiere a pieței și de sondare a opiniei publice", "categorie": "Servicii Profesionale"},
    "7410": {"nume": "Activități de design specializat", "categorie": "Servicii Profesionale"},
    "7420": {"nume": "Activități fotografice", "categorie": "Servicii Profesionale"},
    "7490": {"nume": "Alte activități profesionale, științifice și tehnice n.c.a.", "categorie": "Servicii Profesionale"},

    # ===== IMOBILIARE =====
    "6810": {"nume": "Cumpărarea și vânzarea de bunuri imobiliare proprii", "categorie": "Imobiliare"},
    "6820": {"nume": "Închirierea și subînchirierea bunurilor imobiliare proprii sau închiriate", "categorie": "Imobiliare"},
    "6831": {"nume": "Agenții imobiliare", "categorie": "Imobiliare"},

    # ===== BEAUTY & WELLNESS =====
    "9602": {"nume": "Coafură și alte activități de înfrumusețare", "categorie": "Beauty & Wellness"},
    "9604": {"nume": "Activități de întreținere corporală", "categorie": "Beauty & Wellness"},
    "9311": {"nume": "Activități ale bazelor sportive", "categorie": "Beauty & Wellness"},
    "9313": {"nume": "Activități ale centrelor de fitness", "categorie": "Beauty & Wellness"},
}

# Categorii grupate pentru frontend
CAEN_CATEGORII = [
    "IT",
    "Construcții",
    "Comerț",
    "HoReCa",
    "Transport",
    "Sănătate",
    "Educație",
    "Agricultură",
    "Servicii Profesionale",
    "Imobiliare",
    "Beauty & Wellness",
]


def get_caen_info(cod: str) -> Optional[dict]:
    """Returnează info despre un cod CAEN"""
    if cod and cod in CAEN_DATABASE:
        return {"cod": cod, **CAEN_DATABASE[cod]}
    return None


def search_caen(query: str) -> list:
    """Caută în baza CAEN după cod sau nume"""
    query = query.lower().strip()
    results = []
    for cod, info in CAEN_DATABASE.items():
        if query in cod or query in info["nume"].lower():
            results.append({"cod": cod, **info})
    return results


# ============================================
# ENDPOINTS
# ============================================

@router.get("/search")
async def search_caen_codes(q: str = "", categorie: str = ""):
    """Caută coduri CAEN. ?q=software sau ?q=6201 sau ?categorie=IT"""
    results = []

    if q:
        results = search_caen(q)
    elif categorie:
        results = [
            {"cod": cod, **info}
            for cod, info in CAEN_DATABASE.items()
            if info.get("categorie", "").lower() == categorie.lower()
        ]
    else:
        # Returnează toate, grupate
        results = [{"cod": cod, **info} for cod, info in CAEN_DATABASE.items()]

    return {
        "success": True,
        "count": len(results),
        "results": results,
    }


@router.get("/categorii")
async def get_categorii():
    """Returnează lista categoriilor CAEN"""
    categorii_count = {}
    for info in CAEN_DATABASE.values():
        cat = info.get("categorie", "Altele")
        categorii_count[cat] = categorii_count.get(cat, 0) + 1

    return {
        "success": True,
        "categorii": [
            {"nume": cat, "count": categorii_count.get(cat, 0)}
            for cat in CAEN_CATEGORII
        ]
    }


@router.get("/{cod}")
async def get_caen_code(cod: str):
    """Returnează detalii despre un cod CAEN specific"""
    info = get_caen_info(cod)
    if not info:
        return {"success": False, "error": f"Codul CAEN {cod} nu a fost găsit"}
    return {"success": True, **info}
