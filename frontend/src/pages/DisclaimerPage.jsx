import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';

export default function DisclaimerPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <AlertTriangle className="w-8 h-8 text-yellow-600" />
        <h1 className="text-3xl font-bold">Declinare Responsabilitate</h1>
      </div>
      
      <p className="text-muted-foreground">Ultima actualizare: 23 Decembrie 2025</p>

      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Avertisment Important</AlertTitle>
        <AlertDescription>
          Informațiile de pe FinRomania NU constituie sfaturi de investiții. 
          Orice decizie financiară este responsabilitatea dumneavoastră.
        </AlertDescription>
      </Alert>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">1. Scop informativ</h2>
            <p>
              Toate informațiile, datele, știrile și analizele prezentate pe platforma FinRomania 
              sunt oferite exclusiv în scop informativ și educațional. Conținutul nu trebuie 
              interpretat ca:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Sfaturi de investiții sau financiare</li>
              <li>Recomandări de cumpărare sau vânzare de instrumente financiare</li>
              <li>Analize profesionale de investiții</li>
              <li>Consultanță fiscală sau juridică</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">2. Nu suntem consilieri financiari</h2>
            <p>
              FinRomania NU este o firmă de consultanță financiară, nu deține autorizații de la 
              ASF (Autoritatea de Supraveghere Financiară) și nu oferă servicii de consultanță 
              în investiții.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">3. Acuratețea datelor</h2>
            <p>
              Deși depunem eforturi pentru a prezenta informații corecte și actualizate, 
              NU garantăm:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Acuratețea, completitudinea sau actualitatea informațiilor</li>
              <li>Absența erorilor în datele prezentate</li>
              <li>Actualizarea în timp real a prețurilor sau cotațiilor</li>
              <li>Disponibilitatea neîntreruptă a serviciului</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">4. Surse externe</h2>
            <p>
              Știrile și informațiile sunt agregate din surse terțe (Ziarul Financiar, Profit.ro, 
              Bursa, etc.). Nu ne asumăm responsabilitatea pentru conținutul, acuratețea sau 
              opiniile exprimate în aceste surse externe.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">5. Riscuri asociate investițiilor</h2>
            <p className="font-semibold">
              Investițiile în instrumente financiare implică riscuri semnificative, inclusiv 
              pierderea parțială sau totală a capitalului investit.
            </p>
            <p>
              Performanțele trecute nu garantează rezultate viitoare. Trebuie să înțelegeți 
              pe deplin riscurile înainte de a investi și să nu investiți bani pe care nu vă 
              permiteți să îi pierdeți.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">6. Consultați un profesionist</h2>
            <p>
              Înainte de a lua orice decizie de investiții, vă recomandăm să consultați un 
              consilier financiar autorizat care poate evalua situația dumneavoastră financiară 
              individuală și obiectivele de investiții.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">7. Limitarea răspunderii</h2>
            <p>
              În limita maximă permisă de lege, FinRomania și operatorii săi nu sunt responsabili 
              pentru nicio pierdere sau daună (inclusiv, fără limitare, pierderi financiare, 
              pierderi de profit, pierderi de date) rezultate din utilizarea sau imposibilitatea 
              de a utiliza această platformă.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">8. Date BVB - Mențiune specială</h2>
            <p className="bg-yellow-100 dark:bg-yellow-900 p-4 rounded-lg">
              <strong>Atenție:</strong> Datele despre acțiunile de pe Bursa de Valori București (BVB) 
              prezentate pe această platformă sunt în prezent <strong>date simulate</strong> în scopuri 
              demonstrative. Nu le utilizați pentru decizii de investiții.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">9. Contact</h2>
            <p>
              Pentru clarificări: <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
