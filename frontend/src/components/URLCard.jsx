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
          <a href={url.short_url} target="_blank" rel="noopener noreferrer">
            {url.short_url.replace(/^https?:\/\//, '')}
          </a>
          {isExpired && (
            <span className="badge badge-expired">Expired</span>
          )}
          {url.custom_alias && (
            <span className="badge badge-custom">Custom</span>
          )}
        </div>
        <p className="url-original" title={url.original_url}>
          → {url.original_url}
        </p>
        <div className="url-meta">
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            {createdDate}
          </span>
          {url.expires_at && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              Expires {new Date(url.expires_at).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      <div className="url-card-actions">
        <div className="click-badge" id={`clicks-${url.short_code}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '2px' }}>
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/>
          </svg>
          {url.total_clicks} clicks
        </div>
        <Link
          to={`/analytics/${url.short_code}`}
          className="btn btn-secondary btn-sm"
          id={`analytics-btn-${url.short_code}`}
          title="Analytics"
          style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
        </Link>
        <button
          className="btn btn-secondary btn-sm"
          onClick={handleCopy}
          id={`copy-${url.short_code}`}
          title={copied ? "Copied!" : "Copy URL"}
          style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}
        >
          {copied ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          )}
        </button>
        <button
          className="btn btn-danger btn-sm"
          onClick={handleDelete}
          disabled={deleting}
          id={`delete-${url.short_code}`}
          title="Delete URL"
          style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line>
            <line x1="14" y1="11" x2="14" y2="17"></line>
          </svg>
        </button>
      </div>
    </div>
  );
}
