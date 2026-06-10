/**
 * Analytics Chart Component
 * ──────────────────────────
 * Renders click data as an area chart using Recharts.
 */

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-sm)',
        boxShadow: 'var(--shadow-subtle)',
        padding: '0.75rem 1rem',
        fontSize: '0.8rem',
      }}>
        <p style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: '0.25rem', fontFamily: 'var(--font-mono)' }}>
          {label}
        </p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color, fontWeight: 500, fontFamily: 'var(--font-mono)' }}>
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
          <p>No click data available yet</p>
        </div>
      </div>
    );
  }

  // Reverse to show oldest first
  const chartData = [...data].reverse();

  return (
    <div className="chart-container" id="clicks-chart">
      <h3 className="chart-title">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--border-color)"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{ fill: 'var(--text-secondary)', fontSize: 10, fontWeight: 500, fontFamily: 'var(--font-mono)' }}
            tickLine={false}
            axisLine={{ stroke: 'var(--border-color)', strokeWidth: 1 }}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 10, fontWeight: 500, fontFamily: 'var(--font-mono)' }}
            tickLine={false}
            axisLine={{ stroke: 'var(--border-color)', strokeWidth: 1 }}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontFamily: 'var(--font-family)' }}
          />
          <Area
            type="monotone"
            dataKey="total"
            name="Total Clicks"
            stroke="var(--accent-primary)"
            strokeWidth={1.5}
            fill="rgba(17, 17, 17, 0.03)"
          />
          <Area
            type="monotone"
            dataKey="unique"
            name="Unique Clicks"
            stroke="var(--text-secondary)"
            strokeWidth={1.2}
            fill="rgba(120, 119, 116, 0.02)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
