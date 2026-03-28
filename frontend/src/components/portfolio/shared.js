// Shared constants and formatters for Portfolio components

export const API_URL = process.env.REACT_APP_BACKEND_URL;

export const SECTOR_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#f97316', '#84cc16', '#ec4899', '#6b7280',
];

export const fmt = (v, dec = 2) =>
  v != null
    ? Number(v).toLocaleString('ro-RO', { minimumFractionDigits: dec, maximumFractionDigits: dec })
    : '—';

export const fmtRON = (v) => (v != null ? `${fmt(v)} RON` : '—');
