"""Extended Education Content pentru FinRomania"""

# Education Packages
EDUCATION_PACKAGES = {
    "starter": {
        "id": "edu_starter_pack",
        "name": "Pachet Starter",
        "description": "Mini-Curs Online (6 lecții de bază)",
        "price": 5.00,
        "currency": "ron",
        "lessons_included": ["lesson_1", "lesson_2", "lesson_3", "lesson_4", "lesson_5", "lesson_6"],
        "features": [
            "6 lecții fundamentale",
            "Quiz-uri de verificare",
            "Acces permanent",
            "Certificat de completare"
        ]
    },
    "premium": {
        "id": "edu_premium_pack",
        "name": "Curs Complet Premium",
        "description": "Curs Complet (12 lecții) + E-Book + Bonus",
        "price": 20.00,
        "currency": "ron",
        "lessons_included": "all",  # All lessons
        "features": [
            "12 lecții complete (6 extra)",
            "E-Book PDF descărcabil",
            "Glosar 100+ termeni",
            "Calculatoare interactive",
            "Quiz-uri avansate",
            "Certificat Premium",
            "Actualizări gratuite 1 an"
        ]
    }
}

# Complete course lessons
COURSE_LESSONS = [
    # === LECȚII GRATUITE/STARTER (1-6) ===
    {
        "id": "lesson_1",
        "order": 1,
        "title": "Introducere în Lumea Investițiilor",
        "description": "Descoperă de ce investițiile sunt importante și cum te pot ajuta.",
        "duration": "10 min",
        "tier": "free",  # Available to all
        "quiz": [
            {"q": "Ce este dobânda compusă?", "options": ["Taxă bancară", "Dobândă la dobândă", "Comision"], "correct": 1},
            {"q": "Care e principalul dușman al economiilor?", "options": ["Banca", "Inflația", "Statul"], "correct": 1},
            {"q": "Poți începe să investești cu sume mici?", "options": ["Nu, minim 10.000 RON", "Da, chiar și 50 RON", "Doar peste 1000 RON"], "correct": 1}
        ],
        "content": """## Ce înseamnă să investești?

Investiția reprezintă alocarea resurselor (de obicei bani) cu scopul de a genera un câștig sau profit în viitor.

### De ce să investești?

**1. Protecție împotriva inflației**
Inflația este "tăcutul hoț" care îți reduce puterea de cumpărare. Dacă inflația este 5% pe an, 1000 RON de azi vor valora doar 950 RON peste un an.

**2. Efectul dobânzii compuse**
Albert Einstein a numit dobânda compusă "a opta minune a lumii". Când reinvestești câștigurile, acestea generează la rândul lor câștiguri!

**Exemplu:**
- Investești 1000 RON cu randament 10% anual
- După 10 ani: 2594 RON
- După 30 ani: 17449 RON!

**3. Independență financiară**
Investițiile pe termen lung îți pot asigura un venit pasiv.

### Mitul "Trebuie să fii bogat"
FALS! Poți începe cu 50-100 RON pe lună. Important este să începi cât mai devreme."""
    },
    {
        "id": "lesson_2",
        "order": 2,
        "title": "Tipuri de Instrumente Financiare",
        "description": "Acțiuni, obligațiuni, ETF-uri și fonduri mutuale explicate simplu.",
        "duration": "15 min",
        "tier": "starter",
        "quiz": [
            {"q": "Ce reprezintă o acțiune?", "options": ["Un împrumut", "O parte din companie", "O taxă"], "correct": 1},
            {"q": "Ce sunt ETF-urile?", "options": ["Acțiuni scumpe", "Coșuri de acțiuni", "Obligațiuni"], "correct": 1},
            {"q": "Care instrument are risc mai mic?", "options": ["Acțiuni", "Obligațiuni", "Cripto"], "correct": 1}
        ],
        "content": """## Instrumentele Financiare Explicate

### 1. Acțiunile (Stocks)
O acțiune = o "felie" din proprietatea unei companii.

**Avantaje:** Potențial de creștere nelimitat, dividende
**Dezavantaje:** Volatilitate ridicată, risc de pierdere

### 2. Obligațiunile (Bonds)
Un "împrumut" acordat unei companii sau guvernului.

**Exemplu:** Obligațiuni de stat cu dobândă 7%/an

### 3. ETF-uri
"Coșuri" de acțiuni tranzacționate la bursă. Diversificare instantă!

**Exemplu:** S&P 500 ETF - 500 companii într-o singură achiziție

### 4. Fonduri Mutuale
Similare cu ETF-urile, dar gestionate activ.

### 🎯 Recomandare pentru începători
**Începe cu ETF-uri** - diversificare, costuri mici, simplu."""
    },
    {
        "id": "lesson_3",
        "order": 3,
        "title": "Cum Funcționează Bursa",
        "description": "Mecanismele pieței de capital și formarea prețurilor.",
        "duration": "12 min",
        "tier": "starter",
        "quiz": [
            {"q": "Ce determină prețul unei acțiuni?", "options": ["Guvernul", "Cererea și oferta", "Banca"], "correct": 1},
            {"q": "Ce este un Bull Market?", "options": ["Piață în scădere", "Piață în creștere", "Piață stabilă"], "correct": 1},
            {"q": "BET este...", "options": ["O bancă", "Un indice BVB", "O monedă"], "correct": 1}
        ],
        "content": """## Bursa - Piața de Capital

### Ce este Bursa?
O piață organizată pentru tranzacționare. În România: **BVB** (Bursa de Valori București).

### Cum se formează prețul?
**Cerere și ofertă:**
- Mulți cumpărători → prețul CREȘTE
- Mulți vânzători → prețul SCADE

### Indicii Bursieri
**România:** BET (top 20 companii BVB)
**Global:** S&P 500, Dow Jones, DAX

### Tipuri de Ordine
1. **Market Order** - cumperi imediat la prețul curent
2. **Limit Order** - cumperi doar dacă prețul atinge nivelul dorit

### Bull vs Bear Market
🐂 **Bull** = piață în creștere
🐻 **Bear** = piață în scădere"""
    },
    {
        "id": "lesson_4",
        "order": 4,
        "title": "Strategii pentru Începători",
        "description": "DCA, diversificarea și alte strategii dovedite.",
        "duration": "15 min",
        "tier": "starter",
        "quiz": [
            {"q": "Ce înseamnă DCA?", "options": ["Investiție unică mare", "Investiție periodică fixă", "Împrumut"], "correct": 1},
            {"q": "Diversificarea înseamnă...", "options": ["Toate ouăle într-un coș", "Distribuirea riscului", "Vânzare rapidă"], "correct": 1}
        ],
        "content": """## Strategii de Investiții

### 1. DCA - Dollar Cost Averaging
Investești o sumă fixă regulat (lunar), indiferent de preț.

**Exemplu:** 500 RON/lună în ETF S&P 500

**Avantaje:**
- Elimină stresul de a "ghici" momentul perfect
- Reduce riscul de cumpărare la vârf
- Creează obișnuință

### 2. Diversificarea
"Nu pune toate ouăle într-un singur coș"

**Pe clase de active:** 60% Acțiuni, 30% Obligațiuni, 10% Cash
**Pe zone geografice:** SUA, Europa, Emergente

### 3. Buy and Hold
Cumperi și păstrezi pe termen lung (10-20 ani).

### ⚠️ Greșeli de Evitat
1. Timing-ul pieței
2. Investiții bazate pe emoții
3. Lipsa diversificării"""
    },
    {
        "id": "lesson_5",
        "order": 5,
        "title": "Analiza unei Acțiuni",
        "description": "Cum să evaluezi o companie înainte de a investi.",
        "duration": "18 min",
        "tier": "starter",
        "quiz": [
            {"q": "P/E ratio compară...", "options": ["Preț vs Profit", "Preț vs Vânzări", "Profit vs Datorii"], "correct": 0},
            {"q": "ROE măsoară...", "options": ["Prețul acțiunii", "Eficiența companiei", "Datoriile"], "correct": 1}
        ],
        "content": """## Cum Analizezi o Acțiune

### Indicatori Cheie

**1. P/E Ratio**
Preț / Profit per acțiune
- P/E < 15 = posibil subevaluat
- P/E > 25 = posibil supraevaluat

**2. Dividend Yield**
Dividend anual / Preț × 100
- > 3% = randament atractiv

**3. ROE (Return on Equity)**
- > 15% = excelent
- 10-15% = bun

**4. Debt-to-Equity**
- < 1 = sănătos
- > 2 = risc ridicat

### Checklist
✅ Înțeleg ce face compania?
✅ Are avantaj competitiv?
✅ Profitabilă și în creștere?
✅ Datorie gestionabilă?"""
    },
    {
        "id": "lesson_6",
        "order": 6,
        "title": "Construiește-ți Primul Portofoliu",
        "description": "Ghid pas cu pas pentru a începe să investești.",
        "duration": "15 min",
        "tier": "starter",
        "quiz": [
            {"q": "Ce ar trebui să ai înainte de a investi?", "options": ["Mașină", "Fond de urgență", "Credit"], "correct": 1},
            {"q": "VWCE este...", "options": ["O bancă", "Un ETF global", "O acțiune"], "correct": 1}
        ],
        "content": """## Primul Tău Portofoliu

### Pasul 1: Fond de Urgență
**3-6 luni de cheltuieli** într-un cont de economii.

### Pasul 2: Definește Obiectivele
- Pentru ce investesc?
- Pe ce termen?
- Cât pot investi lunar?

### Pasul 3: Alege Alocarea
**Conservator:** 30% Acțiuni, 60% Obligațiuni
**Echilibrat:** 60% Acțiuni, 30% Obligațiuni
**Agresiv:** 80% Acțiuni, 15% Obligațiuni

### Pasul 4: Deschide Cont de Brokeraj
Opțiuni: Tradeville, XTB, Interactive Brokers

### Pasul 5: Începe cu ETF-uri
**Recomandare:** VWCE (Vanguard All-World)

### Pasul 6: Automatizează
Transfer automat lunar. Nu verifica zilnic!

### 🎉 Felicitări!
Ai parcurs bazele. Acum practică cu portofoliul virtual!"""
    },

    # === LECȚII PREMIUM (7-12) ===
    {
        "id": "lesson_7",
        "order": 7,
        "title": "Psihologia Investitorului",
        "description": "Cum să-ți controlezi emoțiile și să eviți capcanele mentale.",
        "duration": "20 min",
        "tier": "premium",
        "quiz": [
            {"q": "FOMO înseamnă...", "options": ["Fear of Missing Out", "First Order Money Out", "Fund of Mutual Options"], "correct": 0},
            {"q": "Ce să faci când piața scade brusc?", "options": ["Vinzi tot", "Stai calm, analizezi", "Cumperi mai mult imediat"], "correct": 1}
        ],
        "content": """## Psihologia Investițiilor

### Capcanele Mentale

**1. FOMO (Fear of Missing Out)**
Teama de a pierde o oportunitate te face să cumperi la vârf.

**2. Panic Selling**
Vinzi în panică când piața scade, blocând pierderile.

**3. Confirmation Bias**
Cauți doar informații care confirmă ce crezi deja.

**4. Overconfidence**
După câteva câștiguri, crezi că ești expert.

### Reguli de Aur

✅ **Nu verifica portofoliul zilnic**
✅ **Ai un plan și respectă-l**
✅ **Emoțiile sunt dușmanul tău**
✅ **Când alții sunt fricoși, fii lacom (și invers)**

### Exercițiu Practic
Ține un jurnal de investiții. Notează:
- Ce ai cumpărat/vândut
- De ce
- Cum te simțeai

Revizuiește lunar și învață din greșeli."""
    },
    {
        "id": "lesson_8",
        "order": 8,
        "title": "Cum să Citești un Raport Anual",
        "description": "Analizează situațiile financiare ca un profesionist.",
        "duration": "25 min",
        "tier": "premium",
        "quiz": [
            {"q": "Bilanțul arată...", "options": ["Profitul anual", "Active și pasive", "Doar datoriile"], "correct": 1},
            {"q": "Cash flow negativ înseamnă...", "options": ["Compania e falită", "Cheltuie mai mult decât încasează", "Profit mare"], "correct": 1}
        ],
        "content": """## Citirea Raportului Anual

### Cele 3 Situații Financiare

**1. Bilanțul (Balance Sheet)**
- **Active** = ce deține compania
- **Pasive** = ce datorează
- **Capitaluri proprii** = Active - Pasive

**2. Contul de Profit și Pierdere (Income Statement)**
- Venituri
- Cheltuieli
- Profit Net

**3. Fluxul de Numerar (Cash Flow)**
- Cash din operațiuni
- Cash din investiții
- Cash din finanțare

### Ce să cauți

✅ **Venituri în creștere** an de an
✅ **Marje de profit stabile** sau în creștere
✅ **Cash flow pozitiv** din operațiuni
✅ **Datorii sub control** (Debt/Equity < 1)
⚠️ **Red flags:** Scăderi bruște, ajustări contabile

### Unde găsești rapoartele?
- Site-ul companiei (Investor Relations)
- BVB.ro pentru companii românești
- SEC.gov pentru companii americane"""
    },
    {
        "id": "lesson_9",
        "order": 9,
        "title": "Taxe și Impozite în România",
        "description": "Tot ce trebuie să știi despre fiscalitatea investițiilor.",
        "duration": "20 min",
        "tier": "premium",
        "quiz": [
            {"q": "Impozitul pe dividende în România este (2026)...", "options": ["5%", "8%", "16%"], "correct": 2},
            {"q": "Câștigurile din acțiuni internaționale se impozitează cu...", "options": ["5%", "10%", "16%"], "correct": 2}
        ],
        "content": """## Fiscalitatea Investițiilor în România (2026)

### Impozit pe Câștiguri de Capital
**BVB:** 3% (deținere ≥1 an) sau 6% (deținere <1 an) - reținut de broker.
**Internațional:** 16% pe profitul net anual - declarat prin Declarația Unică.

**Exemplu BVB (deținere <1 an):**
- Cumperi acțiuni cu 1000 RON
- Vinzi cu 1500 RON
- Profit: 500 RON
- Impozit: 30 RON (6%)

### Impozit pe Dividende
**16%** reținut la sursă (conform Legea 141/2025).

### Contribuția la Sănătate (CASS)
**10%** se aplică dacă veniturile din investiții depășesc 6 salarii minime/an (24.300 RON în 2026).

### Declarația Unică
Dacă ai câștiguri din piețe internaționale sau datorezi CASS, trebuie să depui **Declarația Unică** până pe 25 mai.

### Tips pentru Optimizare
- Pe BVB, deținerea peste 1 an reduce impozitul de la 6% la 3%
- Păstrează evidența tuturor tranzacțiilor
- Compensează pierderile cu câștigurile (doar piețe internaționale, max 70%)
- Folosește un contabil CECCAR dacă ai multe tranzacții

### ⚠️ Disclaimer
Legislația se poate schimba. Consultă un specialist fiscal."""
    },
    {
        "id": "lesson_10",
        "order": 10,
        "title": "Investiții Alternative",
        "description": "Cripto, imobiliare, aur și alte active.",
        "duration": "22 min",
        "tier": "premium",
        "quiz": [
            {"q": "Bitcoin este...", "options": ["O acțiune", "O criptomonedă", "O obligațiune"], "correct": 1},
            {"q": "REIT-urile investesc în...", "options": ["Cripto", "Imobiliare", "Aur"], "correct": 1}
        ],
        "content": """## Investiții Alternative

### 1. Criptomonede
**Ce sunt:** Active digitale descentralizate
**Exemple:** Bitcoin, Ethereum

**Avantaje:**
- Potențial de creștere mare
- Accesibile 24/7
- Descentralizate

**Dezavantaje:**
- Volatilitate extremă
- Risc de pierdere totală
- Reglementare incertă

**Recomandare:** Maximum 5% din portofoliu

### 2. Imobiliare (prin REIT-uri)
REIT = companii care dețin și administrează proprietăți.

**Avantaje:** Dividende stabile, diversificare
**Dezavantaje:** Sensibile la dobânzi

### 3. Aur
**De ce:** Protecție în criză, hedge împotriva inflației
**Cum:** ETF-uri pe aur, aur fizic

### 4. Obligațiuni de Stat România
**FIDELIS:** Obligațiuni pentru populație
**Avantaje:** Randament bun, risc scăzut

### Regula de Aur
Nu investi în ce nu înțelegi!"""
    },
    {
        "id": "lesson_11",
        "order": 11,
        "title": "Planificarea Pensiei",
        "description": "Cum să-ți asiguri o pensie confortabilă.",
        "duration": "18 min",
        "tier": "premium",
        "quiz": [
            {"q": "Pilonul II de pensie este...", "options": ["Opțional", "Obligatoriu", "Inexistent"], "correct": 1},
            {"q": "Pilonul III este...", "options": ["Obligatoriu", "Voluntar", "Doar pentru angajați"], "correct": 1}
        ],
        "content": """## Planificarea Pensiei

### Sistemul de Pensii în România

**Pilonul I (Public)**
- Obligatoriu
- Pay-as-you-go (tinerii plătesc pensiile actuale)
- NU te baza doar pe asta!

**Pilonul II (Privat Obligatoriu)**
- 3.75% din salariu
- Administrat de fonduri private
- Banii sunt ai tăi

**Pilonul III (Voluntar)**
- Tu decizi cât contribui
- Deductibil fiscal până la 400 EUR/an

### Cât ai nevoie pentru pensie?

**Regula celor 25:**
Cheltuieli anuale × 25 = suma necesară

**Exemplu:**
- Cheltuieli: 3000 RON/lună = 36.000 RON/an
- Necesar: 36.000 × 25 = **900.000 RON**

### Cum să ajungi acolo

1. Începe cât mai devreme
2. Automatizează investițiile
3. Crește contribuția cu fiecare mărire de salariu
4. Nu atinge banii până la pensie!

### Calculul
Cu 500 RON/lună, randament 7%/an:
- În 20 ani: ~260.000 RON
- În 30 ani: ~610.000 RON
- În 40 ani: ~1.300.000 RON"""
    },
    {
        "id": "lesson_12",
        "order": 12,
        "title": "Strategii Avansate",
        "description": "Value investing, growth investing și alte strategii pro.",
        "duration": "25 min",
        "tier": "premium",
        "quiz": [
            {"q": "Value investing caută acțiuni...", "options": ["În creștere rapidă", "Subevaluate", "Volatile"], "correct": 1},
            {"q": "Warren Buffett este cunoscut pentru...", "options": ["Day trading", "Value investing", "Cripto"], "correct": 1}
        ],
        "content": """## Strategii Avansate

### 1. Value Investing
Caută acțiuni subevaluate - preț sub valoarea intrinsecă.

**Indicatori:**
- P/E scăzut
- P/B < 1
- Dividend yield ridicat

**Maestru:** Warren Buffett

### 2. Growth Investing
Caută companii cu creștere rapidă.

**Indicatori:**
- Creștere venituri > 20%/an
- Expansiune pe piețe noi
- Inovație

**Exemple:** Amazon, Tesla în anii de început

### 3. Dividend Investing
Construiești un portofoliu de dividende pentru venit pasiv.

**Strategia:**
- Dividend yield 3-6%
- Istoric de creștere a dividendelor
- Payout ratio < 60%

### 4. Factor Investing
Combini factori: Value + Momentum + Quality

### Rebalansarea
O dată pe an:
1. Verifică alocarea actuală
2. Compară cu ținta
3. Vinde ce a crescut prea mult
4. Cumpără ce a scăzut

### 🎓 Concluzie
Ai parcurs cursul complet! Acum ai bazele pentru a deveni un investitor informat."""
    }
]

