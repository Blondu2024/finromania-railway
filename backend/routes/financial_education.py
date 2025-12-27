"""Financial Education - Educație Financiară pentru Români"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timezone
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/financial-education", tags=["financial_education"])

# Complete Financial Education Curriculum
FINANCIAL_LESSONS = [
    {
        "id": "fin_lesson_1",
        "module": 1,
        "order": 1,
        "title": "Ce Este Educația Financiară și De Ce Contează",
        "subtitle": "Primul pas către libertate financiară",
        "duration": "8 min",
        "difficulty": "beginner",
        "emoji": "💡",
        "tier": "free",
        "content": """
# Educația Financiară - De Ce Contează?

## 💰 Realitatea din România

**Statistici șocante:**
- 70% din români trăiesc de pe o lună pe alta
- 60% nu au economii pentru urgențe
- 85% nu înțeleg cum funcționează dobânzile
- 90% nu au educație financiară formală

**De ce?** Pentru că **NIMENI nu ne învață despre bani!**
- În școală: NU
- În facultate: NU (doar dacă faci Economie)
- De la părinți: Rar (dacă ei știu)

## 🎯 Ce Înseamnă Educație Financiară?

**Nu e:**
- ❌ Cum să devii milionar overnight
- ❌ Scheme de "bani ușor"
- ❌ Doar pentru bogați

**Este:**
- ✅ Cum să-ți faci un buget
- ✅ Cum să economisești regulat
- ✅ Cum să eviți datorii proaste
- ✅ Cum să investești inteligent
- ✅ Cum să te pregătești pentru pensie

## 💡 Ce Vei Învăța în Acest Curs

**Modul 1: Fundamente**
1. Bugete și gestionarea banilor
2. Fond de urgență
3. Dobânzi și inflație

**Modul 2: Instrumente**
4. Conturi bancare
5. Credite smart
6. Asigurări
7. Pensii în RO

**Modul 3: Investiții**
8. De ce să investești
9. Unde să investești în RO
10. ETF-uri și diversificare

**Rezultat:** Vei avea control complet asupra banilor tăi! 💪

## ✅ Promisiunea Noastră

- 🆓 **100% GRATUIT** - Educația nu ar trebui să coste
- 🇷🇴 **Adaptat pentru România** - Exemple cu RON, bănci RO, taxe RO
- 📚 **Practic** - Apply imediat ce înveți
- 🎯 **Pas cu pas** - De la 0 la expert
- ❓ **Quiz-uri** - Verifică-ți înțelegerea

## 🎓 Gata să Începi?

Prima lecție: Cum să-ți faci un buget care funcționează!
""",
        "quiz": [
            {
                "question": "Ce procent din români NU au economii pentru urgențe?",
                "options": ["30%", "60%", "85%", "95%"],
                "correct": 1,
                "explanation": "Corect! ~60% din români nu au economii pentru urgențe. De aceea fondul de urgență e atât de important - Lecția 3!"
            },
            {
                "question": "Educația financiară înseamnă:",
                "options": [
                    "Scheme de îmbogățire rapidă",
                    "Doar pentru bogați",
                    "Cum să gestionezi banii inteligent",
                    "Cum să devii milionar"
                ],
                "correct": 2,
                "explanation": "Perfect! Educația financiară e despre gestionarea inteligentă a banilor - bugete, economii, investiții - pentru ORICINE!"
            }
        ]
    },
    {
        "id": "fin_lesson_2",
        "module": 1,
        "order": 2,
        "title": "Bugetul Personal - Fundația Succesului Financiar",
        "subtitle": "Regula 50/30/20 care funcționează",
        "duration": "12 min",
        "difficulty": "beginner",
        "emoji": "📊",
        "tier": "free",
        "content": """
# Bugetul Personal

## 💰 De Ce Ai Nevoie de Buget?

**Fără buget:**
- Nu știi pe ce se duc banii
- "Dispare" salariul până la final de lună
- Nu ai control
- Nu poți economisi

**Cu buget:**
- ✅ Știi EXACT pe ce cheltuiești
- ✅ Controlezi fiecare leu
- ✅ Economisești automat
- ✅ Atingi obiective financiare

## 📊 Regula 50/30/20

**Formula simplă care funcționează:**

**50% - NEVOI (Esențiale)**
- Chirie/rată
- Utilități (curent, gaz, apă)
- Mâncare (supermarket, nu restaurante!)
- Transport (abonament, benzină)
- Medicamente

**30% - DORINȚE (Plăceri)**
- Restaurante, cafenele
- Haine, gadgeturi
- Vacanțe
- Hobby-uri
- Entertainment (Netflix, cinema)

**20% - ECONOMII & INVESTIȚII**
- Fond urgență (prima prioritate!)
- Investiții (după fond urgență)
- Obiective (mașină, casă, etc.)

## 💡 Exemplu Practic

**Salariu NET: 5,000 RON/lună**

**50% Nevoi (2,500 RON):**
- Chirie: 1,500 RON
- Utilități: 300 RON
- Mâncare: 600 RON
- Transport: 100 RON

**30% Dorințe (1,500 RON):**
- Restaurante: 500 RON
- Haine: 300 RON
- Entertainment: 200 RON
- Ieșiri: 500 RON

**20% Economii (1,000 RON):**
- Fond urgență: 500 RON (până ajungi la 3-6 luni)
- Investiții: 500 RON (după ce ai fond)

## 🎯 Cum Să-ți Faci Bugetul

**Pas 1: Calculează VENITUL**
- Salariu NET (după taxe)
- Alte venituri

**Pas 2: Înregistrează TOATE Cheltuielile**
- 1 lună completă
- FIECARE leu (da, și cafeaua!)
- Apps: Money Pro, Wallet, Excel

**Pas 3: Clasifică în 3 Categorii**
- Nevoi vs Dorințe vs Economii
- Calculează %

**Pas 4: Ajustează**
- Dacă Nevoi > 50% → Reduce chirie sau găsește soluții
- Dacă Economii < 20% → Reduce Dorințele
- Scopul: 50/30/20!

## ⚠️ Greșeli Comune

