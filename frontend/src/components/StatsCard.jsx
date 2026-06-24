import { C } from '../utils/recommendation';

/**
 * A reusable statistic card that highlights key metrics like current price,
 * lowest historical price, highest historical price, and averages.
 * 
 * @param {Object} props
 * @param {string} props.label - Card header label
 * @param {string} props.value - Formatted value to display
 * @param {string} props.color - Theme color for border highlights & bar
 * @param {React.ReactNode} props.icon - Lucide icon component
 * @param {string} [props.subtext] - Small description text
 * @param {number} [props.barValue] - Current progress bar value
 * @param {number} [props.barMax] - Maximum progress bar limit
 */
export default function StatsCard({ label, value, color, icon, subtext, barValue, barMax }) {
  return (
    <div style={{
      background: C.card,
      backdropFilter: 'blur(20px)',
      border: `1px solid ${C.cardBorder}`,
      borderRadius: 12,
      padding: "14px 18px",
      transition: 'border-color 0.2s, transform 0.15s'
    }}
    onMouseEnter={e => { e.currentTarget.style.borderColor = `${color}44`; e.currentTarget.style.transform = 'translateY(-2px)' }}
    onMouseLeave={e => { e.currentTarget.style.borderColor = C.cardBorder; e.currentTarget.style.transform = 'translateY(0)' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <p style={{ color: C.textMuted, fontSize: 9, margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            {label}
          </p>
          <p style={{ color, fontSize: 18, fontWeight: 700, margin: '4px 0 2px', letterSpacing: '-0.02em' }}>
            {value}
          </p>
          {subtext && (
            <p style={{ color: C.textMuted, fontSize: 9, margin: 0 }}>{subtext}</p>
          )}
          {barValue !== undefined && (
            <div style={{
              width: '100%',
              height: 3,
              background: C.cardBorder,
              borderRadius: 2,
              marginTop: 6,
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${Math.min((barValue / barMax) * 100, 100)}%`,
                height: '100%',
                background: color,
                borderRadius: 2
              }} />
            </div>
          )}
        </div>
        <div style={{
          width: 32,
          height: 32,
          borderRadius: '50%',
          background: `${color}15`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: color,
          flexShrink: 0
        }}>
          {icon}
        </div>
      </div>
    </div>
  );
}
