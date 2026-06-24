import { Sparkles, Bell, Gift, Eye } from 'lucide-react';
import { C } from '../utils/recommendation';

/**
 * Static placeholder section representing future features of the platform.
 * Displays "Next Actions" for the user like alerts, comparisons, and tracking.
 */
export default function NextActions() {
  return (
    <div style={{
      background: C.card,
      backdropFilter: 'blur(20px)',
      border: `1px solid ${C.cardBorder}`,
      borderRadius: 14,
      padding: '14px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: 10
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Sparkles size={18} color={C.accent} />
        <p style={{ color: C.text, fontSize: 13, fontWeight: 600, margin: 0 }}>
          🎯 What's Next?
        </p>
      </div>
      
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <button style={{
          padding: '6px 14px',
          background: 'transparent',
          border: `1px solid ${C.cardBorder}`,
          borderRadius: 8,
          color: C.textSecondary,
          fontSize: 11,
          cursor: 'pointer',
          fontFamily: C.font,
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          transition: 'all 0.15s'
        }}
        onMouseEnter={e => { e.currentTarget.style.background = C.cardHover; e.currentTarget.style.borderColor = C.textMuted }}
        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = C.cardBorder }}
        >
          <Bell size={12} />
          Set Alert
        </button>
        <button style={{
          padding: '6px 14px',
          background: 'transparent',
          border: `1px solid ${C.cardBorder}`,
          borderRadius: 8,
          color: C.textSecondary,
          fontSize: 11,
          cursor: 'pointer',
          fontFamily: C.font,
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          transition: 'all 0.15s'
        }}
        onMouseEnter={e => { e.currentTarget.style.background = C.cardHover; e.currentTarget.style.borderColor = C.textMuted }}
        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = C.cardBorder }}
        >
          <Gift size={12} />
          Compare
        </button>
        <button style={{
          padding: '6px 14px',
          background: 'transparent',
          border: `1px solid ${C.cardBorder}`,
          borderRadius: 8,
          color: C.textSecondary,
          fontSize: 11,
          cursor: 'pointer',
          fontFamily: C.font,
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          transition: 'all 0.15s'
        }}
        onMouseEnter={e => { e.currentTarget.style.background = C.cardHover; e.currentTarget.style.borderColor = C.textMuted }}
        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = C.cardBorder }}
        >
          <Eye size={12} />
          Track
        </button>
      </div>
    </div>
  );
}