**1. "Nu-mi ajung banii pentru economii"**
→ Plătește-te PE TINE primul! Economii = prima cheltuială, nu ce rămâne!

**2. "Tracking e plictisitor"**
→ Folosește apps auto (conectare bancară) - Wallet, Revolut

**3. "E prea strict"**
→ 50/30/20 e ghid, nu lege! Adaptează la situația ta

## 💪 Challenge

**Urmărește cheltuielile 1 lună!**
- Fă-ți un spreadsheet simplu
- Sau folosește Wallet app
- La final, vezi unde se duc banii
- **Vei fi ȘOCAT!** (cafele, livrări, Uber...)
""",
        "quiz": [
            {
                "question": "Regula 50/30/20: Ce înseamnă 20%?",
                "options": [
                    "Cheltuieli esențiale",
                    "Plăceri și dorințe",
                    "Economii și investiții",
                    "Taxe"
                ],
                "correct": 2,
                "explanation": "Corect! 20% din venit trebuie să meargă la ECONOMII și INVESTIȚII. E fundația pentru viitorul tău financiar!"
            },
            {
                "question": "Ai salariu 4,000 RON. Cât ar trebui să economisești lunar (regula 20%)?",
                "options": ["400 RON", "800 RON", "1,200 RON", "2,000 RON"],
                "correct": 1,
                "explanation": "Perfect! 20% din 4,000 = 800 RON/lună. În 1 an = 9,600 RON economii! În 5 ani = 48,000 RON (fără dobândă)!"
            }
        ]
    },
    {
        "id": "fin_lesson_3",
        "module": 1,
        "order": 3,
        "title": "Fondul de Urgență - Perna Ta de Siguranță",
        "subtitle": "3-6 luni fără stres financiar",
        "duration": "10 min",
        "difficulty": "beginner",
        "emoji": "🛡️",
        "tier": "free",
        "content": """
# Fondul de Urgență

## 🚨 Ce E și De Ce E VITAL?

**Fond de urgență** = Bani puși deoparte pentru URGENȚE neprevăzute.

**Urgențe:**
- 🚗 Mașina se strică (reparație 2,000 RON)
- 🏥 Probleme medicale (stomatolog, analize)
- 💼 Pierzi job-ul (trebuie să trăiești 3-6 luni)
- 🏠 Locuința (țeava spartă, frigider stricat)

**Fără fond:** Împrumut (dobânzi!), stres, panică! 😰
**Cu fond:** Plătești cash, dormi liniștit! 😊

## 💰 Cât Trebuie Să Ai?

**Formula:**
```
Fond Urgență = Cheltuieli Lunare × 3-6 luni
```

**Exemplu:**
- Cheltuieli lunare: 3,000 RON
- **Minim:** 3,000 × 3 = **9,000 RON**
- **Ideal:** 3,000 × 6 = **18,000 RON**

**Cât depinde de:**
- Job stabil (3 luni) vs instabil (6 luni)
- Singur (3 luni) vs Familie (6 luni)
- Asigurări multe (3 luni) vs puține (6 luni)

## 🏦 Unde Să-l Ții?

**❌ NU aici:**
- Acțiuni (pot scădea când ai nevoie!)
- Investiții pe termen lung
- Crypto (volatil!)
- Cash acasă (furat, incendiu)

**✅ DA aici:**
- **Cont curent** (acces instant!)
- **Cont economii** (dobândă mică dar OK)
- **Depozit la vedere** (retragere oricând)

**Criterii:**
1. ✅ **Lichiditate** - Acces în 24h
2. ✅ **Siguranță** - Garantat (FGDB în RO)
3. ✅ **Dobândă OK** - Măcar ceva (1-3%)

## 📊 Cum Să-l Construiești

**Pas cu Pas:**

**Luna 1-3:** Economisește 1,000 RON/lună
- După 3 luni: 3,000 RON (1 lună cheltuieli)

**Luna 4-6:** Continuă 1,000 RON/lună
- După 6 luni: 6,000 RON (2 luni)

**Luna 7-12:** 1,000 RON/lună
- După 12 luni: 12,000 RON (4 luni) ✅

**Luna 13-18:** 1,000 RON/lună
- După 18 luni: 18,000 RON (6 luni) 🎉

**Apoi:** Stop building fond → Start investing!

## ⚠️ Când Să-l Folosești

**DA:**
- ✅ Urgență medicală
- ✅ Job pierdut
- ✅ Mașină/casă stricate (urgent)

**NU:**
- ❌ Vacanță (economisești separat!)
- ❌ Gadgeturi noi (dorință, nu urgență)
- ❌ Cadouri (planifică în buget)

**Regula:** Dacă NU e urgență → NU atingi fondul!
""",
        "quiz": [
            {
                "question": "Ai cheltuieli de 4,000 RON/lună. Cât fond de urgență îți trebuie (minim)?",
                "options": ["4,000 RON", "8,000 RON", "12,000 RON", "24,000 RON"],
                "correct": 2,
                "explanation": "Corect! Minim 3 luni × 4,000 = 12,000 RON. Ideal ar fi 6 luni (24,000 RON) pentru siguranță maximă!"
            },
            {
                "question": "Unde NU ar trebui să ții fondul de urgență?",
                "options": [
                    "Cont curent",
                    "Cont economii",
                    "Acțiuni pe bursă",
                    "Depozit la vedere"
                ],
                "correct": 2,
                "explanation": "Corect! Acțiunile pot scădea când ai nevoie de bani! Fondul trebuie în conturi LICHIDE și SIGURE (curent, economii, depozit)."
            }
        ]
    },
    {
        "id": "fin_lesson_4",
        "module": 1,
        "order": 4,
        "title": "Dobânzi - Prietenul și Dușmanul Tău",
        "subtitle": "Cum dobânda compusă te poate îmbogăți sau sărăci",
        "duration": "11 min",
        "difficulty": "beginner",
        "emoji": "📈",
        "tier": "free",
        "content": """
# Dobânzi - Puterea Timpului

## 💰 Ce Sunt Dobânzile?

**Dobânda** = "Chiria" banilor.

**Când PRIMEȘTI dobândă:**
- Depozit bancar (tu împrumuți băncii)
- Obligațiuni (împrumuți statului/companiei)
- Conturi economii

