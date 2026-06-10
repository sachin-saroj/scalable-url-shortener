/**
 * Home Page — LinkForge V3
 * ─────────────────────────
 * Premium infrastructure landing page with editorial hero,
 * bento feature grid, architecture strip, and activity feed.
 */

import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import ShortenForm from '../components/ShortenForm';
import { useAuth } from '../context/AuthContext';
import useScrollReveal from '../utils/useScrollReveal';

export default function Home() {
  const { isAuthenticated } = useAuth();
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const heroRef = useRef(null);

  function handleMouseMove(e) {
    if (!heroRef.current) return;
    const rect = heroRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    setMousePos({ x, y });
  }

  return (
    <div className="page-container" style={{ maxWidth: '1200px', padding: '0 2rem 6rem' }}>

      {/* ── HERO SECTION ─────────────────────────────── */}
      <section
        className="hero-section"
        ref={heroRef}
        onMouseMove={handleMouseMove}
      >
        <div className="hero-left">
          <h1 className="hero-heading">
            SHORT LINKS{' '}
            <br />
            BUILT FOR
            <br />
            <span className="accent">INFRASTRUCTURE.</span>
          </h1>

          <p className="hero-subheading">
            Sub-50ms redirects. Redis-powered routing.
            Production-grade analytics. Enterprise-grade reliability
            for teams that build at scale.
          </p>

          <div className="hero-cta-row">
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary" id="hero-dashboard-btn">
                Launch Dashboard
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary" id="hero-signup-btn">
                  Launch Dashboard
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                </Link>
                <a href="#architecture" className="btn btn-secondary" id="hero-explore-btn">
                  Explore Architecture
                </a>
              </>
            )}
          </div>

          <div className="hero-performance">
            <div className="hero-metric">
              <span className="hero-metric-value">99.97%</span>
              <span className="hero-metric-label">Uptime SLA</span>
            </div>
            <div className="hero-metric">
              <span className="hero-metric-value">&lt;47ms</span>
              <span className="hero-metric-label">P95 Latency</span>
            </div>
            <div className="hero-metric">
              <span className="hero-metric-value">12M+</span>
              <span className="hero-metric-label">Routes Processed</span>
            </div>
          </div>
        </div>

        <div className="hero-right">
          <div
            className="hero-image-wrapper"
            style={{
              transform: `translate(${mousePos.x * 12}px, ${mousePos.y * 12}px)`,
            }}
          >
            <img
              src="/hero-infrastructure.png"
              alt="Abstract 3D infrastructure routing sculpture"
              width="560"
              height="560"
              loading="eager"
            />
          </div>
        </div>
      </section>

      {/* ── SHORTEN FORM ─────────────────────────────── */}
      <ShortenForm />

      {/* ── FEATURE BENTO GRID ───────────────────────── */}
      <FeatureGrid />

      {/* ── ARCHITECTURE SECTION ─────────────────────── */}
      <ArchitectureSection />

      {/* ── ACTIVITY FEED ────────────────────────────── */}
      <ActivityFeed />
    </div>
  );
}


