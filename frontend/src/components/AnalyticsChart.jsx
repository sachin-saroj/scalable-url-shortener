/**
 * Analytics Chart Component — LinkForge V3
 * ──────────────────────────────────────────
 * Professional area chart with electric blue / soft purple palette.
 * Subtle grids, thin lines, minimal labels.
 */

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-sm)',
        boxShadow: 'var(--shadow-medium)',
        padding: '0.6rem 0.85rem',
        fontSize: '0.75rem',
      }}>
        <p style={{
          color: 'var(--text-tertiary)',
          fontWeight: 600,
          marginBottom: '0.35rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.65rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}>
          {label}
        </p>
        {payload.map((entry, i) => (
          <p key={i} style={{
            color: entry.color,
            fontWeight: 600,
            fontFamily: 'var(--font-mono)',
            fontSize: '0.8rem',
          }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function AnalyticsChart({ data, title }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-container">
        <h3 className="chart-title">{title}</h3>
        <div className="empty-state" style={{ padding: '2rem' }}>
          <p style={{ fontSize: '0.85rem' }}>No click data available yet</p>
        </div>
      </div>
    );
  }

  // Reverse to show oldest first
  const chartData = [...data].reverse();

  return (
    <div className="chart-container" id="clicks-chart">
      <h3 className="chart-title">{title}</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
          <defs>
            <linearGradient id="gradientBlue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0066FF" stopOpacity={0.08} />
              <stop offset="100%" stopColor="#0066FF" stopOpacity={0.00} />
            </linearGradient>
            <linearGradient id="gradientPurple" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.05} />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0.00} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--border-color)"
            strokeOpacity={0.35}
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{
              fill: 'var(--text-tertiary)',
              fontSize: 8,
              fontWeight: 500,
              fontFamily: 'var(--font-mono)',
            }}
            tickLine={false}
            axisLine={false}
            dy={8}
          />
          <YAxis
            tick={{
              fill: 'var(--text-tertiary)',
              fontSize: 8,
              fontWeight: 500,
              fontFamily: 'var(--font-mono)',
            }}
            tickLine={false}
            axisLine={false}
            width={30}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="total"
            name="Total Volume"
            stroke="#0066FF"
            strokeWidth={1.5}
            fill="url(#gradientBlue)"
            dot={false}
            activeDot={{ r: 4, fill: '#0066FF', stroke: '#fff', strokeWidth: 2 }}
          />
          <Area
            type="monotone"
            dataKey="unique"
            name="Unique Visitors"
            stroke="#8B5CF6"
            strokeWidth={1.2}
            fill="url(#gradientPurple)"
            dot={false}
            activeDot={{ r: 3, fill: '#8B5CF6', stroke: '#fff', strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
