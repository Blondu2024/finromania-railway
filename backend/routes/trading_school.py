"""Trading School Interactive - Educational Content & System"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/trading-school", tags=["trading_school"])

# ============================================
# EDUCATIONAL CONTENT
# ============================================

TRADING_LESSONS = [
    {
        "id": "lesson_1",
        "module": 1,
        "order": 1,
        "title": "Ce Este o Acțiune?",
        "subtitle": "Fundamentele investițiilor",
        "duration": "5 min",
        "difficulty": "beginner",
        "emoji": "📈",
        "content": """
# Ce Este o Acțiune?

## 💡 Definiție Simplă

O **acțiune** este o bucată dintr-o companie. Când cumperi o acțiune, devii **proprietar parțial** al companiei!

## 🏦 Exemplu Concret: Banca Transilvania (TLV)

Imaginează-ți că Banca Transilvania este o pizza 🍕:
- Pizza întreagă = Întreaga companie
- O felie = O acțiune
- Tu cumperi 10 felii = Deții 10 acțiuni

**Dacă pizzeria valorează mai mult (compania crește) → feliile tale valorează mai mult!**

## 💰 Calculul Simplu

**Exemplu:**
- 1 acțiune TLV = 30 RON
- Cumperi 10 acțiuni = 300 RON investiți

**După 1 lună:**
- TLV crește la 33 RON (+10%)
- Ai acum: 10 × 33 = **330 RON**
- **Profit: +30 RON (+10%)**

## ✅ De Reținut

1. Acțiune = proprietate într-o companie
2. Preț crește → Tu câștigi
3. Preț scade → Tu pierzi
4. Poți vinde oricând (dacă e lichiditate)
""",
        "quiz": [
            {
                "question": "Dacă ai 10 acțiuni TLV la 30 RON și prețul crește la 33 RON, cât valorează investiția ta?",
                "options": ["300 RON (la fel)", "330 RON (crește!)", "270 RON (scade)", "360 RON"],
                "correct": 1,
                "explanation": "Corect! 10 acțiuni × 33 RON = 330 RON. Ai făcut +30 RON profit (+10%)!"
            },
            {
                "question": "Ce înseamnă să deții o acțiune?",
                "options": [
                    "Împrumuți bani companiei",
                    "Ești proprietar parțial al companiei",
                    "Ești angajat al companiei",
                    "Primești un discount la produse"
                ],
                "correct": 1,
                "explanation": "Exact! Când deții acțiuni, ești co-proprietar al companiei. Dacă compania merge bine, acțiunile cresc!"
            }
        ],
        "scenario": {
            "title": "Primul Tău Cumpărare",
            "description": "Hai să cumpărăm prima acțiune împreună!",
            "steps": [
                {
                    "step": 1,
                    "text": "Ai 1,000 RON în cont. Vrei să investești în Banca Transilvania (TLV).",
                    "question": "Câte acțiuni poți cumpăra dacă TLV costă 30 RON?",
                    "options": ["10 acțiuni", "30 acțiuni", "33 acțiuni", "100 acțiuni"],
                    "correct": 2,
                    "ai_hint": "Calculează: Bani disponibili ÷ Preț per acțiune = 1,000 ÷ 30 = ?"
                },
                {
                    "step": 2,
                    "text": "Bravo! Ai cumpărat 33 acțiuni TLV la 30 RON. Investiție: 990 RON.",
                    "question": "După 1 lună, TLV e la 33 RON. Vrei să vinzi?",
                    "options": ["DA - iau profit", "NU - aștept mai mult"],
                    "correct": None,
                    "ai_feedback": {
                        "0": "Bună decizie! Ai vândut la 33 RON × 33 = 1,089 RON. Profit: +99 RON (+10%)!",
                        "1": "Riști mai mult, dar poate crește și mai mult! Sau poate scade..."
                    }
                }
            ]
        }
    },
    {
        "id": "lesson_2",
        "module": 1,
        "order": 2,
        "title": "Long vs Short - Două Direcții",
        "subtitle": "Cum câștigi când piața scade?",
        "duration": "7 min",
        "difficulty": "beginner",
        "emoji": "↕️",
        "content": """
# Long vs Short

## 📈 LONG (Cumpărare Clasică)

**Cumperi acum, vinzi mai târziu LA PREȚ MAI MARE**

**Exemplu:**
- Cumperi TLV la 30 RON
- Vinzi la 35 RON
- **Profit: +5 RON per acțiune**

✅ Câștigi când prețul CREȘTE
❌ Pierzi când prețul SCADE

## 📉 SHORT (Vânzare în Lipsă)

**Vinzi acum (împrumutat), cumperi înapoi LA PREȚ MAI MIC**

**Exemplu:**
- "Împrumuți" și vinzi TLV la 30 RON
- Cumperi înapoi la 25 RON
- **Profit: +5 RON per acțiune**