**Când PLĂTEȘTI dobândă:**
- Credit (banca/IFN îți împrumută)
- Card de credit
- Overdraft

## 📊 Dobândă Simplă vs Compusă

### **Dobândă Simplă** (Rară)

**Formula:** Dobândă se calculează DOAR pe suma inițială

**Exemplu:**
- Depui: 10,000 RON
- Dobândă: 5%/an (simplă)
- **An 1:** 10,000 × 5% = +500 RON → Total 10,500 RON
- **An 2:** 10,000 × 5% = +500 RON → Total 11,000 RON
- **An 10:** 10,000 + (500 × 10) = **15,000 RON**

---

### **Dobândă Compusă** (Magică!)

**Formula:** Dobândă se calculează pe sumă + dobânzile anterioare

**"Dobândă la dobândă" = Exponențial!**

**Exemplu:**
- Depui: 10,000 RON
- Dobândă: 5%/an (compusă)
- **An 1:** 10,000 × 5% = +500 RON → **10,500 RON**
- **An 2:** 10,500 × 5% = +525 RON → **11,025 RON**
- **An 3:** 11,025 × 5% = +551 RON → **11,576 RON**
- ...
- **An 10:** **16,289 RON** (vs 15,000 cu simplă!)

**+1,289 RON diferență DOAR din compunere!** 🎉

## 🚀 Puterea Timpului

**Același 10,000 RON la 5% compus:**

- **10 ani:** 16,289 RON (+63%)
- **20 ani:** 26,533 RON (+165%)
- **30 ani:** 43,219 RON (+332%)
- **40 ani:** 70,400 RON (+604%)

**Albert Einstein:** "Dobânda compusă e cea mai puternică forță din univers!"

## 💸 Partea Întunecată - Credite

**Dobânda compusă funcționează ȘI ÎMPOTRIVA TA!**

**Exemplu Credit:**
- Împrumuți: 10,000 RON
- DAE: 15%/an (compusă)
- **An 1:** Datorezi 11,500 RON
- **An 5:** Datorezi 20,114 RON (dublat!)
- **An 10:** Datorezi 40,456 RON (×4!)

**De aceea:**
- ✅ Dobândă la economii = PRIETENA ta
- ❌ Dobândă la credite = DUȘMANUL tău

## 🎯 Lecția Cheie

**Start EARLY!**

**Economii 500 RON/lună la 7% compus:**

**Start la 25 ani (40 ani până la 65):**
- Total investit: 500 × 12 × 40 = 240,000 RON
- **La 65 ani:** **1,310,000 RON!** 🎉

**Start la 35 ani (30 ani până la 65):**
- Total investit: 500 × 12 × 30 = 180,000 RON
- **La 65 ani:** 610,000 RON

**Diferență 10 ani = 700,000 RON pierdut!** 😱

**Timpul bate suma! Start NOW!** ⏰
""",
        "quiz": [
            {
                "question": "10,000 RON la 5% dobândă compusă timp de 20 ani devine aproximativ:",
                "options": ["15,000 RON", "20,000 RON", "26,500 RON", "50,000 RON"],
                "correct": 2,
                "explanation": "Corect! Cu dobândă compusă la 5%, 10,000 RON devine ~26,500 RON în 20 ani. Asta e puterea compunerii!"
            },
            {
                "question": "Când e dobânda compusă DUȘMANUL tău?",
                "options": [
                    "La depozite bancare",
                    "La credite și împrumuturi",
                    "La acțiuni",
                    "Niciodată"
                ],
                "correct": 1,
                "explanation": "Exact! La credite, dobânda compusă lucrează ÎMPOTRIVA ta - datoriile cresc exponențial. De aceea eviți creditele scumpe!"
            }
        ]
    },
    {
        "id": "fin_lesson_5",
        "module": 1,
        "order": 5,
        "title": "Inflația - Dușmanul Invizibil al Economiilor",
        "subtitle": "De ce banii tăi valorează mai puțin în fiecare an",
        "duration": "9 min",
        "difficulty": "beginner",
        "emoji": "📉",
        "tier": "free",
        "content": """
# Inflația

## 📉 Ce Este Inflația?

**Inflația** = Creșterea generală a prețurilor în timp

**Exemplu simplu:**
- **2020:** Pâine = 3 RON
- **2024:** Pâine = 5 RON
- **Inflație:** +67% în 4 ani!

**Rezultat:** Cu aceiași bani cumperi MAI PUȚIN! 😰

## 🇷🇴 Inflația în România

**Istoric recent:**
- **2021:** 5% inflație
- **2022:** 13% inflație (șoc!)
- **2023:** 10% inflație
- **2024:** 7% inflație

**Medie:** ~7-8%/an în România (vs 2-3% în UE)

## 💸 Cum Te Afectează

**Ai 10,000 RON în saltea (0% dobândă):**

**După 1 an (7% inflație):**
- Ai încă: 10,000 RON
- Dar puterea de cumpărare: **9,300 RON** echivalent
- **Pierdere:** -700 RON (-7%)!

**După 10 ani:**
- Ai: 10,000 RON
- Putere cumpărare: **~5,000 RON** echivalent
- **Pierdere:** -50%! Jumătate dispărută! 😱

**Inflația e un taxă invizibilă pe economii!**

## 🛡️ Cum Să Te Protejezi

**❌ PROST: Cash în saltea**
- 0% dobândă
- Pierdere 7%/an din inflație
- **Rezultat:** Sărăcești în fiecare an

**⚠️ OK: Depozit bancar (3-5% dobândă)**
- +5% dobândă
- -7% inflație
- **Rezultat:** Tot pierzi -2%/an (dar mai puțin!)

**✅ BUN: Investiții (8-12% return mediu)**
- +10% return anual
- -7% inflație
- **Rezultat:** +3% REAL gain! Bații inflația! 🎉

## 🎯 Lecția Critică

**"Economisirea" în cont cu 0% dobândă = PIERDERE sigură!**

**De aceea:**
1. Fond urgență → Depozit cu dobândă (minim)
2. Restul economii → **INVESTIȚII** (bate inflația!)

