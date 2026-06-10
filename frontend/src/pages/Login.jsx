/**
 * Login Page — LinkForge V3
 * ──────────────────────────
 * Premium auth with editorial serif title and refined inputs.
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const result = await login(email, password);
      if (result.ok) {
        navigate('/dashboard');
      } else {
        setError(result.data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  }

  return (
    <div className="auth-page">
      <div className="auth-card" id="login-card">
        <h2 className="auth-title">Welcome Back</h2>
        <p className="auth-subtitle">Sign in to access your routes</p>

        <form className="auth-form" onSubmit={handleSubmit} id="login-form">
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              id="login-email"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="login-password">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              id="login-password"
              autoComplete="current-password"
            />
          </div>

          {error && <p className="error-message" id="login-error">{error}</p>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            id="login-submit"
          >
            {loading ? <div className="spinner" /> : 'Sign In'}
          </button>
        </form>

        <p className="auth-switch">
          No account yet? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}
