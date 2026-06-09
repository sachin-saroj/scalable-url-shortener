/**
 * Home Page
 * ──────────
 * Landing page with URL shortening form and feature highlights.
 */

import { Link } from 'react-router-dom';
import ShortenForm from '../components/ShortenForm';
import ScribbleSilhouette from '../components/ScribbleSilhouette';
import { useAuth } from '../context/AuthContext';

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="page-container">
      {/* Hero Section */}
      <div 
        className="hero-grid"
        style={{ 
          display: 'flex',
          flexDirection: 'row',
          flexWrap: 'wrap',
          gap: '3rem',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '5rem', 
          paddingTop: '3rem',
        }}
      >
        {/* Left Column: Text & CTA */}
        <div style={{ 
          flex: '1 1 450px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          textAlign: 'left'
        }}>
          <h1 className="page-title" style={{ 
            fontSize: '3.5rem', 
            lineHeight: '1.05',
            marginBottom: '1.5rem',
            textTransform: 'uppercase',
            fontWeight: 900,
            letterSpacing: '-0.02em'
          }}>
            Bold Connections.<br />
            Forged by Humans.
          </h1>
          <p className="page-subtitle" style={{ 
            fontSize: '1.25rem', 
            marginBottom: '2.5rem',
            lineHeight: '1.6',
            color: 'var(--text-secondary)'
          }}>
            We help developers and teams build high-performance, dithered routing pathways 
            independent of bloated AI agents. Minimalist links, instant redirects, and clean analytics.
          </p>
          
          <div style={{ display: 'flex', gap: '1rem' }}>
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
        </div>

        {/* Right Column: Interactive Scribble Silhouette Video Doodle Reference */}
        <div style={{
          flex: '0 0 auto',
          margin: '0 auto',
          position: 'relative',
        }}>
          {/* Tech overlay wrapper */}
          <div style={{
            position: 'absolute',
            top: '-20px',
            left: '-20px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.6rem',
            color: 'var(--text-tertiary)',
            pointerEvents: 'none',
            lineHeight: '1.4',
            zIndex: 4,
          }}>
            REF_SYS: P-04WKkhA132<br />
            MODEL: HUMAN_SOUL_V1.0
          </div>
          
          <div style={{
            position: 'absolute',
            bottom: '-20px',
            right: '-20px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.6rem',
            color: 'var(--text-tertiary)',
            pointerEvents: 'none',
            lineHeight: '1.4',
            textAlign: 'right',
            zIndex: 4,
          }}>
            SENSORS: RESPONSIVE<br />
            [NO_BOTS_ALLOWED]
          </div>

          <ScribbleSilhouette />
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
