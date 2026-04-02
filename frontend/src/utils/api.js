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
    return localStorage.getItem('access_token');
  }

  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Try refresh token
      const refreshed = await this.tryRefresh();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.getToken()}`;
        return fetch(url, { ...options, headers });
      }
      this.clearTokens();
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    return response;
  }

  async tryRefresh() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (res.ok) {
        const data = await res.json();
        this.setTokens(data.access_token, data.refresh_token);
        return true;
      }
      return false;
    } catch {
      return false;
    }
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
