"""Education routes pentru FinRomania - Curs și E-Book"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
import os
from config.database import get_database
from routes.auth import get_current_user, require_auth
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
)

router = APIRouter(prefix="/education", tags=["education"])

# Fixed package price - NEVER accept from frontend
EDUCATION_PACKAGE = {
    "id": "edu_starter_pack",
    "name": "Pachet Educațional Complet",
    "description": "E-Book PDF + Mini-Curs Online (6 lecții)",
    "price": 5.00,  # 5 RON
    "currency": "ron"
}

# Course content - lessons
COURSE_LESSONS = [
    {
        "id": "lesson_1",
        "order": 1,
        "title": "Introducere în Lumea Investițiilor",
        "description": "Descoperă de ce investițiile sunt importante și cum te pot ajuta să îți atingi obiectivele financiare.",
        "duration": "10 min",
        "content": """## Ce înseamnă să investești?

Investiția reprezintă alocarea resurselor (de obicei bani) cu scopul de a genera un câștig sau profit în viitor. Spre deosebire de economisire, unde banii tăi stau într-un cont și își pierd valoarea din cauza inflației, investițiile îți oferă oportunitatea de a-ți crește averea.

### De ce să investești?

**1. Protecție împotriva inflației**
Inflația este "tăcutul hoț" care îți reduce puterea de cumpărare. Dacă inflația este 5% pe an, 1000 RON de azi vor valora doar 950 RON peste un an în termeni reali.

**2. Efectul dobânzii compuse**
Albert Einstein a numit dobânda compusă "a opta minune a lumii". Când reinvestești câștigurile, acestea generează la rândul lor câștiguri - efect de bulgăre de zăpadă!

**Exemplu practic:**
- Investești 1000 RON cu randament 10% anual
- După 1 an: 1100 RON
- După 10 ani: 2594 RON
- După 30 ani: 17449 RON!

**3. Independență financiară**
Investițiile pe termen lung îți pot asigura un venit pasiv care să îți permită libertatea de a alege cum îți petreci timpul.

### Mitul "Trebuie să fii bogat ca să investești"

FALS! Poți începe cu sume mici - chiar și 50-100 RON pe lună. Important este să începi cât mai devreme pentru a beneficia de efectul timpului.

### Concluzie

Investițiile nu sunt doar pentru "oamenii bogați" sau "experții în finanțe". Cu educație și răbdare, oricine poate deveni un investitor de succes.""",
        "is_free": True
    },
    {
        "id": "lesson_2",
        "order": 2,
        "title": "Tipuri de Instrumente Financiare",
        "description": "Învață diferențele dintre acțiuni, obligațiuni, ETF-uri și fonduri mutuale.",
        "duration": "15 min",
        "content": """## Instrumentele Financiare Explicate Simplu

### 1. Acțiunile (Stocks)

O acțiune reprezintă o "felie" din proprietatea unei companii. Când cumperi o acțiune Apple, devii co-proprietar al Apple!

**Avantaje:**
- Potențial de creștere nelimitat
- Dividende (distribuiri de profit)
- Drept de vot în adunările acționarilor

**Dezavantaje:**
- Volatilitate ridicată
- Risc de pierdere a capitalului
- Necesită cercetare și monitorizare

### 2. Obligațiunile (Bonds)

O obligațiune este un "împrumut" pe care îl acorzi unei companii sau guvernului. În schimb, primești dobândă regulată.

**Exemplu:** Cumperi obligațiuni de stat românești cu dobândă 7% pe an. Investești 10.000 RON și primești 700 RON/an.

**Avantaje:**
- Venit predictibil
- Risc mai mic decât acțiunile
- Prioritate la faliment

**Dezavantaje:**
- Randament mai mic
- Sensibilitate la rata dobânzii

### 3. ETF-uri (Exchange-Traded Funds)

ETF-urile sunt "coșuri" de acțiuni sau obligațiuni tranzacționate la bursă. Un singur ETF îți oferă diversificare instantă!

**Exemplu popular:** S&P 500 ETF - investești în cele mai mari 500 companii americane cu o singură achiziție.