/* ── Feature Bento Grid ──────────────────────────────── */
function FeatureGrid() {
  const ref = useScrollReveal();

  const features = [
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
      ),
      title: 'Sub-50ms Routing',
      desc: 'Synchronous database bypass with high-concurrency Redis caching. Built for massive click loads with zero cold-start penalty.',
      color: 'var(--accent-electric)',
      bgColor: 'var(--accent-electric-dim)',
      large: true,
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
      ),
      title: 'Production Analytics',
      desc: 'Precise click tracking with country codes, referrers, and user agents logged in real time.',
      color: 'var(--accent-purple)',
      bgColor: 'var(--accent-purple-dim)',
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
      ),
      title: 'Security Layer',
      desc: 'SSRF shielding, malicious URL detection, rate limiters, and JWT authorization.',
      color: 'var(--status-success)',
      bgColor: 'var(--status-success-bg)',
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
      ),
      title: 'Custom Aliases',
      desc: 'Claim specific short codes for campaigns. No generic auto-increment hashes.',
      color: 'var(--status-warning)',
      bgColor: 'var(--status-warning-bg)',
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><rect x="7" y="7" width="3" height="3"/><rect x="14" y="7" width="3" height="3"/><rect x="7" y="14" width="3" height="3"/></svg>
      ),
      title: 'QR Generation',
      desc: 'Auto-generated QR vectors for mobile scanning and cross-channel print campaigns.',
      color: 'var(--status-info)',
      bgColor: 'var(--status-info-bg)',
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      ),
      title: 'Strict Expiration',
      desc: 'Exact campaign life spans with automated deletion of expired routes.',
      color: 'var(--status-danger)',
      bgColor: 'var(--status-danger-bg)',
      large: true,
    },
  ];

  return (
    <div
      ref={ref}
      className="reveal"
      style={{ marginTop: '5rem' }}
    >
      <p style={{
        fontSize: '0.65rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        color: 'var(--text-tertiary)',
        marginBottom: '1.5rem',
        textAlign: 'center',
      }}>
        Platform Capabilities
      </p>
      <div className="bento-grid">
        {features.map((f, i) => (
          <div
            key={i}
            className={`bento-cell ${f.large ? 'bento-cell--large' : ''}`}
            style={{ '--reveal-index': i }}
          >
            <div
              className="bento-cell__icon"
              style={{ background: f.bgColor, color: f.color }}
            >
              {f.icon}
            </div>
            <h3 className="bento-cell__title">{f.title}</h3>
            <p className="bento-cell__desc">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}


/* ── Architecture Section ────────────────────────────── */
function ArchitectureSection() {
  const ref = useScrollReveal();

  const techStack = [
    'FastAPI', 'PostgreSQL', 'Redis v7', 'Celery', 'React 18', 'Vite 6', 'SQLAlchemy',
  ];

  return (
    <div ref={ref} className="reveal infra-section" id="architecture">
      <p className="infra-section__label">System Architecture</p>

      <div className="tech-badges">
        {techStack.map((tech) => (
          <span key={tech} className="tech-badge">{tech}</span>
        ))}
      </div>

      <div className="infra-metrics">
        <div className="infra-metric">
          <div className="infra-metric__value">&lt;47ms</div>
          <div className="infra-metric__label">P95 Response Time</div>
        </div>
        <div className="infra-metric">
          <div className="infra-metric__value">98.2%</div>
          <div className="infra-metric__label">Cache Hit Ratio</div>
        </div>
        <div className="infra-metric">
          <div className="infra-metric__value">99.97%</div>
          <div className="infra-metric__label">Uptime (30d)</div>
        </div>
        <div className="infra-metric">
          <div className="infra-metric__value">2.1M</div>
          <div className="infra-metric__label">Redirects / Day</div>
        </div>
      </div>
    </div>
  );
}


/* ── Activity Feed ───────────────────────────────────── */
function ActivityFeed() {
  const ref = useScrollReveal();

  const [activities] = useState([
    { type: 'click', text: 'New click from Mumbai — /api-docs', time: '2s ago', color: 'var(--accent-electric)' },
    { type: 'spike', text: 'Traffic spike detected on /launch', time: '14s ago', color: 'var(--status-warning)' },
    { type: 'redirect', text: 'Redirect processed — /gh-repo → github.com', time: '31s ago', color: 'var(--status-success)' },
    { type: 'cache', text: 'Cache hit recorded — /pricing', time: '45s ago', color: 'var(--accent-purple)' },
    { type: 'share', text: 'Link shared from Reddit — /blog-post', time: '1m ago', color: 'var(--status-info)' },
  ]);

  return (
    <div ref={ref} className="reveal" style={{ marginTop: '4rem' }}>
      <div className="activity-feed">
        <div className="activity-feed__header">
          <span className="live-dot" />
          Recent Activity
        </div>
        {activities.map((a, i) => (
          <div key={i} className="activity-item" style={{ '--reveal-index': i }}>
            <div
              className="activity-item__indicator"
              style={{ background: a.color }}
            />
            <span className="activity-item__text">{a.text}</span>
            <span className="activity-item__time">{a.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
