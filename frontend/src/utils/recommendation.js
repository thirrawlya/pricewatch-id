import { Zap, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

// ── DESIGN SYSTEM ──
export const C = {
  bg: '#0B0F14',
  bgGradient: 'linear-gradient(135deg, #0B0F14 0%, #0D1520 50%, #111827 100%)',
  
  card: 'rgba(17, 24, 39, 0.8)',
  cardBorder: 'rgba(31, 41, 55, 0.3)',
  cardGlow: 'rgba(16, 185, 129, 0.05)',
  cardHover: 'rgba(31, 41, 55, 0.2)',
  
  accent: '#10B981',
  accentGradient: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
  accentGlow: 'rgba(16, 185, 129, 0.15)',
  accentDark: '#065F46',
  
  red: '#EF4444',
  redGradient: 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)',
  redGlow: 'rgba(239, 68, 68, 0.15)',
  
  yellow: '#F59E0B',
  yellowGradient: 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
  yellowGlow: 'rgba(245, 158, 11, 0.15)',
  
  text: '#F8FAFC',
  textSecondary: '#94A3B8',
  textMuted: '#64748B',
  textDim: '#475569',
  
  chartGradient: {
    from: 'rgba(16, 185, 129, 0.3)',
    to: 'rgba(16, 185, 129, 0)'
  },
  
  font: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
};

/**
 * Generates recommendation logic based on historical pricing stats.
 * 
 * @param {Object} analytics - Analytics data from API
 * @returns {Object} Recommendation metrics, labels, colors, and icons
 */
export function getRecommendation(analytics) {
  if (!analytics) return { status: 'loading', label: 'Loading...', icon: <Zap size={20} />, color: C.textMuted };
  
  const { change_pct, current, average, lowest, highest, history } = analytics;
  const dataPoints = history?.length || 0;
  
  const range = highest - lowest;
  const percentile = range > 0 ? ((current - lowest) / range) * 100 : 50;
  
  const confidence = dataPoints < 5 ? 'Low' : dataPoints < 15 ? 'Medium' : 'High';
  const confidenceColor = confidence === 'Low' ? C.yellow : confidence === 'Medium' ? '#F59E0B' : C.accent;
  
  let status = 'neutral';
  let reason = 'Harga dalam posisi normal';
  let savings = 0;
  
  if (change_pct <= -8) {
    status = 'buy';
    savings = average - current;
    reason = `Turun ${Math.abs(change_pct)}% dari rata-rata. Waktu tepat!`;
  } else if (change_pct <= -3) {
    status = 'buy';
    savings = average - current;
    reason = `${Math.abs(change_pct)}% di bawah rata-rata. Mulai menarik.`;
  } else if (change_pct >= 8) {
    status = 'wait';
    savings = current - average;
    reason = `Naik ${change_pct}% dari rata-rata. Lebih baik tunggu.`;
  } else if (change_pct >= 3) {
    status = 'wait';
    savings = current - average;
    reason = `${change_pct}% di atas rata-rata. Tunggu penurunan.`;
  } else if (percentile < 20) {
    status = 'buy';
    savings = average - current;
    reason = 'Mendekati titik terendah historis.';
  } else if (percentile > 80) {
    status = 'wait';
    savings = current - average;
    reason = 'Mendekati titik tertinggi historis.';
  } else {
    status = 'neutral';
    savings = 0;
    reason = 'Harga stabil dalam 30 hari terakhir.';
  }
  
  const config = {
    buy: { 
      label: 'BUY NOW', 
      icon: <CheckCircle size={24} />, 
      color: C.accent, 
      bg: 'rgba(16,185,129,0.1)',
      gradient: C.accentGradient,
      glow: C.accentGlow
    },
    wait: { 
      label: 'WAIT', 
      icon: <XCircle size={24} />, 
      color: C.red, 
      bg: 'rgba(239,68,68,0.1)',
      gradient: C.redGradient,
      glow: C.redGlow
    },
    neutral: { 
      label: 'NEUTRAL', 
      icon: <AlertCircle size={24} />, 
      color: C.yellow, 
      bg: 'rgba(245,158,11,0.1)',
      gradient: C.yellowGradient,
      glow: C.yellowGlow
    }
  };
  
  return { 
    ...config[status], 
    status, 
    reason, 
    percentile, 
    savings,
    confidence,
    confidenceColor,
    dataPoints,
    change_pct,
    current,
    average
  };
}