✅ Câștigi când prețul SCADE
❌ Pierzi când prețul CREȘTE

## ⚠️ Risc SHORT

**LONG:** Pierdere maximă = Investiția ta (prețul ajunge la 0)
**SHORT:** Pierdere = INFINITĂ! (prețul poate crește la infinit)

**De aceea SHORT e pentru avansați!**

## 🎯 Când Folosești

**LONG:** Crezi că compania va merge bine
**SHORT:** Crezi că compania va merge prost (sau piața va scădea)
""",
        "quiz": [
            {
                "question": "Ai făcut SHORT pe TLV la 30 RON (100 acțiuni). Prețul crește la 35 RON. Cât ai pierdut?",
                "options": ["+500 RON (profit)", "-500 RON (pierdere)", "0 RON", "-100 RON"],
                "correct": 1,
                "explanation": "Corect, din păcate! SHORT înseamnă că câștigi când scade. Când crește, PIERZI! (35-30) × 100 = -500 RON"
            },
            {
                "question": "De ce SHORT e mai riscant decât LONG?",
                "options": [
                    "E ilegal",
                    "Pierderea poate fi infinită",
                    "Nu poți câștiga bani",
                    "E mai complicat"
                ],
                "correct": 1,
                "explanation": "Exact! La LONG, pierdere max = investiția (prețul ajunge la 0). La SHORT, prețul poate crește la infinit = pierdere infinită!"
            }
        ]
    },
    {
        "id": "lesson_3",
        "module": 2,
        "order": 3,
        "title": "Leverage - Sabie cu Două Tăișuri",
        "subtitle": "Cum să amplifici profitul... și pierderea",
        "duration": "10 min",
        "difficulty": "intermediate",
        "emoji": "⚡",
        "content": """
# Leverage (Efect de Levier)

## 💰 Ce Este?

**Leverage = Împrumuți bani de la broker pentru a controla mai mulți bani**

Exemplu simplu: E ca și cum ai cumpăra o casă cu credit!

## 🎯 Exemplu Fără Leverage (1x)

**Investești:**
- Ai: 1,000 RON
- Controlezi: 1,000 RON
- Cumperi Oil la 100 RON = 10 unități

**Oil crește la 110 RON (+10%):**
- Vinzi: 10 × 110 = 1,100 RON
- **Profit: +100 RON (+10%)**

## ⚡ Exemplu CU Leverage 5x

**Investești:**
- Ai: 1,000 RON (margin)
- Împrumuți: 4,000 RON de la broker
- Controlezi: 5,000 RON total!
- Cumperi Oil la 100 RON = 50 unități

**Oil crește la 110 RON (+10%):**
- Vinzi: 50 × 110 = 5,500 RON
- Returnezi împrumut: 4,000 RON
- Rămâi cu: 1,500 RON
- **Profit: +500 RON (+50%)** 🎉

## 🚨 DAR Dacă Scade?

**Oil scade la 90 RON (-10%):**
- Vinzi: 50 × 90 = 4,500 RON
- Returnezi împrumut: 4,000 RON
- Rămâi cu: 500 RON
- **Pierdere: -500 RON (-50%)** 😱

## ⚠️ Margin Call

**Dacă pierderile devin prea mari, brokerul ÎNCHIDE FORȚAT poziția!**

Exemplu: Oil scade la 80 RON (-20%)
- Valoare: 50 × 80 = 4,000 RON
- Trebuie să returnezi: 4,000 RON
- **Rămâi cu: 0 RON - Ai pierdut TOT!** 💀

## 📊 Regula de Aur

**Cu leverage 5x:**
- Dacă prețul scade 20% → PIERZI 100% (TOT!)
- **NU folosi leverage mare dacă nu știi ce faci!**

## 💡 Pentru Începători

