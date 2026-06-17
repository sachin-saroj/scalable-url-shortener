import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Platform.css';

export default function Platform() {
  const { isAuthenticated } = useAuth();
  const [url, setUrl] = useState('');
  const [alias, setAlias] = useState('');
  const [mode, setMode] = useState('hit');

  return (
    <div className="platform">
      
      {/* Subdued Background */}
      <div className="platform-bg">
        <video autoPlay loop muted playsInline className="bg-video">
          <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4" />
        </video>
        <div className="bg-overlay" />
      </div>

      {/* Split Navigation */}
      <header className="header">
        <Link to="/" className="logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
          </svg>
          LinkForge
        </Link>

        <nav className="nav-pill">
          <a href="#shorten" className="nav-item active">Shorten</a>
          <a href="#analytics" className="nav-item">Analytics</a>
          <a href="#architecture" className="nav-item">Architecture</a>
        </nav>

        <div className="header-actions">
          <Link to="/login" className="action-link">Sign In</Link>
          <Link to={isAuthenticated ? "/dashboard" : "/register"} className="action-btn">
            {isAuthenticated ? 'Dashboard' : 'Start Building'}
          </Link>
        </div>
      </header>

      {/* Product Hero */}
      <section className="product-hero">
        <div className="hero-container">
          
          <div className="hero-header">
            <h1 className="hero-title">Create short links at global scale</h1>
            <p className="hero-subtitle">Sub-50ms redirects. 99.99% uptime. Production-ready infrastructure.</p>
          </div>

          {/* Product Card - The Hero */}
          <div className="product-card">
            <div className="card-body">
              <div className="form-group">
                <label className="form-label">Destination URL</label>
                <input 
                  type="url" 
                  className="form-input" 
                  placeholder="https://example.com/your-long-url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Custom alias (optional)</label>
                  <div className="input-prefix">
                    <span className="prefix-text">lnk.ge/</span>
                    <input 
                      type="text" 
                      className="form-input-inline" 
                      placeholder="my-link"
                      value={alias}
                      onChange={(e) => setAlias(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Expiration</label>
                  <select className="form-select">
                    <option>Never</option>
                    <option>1 hour</option>
                    <option>1 day</option>
                    <option>1 week</option>
                    <option>1 month</option>
                  </select>
                </div>
              </div>

              <button className="submit-btn">
                <span>Shorten URL</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </button>
            </div>
          </div>

          {/* Live Stats */}
          <div className="stats-bar">
            <div className="stat">
              <span className="stat-value">12ms</span>
              <span className="stat-label">Avg latency</span>
            </div>
            <div className="stat-sep" />
            <div className="stat">
              <span className="stat-value">99.99%</span>
              <span className="stat-label">Uptime</span>
            </div>
            <div className="stat-sep" />
            <div className="stat">
              <span className="stat-value">50M+</span>
              <span className="stat-label">Daily requests</span>
            </div>
            <div className="stat-sep" />
            <div className="stat">
              <span className="stat-value">28</span>
              <span className="stat-label">Edge nodes</span>
            </div>
          </div>

        </div>
      </section>

      {/* Bento Grid Features */}
      <section className="features-bento">
        <div className="bento-container">
          
          <div className="bento-header">
            <span className="bento-label">Platform</span>
            <h2 className="bento-title">Enterprise infrastructure</h2>
          </div>

          <div className="bento-grid">
            
            {/* Large Card */}
            <div className="bento-item large">
              <div className="item-icon blue">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
              </div>
              <h3 className="item-title">Edge routing</h3>
              <p className="item-desc">Redis-powered cache layers deliver sub-50ms redirects across 28 global edge nodes with zero cold starts.</p>
              <div className="item-accent blue-accent" />
            </div>

            {/* Medium Card */}
            <div className="bento-item medium">
              <div className="item-icon green">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
              <h3 className="item-title">Security</h3>
              <p className="item-desc">SSRF prevention and rate limiting.</p>
            </div>

            {/* Tall Card */}
            <div className="bento-item tall">
              <div className="item-icon purple">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="20" x2="18" y2="10"/>
                  <line x1="12" y1="20" x2="12" y2="4"/>
                  <line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
              </div>
              <h3 className="item-title">Analytics</h3>
              <p className="item-desc">Real-time request logging with geolocation and device tracking.</p>
              <div className="mini-chart">
                <div className="chart-bar" style={{height: '40%'}}></div>
                <div className="chart-bar" style={{height: '70%'}}></div>
                <div className="chart-bar" style={{height: '50%'}}></div>
                <div className="chart-bar" style={{height: '90%'}}></div>
                <div className="chart-bar" style={{height: '60%'}}></div>
                <div className="chart-bar" style={{height: '80%'}}></div>
              </div>
            </div>

            {/* Small Cards */}
            <div className="bento-item small">
              <div className="item-icon amber">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
                  <line x1="7" y1="7" x2="7.01" y2="7"/>
                </svg>
              </div>
              <h3 className="item-title">Custom aliases</h3>
            </div>

            <div className="bento-item small">
              <div className="item-icon cyan">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
              </div>
              <h3 className="item-title">QR codes</h3>
            </div>

            {/* Wide Card */}
            <div className="bento-item wide">
              <div className="item-icon red">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </div>
              <h3 className="item-title">Async workers</h3>
              <p className="item-desc">Celery task queues process analytics off the critical path.</p>
            </div>

          </div>
        </div>
      </section>

      {/* Compact Architecture */}
      <section className="architecture-panel" id="architecture">
        <div className="panel-container">
          
          <div className="panel-header">
            <h3 className="panel-title">Request flow</h3>
            <div className="flow-toggle">
              <button 
                className={`toggle-btn ${mode === 'hit' ? 'active' : ''}`}
                onClick={() => setMode('hit')}
              >
                Cache hit
              </button>
              <button 
                className={`toggle-btn ${mode === 'miss' ? 'active' : ''}`}
                onClick={() => setMode('miss')}
              >
                Cache miss
              </button>
            </div>
          </div>

          <div className="flow-diagram">
            <svg viewBox="0 0 600 100" className="diagram-svg">
              <path d="M 80 50 L 180 50" className={`line ${mode === 'hit' ? 'active' : 'dim'}`} />
              <path d="M 240 50 L 80 50" className={`line ${mode === 'hit' ? 'active' : 'dim'}`} />
              <path d="M 80 50 L 280 50" className={`line ${mode === 'miss' ? 'active-alt' : 'dim'}`} />
              <path d="M 340 50 L 440 50" className={`line ${mode === 'miss' ? 'active-alt' : 'dim'}`} />
              <path d="M 280 50 L 240 30" className={`line ${mode === 'miss' ? 'active-alt' : 'dim'}`} />

              <g className={mode === 'hit' ? 'node-on' : 'node-off'}>
                <rect x="10" y="35" width="60" height="30" rx="4" className="node-rect" />
                <text x="40" y="54" className="node-text">Edge</text>
              </g>

              <g className={mode === 'hit' ? 'node-on' : 'node-off'}>
                <rect x="180" y="20" width="60" height="25" rx="4" className="node-rect" />
                <text x="210" y="37" className="node-text">Redis</text>
              </g>

              <g className={mode === 'miss' ? 'node-on' : 'node-off'}>
                <rect x="280" y="35" width="60" height="30" rx="4" className="node-rect" />
                <text x="310" y="54" className="node-text">API</text>
              </g>

              <g className={mode === 'miss' ? 'node-on' : 'node-off'}>
                <rect x="440" y="35" width="60" height="30" rx="4" className="node-rect" />
                <text x="470" y="54" className="node-text">DB</text>
              </g>
            </svg>
          </div>

          <div className="flow-stats">
            <div className="flow-stat">
              <span className="flow-stat-val">{mode === 'hit' ? '12ms' : '174ms'}</span>
              <span className="flow-stat-lab">Latency</span>
            </div>
            <div className="flow-stat">
              <span className="flow-stat-val">99.99%</span>
              <span className="flow-stat-lab">Cache hit rate</span>
            </div>
            <div className="flow-stat">
              <span className="flow-stat-val">{mode === 'hit' ? '0' : '2'}</span>
              <span className="flow-stat-lab">DB operations</span>
            </div>
          </div>

        </div>
      </section>

      {/* Simple Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="tech-stack">
            <span className="tech">FastAPI</span>
            <span className="tech">PostgreSQL</span>
            <span className="tech">Redis</span>
            <span className="tech">Celery</span>
            <span className="tech">React</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
