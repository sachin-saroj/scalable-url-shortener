/**
 * Register Page — LinkForge V3
 * ─────────────────────────────
 * Premium registration with password strength indicator.
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  // Password strength calculation
  function getPasswordStrength(pw) {
    if (!pw) return { level: 0, label: '' };
    let score = 0;
    if (pw.length >= 8) score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;

    if (score <= 1) return { level: 1, label: 'Weak', color: 'var(--status-danger)' };
    if (score <= 3) return { level: 2, label: 'Fair', color: 'var(--status-warning)' };
    return { level: 3, label: 'Strong', color: 'var(--status-success)' };
  }

  const strength = getPasswordStrength(password);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (!email || !username || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      const result = await register(email, username, password);
      if (result.ok) {
        navigate('/dashboard');
      } else {
        setError(result.data.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  }

  return (
    <div className="auth-page">
      <div className="auth-card" id="register-card">
        <h2 className="auth-title">Create Account</h2>
        <p className="auth-subtitle">Start routing in seconds</p>

        <form className="auth-form" onSubmit={handleSubmit} id="register-form">
          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              id="reg-email"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-username">Username</label>
            <input
              type="text"
              className="form-input"
              placeholder="your_handle"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              id="reg-username"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Min. 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              id="reg-password"
              autoComplete="new-password"
            />
            {/* Password strength indicator */}
            {password && (
              <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{
                  display: 'flex',
                  gap: '3px',
                  flex: 1,
                }}>
                  {[1, 2, 3].map((i) => (
                    <div key={i} style={{
                      height: '3px',
                      flex: 1,
                      borderRadius: '2px',
                      background: i <= strength.level ? strength.color : 'var(--border-color)',
                      transition: 'background 200ms ease',
                    }} />
                  ))}
                </div>
                <span style={{
                  fontSize: '0.6rem',
                  fontWeight: 600,
                  fontFamily: 'var(--font-mono)',
                  color: strength.color,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  {strength.label}
                </span>
              </div>
            )}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-confirm">Confirm Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Repeat password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              id="reg-confirm"
              autoComplete="new-password"
            />
          </div>

          {error && <p className="error-message" id="register-error">{error}</p>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            id="register-submit"
          >
            {loading ? <div className="spinner" /> : 'Create Account'}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