- Leverage 1x = SAFE (fără împrumut)
- Leverage 2x = OK (cu Stop Loss!)
- Leverage 5x+ = PERICOL (doar pentru experți)
""",
        "quiz": [
            {
                "question": "Ai 1,000 RON, leverage 5x. Cumperi Oil la 100 RON. Oil scade la 80 RON (-20%). Cât ai pierdut?",
                "options": ["200 RON", "500 RON", "1,000 RON (TOT!)", "100 RON"],
                "correct": 2,
                "explanation": "CORECT! Cu 5x leverage, o scădere de 20% = pierdere de 100% din margin! Asta e MARGIN CALL - ai pierdut tot!"
            },
            {
                "question": "De ce leverage e 'sabie cu două tăișuri'?",
                "options": [
                    "E ilegal",
                    "Amplifică profitul ȘI pierderea",
                    "Costă mult",
                    "E complicat"
                ],
                "correct": 1,
                "explanation": "Exact! Leverage amplifică AMBELE direcții. +10% devine +50%, dar -10% devine -50%!"
            },
            {
                "question": "Ce leverage e sigur pentru începători?",
                "options": ["10x", "5x", "2x cu Stop Loss", "1x (fără leverage)"],
                "correct": 3,
                "explanation": "Bravo! 1x (fără leverage) e cel mai sigur pentru început. După ce înveți, poți încerca 2x cu Stop Loss."
            }
        ],
        "scenario": {
            "title": "Criza Leverage - Învață din Greșeli",
            "steps": [
                {
                    "step": 1,
                    "text": "Ai 5,000 RON. Ești încrezător și alegi leverage 10x pentru Oil.",
                    "ai": "⚠️ Atenție! Cu 10x leverage, controlezi 50,000 RON! O mișcare de doar -10% și pierzi TOT!",
                    "question": "Vrei să continui cu 10x sau schimbi la 2x?",
                    "options": ["10x - sunt sigur!", "2x - mai sigur"],
                    "correct": 1
                },
                {
                    "step": 2,
                    "text": "Ai ales 2x (smart!). Cumperi Oil la 75 RON.",
                    "ai": "Bună decizie! Cu 2x leverage și 5,000 RON margin, controlezi 10,000 RON.",
                    "question": "Setezi Stop Loss?",
                    "options": ["DA - la -5% (71.25 RON)", "NU - risc tot"],
                    "correct": 0
                },
                {
                    "step": 3,
                    "text": "Perfect! Ai setat SL la 71.25 RON. Oil scade la 70 RON (-6.7%).",
                    "ai": "🛡️ STOP LOSS ACTIVAT! Poziția închisă la 71.25 RON. Pierdere: -500 RON (-10%). DAR te-a salvat de pierderi mai mari!",
                    "question": "Ce s-ar fi întâmplat FĂRĂ Stop Loss?",
                    "calculation": "La 70 RON: Pierdere = (75-70) × 133 × 2 = -1,330 RON (-26.6%)"
                }
            ]
        }
    },
    {
        "id": "lesson_4",
        "module": 2,
        "order": 4,
        "title": "Stop Loss - Asigurarea Ta",
        "subtitle": "Cum să nu pierzi tot",
        "duration": "8 min",
        "difficulty": "beginner",
        "emoji": "🛡️",
        "content": """
# Stop Loss - Asigurarea Ta

## 💡 Ce Este?

**Stop Loss** = Ordin automat de vânzare când prețul scade la un nivel setat de tine.

**E ca o plasă de siguranță la circ!** 🎪

## 🎯 Cum Funcționează?

**Exemplu:**
1. Cumperi TLV la 30 RON (100 acțiuni = 3,000 RON)
2. Setezi **Stop Loss la 28.5 RON** (-5%)
3. Dacă TLV scade la 28.5 → VINDE AUTOMAT!

**Rezultat:** Pierdere maximă = -150 RON (-5%)

## 📊 Scenariul Fără SL

**Ce se întâmplă dacă NU setezi Stop Loss?**

**Ziua 1:** TLV = 29 RON (-3.3%) → "Mai aștept..."
**Ziua 2:** TLV = 27 RON (-10%) → "Sigur crește..."
**Ziua 3:** TLV = 24 RON (-20%) → "😱 Am pierdut 600 RON!"

**Cu Stop Loss:** Ai fi pierdut doar 150 RON și închideai la -5%!

## ⚡ Stop Loss + Leverage

**CRITIC:** Cu leverage, Stop Loss e OBLIGATORIU!

Exemplu leverage 5x:
- Investești: 1,000 RON
- Controlezi: 5,000 RON
- Fără SL: O scădere de -20% = PIERZI TOT!
- Cu SL la -5%: Pierdere max = -250 RON (controlabil)

## 💡 Unde Setezi SL?

**Reguli practice:**
- **Day trading:** -2% până -5%
- **Swing trading:** -5% până -10%
- **Long-term:** -10% până -15%

**Cu leverage:** ÎNTOTDEAUNA mai strict! (-3% max cu 5x leverage)
""",
        "quiz": [
            {
                "question": "Ai 3,000 RON investiți în TLV la 30 RON. Setezi SL la 28.5 RON (-5%). Prețul scade la 27 RON. Ce se întâmplă?",
                "options": [
                    "Pierzi tot (3,000 RON)",
                    "Poziția se închide la 28.5, pierzi ~150 RON",
                    "Nu se întâmplă nimic",
                    "Trebuie să vinzi manual"
                ],
                "correct": 1,
                "explanation": "Corect! SL se activează automat la 28.5 RON, limitând pierderea la -5% (~150 RON). Te salvează de scăderea la 27 RON!"
            },
            {
                "question": "Cu leverage 5x, unde e SIGUR să setezi Stop Loss?",
                "options": ["-20%", "-10%", "-3%", "Nu e nevoie"],
                "correct": 2,
                "explanation": "Corect! Cu 5x leverage, -20% în preț = -100% pierdere (TOT). SL la -3% te protejează: -3% × 5 = -15% pierdere (controlabil)."
            }
        ]
    },
    {
        "id": "lesson_5",
        "module": 2,
        "order": 5,
        "title": "Diversificarea - Nu Pune Toate Ouăle într-un Coș",
        "subtitle": "Cum să reduci riscul",
        "duration": "6 min",
        "difficulty": "intermediate",
        "emoji": "🎯",
        "content": """