**Avantaje:**
- Diversificare automată
- Costuri reduse
- Lichiditate ridicată

### 4. Fonduri Mutuale

Similare cu ETF-urile, dar gestionate activ de profesioniști care încearcă să "bată" piața.

**Diferența cheie:** ETF-urile urmăresc un indice pasiv, fondurile mutuale încearcă să îl depășească.

### Recomandare pentru începători

🎯 **Începe cu ETF-uri** - oferă diversificare, costuri mici și nu necesită expertiză în alegerea acțiunilor individuale.""",
        "is_free": False
    },
    {
        "id": "lesson_3",
        "order": 3,
        "title": "Cum Funcționează Bursa",
        "description": "Înțelege mecanismele pieței de capital și cum se formează prețurile.",
        "duration": "12 min",
        "content": """## Bursa - Piața unde se întâlnesc cumpărătorii și vânzătorii

### Ce este Bursa de Valori?

Bursa este o piață organizată unde se tranzacționează instrumente financiare (acțiuni, obligațiuni, etc.). În România avem **Bursa de Valori București (BVB)**.

### Cum se formează prețul?

Prețul unei acțiuni este determinat de **cerere și ofertă**:
- Mulți cumpărători + puțini vânzători = prețul CREȘTE
- Puțini cumpărători + mulți vânzători = prețul SCADE

### Indicii Bursieri

Indicii sunt "termometre" care măsoară performanța pieței:

**România:**
- **BET** - cele mai lichide 20 companii de pe BVB
- **BET-TR** - BET cu dividende reinvestite

**Global:**
- **S&P 500** - 500 cele mai mari companii americane
- **Dow Jones** - 30 companii industriale majore
- **NASDAQ** - focus pe tehnologie
- **DAX** - cele mai mari 40 companii germane

### Programul Bursei

**BVB:** Luni-Vineri, 10:00-17:45 (ora României)
**NYSE/NASDAQ:** Luni-Vineri, 16:30-23:00 (ora României)

### Tipuri de Ordine

**1. Ordin la piață (Market Order)**
Cumperi/vinzi imediat la cel mai bun preț disponibil.

**2. Ordin limită (Limit Order)**
Cumperi/vinzi doar dacă prețul atinge nivelul dorit.

**Exemplu:**
- Acțiunea TLV costă 28 RON
- Plasezi ordin limită de cumpărare la 27 RON
- Ordinul se execută doar dacă prețul scade la 27 RON

### Bull Market vs Bear Market

🐂 **Bull Market** - piață în creștere (optimism)
🐻 **Bear Market** - piață în scădere (pesimism)

### Concluzie

Bursa nu este cazinou! Este o piață reglementată unde poți investi în companii reale și în creșterea economiei.""",
        "is_free": False
    },
    {
        "id": "lesson_4",
        "order": 4,
        "title": "Strategii pentru Începători",
        "description": "Descoperă DCA, diversificarea și alte strategii dovedite de succes.",
        "duration": "15 min",
        "content": """## Strategii de Investiții pentru Începători

### 1. DCA - Dollar Cost Averaging (Investiție Periodică)

Cea mai recomandată strategie pentru începători!

**Cum funcționează:**
Investești o sumă fixă regulat (lunar), indiferent de prețul pieței.

**Exemplu:**
- Investești 500 RON/lună în ETF S&P 500
- Luna 1: preț 100 RON → cumperi 5 unități
- Luna 2: preț 80 RON → cumperi 6.25 unități
- Luna 3: preț 120 RON → cumperi 4.17 unități

**Rezultat:** Preț mediu de achiziție = 96.77 RON (mai mic decât media aritmetică!)

**Avantaje:**
- Elimină stresul de a "ghici" momentul perfect
- Reduce riscul de a cumpăra la vârf
- Creează obișnuința de a investi

### 2. Diversificarea - "Nu pune toate ouăle într-un singur coș"

**Tipuri de diversificare:**

**a) Pe clase de active:**
- 60% Acțiuni
- 30% Obligațiuni
- 10% Cash/Aur

**b) Pe zone geografice:**
- 50% SUA
- 30% Europa
- 20% Piețe emergente

