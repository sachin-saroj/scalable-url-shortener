/**
 * URL Card Component — LinkForge V3
 * ────────────────────────────────────
 * Premium infrastructure object treatment.
 * Clear hierarchy: Short URL → Destination → Metadata.
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../utils/api';

export default function URLCard({ url, onDelete, index = 0 }) {
  const [deleting, setDeleting] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(url.short_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to deactivate this route?')) return;
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
    <div
      className="url-card"
      id={`url-card-${url.short_code}`}
      style={{
        animationDelay: `${index * 60}ms`,
        animation: `fadeSlideUp var(--duration-entrance) var(--ease-out-expo) both`,
      }}
    >
      <div className="url-card-info">
        {/* Primary: Short URL */}
        <div className="url-short">
          <a href={url.short_url} target="_blank" rel="noopener noreferrer">
            {url.short_url.replace(/^https?:\/\//, '')}
          </a>

          {/* Status */}
          {isExpired ? (
            <span className="badge badge-expired">Expired</span>
          ) : (
            <span style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: 'var(--status-success)',
              display: 'inline-block',
              flexShrink: 0,
            }} title="Active" />
          )}
          {url.custom_alias && (
            <span className="badge badge-custom">Custom</span>
          )}
        </div>

        {/* Secondary: Destination URL */}
        <p className="url-original" title={url.original_url}>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '4px', verticalAlign: 'middle', opacity: 0.5 }}>
            <polyline points="9 18 15 12 9 6" />
          </svg>
          {url.original_url}
        </p>

        {/* Tertiary: Metadata */}
        <div className="url-meta">
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            {createdDate}
          </span>
          {url.expires_at && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              Expires {new Date(url.expires_at).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      <div className="url-card-actions">
        {/* Click count */}
        <div className="click-badge" id={`clicks-${url.short_code}`}>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/>
          </svg>
          {url.total_clicks}
        </div>

        {/* Analytics */}
        <Link
          to={`/analytics/${url.short_code}`}
          className="btn btn-secondary btn-sm btn-icon"
          id={`analytics-btn-${url.short_code}`}
          title="Analytics"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
        </Link>

        {/* Copy */}
        <button
          className="btn btn-secondary btn-sm btn-icon"
          onClick={handleCopy}
          id={`copy-${url.short_code}`}
          title={copied ? "Copied!" : "Copy URL"}
        >
          {copied ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--status-success)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          )}
        </button>

        {/* Delete */}
        <button
          className="btn btn-danger btn-sm btn-icon"
          onClick={handleDelete}
          disabled={deleting}
          id={`delete-${url.short_code}`}
          title="Delete route"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </button>
      </div>
    </div>
  );
}
