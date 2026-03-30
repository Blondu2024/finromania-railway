import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Calendar, DollarSign, TrendingUp, Clock, Crown, CalendarDays,
  Filter, ChevronRight, Banknote, Building2, FileText, Download, Lock
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Skeleton } from '../components/ui/skeleton';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Dividend Card Component
const DividendCard = ({ dividend, index, t }) => {
  const isPaid = dividend.status === 'paid';
  const isEstimated = dividend.status === 'estimated';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className={`overflow-hidden hover:shadow-lg transition-all ${
        isPaid ? 'border-green-200 bg-green-50/30' :
        isEstimated ? 'border-blue-200 bg-blue-50/30' : ''
      }`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                isPaid ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'
              }`}>
                <DollarSign className="w-6 h-6" />
              </div>
              <div>
                <Link to={`/stocks/bvb/${dividend.symbol}`}>
                  <p className="font-bold text-lg hover:text-blue-600">{dividend.symbol}</p>
                </Link>
                <p className="text-sm text-muted-foreground">{dividend.name}</p>
              </div>
            </div>

            <div className="text-right">
              <p className="text-2xl font-bold text-green-600">
                {dividend.dividend_per_share} RON
              </p>
              <Badge variant={isPaid ? 'default' : 'secondary'}>
                {isPaid ? t('dividends.paid') : t('dividends.future')}
              </Badge>
              {dividend.data_source?.includes('BVB') && (
                <span className="text-[10px] text-green-600 block mt-0.5">BVB.ro</span>
              )}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t text-sm">
            <div>
              <p className="text-muted-foreground">{t('dividends.exDividend')}</p>
              <p className="font-semibold">{dividend.ex_date}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t('dividends.paymentDate')}</p>
              <p className="font-semibold">{dividend.payment_date}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t('dividends.yield')}</p>
              <p className="font-semibold text-green-600">{dividend.dividend_yield}%</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Event Card Component
const EventCard = ({ event, index }) => {
  const getEventIcon = (type) => {
    switch(type) {
      case 'aga': return <Building2 className="w-5 h-5" />;
      case 'report': return <FileText className="w-5 h-5" />;
      case 'ipo': return <TrendingUp className="w-5 h-5" />;
      default: return <Calendar className="w-5 h-5" />;
    }
  };

  const getEventColor = (type) => {
    switch(type) {
      case 'aga': return 'bg-blue-100 text-blue-600';
      case 'report': return 'bg-blue-100 text-blue-600';
      case 'ipo': return 'bg-green-100 text-green-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className="hover:shadow-md transition-all">
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getEventColor(event.type)}`}>
              {getEventIcon(event.type)}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Link to={`/stocks/bvb/${event.symbol}`}>
                  <Badge variant="outline" className="font-bold">{event.symbol}</Badge>
                </Link>
                <span className="text-sm text-muted-foreground">{event.name}</span>
              </div>
              <h4 className="font-semibold mt-1">{event.title}</h4>
              <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
            </div>
            <div className="text-right">
              <p className="font-bold">{event.date}</p>
              {event.time && <p className="text-sm text-muted-foreground">{event.time}</p>}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Dividend Kings Section
