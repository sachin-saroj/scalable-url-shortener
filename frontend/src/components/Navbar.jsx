/**
 * Navbar Component — LinkForge V3
 * ─────────────────────────────────
 * Premium navigation with frosted glass, editorial brand mark,
 * and technical user badge.
 */

import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'nav-link active' : 'nav-link';

  return (
    <nav className="navbar" id="main-navbar" role="navigation" aria-label="Main navigation">
      <Link to="/" className="navbar-brand">
        {/* Route icon */}
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.7 }}>
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
        LinkForge
      </Link>

      <div className="navbar-links">
        <Link to="/" className={isActive('/')}>
          <span>Home</span>
        </Link>

        {isAuthenticated ? (
          <>
            <Link to="/dashboard" className={isActive('/dashboard')}>
              <span>Dashboard</span>
            </Link>
            <span style={{
              color: 'var(--text-tertiary)',
              fontSize: '0.65rem',
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              padding: '0.25rem 0.6rem',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              letterSpacing: '0.02em',
            }}>
              {user?.username}
            </span>
            <button className="nav-link" onClick={logout} id="logout-btn">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className={isActive('/login')}>
              <span>Login</span>
            </Link>
            <Link to="/register" className="btn btn-primary btn-sm" id="register-nav-btn">
              Get Started
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