**Investițiile NU sunt opționale - sunt NECESARE pentru a-ți păstra puterea de cumpărare!**

## 📊 Exemplu Real

**Ai 50,000 RON economii în 2024:**

**Opțiunea A: Cash acasă (0%)**
- 2034: Putere cumpărare = **25,000 RON**
- **Pierdere:** -25,000 RON! 😱

**Opțiunea B: Depozit 4%**
- 2034: ~74,000 RON
- Minus inflație: Putere = ~37,000 RON
- **Pierdere:** -13,000 RON 😐

**Opțiunea C: Investiții 10%**
- 2034: ~130,000 RON
- Minus inflație: Putere = ~65,000 RON
- **CÂȘTIG:** +15,000 RON! 🎉

**Concluzie:** Investițiile nu sunt "risc" - CASH-ul e riscul real!
""",
        "quiz": [
            {
                "question": "Ai 10,000 RON în saltea. Cu inflație 7%/an, după 10 ani puterea lor de cumpărare e:",
                "options": ["10,000 RON (la fel)", "~7,000 RON", "~5,000 RON", "~15,000 RON"],
                "correct": 2,
                "explanation": "Corect! Cu 7% inflație compusă 10 ani, 10,000 RON valorează ~5,000 RON în putere de cumpărare. AI PIERDUT JUMĂTATE!"
            }
        ]
    },
    # ==================== MODUL 2: INSTRUMENTE FINANCIARE ====================
    {
        "id": "fin_lesson_6",
        "module": 2,
        "order": 6,
        "title": "Conturi Bancare în România",
        "subtitle": "Alegerea contului potrivit pentru tine",
        "duration": "10 min",
        "difficulty": "intermediate",
        "emoji": "🏦",
        "tier": "free",
        "content": """
# Conturi Bancare în România

## 🏦 Tipuri de Conturi

### 1. Cont Curent
**Ce este:** Cont de zi cu zi pentru tranzacții
- ✅ Card de debit inclus
- ✅ Plăți, transferuri, încasări
- ❌ Dobândă: 0% (sau foarte mică)

**Când să folosești:** Salariu, cheltuieli zilnice

### 2. Cont de Economii
**Ce este:** Cont pentru păstrarea banilor
- ✅ Dobândă mai mare (1-4%)
- ✅ Acces la bani oricând
- ❌ Fără card (unele bănci)

**Când să folosești:** Fond de urgență, economii pe termen scurt

### 3. Depozit la Termen
**Ce este:** Bani blocați pe o perioadă
- ✅ Cea mai mare dobândă (3-6%)
- ❌ Nu poți retrage înainte de termen (penalizare)
- Perioade: 1, 3, 6, 12 luni

**Când să folosești:** Economii pe care știi că nu le atingi

## 💰 Bănci Principale în România

| Bancă | Dobândă Economii | Comision Cont |
|-------|------------------|---------------|
| BCR | 1-3% | 0-15 RON/lună |
| BRD | 1-2.5% | 0-12 RON/lună |
| ING | 1.5-3% | 0 RON |
| Raiffeisen | 1-2.5% | 0-10 RON/lună |

## 🎯 Sfaturi Practice

1. **Compară comisioanele** - Unele bănci au 0 RON/lună
2. **Verifică dobânzile** - Variază mult între bănci
3. **Folosește 2-3 conturi:**
   - Cont curent (cheltuieli)
   - Cont economii (fond urgență)
   - Depozit (economii pe termen lung)
""",
        "quiz": [
            {
                "question": "Ce tip de cont oferă cea mai mare dobândă?",
                "options": ["Cont curent", "Cont de economii", "Depozit la termen", "Toate la fel"],
                "correct": 2,
                "explanation": "Depozitul la termen oferă cea mai mare dobândă pentru că banii sunt blocați o perioadă."
            }
        ]
    },
    {
        "id": "fin_lesson_7",
        "module": 2,
        "order": 7,
        "title": "Credite Inteligente vs Datorii Proaste",
        "subtitle": "Când să iei credit și când să eviți",
        "duration": "12 min",
        "difficulty": "intermediate",
        "emoji": "💳",
        "tier": "free",
        "content": """
# Credite - Când DA și Când NU

## 🟢 Credite BUNE (Investiții)

### Credit Ipotecar (Casa)
- ✅ Dobândă mică (5-8%)
- ✅ Locuința crește în valoare
- ✅ Plătești pentru TINE, nu chirie la altcineva
- **Regulă:** Rata < 30% din venit

### Credit pentru Educație
- ✅ Investiție în tine
- ✅ Crește venitul pe termen lung
- ✅ Dobânzi subvenționate

### Credit pentru Afacere
- ✅ Poate genera venit > dobânda
- ⚠️ Riscant - trebuie plan solid

## 🔴 Credite PROASTE (Consum)

### Card de Credit (Nedecont)
- ❌ Dobândă URIAȘĂ (20-30%!)
- ❌ Plătești dublu pentru produse
- ❌ Ciclul datoriilor

### Credit de Nevoi Personale
- ❌ Dobândă mare (10-15%)
- ❌ Pentru lucruri care NU cresc în valoare
- ❌ Vacanțe, gadgeturi, haine = CREDIT PROST

### IFN-uri (Credite Rapide)
- ❌❌ Dobândă CRIMINALĂ (50-200%!)
- ❌ Te îngroapă în datorii
- **EVITĂ CU ORICE PREȚ!**

## 📊 DAE - Ce Trebuie Să Știi

**DAE (Dobânda Anuală Efectivă)** = costul REAL al creditului

Include:
- Dobânda nominală
- Comisioane
- Asigurări obligatorii

**Exemplu:**
- "Dobândă 5%" dar DAE 8% = costul REAL e 8%!

## 🎯 Reguli de Aur

