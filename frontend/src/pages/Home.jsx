/**
 * Home Page — LinkForge V3
 * ─────────────────────────
 * Premium routing infrastructure platform presentation.
 * Inspired by Vercel, Linear, Stripe.
 */

import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import ShortenForm from '../components/ShortenForm';
import { useAuth } from '../context/AuthContext';
import useScrollReveal from '../utils/useScrollReveal';

import AnimatedHeading from '../components/AnimatedHeading';
import FadeIn from '../components/FadeIn';

export default function Home() {
  const { isAuthenticated } = useAuth();
  const heroRef = useRef(null);

  return (
    <div className="w-full min-h-screen bg-black text-white selection:bg-white/10 selection:text-white relative">
      
      {/* ── HERO SECTION ─────────────────────────────── */}
      <section
        className="relative w-full min-h-[calc(100vh-88px)] flex flex-col overflow-hidden"
        ref={heroRef}
      >
        {/* Full-screen Background Video */}
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover -z-10"
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4"
        />

        {/* Hero Content Container */}
        <div className="flex-1 flex flex-col justify-end px-6 md:px-12 lg:px-16 pb-12 lg:pb-16 z-10 w-full">
          {/* Hero Grid Container */}
          <div className="w-full lg:grid lg:grid-cols-2 lg:items-end gap-12">
            
            {/* Left Column: Main Content */}
            <div className="flex flex-col items-start">
              <AnimatedHeading 
                text={"Shaping tomorrow\nwith vision and action."}
                className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4 text-white leading-tight tracking-tight"
                style={{ letterSpacing: '-0.04em' }}
              />

              <FadeIn delay={800} duration={1000}>
                <p className="text-base md:text-lg text-gray-300 mb-5 max-w-[520px]">
                  We back visionaries and craft ventures that define what comes next.
                </p>
              </FadeIn>

              <FadeIn delay={1200} duration={1000} className="w-full">
                <div className="flex flex-wrap gap-4">
                  {isAuthenticated ? (
                    <Link to="/dashboard" className="bg-white !text-black px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors no-underline text-center">
                      Launch Console
                    </Link>
                  ) : (
                    <Link to="/register" className="bg-white !text-black px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors no-underline text-center">
                      Start a Chat
                    </Link>
                  )}
                  <a href="#features" className="liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:!text-black transition-colors no-underline text-center">
                    Explore Now
                  </a>
                </div>
              </FadeIn>
            </div>

            {/* Right Column: Tag */}
            <div className="flex items-end justify-start lg:justify-end mt-8 lg:mt-0">
              <FadeIn delay={1400} duration={1000}>
                <div className="liquid-glass border border-white/20 px-6 py-3 rounded-xl">
                  <span className="text-lg md:text-xl lg:text-2xl font-light text-white">
                    Investing. Building. Advisory.
                  </span>
                </div>
              </FadeIn>
            </div>

          </div>
        </div>
      </section>

      {/* ── LOWER CONTENT WRAPPER ────────────────────── */}
      <div id="features" className="w-full max-w-[1200px] mx-auto px-6 md:px-12 lg:px-16 py-12">
        {/* ── SHORTEN FORM ─────────────────────────────── */}
        <ShortenForm />

        {/* ── FEATURE BENTO GRID ───────────────────────── */}
        <FeatureGrid />

        {/* ── ARCHITECTURE SECTION ─────────────────────── */}
        <ArchitectureSection />

        {/* ── ACTIVITY FEED ────────────────────────────── */}
        <ActivityFeed />

        {/* ── TRUST LAYER ──────────────────────────────── */}
        <TrustLayer />
      </div>
      
    </div>
  );
}


