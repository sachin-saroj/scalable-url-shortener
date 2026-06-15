"""
Tests for Client IP Resolution
────────────────────────────────
"""

from unittest.mock import Mock
from app.utils.client_ip import get_client_ip
from app.config import get_settings


class TestClientIPResolution:
    """Test client IP extraction with trusted proxies."""

    def test_direct_peer_returned_when_no_proxies(self, monkeypatch):
        settings = get_settings()
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", "")

        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1"}

        assert get_client_ip(mock_request) == "192.168.1.100"

    def test_xff_returned_when_peer_is_trusted(self, monkeypatch):
        settings = get_settings()
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", "192.168.1.100, 192.168.1.101")

        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.100"}

        assert get_client_ip(mock_request) == "10.0.0.1"

    def test_direct_peer_returned_when_peer_not_trusted(self, monkeypatch):
        settings = get_settings()
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", "192.168.1.100")

        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.200"
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1"}

        assert get_client_ip(mock_request) == "192.168.1.200"

    def test_unknown_returned_when_no_client(self):
        mock_request = Mock()
        mock_request.client = None
        mock_request.headers = {}

        assert get_client_ip(mock_request) == "unknown"