**c) Pe sectoare:**
- Tehnologie, Sănătate, Finanțe, Energie, etc.

### 3. Buy and Hold (Cumpără și Păstrează)

Cumperi investiții de calitate și le păstrezi pe termen lung (5-10-20 ani), ignorând fluctuațiile pe termen scurt.

**Statistică:** Dacă ai fi investit în S&P 500 în orice moment din ultimii 50 ani și ai fi păstrat 20 ani, nu ai fi pierdut niciodată bani!

### 4. Rebalansarea Portofoliului

O dată pe an, verifică dacă alocarea ta s-a schimbat și readuce-o la ținta inițială.

**Exemplu:**
- Țintă: 70% acțiuni, 30% obligațiuni
- După un an de creștere: 80% acțiuni, 20% obligațiuni
- Rebalansare: vinzi acțiuni, cumperi obligațiuni

### ⚠️ Greșeli de Evitat

1. **Timing-ul pieței** - nimeni nu poate prezice constant piața
2. **Investiții bazate pe emoții** - frica și lăcomia sunt dușmanii tăi
3. **Lipsa diversificării** - nu te baza pe o singură acțiune
4. **Verificarea obsesivă** - nu verifica portofoliul zilnic!

### Regula de Aur

📌 **Investește doar bani pe care îți permiți să îi pierzi și pe care nu îi vei avea nevoie în următorii 5+ ani.**""",
        "is_free": False
    },
    {
        "id": "lesson_5",
        "order": 5,
        "title": "Analiza unei Acțiuni",
        "description": "Învață să evaluezi o companie înainte de a investi.",
        "duration": "18 min",
        "content": """## Cum Analizezi o Acțiune

### Două Abordări Principale

**1. Analiza Fundamentală** - evaluezi compania în sine
**2. Analiza Tehnică** - studiezi graficele și pattern-urile de preț

### Analiza Fundamentală - Indicatori Cheie

**1. P/E Ratio (Price-to-Earnings)**
Cât plătești pentru fiecare leu de profit.

- P/E = Preț acțiune / Profit per acțiune
- P/E < 15 = posibil subevaluat
- P/E > 25 = posibil supraevaluat

**⚠️ Atenție:** Companiile de creștere (tech) au P/E mai mare!

**2. Dividend Yield (Randamentul Dividendului)**
Cât primești anual ca dividend raportat la preț.

- Dividend Yield = Dividend anual / Preț acțiune × 100
- > 3% = randament atractiv

**3. ROE (Return on Equity)**
Cât de eficient folosește compania banii acționarilor.

- ROE > 15% = excelent
- ROE 10-15% = bun
- ROE < 10% = atenție

**4. Debt-to-Equity (Datorie/Capital)**
Cât de îndatorată este compania.

- < 1 = sănătos
- > 2 = risc ridicat

### Analiza Tehnică - Concepte de Bază

**1. Trend**
- Uptrend: minime crescătoare
- Downtrend: maxime descrescătoare
- Sideways: fără direcție clară

**2. Suport și Rezistență**
- Suport: nivel unde prețul tinde să se oprească din scădere
- Rezistență: nivel unde prețul tinde să se oprească din creștere

**3. Medii Mobile**
- MA50: media ultimelor 50 zile
- MA200: media ultimelor 200 zile
- Preț > MA200 = trend pozitiv

### Checklist Înainte de a Cumpăra

✅ Înțeleg ce face compania?
✅ Are avantaj competitiv (moat)?
✅ Profitabilă și în creștere?
✅ Datorie gestionabilă?
✅ Management de încredere?
✅ Preț rezonabil (P/E)?
✅ Diversific suficient?

### Resurse pentru Cercetare

- **Yahoo Finance** - date financiare gratuite
- **TradingView** - grafice și analiză tehnică
- **Rapoarte anuale** - direct de pe site-ul companiei

### Sfat Final

🎯 **Investește în ce înțelegi!** Dacă nu poți explica în 2 minute ce face compania, probabil nu ar trebui să investești în ea.""",
        "is_free": False
    },
    {
        "id": "lesson_6",
        "order": 6,
        "title": "Construiește-ți Primul Portofoliu",
        "description": "Ghid pas cu pas pentru a începe să investești astăzi.",
        "duration": "15 min",
        "content": """## Ghid Practic: Primul Tău Portofoliu

