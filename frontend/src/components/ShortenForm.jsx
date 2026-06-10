/**
 * Shorten Form Component
 * ───────────────────────
 * Main URL shortening form with optional custom alias and expiry.
 */

import { useState } from 'react';
import { api } from '../utils/api';

export default function ShortenForm({ onSuccess }) {
  const [url, setUrl] = useState('');
  const [customAlias, setCustomAlias] = useState('');
  const [expiresIn, setExpiresIn] = useState('');
  const [showOptions, setShowOptions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setResult(null);

    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    try {
      const res = await api.shortenUrl(
        url.trim(),
        customAlias.trim() || null,
        expiresIn || null
      );

      if (res.ok) {
        setResult(res.data);
        setUrl('');
        setCustomAlias('');
        setExpiresIn('');
        if (onSuccess) onSuccess(res.data);
      } else {
        setError(res.data.detail || 'Failed to shorten URL');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  }

  async function handleCopy() {
    if (result) {
      await navigator.clipboard.writeText(result.short_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="shorten-section">
      <form className="shorten-form" onSubmit={handleSubmit} id="shorten-form">
        <div className="form-row">
          <div className="form-input-wrapper">
            <input
              type="text"
              className={`form-input ${error ? 'input-error' : ''}`}
              placeholder="Paste your long URL here..."
              value={url}
              onChange={(e) => { setUrl(e.target.value); setError(''); }}
              id="url-input"
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            id="shorten-btn"
          >
            {loading ? (
              <div className="spinner" />
            ) : (
              'Shorten'
            )}
          </button>
        </div>

        {error && <p className="error-message" id="form-error">{error}</p>}

        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => setShowOptions(!showOptions)}
          style={{ marginTop: '1rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          id="toggle-options"
        >
          {showOptions ? (
            <>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>
              Hide options
            </>
          ) : (
            <>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
              More options
            </>
          )}
        </button>

        {showOptions && (
          <div className="form-options" style={{ animation: 'slideUp 0.2s ease' }}>
            <div>
              <label className="form-label" htmlFor="alias-input">Custom Alias</label>
              <input
                type="text"
                className="form-input"
                placeholder="my-brand"
                value={customAlias}
                onChange={(e) => setCustomAlias(e.target.value)}
                id="alias-input"
              />
            </div>
            <div>
              <label className="form-label" htmlFor="expiry-input">Expires In (hours)</label>
              <input
                type="number"
                className="form-input"
                placeholder="48"
                min="1"
                max="8760"
                value={expiresIn}
                onChange={(e) => setExpiresIn(e.target.value)}
                id="expiry-input"
              />
            </div>
          </div>
        )}
      </form>

      {result && (
        <div className="result-card" id="result-card">
          <p className="result-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Link created successfully!
          </p>
          <div className="result-url">
            <span className="result-url-text" id="result-url">{result.short_url}</span>
            <button
              className="btn btn-secondary btn-sm"
              onClick={handleCopy}
              id="copy-btn"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              {copied ? (
                <>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Copied!
                </>
              ) : (
                <>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                  Copy
                </>
              )}
            </button>
            <a
              href={`/api/v1/qr/${result.short_code}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary btn-sm"
              id="qr-btn"
            >
              QR Code
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