# Glossary of terms
GLOSSARY = {
    "Acțiune": "O parte din proprietatea unei companii, tranzacționabilă la bursă.",
    "Obligațiune": "Un împrumut acordat unei entități (stat sau companie) în schimbul dobânzii.",
    "ETF": "Exchange-Traded Fund - un fond care urmărește un indice și se tranzacționează ca o acțiune.",
    "Dividend": "Partea din profit distribuită acționarilor.",
    "P/E Ratio": "Price-to-Earnings - raportul dintre prețul acțiunii și profitul per acțiune.",
    "ROE": "Return on Equity - rentabilitatea capitalurilor proprii.",
    "Bull Market": "Piață în creștere, caracterizată de optimism.",
    "Bear Market": "Piață în scădere, caracterizată de pesimism.",
    "DCA": "Dollar Cost Averaging - investiție periodică cu sumă fixă.",
    "Diversificare": "Distribuirea investițiilor în mai multe active pentru reducerea riscului.",
    "Volatilitate": "Gradul de variație a prețului unui activ în timp.",
    "Lichiditate": "Ușurința cu care un activ poate fi transformat în cash.",
    "Portofoliu": "Colecția de investiții deținute de un investitor.",
    "Randament": "Câștigul obținut dintr-o investiție, exprimat procentual.",
    "Risc": "Posibilitatea de a pierde o parte sau tot capitalul investit.",
    "Spread": "Diferența dintre prețul de cumpărare și cel de vânzare.",
    "Broker": "Intermediar care execută tranzacții în numele investitorului.",
    "IPO": "Initial Public Offering - prima listare a unei companii la bursă.",
    "Blue Chip": "Acțiuni ale companiilor mari, stabile și de încredere.",
    "Index": "Un indicator care măsoară performanța unui grup de acțiuni.",
    "Capitalizare bursieră": "Valoarea totală a acțiunilor unei companii (preț × număr acțiuni).",
    "CAGR": "Compound Annual Growth Rate - rata de creștere anuală compusă.",
    "Marjă de profit": "Profitul ca procent din venituri.",
    "Cash Flow": "Fluxul de numerar - intrările și ieșirile de bani ale unei companii.",
    "Hedge": "Protecție împotriva unui risc prin investiții compensatoare.",
    "Short Selling": "Vânzarea unui activ împrumutat cu speranța de a-l cumpăra mai ieftin.",
    "FOMO": "Fear of Missing Out - teama de a pierde o oportunitate.",
    "HODL": "Strategie de a păstra investiția pe termen lung (din cripto).",
    "Rebalansare": "Ajustarea portofoliului pentru a menține alocarea țintă.",
    "Fond de urgență": "Economii pentru 3-6 luni de cheltuieli, accesibile rapid.",
    "Inflație": "Creșterea generală a prețurilor și scăderea puterii de cumpărare.",
    "Dobândă compusă": "Dobândă calculată pe suma inițială plus dobânzile acumulate.",
    "Pilonul II": "Pensie privată obligatorie în România.",
    "Pilonul III": "Pensie privată facultativă în România.",
    "REIT": "Real Estate Investment Trust - fond de investiții imobiliare.",
    "Criptomonedă": "Monedă digitală descentralizată (ex: Bitcoin).",
    "Blockchain": "Tehnologie de registru distribuit folosită de criptomonede.",
    "Stablecoin": "Criptomonedă cu valoare stabilă, legată de o monedă fiat.",
    "Market Cap": "Capitalizare de piață - valoarea totală a unui activ.",
    "All-Time High (ATH)": "Cel mai mare preț atins vreodată de un activ.",
    "Support": "Nivel de preț unde cererea oprește scăderea.",
    "Rezistență": "Nivel de preț unde oferta oprește creșterea.",
    "Tendință (Trend)": "Direcția generală a prețului pe o perioadă.",
    "Medie mobilă": "Media prețurilor pe o perioadă (ex: 50 zile, 200 zile).",
    "Ordin limită": "Ordin de cumpărare/vânzare la un preț specificat.",
    "Ordin de piață": "Ordin executat imediat la prețul curent.",
    "Stop Loss": "Ordin automat de vânzare când prețul scade sub un nivel.",
    "Take Profit": "Ordin automat de vânzare când prețul atinge un țintă.",
    "Penny Stock": "Acțiuni cu preț foarte mic (sub $5), de obicei speculative.",
    "Growth Stock": "Acțiuni ale companiilor cu potențial de creștere rapidă.",
    "Value Stock": "Acțiuni subevaluate relativ la valoarea intrinsecă.",
    "Margin Trading": "Tranzacționare cu bani împrumutați de la broker.",
    "Leverage": "Utilizarea capitalului împrumutat pentru a amplifica câștigurile/pierderile.",
    "Portfolio Manager": "Specialist care administrează un portofoliu de investiții.",
    "Asset Allocation": "Distribuirea capitalului între diferite clase de active.",
    "Benchmark": "Standard de comparație pentru performanța investițiilor (ex: S&P 500).",
    "Alpha": "Randament peste benchmark-ul de piață.",
    "Beta": "Măsura volatilității unei acțiuni relativ la piață.",
    "Sharpe Ratio": "Raport care măsoară randamentul ajustat la risc.",
    "Drawdown": "Scăderea maximă de la vârf la minim a valorii portofoliului.",
    "Expense Ratio": "Costul anual al unui fond, exprimat ca procent.",
    "NAV": "Net Asset Value - valoarea netă a activelor unui fond.",
    "AUM": "Assets Under Management - totalul activelor administrate.",
    "PE Forward": "P/E calculat pe baza profiturilor estimate viitoare.",
    "PEG Ratio": "P/E împărțit la rata de creștere a profiturilor.",
    "Book Value": "Valoarea contabilă a unei companii (active minus pasive).",
    "Earnings Per Share (EPS)": "Profitul net împărțit la numărul de acțiuni.",
    "Revenue": "Venitul total al unei companii din vânzări.",
    "EBITDA": "Profit înainte de dobânzi, taxe, depreciere și amortizare.",
    "Free Cash Flow": "Cash generat după cheltuielile de capital.",
    "Working Capital": "Active curente minus pasive curente.",
    "Current Ratio": "Raportul dintre active curente și pasive curente.",
    "Quick Ratio": "Active lichide împărțite la pasive curente.",
    "Gross Margin": "Profitul brut ca procent din venituri.",
    "Net Margin": "Profitul net ca procent din venituri.",
    "Return on Assets (ROA)": "Profitul raportat la totalul activelor.",
    "Debt-to-Equity": "Raportul dintre datorii și capitalul propriu.",
    "Interest Coverage": "Capacitatea de a plăti dobânzile din profit.",
    "Payout Ratio": "Procentul din profit distribuit ca dividende.",
    "Buyback": "Răscumpărarea de acțiuni proprii de către companie.",
    "Stock Split": "Împărțirea unei acțiuni în mai multe acțiuni de valoare mai mică.",
    "Reverse Split": "Combinarea mai multor acțiuni într-una de valoare mai mare.",
    "ADR": "American Depositary Receipt - certificat pentru acțiuni străine în SUA.",
    "OTC": "Over-The-Counter - piață pentru acțiuni nelistate la bursă.",
    "Dark Pool": "Platformă de tranzacționare privată, anonimă.",
    "High-Frequency Trading": "Tranzacționare automată la viteze foarte mari.",
    "Quantitative Analysis": "Analiză bazată pe modele matematice și statistice.",
    "Technical Analysis": "Analiză bazată pe grafice și pattern-uri de preț.",
    "Fundamental Analysis": "Analiză bazată pe datele financiare ale companiei.",
    "Sentiment Analysis": "Analiza emoțiilor și opiniilor pieței.",
    "Moving Average Convergence Divergence (MACD)": "Indicator tehnic de tendință.",
    "Relative Strength Index (RSI)": "Indicator de momentum între 0-100.",
    "Bollinger Bands": "Benzi care arată volatilitatea și niveluri de suport/rezistență.",
    "Fibonacci Retracement": "Niveluri de corecție bazate pe secvența Fibonacci.",
    "Volume": "Numărul de acțiuni tranzacționate într-o perioadă.",
    "Bid": "Prețul maxim pe care cumpărătorul e dispus să-l plătească.",
    "Ask": "Prețul minim pe care vânzătorul îl acceptă.",
    "Market Maker": "Participant care asigură lichiditate prin cotații bid/ask.",
    "Circuit Breaker": "Mecanism de oprire temporară a tranzacțiilor la mișcări extreme.",
}

