# Instrucțiuni pentru Indexare Google Search Console

## Sitemap URL-uri

### Sitemap Principal (Dinamic)
```
https://finromania.ro/api/sitemap.xml
```

Acest sitemap conține **271+ URL-uri** generate automat:
- 20 pagini statice principale
- 20+ acțiuni BVB individuale
- 6+ indici globali
- 200 știri (100 românești + 100 internaționale)
- 25 lecții educaționale

### Cum să submitiți sitemap-ul în Google Search Console:

1. **Accesați** Google Search Console: https://search.google.com/search-console
2. **Selectați** proprietatea finromania.ro
3. **Mergeți la** "Sitemaps" din meniu
4. **Adăugați** sitemap-ul: `api/sitemap.xml`
5. **Apăsați** "Submit"

### Verificare Robots.txt
```
https://finromania.ro/robots.txt
```

### URL-uri Importante pentru Indexare Prioritară

#### Pagini Principale (Priority 1.0 - 0.8)
- https://finromania.ro/ (Homepage)
- https://finromania.ro/stocks (BVB Stocks)
- https://finromania.ro/global (Piețe Globale)
- https://finromania.ro/calculator-fiscal (Calculator Fiscal PRO)
- https://finromania.ro/news (Știri)
- https://finromania.ro/pricing (Prețuri)

#### Acțiuni BVB (Priority 0.8)
- https://finromania.ro/stocks/TLV
- https://finromania.ro/stocks/SNP
- https://finromania.ro/stocks/BRD
- https://finromania.ro/stocks/SNG
- etc.

#### Educație (Priority 0.65-0.7)
- https://finromania.ro/trading-school
- https://finromania.ro/financial-education
- https://finromania.ro/trading-school/1 până la /10
- https://finromania.ro/financial-education/1 până la /15

### Forțare Re-indexare pentru Pagini Importante

În Google Search Console > URL Inspection:
1. Introduceți URL-ul paginii
2. Click "Request Indexing"

### Structura Meta Tags

Fiecare pagină include:
- `<title>` - Titlu optimizat SEO
- `<meta name="description">` - Descriere unică
- `<meta property="og:*">` - Open Graph pentru social
- `<meta name="twitter:*">` - Twitter Cards
- `<script type="application/ld+json">` - Structured Data

### Structured Data Types

1. **WebSite** - Pentru homepage
2. **Organization** - Pentru brand
3. **NewsArticle** - Pentru știri
4. **Course** - Pentru lecții educaționale
5. **FinancialProduct** - Pentru pagini de acțiuni

### Tips pentru Indexare Mai Rapidă

1. **Submitiți sitemap-ul** în Search Console
2. **Cereți indexare** pentru paginile principale
3. **Distribuiți linkuri** pe social media
4. **Adăugați site-ul** în Google Business Profile
5. **Verificați** că nu sunt erori în Coverage report

### Monitorizare

Verificați periodic:
- Coverage > Excluded - pentru probleme
- Sitemaps > Status
- URL Inspection pentru pagini specifice