# Diversificarea Portofoliului

## 🥚 Regula Ouălor

**"Nu pune toate ouăle într-un singur coș"**

Dacă scapi coșul → TOATE ouăle se sparg! 😱

În trading:
- 1 coș = 1 acțiune = RISC MARE
- 5-10 coșuri = 5-10 acțiuni = RISC REDUS

## 📊 Exemplu Practic

**Portofoliu PROST (nediversificat):**
- 10,000 RON → TOT în TLV
- TLV scade 20% → Pierzi 2,000 RON (-20%)

**Portofoliu BUN (diversificat):**
- 2,000 RON → TLV (bancă)
- 2,000 RON → H2O (energie)
- 2,000 RON → SNP (petrol)
- 2,000 RON → Gold (aur)
- 2,000 RON → S&P 500 (indice US)

**Dacă TLV scade 20%:**
- TLV: -400 RON
- Celelalte stabile sau cresc
- **Pierdere totală: -200 RON (-2%)** în loc de -20%!

## 🎯 Reguli de Diversificare

1. **Sectoare diferite:** Bancă + Energie + Tech
2. **Geografii diferite:** România + SUA + Europa
3. **Clase de active:** Acțiuni + Aur + Forex
4. **5-10 poziții** diferite (nu 1, nu 100)

## ⚠️ Greșeală Comună

**"Diversific în 10 acțiuni din același sector"**

Exemplu: 10 bănci românești → TOATE scad când sectorul bancar scade!

**Diversificare REALĂ:** Bancă + Energie + Tech + Aur + Forex
""",
        "quiz": [
            {
                "question": "Ai 10,000 RON. Ce portofoliu e mai bine diversificat?",
                "options": [
                    "10,000 RON în TLV",
                    "5,000 TLV + 5,000 BRD (ambele bănci)",
                    "2,000 TLV + 2,000 H2O + 2,000 SNP + 2,000 Gold + 2,000 S&P500",
                    "1,000 RON în 10 acțiuni diferite"
                ],
                "correct": 2,
                "explanation": "Perfect! Opțiunea C diversifică pe sectoare (bancă, energie, petrol, aur, indice global). Celelalte sunt fie concentrate (A,B) fie prea fragmentate (D)."
            }
        ]
    },
    {
        "id": "lesson_6",
        "module": 3,
        "order": 6,
        "title": "Psihologia Tradingului - Emoțiile Tale",
        "subtitle": "Cum să nu lași frica și lăcomia să decidă",
        "duration": "12 min",
        "difficulty": "intermediate",
        "emoji": "🧠",
        "tier": "premium",
        "content": """
# Psihologia Tradingului

## 🧠 Cel Mai Mare Dușman: TU ÎNSUȚI

**90% din traderi pierd bani NU pentru că nu știu analiza, ci pentru că nu-și controlează emoțiile!**

## 😨 FRICA (Fear)

**Scenariul:**
- Ai profit de +100 RON (+10%)
- Frica: "Dacă scade? Mai bine vând ACUM!"
- Vinzi prea devreme
- Acțiunea crește la +50% fără tine 😢

**Regula:** Setează Take Profit în avans, nu decide emoțional!

## 🤑 LĂCOMIA (Greed)

**Scenariul:**
- Ai profit de +500 RON (+50%)
- Lăcomia: "Poate crește la +100%!"
- Aștepți prea mult
- Acțiunea scade la +10% 😱
- Ai pierdut +400 RON profit!

**Regula:** Respectă-ți planul! Take Profit setat = execută!

## 🎲 FOMO (Fear of Missing Out)

**Scenariul:**
- Vezi știrea: "Bitcoin +20% azi!"
- FOMO: "Trebuie să cumpăr ACUM!"
- Cumperi la vârf (all-time high)
- Scade 30% a doua zi 💀

**Regula:** NU cumpăra din FOMO! Analizează înainte!

## 💔 Revenge Trading

**Scenariul:**
- Pierzi 500 RON pe Oil
- Furie: "Vreau banii înapoi!"
- Intri imediat în altă poziție (fără analiză)
- Pierzi încă 500 RON 😭

**Regula:** După pierdere → PAUZĂ! Nu trade emoțional!

