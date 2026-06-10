/**
 * Analytics Page
 * ───────────────
 * Detailed click analytics for a specific short URL.
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../utils/api';
import AnalyticsChart from '../components/AnalyticsChart';

export default function Analytics() {
  const { shortCode } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAnalytics();
  }, [shortCode]);

  async function loadAnalytics() {
    setLoading(true);
    setError('');
    try {
      const res = await api.getAnalytics(shortCode);
      if (res.ok) {
        setData(res.data);
      } else {
        setError(res.data.detail || 'Failed to load analytics');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="skeleton" style={{ height: '40px', width: '300px', marginBottom: '2rem' }} />
        <div className="stats-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: '100px' }} />
          ))}
        </div>
        <div className="skeleton" style={{ height: '350px', marginTop: '1.5rem' }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="empty-state">
          <div className="empty-state-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
          </div>
          <h3 className="empty-state-title">{error}</h3>
          <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: '1rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="page-container" id="analytics-page">
      {/* Header */}
      <div className="page-header">
        <Link to="/dashboard" style={{
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          marginBottom: '0.75rem',
          textDecoration: 'none'
        }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
          Back to Dashboard
        </Link>
        <h1 className="page-title">Analytics: /{shortCode}</h1>
        <p className="page-subtitle" style={{
          maxWidth: '600px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {data.original_url}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid" id="analytics-stats">
        <div className="stat-card">
          <div className="stat-label">Total Clicks</div>
          <div className="stat-value">{data.total_clicks.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Unique Visitors</div>
          <div className="stat-value">{data.unique_clicks.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Last 24 Hours</div>
          <div className="stat-value">{data.clicks_24h.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Last 7 Days</div>
          <div className="stat-value">{data.clicks_7d.toLocaleString()}</div>
        </div>
      </div>

      {/* Click Chart */}
      <AnalyticsChart
        data={data.clicks_by_day}
        title="Clicks Over Time (Last 30 Days)"
      />

      {/* Bottom Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1.5rem',
      }}>
        {/* Top Countries */}
        <div className="chart-container" id="top-countries">
          <h3 className="chart-title">Top Countries</h3>
          {data.top_countries && data.top_countries.length > 0 ? (
            <ul className="country-list">
              {data.top_countries.map((c, i) => (
                <li className="country-item" key={i}>
                  <span className="country-name" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.7rem',
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '4px',
                      padding: '0.15rem 0.4rem',
                      marginRight: '8px',
                      color: 'var(--text-secondary)',
                      lineHeight: '1',
                      fontWeight: 500
                    }}>
                      {getCountryCode(c.country)}
                    </span>
                    {c.country}
                  </span>
                  <span className="country-clicks">{c.clicks.toLocaleString()}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>
              No geo data available yet
            </p>
          )}
        </div>

        {/* Quick Info */}
        <div className="chart-container" id="quick-info">
          <h3 className="chart-title">Link Details</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <InfoRow
              label="Short URL"
              value={`${window.location.origin}/${shortCode}`}
              mono
            />
            <InfoRow
              label="Created"
              value={new Date(data.created_at).toLocaleString()}
            />
            <InfoRow
              label="Expires"
              value={data.expires_at
                ? new Date(data.expires_at).toLocaleString()
                : 'Never'
              }
            />
            <InfoRow
              label="Click-through Rate"
              value={data.total_clicks > 0
                ? `${Math.round((data.unique_clicks / data.total_clicks) * 100)}% unique`
                : 'N/A'
              }
            />
          </div>

          {/* QR Code Button */}
          <div style={{ marginTop: '1.5rem' }}>
            <a
              href={`/api/v1/qr/${shortCode}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
              id="download-qr"
              style={{ width: '100%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <rect x="7" y="7" width="3" height="3"></rect>
                <rect x="14" y="7" width="3" height="3"></rect>
                <rect x="7" y="14" width="3" height="3"></rect>
                <rect x="14" y="14" width="3" height="3"></rect>
              </svg>
              Download QR Code
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value, mono }) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.5rem 0',
      borderBottom: '1px solid var(--border-color)',
    }}>
      <span style={{ color: 'var(--text-tertiary)', fontSize: '0.85rem' }}>{label}</span>
      <span style={{
        color: 'var(--text-primary)',
        fontSize: '0.85rem',
        fontWeight: 500,
        fontFamily: mono ? 'var(--font-mono)' : 'inherit',
        maxWidth: '220px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
      }}>
        {value}
      </span>
    </div>
  );
}

function getCountryCode(countryName) {
  const codes = {
    'United States': 'US',
    'India': 'IN',
    'United Kingdom': 'GB',
    'Germany': 'DE',
    'France': 'FR',
    'Canada': 'CA',
    'Australia': 'AU',
    'Japan': 'JP',
    'Brazil': 'BR',
    'China': 'CN',
  };
  return codes[countryName] || 'GL'; // Global/Other
}