const DividendKings = ({ kings, t }) => (
  <Card className="bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-200">
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Crown className="w-5 h-5 text-yellow-600" />
        {t('dividends.topYield')}
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-3">
        {kings.map((king, idx) => (
          <motion.div
            key={king.symbol}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm"
          >
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                idx === 0 ? 'bg-yellow-500' : idx === 1 ? 'bg-gray-400' : idx === 2 ? 'bg-amber-600' : 'bg-slate-300'
              }`}>
                {idx + 1}
              </div>
              <div>
                <Link to={`/stocks/bvb/${king.symbol}`}>
                  <p className="font-bold hover:text-blue-600">{king.symbol}</p>
                </Link>
                <p className="text-xs text-muted-foreground">{king.name}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xl font-bold text-green-600">{king.dividend_yield}%</p>
              <p className="text-xs text-muted-foreground">{king.dividend_per_share} {t('dividends.perShare')}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </CardContent>
  </Card>
);

export default function DividendCalendarPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [dividends, setDividends] = useState([]);
  const [events, setEvents] = useState([]);
  const [kings, setKings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [exporting, setExporting] = useState(false);

  const isPro = user?.subscription_level === 'pro' || user?.subscription_level === 'premium';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [divRes, eventsRes, kingsRes] = await Promise.all([
          fetch(`${API_URL}/api/calendar/dividends?upcoming_only=false&include_past=true`),
          fetch(`${API_URL}/api/calendar/events`),
          fetch(`${API_URL}/api/calendar/dividend-kings`)
        ]);

        if (divRes.ok) {
          const data = await divRes.json();
          setDividends(data.dividends || []);
        }
        if (eventsRes.ok) {
          const data = await eventsRes.json();
          setEvents(data.events || []);
        }
        if (kingsRes.ok) {
          const data = await kingsRes.json();
          setKings(data.dividend_kings || []);
        }
      } catch (err) {
        console.error('Error fetching calendar data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const upcomingDividends = dividends.filter(d => d.status !== 'paid');
  const paidDividends = dividends.filter(d => d.status === 'paid');

  const handleExport = async (type) => {
    if (!isPro) {
      window.location.href = '/pricing';
      return;
    }

    setExporting(true);
    try {
      const endpoint = type === 'all' ? 'all' : type === 'dividends' ? 'dividends' : 'events';
      const response = await fetch(`${API_URL}/api/calendar/export/${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calendar_bvb_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
      } else {
        alert(t('dividends.exportError'));
      }
    } catch (err) {
      console.error('Export error:', err);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid md:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-48" />)}
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={t('dividends.seoCalendarTitle')}
        description={t('dividends.seoCalendarDesc')}
      />

      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-4"
        >
          <h1 className="text-2xl sm:text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-2">
            {t('dividends.calendarTitle')}
          </h1>
          <p className="text-muted-foreground mb-1">{t('dividends.calendarSubtitle')}</p>
          <p className="text-xs text-green-600 font-medium mb-4">
            {t('dividends.source')}: BVB.ro ·{' '}
            <a href="https://bvb.ro/FinancialInstruments/CorporateActions/InfoDividend" target="_blank" rel="noopener noreferrer" className="underline hover:text-green-800">
              {t('dividends.verifyOnBVB')} ↗
            </a>
          </p>

          {/* Export Button */}
          <div className="flex justify-center gap-2">
            {isPro ? (
              <Button
                onClick={() => handleExport('all')}
                disabled={exporting}
                className="bg-gradient-to-r from-amber-500 to-orange-500"
              >
                <Download className="w-4 h-4 mr-2" />
                {exporting ? 'Export...' : 'Export Excel (CSV)'}
              </Button>
            ) : (
              <Button
                onClick={() => window.location.href = '/pricing'}
                variant="outline"
                className="border-amber-400"
              >
                <Lock className="w-4 h-4 mr-2" />
                Export Excel
                <Badge className="ml-2 bg-amber-500">PRO</Badge>
              </Button>
            )}
          </div>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <CardContent className="p-4">
              <Banknote className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-sm text-green-100">{t('dividends.totalDividends')}</p>
              <p className="text-2xl font-bold">{dividends.length}</p>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <CardContent className="p-4">
              <Clock className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-sm text-blue-100">{t('dividends.upcoming')}</p>
              <p className="text-2xl font-bold">{upcomingDividends.length}</p>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <CardContent className="p-4">
              <CalendarDays className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-sm text-blue-100">{t('dividends.events')}</p>
              <p className="text-2xl font-bold">{events.length}</p>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white">
            <CardContent className="p-4">
              <Crown className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-sm text-amber-100">{t('dividends.topYield')}</p>
              <p className="text-2xl font-bold">{kings[0]?.dividend_yield || 0}%</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-[1fr,350px] gap-6">
          {/* Left - Dividends & Events */}
          <div className="space-y-6">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="all">{t('dividends.allDividends')}</TabsTrigger>
                <TabsTrigger value="upcoming">{t('dividends.upcomingTab')}</TabsTrigger>
                <TabsTrigger value="events">{t('dividends.eventsTab')}</TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4 mt-4">
                <h3 className="font-bold text-lg">{t('dividends.allDividends')}</h3>
                {dividends.map((div, idx) => (
                  <DividendCard key={`${div.symbol}-${div.ex_date}`} dividend={div} index={idx} t={t} />
                ))}
              </TabsContent>

              <TabsContent value="upcoming" className="space-y-4 mt-4">
                <h3 className="font-bold text-lg">{t('dividends.upcomingEstimates')}</h3>
                {upcomingDividends.length === 0 ? (
                  <Card>
                    <CardContent className="p-8 text-center text-muted-foreground">
                      {t('dividends.noUpcoming')}
                    </CardContent>
                  </Card>
                ) : (
                  upcomingDividends.map((div, idx) => (
                    <DividendCard key={`${div.symbol}-${div.ex_date}`} dividend={div} index={idx} t={t} />
                  ))
                )}
              </TabsContent>

              <TabsContent value="events" className="space-y-4 mt-4">
                <h3 className="font-bold text-lg">{t('dividends.corporateEvents')}</h3>
                {events.map((event, idx) => (
                  <EventCard key={`${event.symbol}-${event.date}`} event={event} index={idx} />
                ))}
              </TabsContent>
            </Tabs>
          </div>

          {/* Right Sidebar - Dividend Kings */}
          <div>
            <DividendKings kings={kings} t={t} />

            {/* Info Card - Glosar */}
            <Card className="mt-6">
              <CardContent className="p-4 text-sm text-muted-foreground">
                <h4 className="font-semibold text-foreground mb-2">{t('dividends.glossaryTitle')}</h4>
                <ul className="space-y-2">
                  <li><strong>{t('dividends.exDividend')}:</strong> {t('dividends.exDividendGlossary')}</li>
                  <li><strong>{t('dividends.recordDate')}:</strong> {t('dividends.recordDateGlossary')}</li>
                  <li><strong>{t('dividends.paymentDate')}:</strong> {t('dividends.paymentDateGlossary')}</li>
                  <li><strong>{t('dividends.yield')}:</strong> {t('dividends.yieldGlossary')}</li>
                </ul>
                <div className="mt-3 p-2 bg-muted rounded text-xs font-mono">
                  {t('dividends.yieldFormula')}
                </div>
              </CardContent>
            </Card>

            {/* Surse & Fiscalitate */}
            <Card className="mt-4">
              <CardContent className="p-4 text-sm text-muted-foreground">
                <h4 className="font-semibold text-foreground mb-2">📋 {t('dividends.sourcesAndTax')}</h4>
                <ul className="space-y-2">
                  <li><strong>{t('dividends.dataSourceLabel')}</strong> {t('dividends.dataSourceText')}{' '}
                    <a href="https://bvb.ro/FinancialInstruments/CorporateActions/InfoDividend" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{t('dividends.dataSourceBVB')} ↗</a>
                  </li>
                  <li><strong>{t('dividends.taxDividend')}</strong></li>
                  <li><strong>CASS:</strong> {t('dividends.cassApplies')}</li>
                  <li>{t('dividends.estimatesNote')}</li>
                </ul>
                <p className="mt-3 text-xs italic">{t('dividends.legalBasisCalendar')}</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
