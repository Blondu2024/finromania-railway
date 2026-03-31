import React from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from './ui/button';

export default function LanguageSwitcher({ className = '' }) {
  const { i18n, t } = useTranslation();
  const currentLang = i18n.language?.startsWith('ro') ? 'ro' : 'en';

  const toggle = () => {
    i18n.changeLanguage(currentLang === 'ro' ? 'en' : 'ro');
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggle}
      className={`h-8 px-2 text-xs font-medium ${className}`}
      title={currentLang === 'ro' ? 'Switch to English' : t('common.switchToRomanian')}
    >
      {currentLang === 'ro' ? '🇬🇧 EN' : '🇷🇴 RO'}
    </Button>
  );
}
