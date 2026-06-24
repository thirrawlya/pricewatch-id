import { BarChart3, Database } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { C } from '../utils/recommendation';

/**
 * Historical price history area chart using Recharts.
 * Supports switching time intervals (30d, 60d, 90d).
 * 
 * @param {Object} props
 * @param {Array} props.data - Formatted chart data [{ date, price }]
 * @param {number} props.average - Average price reference line
 * @param {number} props.days - Current selected active interval
 * @param {Function} props.onChangeDays - Callback when changing interval
 * @param {Object} props.analytics - Raw analytics payload
 */
export default function PriceChart({ data, average, days, onChangeDays, analytics }) {
  return (
    <div style={{
      background: C.card,
      backdropFilter: 'blur(20px)',
      border: `1px solid ${C.cardBorder}`,
      borderRadius: 16,
      padding: "20px 24px"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <BarChart3 size={16} color={C.textMuted} />
          <p style={{ color: C.textMuted, fontSize: 10, margin: 0, fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase" }}>
            Price Trend — {days} days
          </p>
          <span style={{ 
            color: C.textMuted, 
            fontSize: 9, 
            background: C.cardBorder,
            padding: '1px 8px',
            borderRadius: 4
          }}>
            {data.length} records
          </span>
        </div>
        <div style={{ display: "flex", gap: 3 }}>
          {[30, 60, 90].map(d => (
            <button
              key={d}
              onClick={() => onChangeDays(d)}
              style={{
                padding: "3px 12px",
                fontSize: 10,
                fontWeight: days === d ? 600 : 400,
                borderRadius: 6,
                border: `1px solid ${days === d ? C.accent : C.cardBorder}`,
                cursor: "pointer",
                fontFamily: C.font,
                background: days === d ? `${C.accent}22` : "transparent",
                color: days === d ? C.text : C.textMuted,
                transition: 'all 0.2s'
              }}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {data.length < 2 ? (
        <div style={{ 
          height: 200, 
          display: "flex", 
          alignItems: "center", 
          justifyContent: "center", 
          flexDirection: 'column', 
          background: C.bg, 
          borderRadius: 10,
          padding: '20px',
          gap: 6
        }}>
        <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}>
          {[
            { width: 24, height: 18 },
            { width: 36, height: 42 },
            { width: 28, height: 25 },
            { width: 40, height: 48 },
            { width: 22, height: 20 },
            { width: 34, height: 38 },
          ].map((bar, i) => (
            <div
              key={i}
              style={{
                width: bar.width,
                height: bar.height,
                background: `${C.accent}22`,
                borderRadius: 4,
                animation: 'pulse 1.5s ease-in-out infinite',
                animationDelay: `${i * 0.2}s`
              }}
            />
          ))}
        </div>
          <Database size={24} color={C.textMuted} opacity={0.3} />
          <p style={{ color: C.textMuted, fontSize: 12, margin: 0, fontWeight: 500 }}>
            Menunggu lebih banyak data...
          </p>
          <p style={{ color: C.textDim, fontSize: 10, margin: 0 }}>
            {analytics?.history?.length || 0} data points tersedia
          </p>
          <p style={{ color: C.textDim, fontSize: 9, margin: 0 }}>
            🕐 Scraper berjalan setiap hari
          </p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={data} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="40%" stopColor="#10B981" stopOpacity={0.1} />
                <stop offset="100%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="date" 
              tick={{ fill: '#64748B', fontSize: 9, fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
              padding={{ left: 10, right: 10 }}
            />
            <YAxis
              tickFormatter={v => `${(v / 1000000).toFixed(1)}jt`}
              tick={{ fill: '#64748B', fontSize: 9, fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
              width={45}
            />
            <Tooltip 
              contentStyle={{
                background: 'rgba(17, 24, 39, 0.95)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(31, 41, 55, 0.5)',
                borderRadius: 10,
                padding: '10px 14px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
              }}
              labelStyle={{ color: '#94A3B8', fontSize: 10, fontWeight: 500 }}
              itemStyle={{ color: '#F8FAFC', fontSize: 13, fontWeight: 700 }}
            />
            <ReferenceLine 
              y={average} 
              stroke="#64748B" 
              strokeDasharray="6 4" 
              strokeWidth={1.5}
              label={{ 
                value: 'avg', 
                fill: '#64748B', 
                fontSize: 8, 
                fontWeight: 600,
                position: 'right'
              }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#10B981"
              strokeWidth={2.5}
              fill="url(#chartGradient)"
              dot={{ r: 3, fill: '#10B981', strokeWidth: 0 }}
              activeDot={{ r: 5, fill: '#10B981', strokeWidth: 2, stroke: '#F8FAFC' }}
              animationDuration={1500}
              animationEasing="ease-in-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