### Pasul 1: Stabilește-ți Fondul de Urgență

Înainte de a investi, asigură-te că ai **3-6 luni de cheltuieli** într-un cont de economii. Aceasta este plasa ta de siguranță!

### Pasul 2: Definește-ți Obiectivele

**Întrebări cheie:**
- Pentru ce investesc? (pensie, casă, educație copii)
- Pe ce termen? (scurt < 3 ani, mediu 3-10 ani, lung > 10 ani)
- Cât pot investi lunar fără să afectez stilul de viață?

### Pasul 3: Alege Alocarea Activelor

**Portofoliu Conservator (risc scăzut):**
- 30% Acțiuni (ETF-uri)
- 60% Obligațiuni
- 10% Cash

**Portofoliu Echilibrat (risc mediu):**
- 60% Acțiuni (ETF-uri)
- 30% Obligațiuni
- 10% Cash/Aur

**Portofoliu Agresiv (risc ridicat):**
- 80% Acțiuni (ETF-uri)
- 15% Obligațiuni
- 5% Cripto (opțional)

### Pasul 4: Deschide un Cont de Brokeraj

**Opțiuni pentru România:**
- **Tradeville** - broker românesc, acces BVB + internațional
- **XTB** - fără comision pentru acțiuni/ETF-uri
- **Interactive Brokers** - profesional, acces global

### Pasul 5: Începe cu ETF-uri Simple

**Portofoliu minim recomandat:**

1. **VWCE (Vanguard FTSE All-World)** - 70%
   - Acces la 3000+ companii din întreaga lume
   - O singură investiție = diversificare globală

2. **Obligațiuni guvernamentale RO sau ETF obligațiuni** - 30%
   - Stabilitate și venit

### Pasul 6: Automatizează

- Setează transfer automat lunar către contul de brokeraj
- Cumpără la aceeași dată în fiecare lună (DCA)
- Nu te uita la portofoliu mai des de o dată pe lună

### Exemplu Practic

**Buget: 500 RON/lună**

| Investiție | Alocare | Sumă |
|------------|---------|------|
| VWCE (ETF Global) | 70% | 350 RON |
| Obligațiuni RO | 30% | 150 RON |

**În 10 ani cu randament 7%:** ~86.000 RON (din 60.000 investiți)

### Checklist Final

✅ Fond de urgență: 3-6 luni cheltuieli
✅ Obiective clare definite
✅ Alocare adaptată profilului de risc
✅ Cont de brokeraj deschis
✅ Primele investiții făcute
✅ Automatizare setată
✅ Calendar de rebalansare anuală

### Felicitări! 🎉

Ai parcurs toate lecțiile! Acum ai cunoștințele de bază pentru a începe călătoria ta în lumea investițiilor.