/* ── Feature Bento Grid ──────────────────────────────── */
function FeatureGrid() {
  const ref = useScrollReveal();

  return (
    <div
      ref={ref}
      className="reveal"
      style={{ marginTop: '6rem' }}
    >
      <p style={{
        fontSize: '0.65rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        color: 'var(--text-tertiary)',
        marginBottom: '2rem',
        textAlign: 'center',
      }}>
        Platform Engine Capabilities
      </p>
      
      {/* 4-column Bento grid system */}
      <div className="bento-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        
        {/* Large Card: Spans 3 columns */}
        <div className="bento-cell bento-cell--large" style={{ gridColumn: 'span 3', borderTop: '2px solid var(--accent-electric)' }}>
          <div className="bento-cell__icon" style={{ background: 'var(--accent-electric-dim)', color: 'var(--accent-electric)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </div>
          <h3 className="bento-cell__title" style={{ fontSize: '1.25rem' }}>Sub-50ms Global Routing</h3>
          <p className="bento-cell__desc" style={{ fontSize: '0.9rem', maxWidth: '640px' }}>
            Synchronous database bypass utilizing high-concurrency Redis caching layers. Active routes resolve near-instantaneously at the edge, offering production-grade throughput with zero cold-start delay.
          </p>
        </div>

        {/* Medium Card: Spans 1 column */}
        <div className="bento-cell">
          <div className="bento-cell__icon" style={{ background: 'var(--accent-purple-dim)', color: 'var(--accent-purple)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </div>
          <h3 className="bento-cell__title">Analytics</h3>
          <p className="bento-cell__desc">Detailed request logging capturing visitor locations, referrers, and system performance telemetry.</p>
        </div>

        {/* Row 2: Medium cards (span 1 col each) */}
        <div className="bento-cell">
          <div className="bento-cell__icon" style={{ background: 'var(--status-success-bg)', color: 'var(--status-success)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <h3 className="bento-cell__title">Security Shield</h3>
          <p className="bento-cell__desc">SSRF prevention, host filtering, malicious redirect prevention, and active JWT path authentication.</p>
        </div>

        <div className="bento-cell">
          <div className="bento-cell__icon" style={{ background: 'var(--status-warning-bg)', color: 'var(--status-warning)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          </div>
          <h3 className="bento-cell__title">Custom Aliases</h3>
          <p className="bento-cell__desc">Override generic hashes with clean, branded path parameters to sustain routing consistency.</p>
        </div>

        <div className="bento-cell">
          <div className="bento-cell__icon" style={{ background: 'var(--status-info-bg)', color: 'var(--status-info)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><rect x="7" y="7" width="3" height="3"/><rect x="14" y="7" width="3" height="3"/><rect x="7" y="14" width="3" height="3"/></svg>
          </div>
          <h3 className="bento-cell__title">QR Engine</h3>
          <p className="bento-cell__desc">Instantly compile high-definition QR vector blocks corresponding to active routing destinations.</p>
        </div>

        <div className="bento-cell">
          <div className="bento-cell__icon" style={{ background: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <h3 className="bento-cell__title">Expiration</h3>
          <p className="bento-cell__desc">Configure exact Campaign TTL limits to automatically flush inactive routes from database nodes.</p>
        </div>

        {/* Row 3: Small cards (caching 1 col, workers 1 col, rate limiting 2 cols) */}
        <div className="bento-cell">
          <div className="bento-cell__icon" style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <h3 className="bento-cell__title">Active Caching</h3>
          <p className="bento-cell__desc">Custom HTTP headers and cache controls tailored for immediate edge replication.</p>
        </div>

        <div className="bento-cell">
          <div className="bento-cell__icon" style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <h3 className="bento-cell__title">Async Workers</h3>
          <p className="bento-cell__desc">Celery task queues process incoming analytics off the critical path, keeping redirects fast.</p>
        </div>

        <div className="bento-cell" style={{ gridColumn: 'span 2' }}>
          <div className="bento-cell__icon" style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          </div>
          <h3 className="bento-cell__title">Rate Limiting Protection</h3>
          <p className="bento-cell__desc">Adaptive token-bucket rate limiters defend downstream services against DDoS surges and bot crawlers, preserving network balance.</p>
        </div>

      </div>
    </div>
  );
}


/* ── Interactive Architecture Visualizer ───────────────── */
function ArchitectureSection() {
  const ref = useScrollReveal();
  const [simMode, setSimMode] = useState('hit'); // 'hit' | 'miss'

  return (
    <div ref={ref} className="reveal arch-section" id="architecture">
      <p style={{
        fontSize: '0.65rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        color: 'var(--text-tertiary)',
        textAlign: 'center',
        marginBottom: '0.5rem',
      }}>
        Interactive Architecture
      </p>
      
      <div className="arch-visualizer">
        <div className="arch-visualizer__header">
          <div className="arch-visualizer__title">
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: simMode === 'hit' ? 'var(--accent-electric)' : 'var(--accent-purple)',
              boxShadow: simMode === 'hit' ? '0 0 8px var(--accent-electric)' : '0 0 8px var(--accent-purple)',
              display: 'inline-block',
            }} />
            Execution Flow Simulation
          </div>
          <div className="arch-visualizer__controls">
            <button
              className={`btn btn-sm ${simMode === 'hit' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSimMode('hit')}
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.65rem',
                borderRadius: '4px',
                borderColor: simMode === 'hit' ? 'var(--accent-electric)' : 'var(--border-color)',
                background: simMode === 'hit' ? 'var(--accent-electric)' : 'transparent',
              }}
            >
              Cache Hit (Sub-50ms)
            </button>
            <button
              className={`btn btn-sm ${simMode === 'miss' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSimMode('miss')}
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.65rem',
                borderRadius: '4px',
                borderColor: simMode === 'miss' ? 'var(--accent-purple)' : 'var(--border-color)',
                background: simMode === 'miss' ? 'var(--accent-purple)' : 'transparent',
              }}
            >
              Cache Miss (Write/DB Query)
            </button>
          </div>
        </div>

        <div className="arch-svg-container">
          <svg viewBox="0 0 800 200" className="architecture-svg">
            {/* Connection Paths */}
            
            {/* Cache Hit Path: Client -> Redis -> Client */}
            <path
              id="edge-to-redis"
              className={`connection-line ${simMode === 'hit' ? 'active' : ''}`}
              d="M 160 85 C 230 50, 270 40, 320 40"
            />
            {simMode === 'hit' && (
              <path
                className="connection-line active flow-dot"
                d="M 160 85 C 230 50, 270 40, 320 40"
              />
            )}
            
            <path
              id="redis-to-edge"
              className={`connection-line ${simMode === 'hit' ? 'active' : ''}`}
              d="M 320 50 C 270 50, 230 110, 160 105"
            />
            {simMode === 'hit' && (
              <path
                className="connection-line active flow-dot"
                d="M 320 50 C 270 50, 230 110, 160 105"
                style={{ animationDirection: 'reverse' }}
              />
            )}

            {/* Cache Miss Path: Client -> FastAPI -> Postgres -> FastAPI -> Redis -> Client */}
            {/* Edge to FastAPI */}
            <path
              id="edge-to-fastapi"
              className={`connection-line ${simMode === 'miss' ? 'active-alt' : ''}`}
              d="M 160 95 L 480 95"
            />
            {simMode === 'miss' && (
              <path
                className="connection-line active-alt flow-dot"
                d="M 160 95 L 480 95"
              />
            )}

            {/* FastAPI to Postgres */}
            <path
              id="fastapi-to-postgres"
              className={`connection-line ${simMode === 'miss' ? 'active-alt' : ''}`}
              d="M 580 95 L 680 95"
            />
            {simMode === 'miss' && (
              <path
                className="connection-line active-alt flow-dot"
                d="M 580 95 L 680 95"
              />
            )}
            
            {/* Postgres to FastAPI (Reverse flow) */}
            {simMode === 'miss' && (
              <path
                className="connection-line active-alt flow-dot"
                d="M 580 95 L 680 95"
                style={{ animationDirection: 'reverse' }}
              />
            )}

            {/* FastAPI writes cache to Redis */}
            <path
              id="fastapi-to-redis"
              className={`connection-line ${simMode === 'miss' ? 'active-alt' : ''}`}
              d="M 530 80 C 470 50, 420 40, 380 40"
            />
            {simMode === 'miss' && (
              <path
                className="connection-line active-alt flow-dot"
                d="M 530 80 C 470 50, 420 40, 380 40"
                style={{ animationDirection: 'reverse' }}
              />
            )}

            {/* Nodes */}
            
            {/* Client / Edge node */}
            <g className={`node-group ${simMode === 'hit' ? 'active-blue' : 'active-purple'}`}>
              <rect x="40" y="65" width="120" height="60" className="node-rect" />
              <text x="100" y="93" textAnchor="middle" className="node-text-title">EDGE ROUTING</text>
              <text x="100" y="108" textAnchor="middle" className="node-text-sub">LinkForge DNS</text>
            </g>

            {/* Redis Caching Node */}
            <g className={`node-group ${simMode === 'hit' ? 'active-blue' : 'active'}`}>
              <rect x="280" y="15" width="100" height="50" className="node-rect" />
              <text x="330" y="40" textAnchor="middle" className="node-text-title">REDIS V7</text>
              <text x="330" y="52" textAnchor="middle" className="node-text-sub">In-Memory Cache</text>
            </g>

            {/* FastAPI Core Node */}
            <g className={`node-group ${simMode === 'miss' ? 'active-purple' : ''}`}>
              <rect x="480" y="65" width="100" height="60" className="node-rect" />
              <text x="530" y="93" textAnchor="middle" className="node-text-title">FASTAPI</text>
              <text x="530" y="108" textAnchor="middle" className="node-text-sub">App Service</text>
            </g>

            {/* Postgres Node */}
            <g className={`node-group ${simMode === 'miss' ? 'active-purple' : ''}`}>
              <rect x="680" y="65" width="100" height="60" className="node-rect" />
              <text x="730" y="93" textAnchor="middle" className="node-text-title">POSTGRESQL</text>
              <text x="730" y="108" textAnchor="middle" className="node-text-sub">Persistent Storage</text>
            </g>
          </svg>
        </div>

        <div className="arch-status-panel">
          <div className="arch-status-item">
            <span className="arch-status-lbl">Execution Node</span>
            <span className="arch-status-val">{simMode === 'hit' ? 'Edge RAM (Bypassed SQLite/Postgres)' : 'Main Engine Worker'}</span>
          </div>
          <div className="arch-status-item">
            <span className="arch-status-lbl">Latency Score</span>
            <span className="arch-status-val" style={{ color: simMode === 'hit' ? 'var(--status-success)' : 'var(--status-warning)' }}>
              {simMode === 'hit' ? '12ms' : '174ms'}
            </span>
          </div>
          <div className="arch-status-item">
            <span className="arch-status-lbl">Database Operations</span>
            <span className="arch-status-val">{simMode === 'hit' ? '0 read / 0 write' : '1 read / 1 write (Celery cache pop)'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}


/* ── Live Activity Feed ──────────────────────────────── */
function ActivityFeed() {
  const ref = useScrollReveal();
  const [activities, setActivities] = useState([
    { id: 1, type: 'click', text: 'New redirect logged from Paris — /api-docs', time: '1s ago', color: 'var(--accent-electric)' },
    { id: 2, type: 'spike', text: 'Traffic surge detected on /product-launch', time: '12s ago', color: 'var(--status-warning)' },
    { id: 3, type: 'redirect', text: 'Route resolved: /docs → docs.linkforge.infra', time: '28s ago', color: 'var(--status-success)' },
    { id: 4, type: 'cache', text: 'Redis cache pop recorded — /pricing', time: '41s ago', color: 'var(--accent-purple)' },
    { id: 5, type: 'sec', text: 'SQL Injection attempt shielded on /register', time: '1m ago', color: 'var(--status-danger)' },
  ]);

  // Generate simulated real-time events to make the platform feel ALIVE
  useEffect(() => {
    const locations = ['New York', 'Tokyo', 'London', 'San Francisco', 'Mumbai', 'Berlin', 'Singapore', 'Sydney'];
    const paths = ['/docs', '/dashboard', '/register', '/login', '/pricing', '/api/v1/auth', '/github', '/metrics'];
    const types = [
      { key: 'click', template: (loc, path) => `New redirect logged from ${loc} — ${path}`, color: 'var(--accent-electric)' },
      { key: 'redirect', template: (loc, path) => `Route resolved: ${path} → internal.engine.cluster`, color: 'var(--status-success)' },
      { key: 'cache', template: (loc, path) => `Redis cache hit recorded — ${path}`, color: 'var(--accent-purple)' },
    ];

    const timer = setInterval(() => {
      const randomLoc = locations[Math.floor(Math.random() * locations.length)];
      const randomPath = paths[Math.floor(Math.random() * paths.length)];
      const randomType = types[Math.floor(Math.random() * types.length)];

      const newEvent = {
        id: Date.now(),
        type: randomType.key,
        text: randomType.template(randomLoc, randomPath),
        time: 'Just now',
        color: randomType.color,
      };

      setActivities((prev) => {
        // Shift, update time labels of others, and append new
        const updated = prev.map((act) => {
          if (act.time === 'Just now') return { ...act, time: '3s ago' };
          if (act.time.includes('s ago')) {
            const sec = parseInt(act.time) + 4;
            return { ...act, time: `${sec}s ago` };
          }
          return act;
        });
        return [newEvent, ...updated.slice(0, 4)];
      });
    }, 4000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div ref={ref} className="reveal" style={{ marginTop: '4rem' }}>
      <div className="activity-feed">
        <div className="activity-feed__header">
          <span className="live-dot" />
          Production Activity Feed
        </div>
        {activities.map((a, i) => (
          <div key={a.id} className="activity-item" style={{ '--reveal-index': i, animation: 'fadeIn var(--duration-fast) var(--ease-out-expo) both' }}>
            <div
              className="activity-item__indicator"
              style={{
                background: a.color,
                boxShadow: `0 0 6px ${a.color}`,
              }}
            />
            <span className="activity-item__text">{a.text}</span>
            <span className="activity-item__time">{a.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}


/* ── Premium Trust Layer ─────────────────────────────── */
function TrustLayer() {
  const ref = useScrollReveal();

  const technologies = [
    { name: 'FastAPI', desc: 'Asynchronous Server' },
    { name: 'PostgreSQL', desc: 'Relational Database' },
    { name: 'Redis v7', desc: 'In-Memory Caching' },
    { name: 'Celery', desc: 'Distributed Task Queue' },
    { name: 'React 18', desc: 'UI Component Layer' },
    { name: 'Docker', desc: 'Platform Isolation' },
  ];

  return (
    <div ref={ref} className="reveal" style={{ marginTop: '5rem', borderTop: '1px solid var(--border-color)', paddingTop: '4rem' }}>
      <p style={{
        fontSize: '0.65rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        color: 'var(--text-tertiary)',
        textAlign: 'center',
        marginBottom: '1.5rem',
      }}>
        Engine Infrastructure Stack
      </p>
      
      <div className="trust-badges">
        {technologies.map((t) => (
          <div key={t.name} className="trust-badge-chip">
            <span style={{
              width: 5,
              height: 5,
              borderRadius: '50%',
              background: 'var(--text-secondary)',
              display: 'inline-block',
            }} />
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{t.name}</span>
            <span style={{ color: 'var(--text-tertiary)', fontSize: '0.6rem' }}>/ {t.desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
