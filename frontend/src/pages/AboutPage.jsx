import React from 'react';
import { Heart, Target, Users, Zap, Award, TrendingUp, BookOpen, Globe } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';

export default function AboutPage() {
  return (
    <>
      <SEO 
        title="Despre Noi - Misiunea FinRomania"
        description="Descoperă misiunea FinRomania: să democratizăm educația financiară în România prin instrumente gratuite, date reale BVB, și lecții interactive de trading."
        url="https://finromania-3.preview.emergentagent.com/about"
      />
      
      <div className="max-w-5xl mx-auto px-4 py-12 space-y-16">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <div className="inline-block p-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full">
            <Heart className="w-16 h-16 text-white" />
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold">
            Misiunea Noastră
          </h1>
          <p className="text-xl sm:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Să democratizăm educația financiară în România - să facă accesibilă învățarea trading-ului și investițiilor pentru toți românii, 100% gratuit, în limba română.
          </p>
        </div>

        {/* Story Section */}
        <Card className="border-2 border-blue-200">
          <CardContent className="p-8 md:p-12">
            <div className="prose prose-lg max-w-none">
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
                <Target className="w-8 h-8 text-blue-600" />
                De Ce Am Creat FinRomania?
              </h2>
              
              <p className="text-lg leading-relaxed text-muted-foreground">
                În România, educația financiară este aproape inexistentă. Milioane de români vor să învețe despre investiții, bursa de valori, și trading - dar resurse de calitate în limba română sunt rare sau foarte scumpe.
              </p>
              
              <p className="text-lg leading-relaxed text-muted-foreground">
                <strong>FinRomania</strong> a fost creat pentru a schimba asta. Credem că fiecare român merită acces la educație financiară de calitate, indiferent de venit sau background. De aceea am construit prima platformă educațională de trading complet <strong>gratuită</strong> din România.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Values */}
        <div>
          <h2 className="text-3xl font-bold text-center mb-8">Valorile Noastre</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
                  <Globe className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">100% Gratuit</h3>
                <p className="text-sm text-muted-foreground">
                  Educația nu ar trebui să coste. Totul e gratuit, pentru totdeauna.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-green-100 rounded-full mb-4">
                  <BookOpen className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">Calitate</h3>
                <p className="text-sm text-muted-foreground">
                  Date reale, lecții profesionale, AI avansat - nu compromitem niciodată.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-purple-100 rounded-full mb-4">
                  <Zap className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">Inovație</h3>
                <p className="text-sm text-muted-foreground">
                  Primă platformă cu AI Advisor și lecții interactive în română.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-orange-100 rounded-full mb-4">
                  <Users className="w-8 h-8 text-orange-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">Comunitate</h3>
                <p className="text-sm text-muted-foreground">
                  Construim o comunitate de investitori educați în România.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Features Highlight */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-center mb-8">Ce Oferim</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">Date Reale BVB</h3>
                <p className="text-sm text-muted-foreground">
                  Prețuri live de pe Bursa de Valori București, actualizate la fiecare 5 minute. Nu folosim date simulate - vezi piața reală!
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-purple-600 text-white rounded-lg flex items-center justify-center">
                  <BookOpen className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">Trading School Interactive</h3>
                <p className="text-sm text-muted-foreground">
                  17 lecții complete cu quizzes și scenarii practice. De la începător la avansat, înveți prin practică ghidată.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-600 text-white rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">AI Advisor Personal</h3>
                <p className="text-sm text-muted-foreground">
                  Asistent AI care răspunde la întrebările tale despre trading, investiții, și analiză financiară - disponibil 24/7.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-orange-600 text-white rounded-lg flex items-center justify-center">
                  <Award className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">Instrumente Profesionale</h3>
                <p className="text-sm text-muted-foreground">
                  Glosar 99 termeni, convertor valutar live, știri automate, evaluare risc - tot ce ai nevoie pentru a începe.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-4xl font-bold text-blue-600 mb-2">17</div>
            <div className="text-sm text-muted-foreground">Lecții Interactive</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-green-600 mb-2">99</div>
            <div className="text-sm text-muted-foreground">Termeni în Glosar</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-purple-600 mb-2">20+</div>
            <div className="text-sm text-muted-foreground">Acțiuni BVB Live</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-orange-600 mb-2">100%</div>
            <div className="text-sm text-muted-foreground">Gratuit</div>
          </div>
        </div>

        {/* CTA */}
        <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0">
          <CardContent className="p-8 md:p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">Începe Să Înveți Astăzi</h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Alatură-te miilor de români care învață trading pe FinRomania. Gratuit, în limba română, cu date reale.
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Link to="/trading-school">
                <button className="bg-white text-blue-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-blue-50 transition-colors">
                  🎓 Începe Trading School
                </button>
              </Link>
              <Link to="/stocks">
                <button className="bg-white/20 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-white/30 transition-colors border-2 border-white/40">
                  📈 Explorează BVB
                </button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Team / Contact */}
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">Ai Întrebări?</h2>
          <p className="text-muted-foreground">
            Suntem aici să te ajutăm! Contactează-ne sau întreabă AI Advisor-ul.
          </p>
          <div className="flex gap-3 justify-center">
            <Link to="/faq">
              <button className="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
                ❓ FAQ
              </button>
            </Link>
            <Link to="/advisor">
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                🤖 Întreabă AI
              </button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}