**Următorul pas:** Creează-ți un cont pe FinRomania și folosește portofoliul virtual pentru a practica fără risc!""",
        "is_free": False
    }
]

class CheckoutRequest(BaseModel):
    origin_url: str

class LessonProgress(BaseModel):
    lesson_id: str
    completed: bool = False

@router.get("/package")
async def get_education_package():
    """Get education package details"""
    return {
        **EDUCATION_PACKAGE,
        "lessons_count": len(COURSE_LESSONS),
        "includes": [
            "E-Book PDF: Ghidul Începătorului în Investiții (~40 pagini)",
            "Mini-Curs Online: 6 lecții interactive",
            "Quiz final cu certificat de completare",
            "Acces permanent la conținut"
        ]
    }

@router.get("/lessons")
async def get_lessons(request: Request):
    """Get all lessons - free preview for first lesson, full content for paid users"""
    user = await get_current_user(request)
    
    # Check if user has purchased
    has_access = False
    if user:
        db = await get_database()
        purchase = await db.education_purchases.find_one({
            "user_id": user["user_id"],
            "status": "completed"
        })
        has_access = purchase is not None
    
    lessons = []
    for lesson in COURSE_LESSONS:
        lesson_data = {
            "id": lesson["id"],
            "order": lesson["order"],
            "title": lesson["title"],
            "description": lesson["description"],
            "duration": lesson["duration"],
            "is_free": lesson["is_free"],
            "is_locked": not lesson["is_free"] and not has_access
        }
        
        # Include content only for free lessons or if user has access
        if lesson["is_free"] or has_access:
            lesson_data["content"] = lesson["content"]
        
        lessons.append(lesson_data)
    
    return {
        "lessons": lessons,
        "has_access": has_access,
        "total_lessons": len(lessons),
        "free_lessons": sum(1 for l in lessons if l["is_free"])
    }

@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, request: Request):
    """Get single lesson content"""
    user = await get_current_user(request)
    
    lesson = next((l for l in COURSE_LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lecția nu a fost găsită")
    
    # Check access
    has_access = lesson["is_free"]
    if not has_access and user:
        db = await get_database()
        purchase = await db.education_purchases.find_one({
            "user_id": user["user_id"],
            "status": "completed"
        })
        has_access = purchase is not None
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Trebuie să achiziționezi pachetul pentru această lecție")
    
    return lesson

@router.post("/checkout")
async def create_checkout(data: CheckoutRequest, request: Request):
    """Create Stripe checkout session for education package"""
    user = await get_current_user(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="Trebuie să fii autentificat pentru a cumpăra")
    
    db = await get_database()
    
    # Check if already purchased
    existing = await db.education_purchases.find_one({
        "user_id": user["user_id"],
        "status": "completed"
    })
    if existing:
        raise HTTPException(status_code=400, detail="Ai achiziționat deja acest pachet")
    
    # Initialize Stripe
    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    # Build URLs from frontend origin
    success_url = f"{data.origin_url}/education/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{data.origin_url}/education"
    
    # Create checkout session
    checkout_request = CheckoutSessionRequest(
        amount=EDUCATION_PACKAGE["price"],
        currency=EDUCATION_PACKAGE["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["user_id"],
            "user_email": user["email"],
            "package_id": EDUCATION_PACKAGE["id"],
            "product_type": "education_package"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create pending transaction record
    await db.payment_transactions.insert_one({
        "id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": user["user_id"],
        "email": user["email"],
        "amount": EDUCATION_PACKAGE["price"],
        "currency": EDUCATION_PACKAGE["currency"],
        "product_type": "education_package",
        "package_id": EDUCATION_PACKAGE["id"],
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "url": session.url,
        "session_id": session.session_id
    }

@router.get("/checkout/status/{session_id}")
async def check_checkout_status(session_id: str, request: Request):
    """Check payment status and grant access if paid"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = await get_database()
    
    # Get transaction
    transaction = await db.payment_transactions.find_one({
        "session_id": session_id,
        "user_id": user["user_id"]
    })
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # If already completed, return success
    if transaction.get("payment_status") == "paid":
        return {
            "status": "complete",
            "payment_status": "paid",
            "access_granted": True
        }
    
    # Check with Stripe
    api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "payment_status": status.payment_status,
            "status": status.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # If paid, grant access (only once)
    if status.payment_status == "paid":
        existing_purchase = await db.education_purchases.find_one({
            "session_id": session_id
        })
        
        if not existing_purchase:
            await db.education_purchases.insert_one({
                "id": f"edu_{uuid.uuid4().hex[:12]}",
                "user_id": user["user_id"],
                "email": user["email"],
                "session_id": session_id,
                "package_id": EDUCATION_PACKAGE["id"],
                "amount": EDUCATION_PACKAGE["price"],
                "currency": EDUCATION_PACKAGE["currency"],
                "status": "completed",
                "purchased_at": datetime.now(timezone.utc).isoformat()
            })
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "access_granted": status.payment_status == "paid"
    }

@router.get("/my-access")
async def check_my_access(user: dict = Depends(require_auth)):
    """Check if current user has access to education content"""
    db = await get_database()
    purchase = await db.education_purchases.find_one({
        "user_id": user["user_id"],
        "status": "completed"
    }, {"_id": 0})
    
    return {
        "has_access": purchase is not None,
        "purchase": purchase
    }
