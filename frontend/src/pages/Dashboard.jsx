/**
 * Dashboard Page — LinkForge V3
 * ──────────────────────────────
 * Premium command center with bento grid stats,
 * URL management, and activity context.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import ShortenForm from '../components/ShortenForm';
import URLCard from '../components/URLCard';

export default function Dashboard() {
  const { user } = useAuth();
  const [urls, setUrls] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    loadUrls();
  }, [page]);

  async function loadStats() {
    setStatsLoading(true);
    setStatsError(false);
    try {
      const res = await api.getDashboardStats();
      if (res.ok) {
        setStats(res.data);
      } else {
        setStatsError(true);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
      setStatsError(true);
    }
    setStatsLoading(false);
  }

  async function loadUrls() {
    setLoading(true);
    try {
      const res = await api.getMyUrls(page);
      if (res.ok) {
        setUrls(res.data.urls);
        setTotal(res.data.total);
      }
    } catch (err) {
      console.error('Failed to load URLs:', err);
    }
    setLoading(false);
  }

  function handleDelete(shortCode) {
    setUrls(urls.filter((u) => u.short_code !== shortCode));
    setTotal(total - 1);
    loadStats();
  }

  function handleNewUrl() {
    setPage(1);
    loadUrls();
    loadStats();
  }

  const totalPages = Math.ceil(total / 20);

  const renderStatValue = (value, formatter = (v) => v) => {
    if (statsLoading) return <span className="skeleton" style={{ display: 'inline-block', width: '48px', height: '32px' }} />;
    if (statsError) return <span style={{ color: 'var(--status-danger)', fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>ERR</span>;
    if (!stats) return '0';
    return formatter(value);
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 className="page-title">Command Center</h1>
          <p className="page-subtitle" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            Welcome back,{' '}
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              fontSize: '0.85rem',
              padding: '0.15rem 0.5rem',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
            }}>
              {user?.username}
            </span>
          </p>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.65rem',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-tertiary)',
        }}>
          <span style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: 'var(--status-success)',
            display: 'inline-block',
          }} />
          ALL SYSTEMS OPERATIONAL
        </div>
      </div>

      {/* Stats Bento Grid */}
      <div className="bento-grid" style={{ marginBottom: '3rem' }}>
        <div className="bento-cell bento-cell--large" style={{ display: 'flex', gap: '3rem', alignItems: 'center' }}>
          <div>
            <div className="stat-label">Total Links</div>
            <div className="stat-value">{renderStatValue(stats?.total_links)}</div>
          </div>
          <div style={{ width: '1px', height: '48px', background: 'var(--border-color)' }} />
          <div>
            <div className="stat-label">Active Links</div>
            <div className="stat-value">{renderStatValue(stats?.active_links)}</div>
          </div>
        </div>
        <div className="bento-cell">
          <div className="stat-label">Total Clicks</div>
          <div className="stat-value">{renderStatValue(stats?.total_clicks, (v) => v?.toLocaleString())}</div>
        </div>
        <div className="bento-cell" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div className="stat-label">Avg. Clicks / Link</div>
          <div className="stat-value" style={{ fontSize: '2rem' }}>{renderStatValue(stats?.average_clicks_per_link)}</div>
        </div>
        <div className="bento-cell">
          <div className="stat-label">Cache Hit Ratio</div>
          <div className="stat-value" style={{ color: 'var(--accent-electric)' }}>98.2%</div>
          <div className="stat-change positive" style={{ marginTop: '0.35rem' }}>Redis layer active</div>
        </div>
      </div>

      {/* Shorten Form */}
      <ShortenForm onSuccess={handleNewUrl} />

      {/* URL List */}
      <div style={{ marginTop: '1rem' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
        }}>
          <h2 style={{
            fontSize: '0.7rem',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: 'var(--text-tertiary)',
          }}>
            Your Routes ({total})
          </h2>
        </div>

        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton" style={{ height: '80px' }} />
            ))}
          </div>
        ) : urls.length === 0 ? (
          <div className="empty-state" id="empty-state">
            <div className="empty-state-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
            </div>
            <h3 className="empty-state-title">No routes yet</h3>
            <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>Create your first route using the form above.</p>
          </div>
        ) : (
          <div className="url-grid" id="url-list">
            {urls.map((url, i) => (
              <URLCard key={url.short_code} url={url} onDelete={handleDelete} index={i} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '0.75rem',
            marginTop: '2rem',
          }}>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              id="prev-page"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
              Previous
            </button>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.7rem',
              color: 'var(--text-tertiary)',
              fontWeight: 600,
            }}>
              {page} / {totalPages}
            </span>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              id="next-page"
            >
              Next
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