## ✅ Reguli de Aur

1. **Fă un PLAN** înainte de trade
2. **Respectă-ți Stop Loss** (nu-l muți!)
3. **Nu trade după pierderi mari** (pauză 24h)
4. **Setează limite zilnice** (max 3 trades/zi)
5. **Jurnal de trading** (notează de ce ai intrat/ieșit)
""",
        "quiz": [
            {
                "question": "Ai +200 RON profit (+20%). Frica te face să vinzi. Acțiunea apoi crește la +50%. Ce greșeală ai făcut?",
                "options": [
                    "Ai vândut prea devreme din FRICĂ",
                    "Ai așteptat prea mult din LĂCOMIE",
                    "Ai cumpărat din FOMO",
                    "Revenge trading"
                ],
                "correct": 0,
                "explanation": "Corect! FRICA te-a făcut să vinzi prea devreme. Dacă aveai Take Profit setat în avans, nu dădeai emoțiilor să decidă!"
            },
            {
                "question": "După ce pierzi 500 RON, ce ar trebui să faci?",
                "options": [
                    "Intru imediat în alt trade să recuperez",
                    "PAUZĂ 24h - nu tradez emoțional",
                    "Cresc leverage-ul pentru recovery rapid",
                    "Schimb strategia complet"
                ],
                "correct": 1,
                "explanation": "Perfect! După pierdere mare, ia o PAUZĂ. Revenge trading = calea spre pierderi mai mari. Liniștește-te, analizează ce-a mers prost, apoi revino."
            }
        ]
    },
    {
        "id": "lesson_7",
        "module": 3,
        "order": 7,
        "title": "Cum Citești un Grafic - Candlesticks",
        "subtitle": "Limbajul vizual al pieței",
        "duration": "15 min",
        "difficulty": "intermediate",
        "emoji": "📊",
        "tier": "premium",
        "content": """
# Cum Citești Graficele - Candlesticks

## 🕯️ Ce Este un Candlestick?

Un **candlestick** (lumânare) arată 4 prețuri într-o perioadă (1 min, 5 min, 1 zi):

1. **Open** (deschidere)
2. **Close** (închidere)
3. **High** (maxim)
4. **Low** (minim)

## 🟢 Green Candle (Bullish)

```
      |  ← High (maxim)
    ┌───┐
    │   │ ← Body (Open → Close)
    │   │
    └───┘ ← Close (mai sus)
      |  ← Open
      |  ← Low (minim)
```

**Înseamnă:** Prețul a CRESCUT (close > open) → Cumpărători au câștigat!

## 🔴 Red Candle (Bearish)

```
      |  ← High
      |  ← Open (mai sus)
    ┌───┐
    │   │ ← Body (Open → Close)
    └───┘ ← Close (mai jos)
      |  ← Low
```

**Înseamnă:** Prețul a SCĂZUT (close < open) → Vânzători au câștigat!

## 📈 Pattern-uri Importante

**1. Hammer (Ciocan)** 🔨
- Body mic sus
- Shadow lung jos
- **Semnificație:** Vânzătorii au încercat să coboare prețul, dar cumpărătorii l-au împins înapoi SUS
- **Semnal:** Posibilă CREȘTERE

**2. Shooting Star (Stea Căzătoare)** ⭐
- Body mic jos
- Shadow lung sus
- **Semnificație:** Cumpărătorii au încercat să urce prețul, dar vânzătorii l-au tras înapoi JOS
- **Semnal:** Posibilă SCĂDERE

**3. Doji (Cruce)** ✝️
- Open = Close (aproape)
- Shadows egale
- **Semnificație:** INDECIS - nimeni nu câștigă
- **Semnal:** Posibilă SCHIMBARE de trend

## 💡 Cum Folosești în Trading

**Green candles multe la rând** → Trend UP (bullish)
**Red candles multe la rând** → Trend DOWN (bearish)
**Pattern Hammer la bază** → Posibil rebound (cumpără!)
**Pattern Shooting Star la vârf** → Posibilă corecție (vinde!)
""",
        "quiz": [
            {
                "question": "Un candle VERDE (green) înseamnă:",
                "options": [
                    "Prețul a scăzut",
                    "Prețul a crescut (close > open)",
                    "Prețul e stabil",
                    "Volumul e mare"
                ],
                "correct": 1,
                "explanation": "Corect! Green candle = Close mai sus decât Open = prețul a CRESCUT în acea perioadă. Cumpărătorii au câștigat!"
            },
            {
                "question": "Pattern 'Hammer' (ciocan) la baza unui trend de scădere semnalează:",
                "options": [
                    "Va continua să scadă",
                    "Posibil rebound (creștere)",
                    "Nu înseamnă nimic",
                    "Trebuie să vinzi"
                ],
                "correct": 1,
                "explanation": "Perfect! Hammer la bază = vânzătorii au încercat să coboare dar cumpărătorii i-au oprit. Semnal de posibilă inversare UP!"
            }
        ]
    },
    {
        "id": "lesson_8",
        "module": 3,
        "order": 8,
        "title": "Indicatori Tehnici - RSI",
        "subtitle": "Cel mai popular indicator pentru începători",
        "duration": "10 min",
        "difficulty": "intermediate",
        "emoji": "📉",
        "tier": "premium",
        "content": """
