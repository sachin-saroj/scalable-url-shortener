"""
Tests for URL Validation
──────────────────────────
"""

from app.utils.validators import is_valid_url, sanitize_url


class TestURLValidation:
    """Test URL format and safety validation."""

    def test_valid_http_url(self):
        is_valid, _error = is_valid_url("http://example.com")
        assert is_valid is True

    def test_valid_https_url(self):
        is_valid, _error = is_valid_url("https://example.com/path?q=1")
        assert is_valid is True

    def test_invalid_no_scheme(self):
        is_valid, error = is_valid_url("example.com")
        assert is_valid is False
        assert "http" in error.lower()

    def test_invalid_javascript_scheme(self):
        is_valid, _error = is_valid_url("javascript:alert(1)")
        assert is_valid is False

    def test_invalid_file_scheme(self):
        is_valid, _error = is_valid_url("file:///etc/passwd")
        assert is_valid is False

    def test_blocked_localhost(self):
        is_valid, error = is_valid_url("http://localhost/admin")
        assert is_valid is False
        assert "private" in error.lower()

    def test_blocked_private_ip(self):
        is_valid, _error = is_valid_url("http://192.168.1.1/admin")
        assert is_valid is False

    def test_blocked_loopback(self):
        is_valid, _error = is_valid_url("http://127.0.0.1:8080")
        assert is_valid is False

    def test_too_long_url(self):
        long_url = "https://example.com/" + "a" * 3000
        is_valid, error = is_valid_url(long_url)
        assert is_valid is False
        assert "length" in error.lower()


class TestURLSanitize:
    """Test URL sanitization."""

    def test_strip_whitespace(self):
        assert sanitize_url("  https://example.com  ") == "https://example.com"

    def test_remove_null_bytes(self):
        assert sanitize_url("https://example.com\x00") == "https://example.com"

    def test_remove_control_chars(self):
        assert sanitize_url("https://example.com\x01\x02") == "https://example.com"