1. **Niciodată credit pentru DORINȚE** - Doar pentru NEVOI sau INVESTIȚII
2. **DAE < 10%** = acceptabil
3. **Rata totală < 40% din venit** (toate creditele)
4. **Card credit = RAMBURSARE INTEGRALĂ lunar**
5. **Evită IFN-urile** cu orice preț!
""",
        "quiz": [
            {
                "question": "Care credit este considerat 'BUN' (investiție)?",
                "options": ["Credit vacanță", "Credit telefon nou", "Credit ipotecar", "Credit IFN rapid"],
                "correct": 2,
                "explanation": "Creditul ipotecar e o investiție - casa crește în valoare și plătești pentru tine, nu chirie altcuiva!"
            },
            {
                "question": "Ce înseamnă DAE 15%?",
                "options": ["Rata lunară", "Costul total anual real al creditului", "Comisionul băncii", "Dobânda pe lună"],
                "correct": 1,
                "explanation": "DAE (Dobânda Anuală Efectivă) e costul REAL total al creditului, incluzând toate comisioanele!"
            }
        ]
    },
    {
        "id": "fin_lesson_8",
        "module": 2,
        "order": 8,
        "title": "Asigurări - Care Sunt Necesare?",
        "subtitle": "Protejează-te fără să arunci banii",
        "duration": "10 min",
        "difficulty": "intermediate",
        "emoji": "🛡️",
        "tier": "free",
        "content": """
# Asigurări în România

## ✅ Asigurări NECESARE

### 1. Asigurare Auto (RCA)
- **Obligatorie** legal
- Acoperă daunele pe care le produci altora
- Cost: 500-2000 RON/an

### 2. Asigurare de Sănătate
- CNAS (de la stat) - obligatorie
- **Privată:** Pentru servicii rapide, de calitate
- Cost privat: 100-300 EUR/an

### 3. Asigurare de Viață (dacă ai familie)
- Protejează familia dacă ți se întâmplă ceva
- **Când:** Ai copii, credit ipotecar, soț/soție dependent
- Cost: 200-500 RON/an

### 4. Asigurare Locuință
- **PAD** (obligatorie pentru credite)
- Incendiu, cutremur, inundație
- Cost: 50-200 RON/an

## ⚠️ Asigurări OPȚIONALE

### CASCO Auto
- Acoperă daunele la MAȘINA TA
- **Când merită:** Mașină nouă/scumpă
- Cost: 1000-3000 RON/an

### Asigurare de Călătorie
- **Când:** Călătorii în afara UE
- Cost: 20-100 RON/călătorie

## 🎯 Sfaturi

1. **Nu te supraasigura** - Plătești pentru nimic
2. **Compară prețuri** - Diferențe mari între asigurători
3. **Citește contractul** - Ce NU acoperă?
4. **Prioritizează:**
   - RCA (obligatoriu)
   - Sănătate privată
   - Viață (dacă ai familie)
   - Locuință
""",
        "quiz": [
            {
                "question": "Care asigurare este OBLIGATORIE pentru șoferi?",
                "options": ["CASCO", "RCA", "Asigurare de viață", "Niciuna"],
                "correct": 1,
                "explanation": "RCA (Răspundere Civilă Auto) este obligatorie legal pentru toți șoferii din România!"
            }
        ]
    },
    {
        "id": "fin_lesson_9",
        "module": 2,
        "order": 9,
        "title": "Sistemul de Pensii în România",
        "subtitle": "Pilonul I, II, III - Ce trebuie să știi",
        "duration": "11 min",
        "difficulty": "intermediate",
        "emoji": "👴",
        "tier": "free",
        "content": """
# Pensii în România

## 📊 Cele 3 Piloane

### Pilonul I - Pensia de Stat
**Ce este:** Pensia publică de la stat
- **Contribuție:** 25% din salariu (obligatoriu)
- **Problemă:** Banii tăi plătesc pensionarii de AZI
- **Risc:** Fondul de pensii e sub-finanțat

**Realitatea:**
- Pensia medie: ~2000 RON (2024)
- Probabil va scădea vs inflație

### Pilonul II - Pensia Obligatorie Privată
**Ce este:** Fond privat de pensii (NN, Allianz, etc.)
- **Contribuție:** 3.75% din salariu (obligatoriu)
- **Avantaj:** Banii SUNT AI TĂI
- **Investiți:** În acțiuni, obligațiuni

**La pensie:** Primești TOATE contribuțiile + randament

### Pilonul III - Pensia Voluntară
**Ce este:** Economisești TU extra pentru pensie
- **Contribuție:** Cât vrei tu (opțional)
- **Avantaj fiscal:** Deducere până la 400 EUR/an
- **Flexibilitate:** Poți retrage după 5 ani

## 🧮 Calculator Realist

**Salariu: 5000 RON net | 40 ani contribuție**

| Pilon | Contribuție/lună | La pensie (estimat) |
|-------|------------------|---------------------|
| I (stat) | ~1250 RON | ~2500 RON/lună |
| II (privat) | ~190 RON | ~150,000 RON total |
| III (voluntar) | 200 RON TU | ~200,000 RON total |

## 🎯 Ce Să Faci

1. **Nu te baza pe statul** - Pilonul I e nesigur
2. **Verifică Pilonul II** - Alege fondul cu cel mai bun randament
3. **Contribuie la Pilonul III** - Măcar 200-400 RON/lună
4. **Investește separat** - ETF-uri, acțiuni (lecțiile următoare!)
""",
        "quiz": [
            {
                "question": "Care pilon de pensie îți aparține 100% și poți alege unde se investesc banii?",
                "options": ["Pilonul I (stat)", "Pilonul II (privat obligatoriu)", "Pilonul III (voluntar)", "Niciunul"],
                "correct": 2,
                "explanation": "Pilonul III e complet voluntar - tu decizi cât contribui și la ce fond, iar banii sunt 100% ai tăi!"
            }
        ]
    },
    {
        "id": "fin_lesson_10",
        "module": 2,
        "order": 10,
        "title": "Taxe și Impozite în România",
        "subtitle": "Ce plătești și cum să optimizezi legal",
        "duration": "10 min",
        "difficulty": "intermediate",
        "emoji": "📋",
        "tier": "free",
        "content": """
# Taxe în România

## 💰 Ce Plătești ca Angajat

**Din salariul BRUT:**
- **CAS (pensii):** 25%
- **CASS (sănătate):** 10%
- **Impozit pe venit:** 10%