# RSI - Relative Strength Index

## 📊 Ce Este RSI?

**RSI** măsoară dacă o acțiune este:
- **Supracumpărată** (overbought) → Posibil să scadă
- **Supravândută** (oversold) → Posibil să crească

**Scală:** 0 - 100

## 🎯 Cum Citești RSI

```
100 ──────────────── Extrem supracumpărat
 70 ──────────────── ZONA ROȘIE (Overbought)
 50 ──────────────── Neutru
 30 ──────────────── ZONA VERDE (Oversold)
  0 ──────────────── Extrem supravândut
```

**Reguli Simple:**
- 🔴 **RSI > 70:** SUPRACUMPĂRAT → Posibil să scadă (ia profit sau nu cumpăra!)
- 🟢 **RSI < 30:** SUPRAVÂNDUT → Posibil să crească (oportunitate cumpărare!)
- 🟡 **RSI 30-70:** NEUTRU → Niciun semnal clar

## 💡 Strategia Simplă

**Exemplu TLV:**

**Ziua 1:** RSI = 75 (supracumpărat)
- **NU cumpăra!** E prea sus
- Așteaptă corecție

**Ziua 5:** RSI = 28 (supravândut)
- **Oportunitate!** Cumpără
- TLV a scăzut prea mult, probabil rebound

**Ziua 10:** RSI = 72 (supracumpărat din nou)
- **Vinde!** Ia profit
- E din nou prea sus

**Profit:** Ai cumpărat jos (RSI 28) și ai vândut sus (RSI 72)!

## ⚠️ Atenție - RSI Nu E Magic!

**RSI poate rămâne în extremă mult timp!**

- RSI > 70 timp de săptămâni (trend puternic UP)
- RSI < 30 timp de săptămâni (trend puternic DOWN)

**Regula:** Combină RSI cu alte semnale (trend, volume, news)

## 🎯 RSI + Stop Loss

**Când cumperi la RSI 28:**
- Setează SL la -5% sub entry
- Dacă nu crește în 2-3 zile → Ieși
- NU așteptat infinit "să revină"
""",
        "quiz": [
            {
                "question": "TLV are RSI = 78. Ce ar trebui să faci?",
                "options": [
                    "Cumpăr - e în creștere!",
                    "NU cumpăr - e supracumpărat, risc de corecție",
                    "Cumpăr cu leverage mare",
                    "Short - sigur scade"
                ],
                "correct": 1,
                "explanation": "Corect! RSI 78 = SUPRACUMPĂRAT. Riscant să cumperi acum. Mai bine aștepți corecție la RSI < 50 sau < 30."
            },
            {
                "question": "RSI < 30 înseamnă ÎNTOTDEAUNA că trebuie să cumperi?",
                "options": [
                    "DA - e semnal sigur!",
                    "NU - e doar un indicator, combină cu alții",
                    "DA - dar cu leverage mare",
                    "NU - e semnal de vânzare"
                ],
                "correct": 1,
                "explanation": "Perfect! RSI < 30 e un SEMNAL bun, dar NU garantat. Combină cu trend, volume, news. Și ÎNTOTDEAUNA folosește Stop Loss!"
            }
        ]
    },
    {
        "id": "lesson_9",
        "module": 3,
        "order": 9,
        "title": "MACD - Moving Average Convergence Divergence",
        "subtitle": "Indicator de trend și momentum",
        "duration": "12 min",
        "difficulty": "advanced",
        "emoji": "📈",
        "tier": "premium",
        "content": """
# MACD - Indicator de Trend

## 📊 Ce Este MACD?

**MACD** arată:
1. **Direcția trendului** (UP sau DOWN)
2. **Puterea trendului** (puternic sau slab)
3. **Posibile inversări** (când se schimbă trendul)

**Componente:**
- **MACD Line** (linia rapidă)
- **Signal Line** (linia lentă)
- **Histogram** (diferența dintre ele)

## 🎯 Semnale de Trading

### **Semnal CUMPĂRARE** ✅
- MACD Line trece PESTE Signal Line
- Histogram devine POZITIV (verde)
- **Înseamnă:** Momentum UP, trend bullish începe!

### **Semnal VÂNZARE** ❌
- MACD Line trece SUB Signal Line
- Histogram devine NEGATIV (roșu)
- **Înseamnă:** Momentum DOWN, trend bearish începe!

