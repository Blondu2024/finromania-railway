import React, { useState } from 'react';

const FALLBACK_COLORS = [
  'bg-blue-100 dark:bg-blue-900/30 text-blue-600',
  'bg-green-100 dark:bg-green-900/30 text-green-600',
  'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
  'bg-orange-100 dark:bg-orange-900/30 text-orange-600',
  'bg-pink-100 dark:bg-pink-900/30 text-pink-600',
  'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-600',
];

function getColorForSymbol(symbol) {
  let hash = 0;
  for (let i = 0; i < (symbol || '').length; i++) {
    hash = symbol.charCodeAt(i) + ((hash << 5) - hash);
  }
  return FALLBACK_COLORS[Math.abs(hash) % FALLBACK_COLORS.length];
}

export default function StockLogo({ symbol, logoUrl, size = 'md', className = '' }) {
  const [imgError, setImgError] = useState(false);

  const sizeClasses = {
    sm: 'w-5 h-5 text-[10px]',
    md: 'w-6 h-6 text-xs',
    lg: 'w-8 h-8 text-sm',
    xl: 'w-10 h-10 text-base',
  };

  const sizeClass = sizeClasses[size] || sizeClasses.md;

  if (logoUrl && !imgError) {
    return (
      <img
        src={logoUrl}
        alt={symbol}
        className={`${sizeClass} rounded-full object-contain bg-white shrink-0 ${className}`}
        onError={() => setImgError(true)}
      />
    );
  }

  const colorClass = getColorForSymbol(symbol);
  return (
    <div className={`${sizeClass} rounded-full flex items-center justify-center font-bold shrink-0 ${colorClass} ${className}`}>
      {(symbol || '?').charAt(0)}
    </div>
  );
}