**Exemplu: Brut 7000 RON**
- CAS: 1750 RON
- CASS: 700 RON
- Impozit: 455 RON
- **NET: ~4095 RON**

## 📊 Alte Taxe Importante

### Impozit pe Dividende
- **8%** din dividende primite
- Plătit de companie la sursă

### Impozit pe Câștiguri din Investiții
- **10%** din profit (acțiuni, ETF-uri)
- Plătit DOAR când vinzi cu profit

### Impozit pe Chirii
- **10%** din chirie (după deduceri)
- Poți deduce 40% cheltuieli

### TVA
- **19%** standard
- **9%** (alimente, medicamente)
- **5%** (cărți, hoteluri)

## 🎯 Optimizări Legale

1. **Pilonul III Pensii**
   - Deducere până la 400 EUR/an din impozit

2. **Asigurări de Sănătate Private**
   - Deducere până la 400 EUR/an

3. **PFA/SRL pentru Freelanceri**
   - Taxe mai mici vs contract de muncă
   - Consultă un contabil!

4. **Investiții pe Termen Lung**
   - Ții > 1 an = mai puține taxe la vânzare

## ⚠️ Evită Evaziunea!

- **Evaziune fiscală** = ILEGAL
- **Optimizare fiscală** = LEGAL
- Diferența: folosești cadrul legal, nu îl încalci
""",
        "quiz": [
            {
                "question": "Cât impozit plătești pe profitul din acțiuni vândute?",
                "options": ["0%", "5%", "10%", "16%"],
                "correct": 2,
                "explanation": "În România, impozitul pe câștigurile din investiții (capital gains) este 10% din profit."
            }
        ]
    },
    # ==================== MODUL 3: INTRODUCERE ÎN INVESTIȚII ====================
    {
        "id": "fin_lesson_11",
        "module": 3,
        "order": 11,
        "title": "De Ce Să Investești?",
        "subtitle": "Investițiile nu sunt opționale",
        "duration": "9 min",
        "difficulty": "advanced",
        "emoji": "🚀",
        "tier": "free",
        "content": """
# De Ce Trebuie Să Investești

## 💸 Problema: Inflația Te Sărăcește

Am învățat în Lecția 5:
- Cash pierde 7%/an din valoare
- Depozitul bancar abia ține pasul
- **Singura soluție:** Investiții!

## 📊 Randamente Istorice

**Medie anuală pe 30+ ani:**
- 💵 Cash: 0% (- inflație = PIERDERE)
- 🏦 Depozit: 3-4%
- 🏠 Imobiliare: 5-7%
- 📈 Obligațiuni: 4-6%
- 📊 Acțiuni (S&P 500): **10-11%**

## 🧮 Puterea Investițiilor

**500 RON/lună timp de 30 ani:**

| Unde | Randament | Total Final |
|------|-----------|-------------|
| Saltea | 0% | 180,000 RON |
| Depozit | 3% | 290,000 RON |
| Acțiuni | 10% | **1,130,000 RON** |

**Diferența:** 850,000 RON! 🤯

## 🎯 De Ce Mulți Nu Investesc

1. **"E prea riscant"**
   - Riscul real e să NU investești
   - Pe termen lung, acțiunile CRESC

2. **"Nu am bani"**
   - Poți începe cu 100 RON/lună
   - Contează CONSISTENȚA, nu suma

3. **"Nu mă pricep"**
   - ETF-uri = simplu, diversificat
   - Nu trebuie să fii expert

4. **"O să pierd tot"**
   - Diversificare = protecție
   - În 100+ ani, S&P 500 a crescut MEREU pe termen lung

## ✅ Concluzie

**A investi NU e despre:**
- Scheme de îmbogățire rapidă
- A "ghici" piața
- A deveni milionar overnight

**A investi ESTE despre:**
- A-ți proteja banii de inflație
- A construi avere în timp
- A avea opțiuni la pensie
""",
        "quiz": [
            {
                "question": "Care instrument financiar a avut cel mai mare randament istoric pe 30+ ani?",
                "options": ["Cash", "Depozit bancar", "Obligațiuni", "Acțiuni (S&P 500)"],
                "correct": 3,
                "explanation": "Acțiunile (ex: S&P 500) au avut randament mediu de 10-11% pe an, bătând inflația și toate celelalte instrumente!"
            }
        ]
    },
    {
        "id": "fin_lesson_12",
        "module": 3,
        "order": 12,
        "title": "Unde Poți Investi în România",
        "subtitle": "Opțiuni pentru începători",
        "duration": "12 min",
        "difficulty": "advanced",
        "emoji": "🇷🇴",
        "tier": "free",
        "content": """
# Opțiuni de Investiții în România

## 1. 🏦 Depozite și Titluri de Stat

### Depozite Bancare
- Risc: ZERO (garantat FGDB până la 100,000 EUR)
- Randament: 3-6%/an
- **Pentru:** Fond de urgență

### Titluri de Stat (Tezaur, Fidelis)
- Risc: Foarte mic (garantat de stat)
- Randament: 5-7%/an
- **Pentru:** Economii pe termen mediu

## 2. 📈 Bursa (Acțiuni)

### BVB (Bursa de Valori București)
- Acțiuni românești: Banca Transilvania, OMV Petrom, etc.
- Risc: Mediu-mare
- Randament: 8-15%/an (variabil)

### Burse Internaționale
- Apple, Google, Tesla, etc.
- Prin brokeri precum: XTB, eToro, Interactive Brokers
- Risc: Mediu-mare

## 3. 📊 ETF-uri (RECOMANDAT pentru Începători!)

**Ce sunt:** Fonduri care urmăresc un indice
- **Ex:** S&P 500 ETF = 500 cele mai mari companii din SUA

**Avantaje:**
- ✅ Diversificare automată
- ✅ Costuri mici
- ✅ Nu trebuie să alegi acțiuni individuale
- ✅ Randament mediu piață

**ETF-uri populare:**
- VWCE (Vanguard All-World) - Toată lumea
- CSPX (S&P 500) - SUA
- EUNL (Europe) - Europa

## 4. 🏠 Imobiliare

**Direct:**
- Cumperi apartament pentru închiriat
- Randament: 4-7%/an + apreciere
- Nevoie: Capital mare (50,000+ EUR)

