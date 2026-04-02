/**
 * URL Card Component
 * ───────────────────
 * Displays a single shortened URL with actions.
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../utils/api';

export default function URLCard({ url, onDelete }) {
  const [deleting, setDeleting] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(url.short_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to deactivate this URL?')) return;
    setDeleting(true);
    const res = await api.deleteUrl(url.short_code);
    if (res.ok) {
      onDelete(url.short_code);
    }
    setDeleting(false);
  }

  const isExpired = url.expires_at && new Date(url.expires_at) < new Date();
  const createdDate = new Date(url.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  });

  return (
    <div className="url-card" id={`url-card-${url.short_code}`}>
      <div className="url-card-info">
        <div className="url-short">
          <a href={url.short_url} target="_blank" rel="noopener">
            {url.short_url.replace(/^https?:\/\//, '')}
          </a>
          {isExpired && (
            <span style={{
              fontSize: '0.7rem',
              background: 'var(--status-danger-bg)',
              color: 'var(--status-danger)',
              padding: '0.2rem 0.5rem',
              borderRadius: 'var(--radius-full)',
            }}>EXPIRED</span>
          )}
          {url.custom_alias && (
            <span style={{
              fontSize: '0.7rem',
              background: 'var(--status-info-bg)',
              color: 'var(--status-info)',
              padding: '0.2rem 0.5rem',
              borderRadius: 'var(--radius-full)',
            }}>CUSTOM</span>
          )}
        </div>
        <p className="url-original" title={url.original_url}>
          → {url.original_url}
        </p>
        <div className="url-meta">
          <span>📅 {createdDate}</span>
          {url.expires_at && (
            <span>⏰ Expires {new Date(url.expires_at).toLocaleDateString()}</span>
          )}
        </div>
      </div>

      <div className="url-card-actions">
        <div className="click-badge" id={`clicks-${url.short_code}`}>
          👆 {url.total_clicks} clicks
        </div>
        <Link
          to={`/analytics/${url.short_code}`}
          className="btn btn-secondary btn-sm"
          id={`analytics-btn-${url.short_code}`}
        >
          📊
        </Link>
        <button
          className="btn btn-secondary btn-sm"
          onClick={handleCopy}
          id={`copy-${url.short_code}`}
        >
          {copied ? '✓' : '📋'}
        </button>
        <button
          className="btn btn-danger btn-sm"
          onClick={handleDelete}
          disabled={deleting}
          id={`delete-${url.short_code}`}
        >
          🗑
        </button>
      </div>
    </div>
  );
}
