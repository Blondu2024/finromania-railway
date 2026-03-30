import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowLeft, Shield } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';

export default function PrivacyPolicyPage() {
  const { t } = useTranslation();
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <Shield className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">Politica de Confidențialitate</h1>
      </div>
      
      <p className="text-muted-foreground">Ultima actualizare: 23 Decembrie 2025</p>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">1. Introducere</h2>
            <p>
              FinRomania ("noi", "al nostru" sau "Platforma") respectă confidențialitatea vizitatorilor 
              și utilizatorilor săi. Această Politică de Confidențialitate explică modul în care colectăm, 
              folosim, divulgăm și protejăm informațiile dumneavoastră atunci când vizitați site-ul nostru.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">2. Informații pe care le colectăm</h2>
            <p>Putem colecta următoarele tipuri de informații:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Informații de navigare:</strong> adresa IP, tipul de browser, paginile vizitate, ora vizitei</li>
              <li><strong>Cookie-uri:</strong> folosim cookie-uri pentru a îmbunătăți experiența de utilizare (vezi Politica de Cookie-uri)</li>
              <li><strong>Preferințe:</strong> setările temei (mod întunecat/luminos)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">3. Cum folosim informațiile</h2>
            <p>Informațiile colectate sunt folosite pentru:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Furnizarea și menținerea serviciului nostru</li>
              <li>Îmbunătățirea și personalizarea experienței utilizatorului</li>
              <li>Analizarea modului în care este utilizat site-ul</li>
              <li>Detectarea și prevenirea problemelor tehnice</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">4. Partajarea informațiilor</h2>
            <p>
              Nu vindem, nu comercializăm și nu transferăm în alt mod informațiile dumneavoastră 
              personale către terți, cu excepția cazurilor în care este necesar pentru furnizarea 
              serviciului (de exemplu, furnizori de hosting).
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">5. Securitatea datelor</h2>
            <p>
              Implementăm măsuri de securitate adecvate pentru a proteja informațiile dumneavoastră 
              împotriva accesului neautorizat, modificării, divulgării sau distrugerii.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">6. Drepturile dumneavoastră (GDPR)</h2>
            <p>Conform Regulamentului General privind Protecția Datelor (GDPR), aveți dreptul:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Să accesați datele personale pe care le deținem despre dumneavoastră</li>
              <li>Să solicitați rectificarea datelor inexacte</li>
              <li>Să solicitați ștergerea datelor</li>
              <li>Să vă opuneți prelucrării datelor</li>
              <li>Să solicitați portabilitatea datelor</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">7. Contact</h2>
            <p>
              Pentru orice întrebări legate de această Politică de Confidențialitate, 
              ne puteți contacta la: <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