**Indirect (REIT-uri):**
- Fonduri imobiliare pe bursă
- Poți investi de la 100 RON
- Lichiditate mare

## 🎯 Recomandare pentru Începători

**Portofoliu simplu:**
1. **Fond urgență** → Depozit/Titluri de Stat
2. **Investiții termen lung** → ETF pe S&P 500 sau All-World
3. **Contribuție lunară** → 200-500 RON constant
""",
        "quiz": [
            {
                "question": "Ce instrument e RECOMANDAT pentru începători?",
                "options": ["Acțiuni individuale", "Crypto", "ETF-uri", "Forex"],
                "correct": 2,
                "explanation": "ETF-urile oferă diversificare automată, costuri mici și nu necesită alegerea acțiunilor individuale - perfecte pentru începători!"
            }
        ]
    },
    {
        "id": "fin_lesson_13",
        "module": 3,
        "order": 13,
        "title": "ETF-uri - Ghid Complet",
        "subtitle": "Cel mai simplu mod de a investi",
        "duration": "11 min",
        "difficulty": "advanced",
        "emoji": "📊",
        "tier": "free",
        "content": """
# ETF-uri - Tot Ce Trebuie Să Știi

## 📖 Ce Este un ETF?

**ETF (Exchange Traded Fund)** = Fond de investiții tranzacționat la bursă

**Imaginează-ți:**
- Vrei să cumperi acțiuni la 500 companii (S&P 500)
- Ar costa zeci de mii de dolari
- **ETF:** Cumperi 1 unitate care CONȚINE toate 500!

## 🎯 De Ce ETF-uri?

### ✅ Avantaje
1. **Diversificare instantă** - Sute/mii de companii
2. **Costuri mici** - TER 0.03-0.20%/an
3. **Simplu** - Cumperi ca o acțiune
4. **Lichid** - Vinzi oricând
5. **Transparent** - Știi exact ce conține

### ❌ Dezavantaje
1. Nu bați piața (urmărești media)
2. Randament depinde de piață

## 📊 ETF-uri Populare

| ETF | Ce Urmărește | TER | Randament Mediu |
|-----|--------------|-----|-----------------|
| VWCE | Toată lumea | 0.22% | 8-9% |
| CSPX | S&P 500 | 0.07% | 10-11% |
| EUNL | Europa | 0.12% | 6-8% |
| IWDA | Țări dezvoltate | 0.20% | 8-9% |

## 🛒 Cum Cumperi ETF-uri în România

**Pas 1: Alege un broker**
- XTB (0 comision)
- Interactive Brokers
- Trading 212

**Pas 2: Deschide cont**
- Online, 15-30 minute
- Verificare identitate

**Pas 3: Alimentează contul**
- Transfer bancar

**Pas 4: Cumpără ETF-ul**
- Caută simbolul (ex: VWCE)
- Alege suma
- Cumpără!

## 🎯 Strategie Recomandată

**DCA (Dollar Cost Averaging):**
- Investești ACEEAȘI sumă lunar
- Ex: 300 RON pe 15 ale fiecărei luni
- Nu contează dacă piața e sus sau jos
- Pe termen lung: randament optim!
""",
        "quiz": [
            {
                "question": "Ce este TER la un ETF?",
                "options": ["Taxa de tranzacție", "Costul anual al fondului", "Randamentul garantat", "Taxa de retragere"],
                "correct": 1,
                "explanation": "TER (Total Expense Ratio) e costul anual de administrare al fondului - cu cât mai mic, cu atât mai bine! (ex: 0.07%)"
            },
            {
                "question": "Ce strategie e recomandată pentru investiții în ETF-uri?",
                "options": ["All-in când piața e jos", "Cumpără și vinde frecvent", "DCA (sumă fixă lunar)", "Doar când ai bani extra"],
                "correct": 2,
                "explanation": "DCA (Dollar Cost Averaging) - investești aceeași sumă lunar indiferent de piață. Pe termen lung, e cea mai sigură strategie!"
            }
        ]
    },
    {
        "id": "fin_lesson_14",
        "module": 3,
        "order": 14,
        "title": "Diversificarea - Nu Pune Toate Ouăle într-un Coș",
        "subtitle": "Cum să reduci riscul investițiilor",
        "duration": "9 min",
        "difficulty": "advanced",
        "emoji": "🥚",
        "tier": "free",
        "content": """
# Diversificarea Portofoliului

## 🎯 Ce Este Diversificarea?

**Principiu:** Nu pune toți banii într-o singură investiție

**De ce?**
- Dacă acea investiție scade → Pierzi TOT
- Dacă ai mai multe → Pierderile se compensează

## 📊 Tipuri de Diversificare

### 1. Pe Clase de Active
- Acțiuni (creștere)
- Obligațiuni (stabilitate)
- Cash (siguranță)
- Imobiliare (venit pasiv)

### 2. Geografică
- SUA
- Europa
- Asia
- Piețe emergente

### 3. Pe Sectoare
- Tehnologie
- Sănătate
- Financiar
- Energie

### 4. Pe Timp
- Investiții lunare (DCA)
- Nu totul deodată

## 🧮 Portofolii Model

### Agresiv (20-35 ani)
- 90% Acțiuni (ETF VWCE)
- 10% Obligațiuni/Cash

### Moderat (35-50 ani)
- 70% Acțiuni
- 20% Obligațiuni
- 10% Cash

### Conservator (50+ ani)
- 40% Acțiuni
- 40% Obligațiuni
- 20% Cash

## 💡 Regula 110

**Câte acțiuni să ai:**
- 110 - Vârsta ta = % în acțiuni

**Exemplu:**
- 30 ani: 110 - 30 = 80% acțiuni
- 50 ani: 110 - 50 = 60% acțiuni

## 🎯 Sfaturi Practice

1. **Un singur ETF global = diversificare automată**
   - VWCE = 3000+ companii din toată lumea

2. **Nu te complica**
   - 1-3 ETF-uri sunt suficiente

3. **Rebalansare anuală**
   - Ajustează proporțiile o dată pe an