## 💡 Divergențe (Advanced)

### **Divergență Bullish** (Cumpărare!)
- Preț: Face LOW mai jos
- MACD: Face LOW mai sus
- **Înseamnă:** Vânzătorii slăbesc, posibil rebound!

### **Divergență Bearish** (Vânzare!)
- Preț: Face HIGH mai sus
- MACD: Face HIGH mai jos
- **Înseamnă:** Cumpărătorii slăbesc, posibilă corecție!

## 🎯 Strategia Simplă

**Exemplu Oil:**
1. Așteaptă MACD cross (linia trece peste signal)
2. Confirmă cu RSI (nu fie > 70)
3. Intră în poziție
4. Setează SL la -5%
5. Ieși când MACD cross invers SAU Take Profit

## ⚠️ False Signals

**MACD dă multe false signals în piețe laterale!**

**Best use:** Trending markets (când e clar UP sau DOWN)
**Evită:** Sideways/choppy markets
""",
        "quiz": [
            {
                "question": "MACD Line trece PESTE Signal Line. Ce înseamnă?",
                "options": [
                    "Semnal VÂNZARE",
                    "Semnal CUMPĂRARE",
                    "Nimic special",
                    "Trebuie să aștept"
                ],
                "correct": 1,
                "explanation": "Corect! MACD cross UP (peste signal) = semnal BULLISH de cumpărare. Momentum se schimbă în favoarea cumpărătorilor!"
            }
        ]
    },
    {
        "id": "lesson_10",
        "module": 4,
        "order": 10,
        "title": "Strategii de Trading - Day Trading",
        "subtitle": "Cum să câștigi în aceeași zi",
        "duration": "15 min",
        "difficulty": "advanced",
        "emoji": "⚡",
        "tier": "premium",
        "content": """
# Day Trading - Tranzacții Intraday

## ⏰ Ce Este Day Trading?

**Cumperi și vinzi în ACEEAȘI ZI!**

Caracteristici:
- Poziții deschise: 5 min - 8 ore
- Închizi TOATE pozițiile înainte de closing
- Profiți din mișcări mici (1-3%)
- Multe tranzacții (5-20/zi)

## 💰 Exemplu Realist

**Dimineață 09:00:**
- Oil = 75.00 USD
- RSI = 32 (oversold)
- MACD = Bullish cross
- **CUMPĂR:** 100 unități cu 2x leverage

**După-masă 14:00:**
- Oil = 76.50 USD (+2%)
- RSI = 68 (aproape overbought)
- **VÂND:** Profit = (76.50 - 75.00) × 100 × 2 = **+300 USD**

**Timp total:** 5 ore
**Profit:** +300 USD (+40% cu 2x leverage)

## 🎯 Reguli Day Trading

1. **Volatilitate mare** (Oil, Gold, Forex)
2. **Lichiditate mare** (cumperi/vinzi instant)
3. **Stop Loss STRICT** (-1% până -2%)
4. **Profit mic dar sigur** (+1% până +3%)
5. **Ratio 2:1** (risc 1% pentru profit 2%)

## ⚠️ Riscuri Day Trading

**1. Overtrading**
- Prea multe trades → Pierderi din comisioane
- Oboseală → Decizii proaste

**2. Stress Mare**
- Monitorizare constantă (8 ore/zi)
- Presiune psihologică

**3. Capital Mare Necesar**
- Pentru profit decent din +1-2% mișcări

## ✅ E Day Trading Pentru Tine?

**DA dacă:**
- ✅ Ai timp 4-8 ore/zi
- ✅ Poți lua decizii rapide
- ✅ Rezistă la stress
- ✅ Ai capital > 10,000 USD

**NU dacă:**
- ❌ Ai job full-time
- ❌ Vrei "bani ușori"
- ❌ Capital mic < 5,000 USD
- ❌ Nu ești disciplinat
""",
        "quiz": [
            {
                "question": "Care e diferența principală între Day Trading și Swing Trading?",
                "options": [
                    "Day trading = închizi tot în aceeași zi",
                    "Day trading = leverage mai mare",
                    "Nu există diferență",
                    "Day trading = mai puțin risc"
                ],
                "correct": 0,
                "explanation": "Corect! Day trading = TOATE pozițiile se închid înainte de closing. Swing trading = ții poziții 2-10 zile."
            }
        ]
    }
]

# Tier pricing
PREMIUM_TIER_PRICE = 10.00  # RON
PREMIUM_TIER_CURRENCY = "ron"

# ============================================
# MODELS
# ============================================

class QuizAnswer(BaseModel):
    lesson_id: str
    answers: List[int]  # List of selected answer indices

class ScenarioProgress(BaseModel):
    lesson_id: str
    scenario_step: int
    answer: int

# ============================================
# ROUTES
# ============================================

@router.get("/lessons")
async def get_all_lessons():
    """Get all trading school lessons"""
    return {
        "lessons": TRADING_LESSONS,
        "total": len(TRADING_LESSONS),
        "modules": {
            "module_1": "Fundamentele (Beginner)",
            "module_2": "Risk Management (Intermediate)"
        }
    }

@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get specific lesson"""
    for lesson in TRADING_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found")

