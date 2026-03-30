import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Mail, MapPin, Clock, Send, MessageSquare } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Alert, AlertDescription } from '../components/ui/alert';

export default function ContactPage() {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // În producție, aici ar fi un API call
    console.log('Form submitted:', formData);
    setSubmitted(true);
    setFormData({ name: '', email: '', subject: '', message: '' });
  };

  return (
    <>
    <SEO title={`${t('contact.title')} | FinRomania`} description={t('contact.intro')} />
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> {t('common.back')}
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <MessageSquare className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">{t('contact.title')}</h1>
      </div>

      <p className="text-muted-foreground">
        {t('contact.intro')}
      </p>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Contact Info */}
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium">{t('contact.email')}</p>
                <p className="text-sm text-muted-foreground">contact@finromania.ro</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium">{t('contact.location')}</p>
                <p className="text-sm text-muted-foreground">București, România</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Clock className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium">{t('contact.responseTime')}</p>
                <p className="text-sm text-muted-foreground">{t('contact.responseValue')}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contact Form */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>{t('contact.sendMessage')}</CardTitle>
          </CardHeader>
          <CardContent>
            {submitted && (
              <Alert className="mb-4 bg-green-100 dark:bg-green-900 border-green-500">
                <AlertDescription>
                  ✅ {t('contact.success')}
                </AlertDescription>
              </Alert>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">{t('contact.yourName')}</label>
                  <Input 
                    placeholder="Numele tău" 
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">{t('contact.email')}</label>
                  <Input 
                    type="email" 
                    placeholder="email@example.com" 
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">{t('contact.subject')}</label>
                <Input 
                  placeholder="Subiectul mesajului" 
                  value={formData.subject}
                  onChange={(e) => setFormData({...formData, subject: e.target.value})}
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">{t('contact.message')}</label>
                <Textarea 
                  placeholder="Scrie mesajul tău aici..." 
                  rows={5}
                  value={formData.message}
                  onChange={(e) => setFormData({...formData, message: e.target.value})}
                  required
                />
              </div>
              <Button type="submit" className="w-full md:w-auto">
                <Send className="w-4 h-4 mr-2" /> {t('contact.send')}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* FAQ Section */}
      <Card>
        <CardHeader>
          <CardTitle>Întrebări frecvente</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="font-medium">De unde provin datele despre acțiuni?</p>
            <p className="text-sm text-muted-foreground">
              Datele despre indicii globali provin de la Yahoo Finance. Datele BVB sunt momentan 
              simulate în scopuri demonstrative.
            </p>
          </div>
          <div>
            <p className="font-medium">De unde provin știrile?</p>
            <p className="text-sm text-muted-foreground">
              Știrile sunt agregate din surse românești de încredere: Ziarul Financiar, Profit.ro, 
              Bursa, Wall-Street.ro și alte publicații financiare.
            </p>
          </div>
          <div>
            <p className="font-medium">Cât de des se actualizează datele?</p>
            <p className="text-sm text-muted-foreground">
              Cursurile valutare BNR se actualizează zilnic. Indicii globali și știrile se 
              actualizează la fiecare 15 minute.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
    </>
  );
}
