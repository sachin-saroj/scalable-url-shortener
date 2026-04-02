/**
 * Dashboard Page
 * ────────────────
 * Shows user's shortened URLs with stats overview.
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

  useEffect(() => {
    loadUrls();
  }, [page]);

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
  }

  function handleNewUrl() {
    // Reload first page to show new URL
    setPage(1);
    loadUrls();
  }

  const totalClicks = urls.reduce((sum, u) => sum + (u.total_clicks || 0), 0);
  const activeUrls = urls.filter((u) => u.is_active && !(u.expires_at && new Date(u.expires_at) < new Date()));
  const totalPages = Math.ceil(total / 20);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome back, {user?.username}! Manage your links and track performance.</p>
      </div>

      {/* Stats Overview */}
      <div className="stats-grid">
        <div className="stat-card" id="stat-total-urls">
          <div className="stat-label">Total Links</div>
          <div className="stat-value">{total}</div>
        </div>
        <div className="stat-card" id="stat-active-urls">
          <div className="stat-label">Active Links</div>
          <div className="stat-value">{activeUrls.length}</div>
        </div>
        <div className="stat-card" id="stat-total-clicks">
          <div className="stat-label">Total Clicks</div>
          <div className="stat-value">{totalClicks.toLocaleString()}</div>
        </div>
        <div className="stat-card" id="stat-avg-clicks">
          <div className="stat-label">Avg. Clicks/Link</div>
          <div className="stat-value">
            {urls.length > 0 ? Math.round(totalClicks / urls.length) : 0}
          </div>
        </div>
      </div>

      {/* Shorten Form */}
      <ShortenForm onSuccess={handleNewUrl} />

      {/* URL List */}
      <div style={{ marginTop: '1rem' }}>
        <h2 style={{
          fontSize: '1.2rem',
          fontWeight: 700,
          marginBottom: '1rem',
          color: 'var(--text-primary)',
        }}>
          Your Links ({total})
        </h2>

        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton" style={{ height: '80px' }} />
            ))}
          </div>
        ) : urls.length === 0 ? (
          <div className="empty-state" id="empty-state">
            <div className="empty-state-icon">🔗</div>
            <h3 className="empty-state-title">No links yet</h3>
            <p>Create your first short link using the form above!</p>
          </div>
        ) : (
          <div className="url-grid" id="url-list">
            {urls.map((url) => (
              <URLCard key={url.short_code} url={url} onDelete={handleDelete} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '0.5rem',
            marginTop: '2rem',
          }}>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              id="prev-page"
            >
              ← Previous
            </button>
            <span style={{
              padding: '0.5rem 1rem',
              color: 'var(--text-secondary)',
              fontSize: '0.85rem',
            }}>
              Page {page} of {totalPages}
            </span>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              id="next-page"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
