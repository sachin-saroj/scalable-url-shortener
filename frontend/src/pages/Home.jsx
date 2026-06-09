/**
 * Home Page
 * ──────────
 * Landing page with URL shortening form and feature highlights.
 */

import { Link } from 'react-router-dom';
import ShortenForm from '../components/ShortenForm';
import { useAuth } from '../context/AuthContext';

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="page-container">
      {/* Hero Section */}
      <div style={{ 
        textAlign: 'center', 
        marginBottom: '4rem', 
        paddingTop: '3rem',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <h1 className="page-title" style={{ 
          fontSize: '3.5rem', 
          lineHeight: '1.1',
          marginBottom: '1.5rem',
          maxWidth: '800px',
          textTransform: 'uppercase',
          fontWeight: 900
        }}>
          Bold Connections. Forged by Humans.
        </h1>
        <p className="page-subtitle" style={{ 
          fontSize: '1.2rem', 
          maxWidth: '650px', 
          margin: '0 auto 2rem auto',
          lineHeight: '1.6',
          color: 'var(--text-secondary)'
        }}>
          We help developers and teams build high-performance, dithered routing pathways 
          independent of bloated AI agents. Minimalist links, instant redirects, and clean analytics.
        </p>
        
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '3.5rem' }}>
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn btn-primary" id="hero-dashboard-btn">
              Go to Dashboard ↗
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary" id="hero-signup-btn">
                Get Started ↗
              </Link>
              <Link to="/login" className="btn btn-secondary" id="hero-login-btn">
                Log In
              </Link>
            </>
          )}
        </div>

        {/* Hero Vector Schematic Illustration (Human meets Machine) */}
        <div style={{
          width: '100%',
          maxWidth: '750px',
          height: '280px',
          background: '#ffffff',
          border: '2px solid #000000',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-flat)',
          overflow: 'hidden',
          position: 'relative',
          marginBottom: '4rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {/* Schematic Overlay Grid */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: 'radial-gradient(#e4e4e7 1px, transparent 1px)',
            backgroundSize: '16px 16px',
            opacity: 0.8,
            pointerEvents: 'none'
          }} />

          {/* Technical Info Overlays */}
          <div style={{
            position: 'absolute',
            top: '12px',
            left: '16px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.65rem',
            textAlign: 'left',
            color: 'var(--text-tertiary)',
            pointerEvents: 'none',
            lineHeight: '1.4'
          }}>
            SYSTEM: L-FORGE.V1_INIT<br />
            TARGET: REDIS_CACHE_DEGRADED<br />
            SSRF_SHIELD: ACTIVE<br />
            STATUS: [ONLINE]
          </div>

          <div style={{
            position: 'absolute',
            bottom: '12px',
            right: '16px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.65rem',
            textAlign: 'right',
            color: 'var(--text-tertiary)',
            pointerEvents: 'none',
            lineHeight: '1.4'
          }}>
            COORD: 40.7128° N, 74.0060° W<br />
            LATENCY: 14ms (EDGE)<br />
            [NO_LARGE_LANGUAGE_MODELS_USED]
          </div>

          {/* SVG Hands Schematic Drawing */}
          <svg 
            width="100%" 
            height="100%" 
            viewBox="0 0 700 260" 
            style={{ position: 'relative', zIndex: 1 }}
          >
            {/* Horizontal Axis Line */}
            <line x1="50" y1="130" x2="650" y2="130" stroke="#e4e4e7" strokeWidth="1" strokeDasharray="4 4" />
            
            {/* Left Hand: Robotic Mechanical Arm */}
            <g transform="translate(10, 0)">
              {/* Arm structure */}
              <line x1="40" y1="130" x2="160" y2="130" stroke="#000000" strokeWidth="4" />
              <rect x="160" y="105" width="45" height="50" fill="none" stroke="#000000" strokeWidth="2" />
              <text x="165" y="120" fontSize="8" fontFamily="var(--font-mono)">ARM_V1</text>
              <circle cx="182.5" cy="130" r="10" fill="none" stroke="#000000" strokeWidth="2" strokeDasharray="2 2" />
              
              {/* Jointed metallic fingers */}
              {/* Finger 1 (Bottom Thumb) */}
              <path d="M 205 145 L 235 160 L 265 155" fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="235" cy="160" r="3" fill="#000000" />
              
              {/* Finger 2 (Pointer) */}
              <path d="M 205 120 L 250 115 L 290 120 L 315 125" fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="250" cy="115" r="3" fill="#000000" />
              <circle cx="290" cy="120" r="3" fill="#000000" />
              <text x="235" y="105" fontSize="7" fontFamily="var(--font-mono)" opacity="0.6">ACTUATOR_02</text>
              
              {/* Finger 3 (Middle) */}
              <path d="M 205 130 L 260 130 L 285 135" fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="260" cy="130" r="3" fill="#000000" />
            </g>

            {/* Spark/Connection Node in Center */}
            <g transform="translate(340, 126)">
              {/* Target rings */}
              <circle cx="0" cy="0" r="12" fill="none" stroke="#000000" strokeWidth="1" strokeDasharray="3 3" />
              <circle cx="0" cy="0" r="6" fill="#000000" />
              <line x1="-18" y1="0" x2="18" y2="0" stroke="#000000" strokeWidth="1" />
              <line x1="0" y1="-18" x2="0" y2="18" stroke="#000000" strokeWidth="1" />
              <path d="M -8 -8 L 8 8" stroke="#000000" strokeWidth="1" />
              <path d="M 8 -8 L -8 8" stroke="#000000" strokeWidth="1" />
              <text x="12" y="-12" fontSize="8" fontFamily="var(--font-mono)" fontWeight="bold">LINK_NODE</text>
            </g>

            {/* Right Hand: Human Outline */}
            <g transform="translate(0, 0)">
              {/* Human arm line */}
              <path d="M 640 145 C 590 145 540 135 500 130" fill="none" stroke="#000000" strokeWidth="2" />
              <path d="M 640 115 C 600 115 560 120 520 125" fill="none" stroke="#000000" strokeWidth="2" />
              
              {/* Human fingers */}
              {/* Index Finger reaching out */}
              <path d="M 500 130 C 460 125 410 122 363 125" fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" />
              
              {/* Middle Finger curled down slightly */}
              <path d="M 500 133 C 470 135 440 145 425 145" fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" />
              
              {/* Ring Finger */}
              <path d="M 500 136 C 475 142 450 155 435 155" fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" />
              
              {/* Thumb */}
              <path d="M 510 125 C 490 110 460 102 445 105" fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" />
              
              <text x="470" y="168" fontSize="7" fontFamily="var(--font-mono)" opacity="0.6">ANALOG_INPUT</text>
            </g>
          </svg>
        </div>
      </div>

      {/* Shorten Form */}
      <ShortenForm />

      {/* Feature Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.5rem',
        marginTop: '5rem',
      }}>
        <FeatureCard
          icon="⚡"
          title="Sub-50ms Routing"
          desc="Synchronous database bypass with high-concurrency Redis caching. Built to process massive click loads instantly."
        />
        <FeatureCard
          icon="📊"
          title="Dithered Metrics"
          desc="Pure, precise analytics logging. Detailed tracking of country codes, referrers, and user agents in real time."
        />
        <FeatureCard
          icon="🛡️"
          title="Industrial Security"
          desc="SSRF shielding, malicious URL checks, strict rate limiters, and clean JSON Web Token authorization schemas."
        />
        <FeatureCard
          icon="🏷️"
          title="Custom Aliases"
          desc="Claim specific, high-recall string codes for custom campaigns, eliminating generic auto-increment hashes."
        />
        <FeatureCard
          icon="📱"
          title="Static QR Generation"
          desc="Auto-generated QR vectors for reliable mobile scanning, print campaigns, and cross-channel physical endpoints."
        />
        <FeatureCard
          icon="⏰"
          title="Strict Expiration"
          desc="Configure exact campaign life spans with automated deletion of legacy routes, maintaining database efficiency."
        />
      </div>

      {/* Tech Stack Index */}
      <div style={{
        textAlign: 'center',
        marginTop: '6rem',
        padding: '3rem 2rem',
        borderTop: '2px solid #000000',
        background: '#ffffff',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-flat)',
      }}>
        <p style={{ 
          marginBottom: '1.5rem', 
          fontWeight: 700, 
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: 'var(--text-primary)',
          fontSize: '0.9rem'
        }}>
          LinkForge Tech Stack Matrix
        </p>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '1rem',
          flexWrap: 'wrap',
        }}>
          {['FastAPI', 'PostgreSQL', 'Redis_v7', 'Celery_Workers', 'React_18', 'Vite_6', 'SQLite_Fallbacks'].map((tech) => (
            <span key={tech} style={{
              padding: '0.5rem 1rem',
              background: '#f4f4f7',
              border: '2px solid #000000',
              borderRadius: 'var(--radius-pill)',
              fontSize: '0.75rem',
              fontWeight: 700,
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-primary)',
            }}>
              {tech}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="card" style={{ cursor: 'default' }}>
      <div style={{ fontSize: '2.25rem', marginBottom: '1rem' }}>{icon}</div>
      <h3 style={{
        fontSize: '1.2rem',
        fontWeight: 700,
        textTransform: 'uppercase',
        marginBottom: '0.75rem',
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-brand)'
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '0.9rem',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
      }}>
        {desc}
      </p>
    </div>
  );
}
