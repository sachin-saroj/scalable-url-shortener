import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import useScrollReveal from '../utils/useScrollReveal';
import AnimatedHeading from '../components/AnimatedHeading';
import FadeIn from '../components/FadeIn';

export default function Platform() {
  const { isAuthenticated } = useAuth();
  const heroRef = useRef(null);

  return (
    <div className="w-full min-h-screen bg-black text-white selection:bg-white/10 selection:text-white relative">
      
      {/* Fixed Background Video */}
      <div className="fixed inset-0 -z-10 w-full h-full">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4"
        />
      </div>

      {/* ── HERO SECTION ── */}
      <section 
        className="relative w-full min-h-screen flex flex-col justify-end px-6 md:px-12 lg:px-16 pb-12 lg:pb-16"
        ref={heroRef}
      >
        <div className="w-full lg:grid lg:grid-cols-2 lg:items-end gap-12 z-10">
          
          {/* Left Column: Main Content */}
          <div className="flex flex-col items-start">
            <AnimatedHeading 
              text={"Built for scale.\nEngineered for uptime."}
              className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4 text-white leading-tight tracking-tight"
              style={{ letterSpacing: '-0.04em' }}
            />

            <FadeIn delay={800} duration={1000}>
              <p className="text-base md:text-lg text-gray-300 mb-5 max-w-[520px]">
                FastAPI async API, PostgreSQL persistence, Redis cache, Celery workers — production URL shortener stack.
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
                    Open Console
                  </Link>
                )}
                <a href="#architecture" className="liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:!text-black transition-colors no-underline text-center">
                  View Architecture
                </a>
              </div>
            </FadeIn>
          </div>

          {/* Right Column: Tag */}
          <div className="flex items-end justify-start lg:justify-end mt-8 lg:mt-0">
            <FadeIn delay={1400} duration={1000}>
              <div className="liquid-glass border border-white/20 px-6 py-3 rounded-xl">
                <span className="text-lg md:text-xl lg:text-2xl font-light text-white">
                  FastAPI · Redis · PostgreSQL · Celery
                </span>
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── LOWER CONTENT WRAPPER (Liquid Glass Styled) ── */}
      <div className="w-full max-w-[1200px] mx-auto px-6 md:px-12 lg:px-16 py-12 relative z-10">
        
        {/* ── Feature Bento Grid ── */}
        <FeatureGrid />

        {/* ── Interactive Architecture Visualizer ── */}
        <ArchitectureSection />

        {/* ── Live Activity Feed ── */}
        <ActivityFeed />

        {/* ── Trust Layer ── */}
        <TrustLayer />
      </div>

    </div>
  );
}