@router.post("/quiz/submit")
async def submit_quiz(quiz_data: QuizAnswer, user: dict = Depends(require_auth)):
    """Submit quiz answers and get score"""
    db = await get_database()
    
    # Find lesson
    lesson = None
    for l in TRADING_LESSONS:
        if l["id"] == quiz_data.lesson_id:
            lesson = l
            break
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Calculate score
    quiz = lesson.get("quiz", [])
    correct_count = 0
    results = []
    
    for idx, answer in enumerate(quiz_data.answers):
        if idx < len(quiz):
            is_correct = answer == quiz[idx]["correct"]
            if is_correct:
                correct_count += 1
            
            results.append({
                "question": quiz[idx]["question"],
                "your_answer": quiz[idx]["options"][answer] if answer < len(quiz[idx]["options"]) else "Invalid",
                "correct": is_correct,
                "explanation": quiz[idx]["explanation"]
            })
    
    score_percent = (correct_count / len(quiz)) * 100 if len(quiz) > 0 else 0
    passed = score_percent >= 80
    
    # Save progress
    await db.user_progress.update_one(
        {"user_id": user["user_id"]},
        {
            "$set": {
                f"lessons.{quiz_data.lesson_id}": {
                    "completed": passed,
                    "score": score_percent,
                    "attempts": 1,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        },
        upsert=True
    )
    
    return {
        "lesson_id": quiz_data.lesson_id,
        "score": score_percent,
        "correct": correct_count,
        "total": len(quiz),
        "passed": passed,
        "results": results,
        "message": "Felicitări! Ai trecut!" if passed else "Mai încearcă! Trebuie 80%+ pentru a trece."
    }

@router.get("/progress")
async def get_progress(user: dict = Depends(require_auth)):
    """Get user learning progress"""
    db = await get_database()
    
    progress = await db.user_progress.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not progress:
        return {
            "completed_lessons": [],
            "total_lessons": len(TRADING_LESSONS),
            "progress_percent": 0,
            "current_module": 1,
            "has_premium": False
        }
    
    completed = progress.get("lessons", {})
    completed_count = sum(1 for l in completed.values() if l.get("completed"))
    
    return {
        "completed_lessons": list(completed.keys()),
        "total_lessons": len(TRADING_LESSONS),
        "progress_percent": (completed_count / len(TRADING_LESSONS)) * 100,
        "lessons_detail": completed,
        "has_premium": progress.get("has_premium", False)
    }

@router.post("/purchase-premium")
async def purchase_premium(user: dict = Depends(require_auth)):
    """Create Stripe checkout for premium access"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        import os
        
        api_key = os.environ.get("STRIPE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Stripe not configured")
        
        stripe_client = StripeCheckout(api_key=api_key)
        
        # Create checkout session
        request = CheckoutSessionRequest(
            success_url=f"{os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')}/trading-school?success=true",
            cancel_url=f"{os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')}/trading-school",
            price=PREMIUM_TIER_PRICE,
            currency=PREMIUM_TIER_CURRENCY,
            quantity=1,
            product_name="Trading School Premium",
            product_description="Acces complet la toate cele 25 lecții interactive de trading"
        )
        
        response = stripe_client.create_checkout_session(request)
        
        # Save pending purchase
        db = await get_database()
        await db.premium_purchases.insert_one({
            "user_id": user["user_id"],
            "session_id": response.id,
            "product": "trading_school_premium",
            "price": PREMIUM_TIER_PRICE,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {"checkout_url": response.url, "session_id": response.id}
        
    except Exception as e:
        logger.error(f"Error creating checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check-premium")
async def check_premium_access(user: dict = Depends(require_auth)):
    """Check if user has premium access"""
    db = await get_database()
    
    # Check if purchased
    purchase = await db.premium_purchases.find_one({
        "user_id": user["user_id"],
        "product": "trading_school_premium",
        "status": "completed"
    })
    
    has_premium = purchase is not None
    
    # Update progress
    if has_premium:
        await db.user_progress.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"has_premium": True}},
            upsert=True
        )
    
    return {
        "has_premium": has_premium,
        "total_lessons": len(TRADING_LESSONS),
        "free_lessons": len([l for l in TRADING_LESSONS if l.get("tier") != "premium"]),
        "premium_lessons": len([l for l in TRADING_LESSONS if l.get("tier") == "premium"])
    }