""",
        "quiz": [
            {
                "question": "Conform regulii 110, cât % în acțiuni ar trebui să aibă cineva de 40 ani?",
                "options": ["40%", "60%", "70%", "90%"],
                "correct": 2,
                "explanation": "110 - 40 = 70%. La 40 de ani, aproximativ 70% din portofoliu ar trebui să fie în acțiuni."
            }
        ]
    },
    {
        "id": "fin_lesson_15",
        "module": 3,
        "order": 15,
        "title": "Plan de Acțiune - Începe ACUM!",
        "subtitle": "Pașii concreți pentru a începe să investești",
        "duration": "8 min",
        "difficulty": "advanced",
        "emoji": "🎯",
        "tier": "free",
        "content": """
# Plan de Acțiune - Începe Azi!

## ✅ Checklist Final

### Pas 1: Fundamente (Săptămâna 1)
- [ ] Fă-ți un buget 50/30/20
- [ ] Calculează cheltuielile lunare
- [ ] Setează un obiectiv de economii

### Pas 2: Fond de Urgență (Luna 1-6)
- [ ] Deschide cont de economii separat
- [ ] Pune 500-1000 RON/lună
- [ ] Țintă: 3-6 luni de cheltuieli

### Pas 3: Pregătire Investiții (Luna 3)
- [ ] Deschide cont la broker (XTB, IBKR)
- [ ] Verifică identitatea
- [ ] Alimentează cu 100-500 RON (test)

### Pas 4: Începe să Investești (Luna 4+)
- [ ] Alege ETF-ul (VWCE sau CSPX)
- [ ] Setează transfer automat lunar
- [ ] Cumpără la aceeași dată lunar

### Pas 5: Menținere (Permanent)
- [ ] NU te uita la portofoliu zilnic
- [ ] Investește CONSISTENT
- [ ] Rebalansează anual

## 🎯 Sumarul Cursului

### Ce Ai Învățat:
1. ✅ Bugetul 50/30/20
2. ✅ Fondul de urgență
3. ✅ Dobânzi și inflație
4. ✅ Conturi și credite
5. ✅ Asigurări și pensii
6. ✅ Taxe în România
7. ✅ De ce să investești
8. ✅ Unde să investești
9. ✅ ETF-uri și diversificare

### Reguli de Aur:
- 💰 Plătește-te PE TINE primul
- 🛡️ Fond urgență ÎNAINTE de investiții
- 📈 Investește CONSISTENT (DCA)
- 🥚 DIVERSIFICĂ
- ⏰ TIMP în piață > Timing piața
- 🧘 Rămâi CALM în scăderi

## 🏆 Felicitări!

Ai parcurs primul pas spre libertate financiară!

**Următorii pași:**
1. Aplică ce ai învățat
2. Continuă să te educi
3. Vorbește cu un consilier financiar dacă ai nevoie
4. Distribuie cunoștințele și altora!

**Amintește-ți:**
> "Cel mai bun moment să începi să investești era acum 20 de ani. Al doilea cel mai bun moment este ACUM."
""",
        "quiz": [
            {
                "question": "Care este ordinea corectă a pașilor financiari?",
                "options": [
                    "Investiții → Fond urgență → Buget",
                    "Buget → Fond urgență → Investiții",
                    "Fond urgență → Investiții → Buget",
                    "Investiții → Buget → Fond urgență"
                ],
                "correct": 1,
                "explanation": "Corect! Prima faci buget, apoi construiești fondul de urgență, și ABIA APOI începi să investești!"
            },
            {
                "question": "Care e cea mai importantă regulă pentru investiții pe termen lung?",
                "options": [
                    "Să ghicești când piața e la minim",
                    "Să investești consistent și să ai răbdare",
                    "Să urmărești știrile zilnic",
                    "Să schimbi strategia frecvent"
                ],
                "correct": 1,
                "explanation": "Consistența și răbdarea sunt cheile succesului! Timp în piață bate timing-ul pieței. Investește regulat și lasă timpul să lucreze pentru tine!"
            }
        ]
    }
]

# Total lessons tracking
FREE_FIN_LESSONS = len([l for l in FINANCIAL_LESSONS if l.get("tier", "free") == "free"])
TOTAL_FIN_LESSONS = len(FINANCIAL_LESSONS)

# Quiz submission
class QuizAnswer(BaseModel):
    lesson_id: str
    answers: List[int]

@router.get("/lessons")
async def get_financial_lessons():
    """Get all financial education lessons"""
    return {
        "lessons": FINANCIAL_LESSONS,
        "total": len(FINANCIAL_LESSONS),
        "modules": {
            "module_1": "Fundamente Finanțe Personale",
            "module_2": "Instrumente Financiare în România",
            "module_3": "Introducere în Investiții"
        }
    }

@router.get("/lessons/{lesson_id}")
async def get_financial_lesson(lesson_id: str):
    """Get specific lesson"""
    for lesson in FINANCIAL_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found")

@router.post("/quiz/submit")
async def submit_financial_quiz(quiz_data: QuizAnswer, user: dict = Depends(require_auth)):
    """Submit quiz answers"""
    db = await get_database()
    
    lesson = None
    for l in FINANCIAL_LESSONS:
        if l["id"] == quiz_data.lesson_id:
            lesson = l
            break
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
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
    await db.user_financial_progress.update_one(
        {"user_id": user["user_id"]},
        {
            "$set": {
                f"lessons.{quiz_data.lesson_id}": {
                    "completed": passed,
                    "score": score_percent,
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
async def get_financial_progress(user: dict = Depends(require_auth)):
    """Get learning progress"""
    db = await get_database()
    
    progress = await db.user_financial_progress.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not progress:
        return {
            "completed_lessons": [],
            "total_lessons": len(FINANCIAL_LESSONS),
            "progress_percent": 0
        }
    
    completed = progress.get("lessons", {})
    completed_count = sum(1 for l in completed.values() if l.get("completed"))
    
    return {
        "completed_lessons": list(completed.keys()),
        "total_lessons": len(FINANCIAL_LESSONS),
        "progress_percent": (completed_count / len(FINANCIAL_LESSONS)) * 100,
        "lessons_detail": completed
    }
