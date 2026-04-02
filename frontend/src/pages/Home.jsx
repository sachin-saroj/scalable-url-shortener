/**
 * Home Page
 * ──────────
 * Landing page with URL shortening form and feature highlights.
 */

import ShortenForm from '../components/ShortenForm';

export default function Home() {
  return (
    <div className="page-container">
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: '3rem', paddingTop: '2rem' }}>
        <h1 className="page-title" style={{ fontSize: '3rem', marginBottom: '1rem' }}>
          Shorten. Track. Scale.
        </h1>
        <p className="page-subtitle" style={{ fontSize: '1.15rem', maxWidth: '600px', margin: '0 auto' }}>
          Transform long URLs into powerful short links with real-time analytics,
          QR codes, and enterprise-grade performance.
        </p>
      </div>

      {/* Shorten Form */}
      <ShortenForm />

      {/* Feature Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.25rem',
        marginTop: '4rem',
      }}>
        <FeatureCard
          icon="⚡"
          title="Lightning Fast"
          desc="Sub-50ms redirects powered by Redis caching. Your users never wait."
        />
        <FeatureCard
          icon="📊"
          title="Deep Analytics"
          desc="Track clicks, unique visitors, geo-location, devices, and referrers in real time."
        />
        <FeatureCard
          icon="🔐"
          title="Secure by Design"
          desc="Rate limiting, malicious URL detection, JWT auth, and SSRF prevention built-in."
        />
        <FeatureCard
          icon="🏷️"
          title="Custom Aliases"
          desc="Brand your links with memorable custom short codes like /my-brand."
        />
        <FeatureCard
          icon="📱"
          title="QR Codes"
          desc="Auto-generated QR codes for every short link. Perfect for print & mobile."
        />
        <FeatureCard
          icon="⏰"
          title="Link Expiry"
          desc="Set auto-expiry on links. Perfect for campaigns, events, and time-sensitive content."
        />
      </div>

      {/* Tech Stack */}
      <div style={{
        textAlign: 'center',
        marginTop: '4rem',
        padding: '2rem',
        color: 'var(--text-tertiary)',
        fontSize: '0.85rem',
      }}>
        <p style={{ marginBottom: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          Built with production-grade architecture
        </p>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '1.5rem',
          flexWrap: 'wrap',
        }}>
          {['FastAPI', 'PostgreSQL', 'Redis', 'Celery', 'React', 'Docker'].map((tech) => (
            <span key={tech} style={{
              padding: '0.35rem 0.85rem',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.8rem',
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

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="card" style={{ cursor: 'default' }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{icon}</div>
      <h3 style={{
        fontSize: '1.05rem',
        fontWeight: 700,
        marginBottom: '0.5rem',
        color: 'var(--text-primary)',
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '0.875rem',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
      }}>
        {desc}
      </p>
    </div>
  );
}
