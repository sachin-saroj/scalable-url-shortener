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
        border: '2px solid #000000',
        borderRadius: 'var(--radius-sm)',
        boxShadow: '2px 2px 0px 0px #000000',
        padding: '0.75rem 1rem',
        fontSize: '0.8rem',
      }}>
        <p style={{ color: 'var(--text-primary)', fontWeight: 700, marginBottom: '0.25rem', fontFamily: 'var(--font-mono)' }}>
          {label}
        </p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color, fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
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
          <defs>
            <linearGradient id="gradientTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#000000" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#000000" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradientUnique" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#71717a" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#71717a" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#e4e4e7"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontWeight: 700 }}
            tickLine={false}
            axisLine={{ stroke: '#000000', strokeWidth: 2 }}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontWeight: 700 }}
            tickLine={false}
            axisLine={{ stroke: '#000000', strokeWidth: 2 }}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase' }}
          />
          <Area
            type="monotone"
            dataKey="total"
            name="Total Clicks"
            stroke="#000000"
            strokeWidth={3}
            fill="url(#gradientTotal)"
          />
          <Area
            type="monotone"
            dataKey="unique"
            name="Unique Clicks"
            stroke="#71717a"
            strokeWidth={2}
            fill="url(#gradientUnique)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
