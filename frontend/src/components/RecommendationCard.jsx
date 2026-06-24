import { Bell, BarChart3 } from 'lucide-react';
import { C, getRecommendation } from '../utils/recommendation';
import { fmt } from '../utils/formatters';

/**
 * Buying recommendation panel. Displays a clear buy/wait recommendation badge,
 * actual saving amounts, confidence metrics, and price history status.
 * 
 * @param {Object} props
 * @param {Object} props.analytics - Raw API analytics payload
 * @param {number} props.days - Current time window in days
 */
export default function RecommendationCard({ analytics }) {
  if (!analytics) return null;
  
  const rec = getRecommendation(analytics);
  const { 
    status, 
    label, 
    icon, 
    color, 
    bg, 
    gradient, 
    glow, 
    reason, 
    savings, 
    confidence, 
    confidenceColor, 
    dataPoints, 
    change_pct, 
    current, 
    percentile 
  } = rec;
  
  return (
    <div style={{
      background: `linear-gradient(135deg, ${bg} 0%, rgba(17,24,39,0.8) 100%)`,
      backdropFilter: 'blur(20px)',
      borderRadius: 20,
      padding: '28px 32px',
      border: `1px solid ${color}44`,
      boxShadow: `0 8px 48px ${glow}`,
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute',
        top: -120,
        right: -120,
        width: 300,
        height: 300,
        background: `radial-gradient(circle, ${glow}, transparent 70%)`,
        borderRadius: '50%',
        pointerEvents: 'none'
      }} />
      
      <div style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 12 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${gradient}, ${color}44)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 4px 20px ${glow}`
          }}>
            {icon}
          </div>
          <div>
            <p style={{ color, fontSize: 22, fontWeight: 800, margin: 0, letterSpacing: '-0.02em' }}>
              {label}
            </p>
            <p style={{ color: C.textSecondary, fontSize: 13, margin: 0, fontWeight: 500 }}>
              {reason}
            </p>
          </div>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 12 }}>
            <div style={{ textAlign: 'center' }}>
              <p style={{ color: C.textMuted, fontSize: 8, margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Confidence</p>
              <p style={{ color: confidenceColor, fontSize: 13, fontWeight: 700, margin: 0 }}>{confidence}</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <p style={{ color: C.textMuted, fontSize: 8, margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Records</p>
              <p style={{ color: C.text, fontSize: 13, fontWeight: 700, margin: 0 }}>{dataPoints}</p>
            </div>
          </div>
        </div>
        
        <div style={{ marginBottom: 8 }}>
          <p style={{ 
            color: C.text, 
            fontSize: 44, 
            fontWeight: 800, 
            margin: 0,
            letterSpacing: '-0.03em'
          }}>
            {fmt(current)}
          </p>
          <p style={{ 
            color: change_pct < 0 ? C.accent : change_pct > 0 ? C.red : C.textSecondary,
            fontSize: 16,
            fontWeight: 600,
            margin: 0
          }}>
            {change_pct < 0 ? '↓' : change_pct > 0 ? '↑' : '→'} {Math.abs(change_pct)}% 
            {change_pct < 0 ? ' lebih murah' : change_pct > 0 ? ' lebih mahal' : ' stabil'}
          </p>
        </div>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 10,
          marginTop: 16
        }}>
          <div style={{
            background: C.bg,
            borderRadius: 10,
            padding: '12px 16px',
            border: `1px solid ${C.cardBorder}`
          }}>
            <p style={{ color: C.textMuted, fontSize: 9, margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Position</p>
            <p style={{ color: C.text, fontSize: 16, fontWeight: 700, margin: 0 }}>
              {Math.round(percentile)}%
            </p>
            <p style={{ color: C.textMuted, fontSize: 9, margin: 0 }}>
              {percentile < 30 ? '⬇️ Below average' : 
               percentile > 70 ? '⬆️ Above average' : 
               '📊 At average'}
            </p>
          </div>
          <div style={{
            background: C.bg,
            borderRadius: 10,
            padding: '12px 16px',
            border: `1px solid ${C.cardBorder}`
          }}>
            <p style={{ color: C.textMuted, fontSize: 9, margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Range</p>
            <p style={{ color: C.text, fontSize: 16, fontWeight: 700, margin: 0 }}>
              {fmt(analytics.highest - analytics.lowest)}
            </p>
            <p style={{ color: C.textMuted, fontSize: 9, margin: 0 }}>
              {analytics.highest - analytics.lowest > 0 ? '📊 Volatile' : '📊 Stable'}
            </p>
          </div>
        </div>
        
        {savings > 0 && (
          <div style={{
            background: `linear-gradient(135deg, ${color}15, transparent)`,
            borderRadius: 10,
            padding: '10px 16px',
            marginTop: 12,
            border: `1px solid ${color}22`
          }}>
            <p style={{ color, fontSize: 13, fontWeight: 600, margin: 0 }}>
              {status === 'buy' ? '💰 Hemat' : '💸 Potensi rugi'} <strong>{fmt(savings)}</strong>
            </p>
          </div>
        )}
        
        <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
          <button style={{
            padding: '8px 20px',
            background: gradient,
            border: 'none',
            borderRadius: 10,
            color: '#fff',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: 12,
            fontFamily: C.font,
            boxShadow: `0 4px 16px ${glow}`,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            transition: 'transform 0.15s'
          }}
          onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.02)'}
          onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
          >
            <Bell size={14} />
            {status === 'buy' ? 'Beli Sekarang' : status === 'wait' ? 'Pantau Harga' : 'Lihat Detail'}
          </button>
          <button style={{
            padding: '8px 16px',
            background: 'transparent',
            border: `1px solid ${C.cardBorder}`,
            borderRadius: 10,
            color: C.textSecondary,
            fontWeight: 500,
            cursor: 'pointer',
            fontSize: 12,
            fontFamily: C.font,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            transition: 'all 0.15s'
          }}
          onMouseEnter={e => { e.currentTarget.style.background = C.cardHover; e.currentTarget.style.borderColor = C.textMuted }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = C.cardBorder }}
          >
            <BarChart3 size={14} />
            Full Analysis
          </button>
        </div>
      </div>
    </div>
  );
}
