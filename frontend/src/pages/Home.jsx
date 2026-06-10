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
            fontFamily: 'var(--font-brand)',
            fontSize: '4.5rem', 
            lineHeight: '1.05',
            marginBottom: '1.5rem',
            fontWeight: 400,
            fontStyle: 'italic',
            letterSpacing: '-0.03em',
            textTransform: 'none'
          }}>
            Bold connections.<br />
            Forged by humans.
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
              <Link to="/dashboard" className="btn btn-primary" id="hero-dashboard-btn" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                Go to Dashboard
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary" id="hero-signup-btn" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  Get Started
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
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
          icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>}
          title="Sub-50ms Routing"
          desc="Synchronous database bypass with high-concurrency Redis caching. Built to process massive click loads instantly."
          badgeColor="var(--status-danger-bg)"
          badgeTextColor="var(--status-danger)"
        />
        <FeatureCard
          icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>}
          title="Dithered Metrics"
          desc="Pure, precise analytics logging. Detailed tracking of country codes, referrers, and user agents in real time."
          badgeColor="var(--status-info-bg)"
          badgeTextColor="var(--status-info)"
        />
        <FeatureCard
          icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>}
          title="Industrial Security"
          desc="SSRF shielding, malicious URL checks, strict rate limiters, and clean JSON Web Token authorization schemas."
          badgeColor="var(--status-success-bg)"
          badgeTextColor="var(--status-success)"
        />
        <FeatureCard
          icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>}
          title="Custom Aliases"
          desc="Claim specific, high-recall string codes for custom campaigns, eliminating generic auto-increment hashes."
          badgeColor="var(--status-warning-bg)"
          badgeTextColor="var(--status-warning)"
        />
        <FeatureCard
          icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>}
          title="Static QR Generation"
          desc="Auto-generated QR vectors for reliable mobile scanning, print campaigns, and cross-channel physical endpoints."
          badgeColor="var(--status-info-bg)"
          badgeTextColor="var(--status-info)"
        />
        <FeatureCard
          icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>}
          title="Strict Expiration"
          desc="Configure exact campaign life spans with automated deletion of legacy routes, maintaining database efficiency."
          badgeColor="var(--status-danger-bg)"
          badgeTextColor="var(--status-danger)"
        />
      </div>

      {/* Tech Stack Index */}
      <div style={{
        textAlign: 'center',
        marginTop: '6rem',
        padding: '3rem 2rem',
        borderTop: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-subtle)',
      }}>
        <p style={{ 
          marginBottom: '1.5rem', 
          fontWeight: 600, 
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          color: 'var(--text-secondary)',
          fontSize: '0.8rem'
        }}>
          LinkForge Tech Stack Matrix
        </p>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '0.75rem',
          flexWrap: 'wrap',
        }}>
          {['FastAPI', 'PostgreSQL', 'Redis_v7', 'Celery_Workers', 'React_18', 'Vite_6', 'SQLite_Fallbacks'].map((tech) => (
            <span key={tech} style={{
              padding: '0.4rem 0.85rem',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-pill)',
              fontSize: '0.75rem',
              fontWeight: 500,
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-secondary)',
            }}>
              {tech}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, desc, badgeColor, badgeTextColor }) {
  return (
    <div className="card" style={{ cursor: 'default' }}>
      <div style={{
        width: '36px',
        height: '36px',
        borderRadius: '6px',
        background: badgeColor,
        color: badgeTextColor,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '1.25rem'
      }}>
        {icon}
      </div>
      <h3 style={{
        fontSize: '1.05rem',
        fontWeight: 600,
        marginBottom: '0.5rem',
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-family)'
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '0.85rem',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
      }}>
        {desc}
      </p>
    </div>
  );
}