/* ── Feature Bento Grid ── */
function FeatureGrid() {
  const ref = useScrollReveal();

  return (
    <div
      ref={ref}
      className="reveal"
      style={{ marginTop: '4rem' }}
    >
      <p style={{
        fontSize: '0.65rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        color: '#9ca3af',
        marginBottom: '2rem',
        textAlign: 'center',
      }}>
        Platform Engine Capabilities
      </p>
      
      <div className="bento-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        
        {/* Large Card: Spans 3 columns */}
        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all" style={{ gridColumn: 'span 3' }}>
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#ffffff' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </div>
          <h3 className="text-xl font-normal text-white mb-2">Sub-50ms Global Routing</h3>
          <p className="text-sm text-gray-300 leading-relaxed max-w-[640px]">
            Synchronous database bypass utilizing high-concurrency Redis caching layers. Active routes resolve near-instantaneously at the edge, offering production-grade throughput with zero cold-start delay.
          </p>
        </div>

        {/* Medium Card: Spans 1 column */}
        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#ffffff' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">Analytics</h3>
          <p className="text-xs text-gray-300 leading-relaxed">Detailed request logging capturing visitor locations, referrers, and system performance telemetry.</p>
        </div>

        {/* Row 2 */}
        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(52, 211, 153, 0.1)', color: '#34d399' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">Security Shield</h3>
          <p className="text-xs text-gray-300 leading-relaxed">SSRF prevention, host filtering, malicious redirect prevention, and active JWT path authentication.</p>
        </div>

        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(251, 191, 36, 0.1)', color: '#fbbf24' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">Custom Aliases</h3>
          <p className="text-xs text-gray-300 leading-relaxed">Override generic hashes with clean, branded path parameters to sustain routing consistency.</p>
        </div>

        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(96, 165, 250, 0.1)', color: '#60a5fa' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><rect x="7" y="7" width="3" height="3"/><rect x="14" y="7" width="3" height="3"/><rect x="7" y="14" width="3" height="3"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">QR Engine</h3>
          <p className="text-xs text-gray-300 leading-relaxed">Instantly compile high-definition QR vector blocks corresponding to active routing destinations.</p>
        </div>

        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(248, 113, 113, 0.1)', color: '#f87171' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">Expiration</h3>
          <p className="text-xs text-gray-300 leading-relaxed">Configure exact Campaign TTL limits to automatically flush inactive routes from database nodes.</p>
        </div>

        {/* Row 3 */}
        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#ffffff' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">Active Caching</h3>
          <p className="text-xs text-gray-300 leading-relaxed">Custom HTTP headers and cache controls tailored for immediate edge replication.</p>
        </div>

        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#ffffff' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">Async Workers</h3>
          <p className="text-xs text-gray-300 leading-relaxed">Celery task queues process incoming analytics off the critical path, keeping redirects fast.</p>
        </div>

        <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8 hover:border-white/40 transition-all" style={{ gridColumn: 'span 2' }}>
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-5" style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#ffffff' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          </div>
          <h3 className="text-lg font-normal text-white mb-2">Rate Limiting Protection</h3>
          <p className="text-xs text-gray-300 leading-relaxed">Adaptive token-bucket rate limiters defend downstream services against DDoS surges and bot crawlers, preserving network balance.</p>
        </div>

      </div>
    </div>
  );
}

/* ── Interactive Architecture Visualizer ── */
function ArchitectureSection() {
  const ref = useScrollReveal();
  const [simMode, setSimMode] = useState('hit'); // 'hit' | 'miss'

  return (
    <div ref={ref} className="reveal arch-section" id="architecture" style={{ marginTop: '6rem' }}>
      <p style={{
        fontSize: '0.65rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        color: '#9ca3af',
        textAlign: 'center',
        marginBottom: '0.5rem',
      }}>
        Interactive Architecture
      </p>
      
      <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8">
        <div className="arch-visualizer__header">
          <div className="arch-visualizer__title">
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: simMode === 'hit' ? '#ffffff' : '#9ca3af',
              boxShadow: simMode === 'hit' ? '0 0 8px #ffffff' : '0 0 8px #9ca3af',
              display: 'inline-block',
            }} />
            Execution Flow Simulation
          </div>
          <div className="arch-visualizer__controls">
            <button
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${simMode === 'hit' ? 'bg-white text-black border-white' : 'bg-transparent text-white border-white/20 hover:bg-white/10'}`}
              onClick={() => setSimMode('hit')}
            >
              Cache Hit (Sub-50ms)
            </button>
            <button
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${simMode === 'miss' ? 'bg-white text-black border-white' : 'bg-transparent text-white border-white/20 hover:bg-white/10'}`}
              onClick={() => setSimMode('miss')}
            >
              Cache Miss (Write/DB Query)
            </button>
          </div>
        </div>

        <div className="arch-svg-container">
          <svg viewBox="0 0 800 200" className="architecture-svg">
            
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

            {/* Cache Miss Path */}
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
            
            {simMode === 'miss' && (
              <path
                className="connection-line active-alt flow-dot"
                d="M 580 95 L 680 95"
                style={{ animationDirection: 'reverse' }}
              />
            )}

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
            <g className={`node-group ${simMode === 'hit' ? 'active-blue' : 'active-purple'}`}>
              <rect x="40" y="65" width="120" height="60" className="node-rect" />
              <text x="100" y="93" textAnchor="middle" className="node-text-title">EDGE ROUTING</text>
              <text x="100" y="108" textAnchor="middle" className="node-text-sub">LinkForge DNS</text>
            </g>

            <g className={`node-group ${simMode === 'hit' ? 'active-blue' : 'active'}`}>
              <rect x="280" y="15" width="100" height="50" className="node-rect" />
              <text x="330" y="40" textAnchor="middle" className="node-text-title">REDIS V7</text>
              <text x="330" y="52" textAnchor="middle" className="node-text-sub">In-Memory Cache</text>
            </g>

            <g className={`node-group ${simMode === 'miss' ? 'active-purple' : ''}`}>
              <rect x="480" y="65" width="100" height="60" className="node-rect" />
              <text x="530" y="93" textAnchor="middle" className="node-text-title">FASTAPI</text>
              <text x="530" y="108" textAnchor="middle" className="node-text-sub">App Service</text>
            </g>

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
            <span className="arch-status-val" style={{ color: simMode === 'hit' ? '#34d399' : '#fbbf24' }}>
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

