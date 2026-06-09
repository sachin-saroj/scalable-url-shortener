/**
 * Navbar Component
 * ─────────────────
 */

import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'nav-link active' : 'nav-link';

  return (
    <nav className="navbar" id="main-navbar">
      <Link to="/" className="navbar-brand">
        LinkForge®
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
              fontSize: '0.8rem',
              fontFamily: 'var(--font-mono)',
              fontWeight: 700,
              padding: '0 0.5rem',
            }}>
              [{user?.username?.toUpperCase()}]
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
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
