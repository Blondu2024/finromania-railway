import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';

export default function TermsOfServicePage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <FileText className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">Termeni și Condiții</h1>
      </div>
      
      <p className="text-muted-foreground">Ultima actualizare: 23 Decembrie 2025</p>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">1. Acceptarea termenilor</h2>
            <p>
              Prin accesarea și utilizarea platformei FinRomania, acceptați să fiți legat de acești 
              Termeni și Condiții. Dacă nu sunteți de acord cu acești termeni, vă rugăm să nu 
              utilizați site-ul nostru.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">2. Descrierea serviciului</h2>
            <p>
              FinRomania este o platformă de informare financiară care oferă:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Știri financiare din surse românești</li>
              <li>Informații despre acțiuni de pe Bursa de Valori București</li>
              <li>Cursuri valutare de la Banca Națională a României</li>
              <li>Informații despre indici bursieri globali</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">3. Disclaimer financiar</h2>
            <p className="font-semibold text-red-600 dark:text-red-400">
              IMPORTANT: Informațiile prezentate pe FinRomania au caracter exclusiv informativ și 
              NU constituie sfaturi de investiții, recomandări financiare sau îndemnuri de a cumpăra 
              sau vinde instrumente financiare.
            </p>
            <p>
              Deciziile de investiții trebuie luate pe baza propriei cercetări și, dacă este necesar, 
              cu consultarea unui consilier financiar autorizat. Nu ne asumăm responsabilitatea pentru 
              pierderile financiare rezultate din decizii bazate pe informațiile de pe această platformă.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">4. Proprietate intelectuală</h2>
            <p>
              Conținutul platformei FinRomania, inclusiv logo-ul, designul, textele și codul sursă, 
              este protejat de drepturile de autor. Știrile agregate sunt proprietatea surselor 
              originale și sunt utilizate conform legilor privind drepturile de autor.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">5. Surse de date</h2>
            <p>Datele prezentate provin din următoarele surse:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Știri:</strong> Ziarul Financiar, Profit.ro, Bursa, Wall-Street.ro, Capital.ro</li>
              <li><strong>Cursuri valutare:</strong> Banca Națională a României (BNR)</li>
              <li><strong>Indici globali:</strong> Yahoo Finance</li>
              <li><strong>Date BVB:</strong> Date simulate (în curs de implementare date reale)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">6. Limitarea răspunderii</h2>
            <p>
              FinRomania nu garantează acuratețea, completitudinea sau actualitatea informațiilor 
              prezentate. Datele pot fi întârziate sau pot conține erori. Utilizați informațiile 
              pe propria răspundere.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">7. Disponibilitatea serviciului</h2>
            <p>
              Ne rezervăm dreptul de a modifica, suspenda sau întrerupe serviciul în orice moment, 
              fără notificare prealabilă. Nu garantăm disponibilitatea continuă a platformei.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">8. Modificări ale termenilor</h2>
            <p>
              Ne rezervăm dreptul de a modifica acești Termeni și Condiții în orice moment. 
              Continuarea utilizării platformei după modificări constituie acceptarea noilor termeni.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">9. Legislație aplicabilă</h2>
            <p>
              Acești termeni sunt guvernați de legile României. Orice dispută va fi soluționată 
              de instanțele competente din România.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">10. Contact</h2>
            <p>
              Pentru întrebări despre acești Termeni și Condiții: <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