/* ── Live Activity Feed ── */
function ActivityFeed() {
  const ref = useScrollReveal();
  const [activities, setActivities] = useState([
    { id: 1, type: 'click', text: 'New redirect logged from Paris — /api-docs', time: '1s ago', color: '#ffffff' },
    { id: 2, type: 'spike', text: 'Traffic surge detected on /product-launch', time: '12s ago', color: '#fbbf24' },
    { id: 3, type: 'redirect', text: 'Route resolved: /docs → docs.linkforge.infra', time: '28s ago', color: '#34d399' },
    { id: 4, type: 'cache', text: 'Redis cache pop recorded — /pricing', time: '41s ago', color: '#9ca3af' },
    { id: 5, type: 'sec', text: 'SQL Injection attempt shielded on /register', time: '1m ago', color: '#f87171' },
  ]);

  useEffect(() => {
    const locations = ['New York', 'Tokyo', 'London', 'San Francisco', 'Mumbai', 'Berlin', 'Singapore', 'Sydney'];
    const paths = ['/docs', '/dashboard', '/register', '/login', '/pricing', '/api/v1/auth', '/github', '/metrics'];
    const types = [
      { key: 'click', template: (loc, path) => `New redirect logged from ${loc} — ${path}`, color: '#ffffff' },
      { key: 'redirect', template: (loc, path) => `Route resolved: ${path} → internal.engine.cluster`, color: '#34d399' },
      { key: 'cache', template: (loc, path) => `Redis cache hit recorded — ${path}`, color: '#9ca3af' },
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
      <div className="liquid-glass border border-white/20 rounded-xl p-6 md:p-8">
        <div className="activity-feed__header mb-4 flex items-center gap-2 text-sm font-semibold tracking-wide text-white">
          <span className="live-dot w-2 h-2 rounded-full bg-green-500 animate-ping inline-block" />
          Production Activity Feed
        </div>
        <div className="flex flex-col gap-3">
          {activities.map((a, i) => (
            <div key={a.id} className="flex items-center justify-between text-xs border-b border-white/5 pb-2" style={{ '--reveal-index': i, animation: 'fadeIn 280ms var(--ease-out-expo) both' }}>
              <div className="flex items-center gap-2">
                <div
                  className="w-1.5 h-1.5 rounded-full"
                  style={{
                    background: a.color,
                    boxShadow: `0 0 6px ${a.color}`,
                  }}
                />
                <span className="text-gray-300">{a.text}</span>
              </div>
              <span className="text-gray-500 font-mono">{a.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Premium Trust Layer ── */
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
    <div ref={ref} className="reveal" style={{ marginTop: '5rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '4rem' }}>
      <p style={{
        fontSize: '0.65rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        color: '#9ca3af',
        textAlign: 'center',
        marginBottom: '1.5rem',
      }}>
        Engine Infrastructure Stack
      </p>
      
      <div className="flex flex-wrap gap-4 justify-center">
        {technologies.map((t) => (
          <div key={t.name} className="liquid-glass border border-white/20 px-4 py-2 rounded-full flex items-center gap-2 text-xs">
            <span style={{
              width: 5,
              height: 5,
              borderRadius: '50%',
              background: '#ffffff',
              display: 'inline-block',
            }} />
            <span className="font-semibold text-white">{t.name}</span>
            <span className="text-gray-400 font-light">/ {t.desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
