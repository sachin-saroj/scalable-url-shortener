/**
 * API Client
 * ──────────
 * Centralized fetch wrapper with auth token management.
 */

const API_BASE = '/api/v1';

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE;
  }

  getToken() {
    return null;
  }

  setTokens(access, refresh) {
    // Cookies set automatically by the backend
  }

  clearTokens() {
    // Cookies cleared automatically by backend logout
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include',
    });

    if (response.status === 401 && !path.startsWith('/auth/login') && !path.startsWith('/auth/register')) {
      // Try refresh token
      const refreshed = await this.tryRefresh();
      if (refreshed) {
        return fetch(url, {
          ...options,
          headers,
          credentials: 'include',
        });
      }
      const isPublicPage = ['/', '/login', '/register'].includes(window.location.pathname);
      if (!isPublicPage) {
        window.location.href = '/login';
      }
      throw new Error('Session expired');
    }

    return response;
  }

  async tryRefresh() {
    try {
      const res = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      return res.ok;
    } catch {
      return false;
    }
  }

  async logout() {
    const res = await this.request('/auth/logout', {
      method: 'POST',
    });
    return { ok: res.ok };
  }

  // ── Auth ────────────────────────────────────
  async register(email, username, password) {
    const res = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    });
    return { ok: res.ok, status: res.status, data: await res.json() };
  }

  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return { ok: res.ok, status: res.status, data: await res.json() };
  }

  async getMe() {
    const res = await this.request('/auth/me');
    return { ok: res.ok, data: await res.json() };
  }

  // ── URLs ────────────────────────────────────
  async shortenUrl(url, customAlias, expiresInHours) {
    const body = { url };
    if (customAlias) body.custom_alias = customAlias;
    if (expiresInHours) body.expires_in_hours = parseInt(expiresInHours);

    const res = await this.request('/shorten', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return { ok: res.ok, status: res.status, data: await res.json() };
  }

  async getDashboardStats() {
    const res = await this.request('/urls/stats');
    return { ok: res.ok, status: res.status, data: await res.json() };
  }

  async getMyUrls(page = 1) {
    const res = await this.request(`/urls?page=${page}`);
    return { ok: res.ok, data: await res.json() };
  }

  async deleteUrl(shortCode) {
    const res = await this.request(`/urls/${shortCode}`, { method: 'DELETE' });
    return { ok: res.ok, status: res.status };
  }

  // ── Analytics ───────────────────────────────
  async getAnalytics(shortCode) {
    const res = await this.request(`/analytics/${shortCode}`);
    return { ok: res.ok, data: await res.json() };
  }
}

export const api = new ApiClient();
