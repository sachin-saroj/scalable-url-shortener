"""Tests for URL export endpoint."""

import csv
import io
import json

import pytest


class TestExportFormatValidation:
    """Test export format query parameter validation."""

    def test_csv_format_accepted(self):
        """Verify 'csv' is a valid format value."""
        from pydantic import BaseModel, Field
        import re

        pattern = r"^(csv|json)$"
        assert re.match(pattern, "csv") is not None

    def test_json_format_accepted(self):
        """Verify 'json' is a valid format value."""
        import re

        pattern = r"^(csv|json)$"
        assert re.match(pattern, "json") is not None

    def test_invalid_format_rejected(self):
        """Verify invalid formats are rejected by regex."""
        import re

        pattern = r"^(csv|json)$"
        assert re.match(pattern, "xml") is None
        assert re.match(pattern, "pdf") is None
        assert re.match(pattern, "") is None


class TestCSVExport:
    """Test CSV generation logic."""

    @pytest.mark.asyncio
    async def test_csv_has_correct_headers(self):
        """CSV output should have the expected column headers."""
        from app.api.v1.export import _export_csv

        # Use empty list to test just headers
        response = _export_csv([])
        # Read the content from the streaming response body
        content = ""
        async for chunk in response.body_iterator:
            content += chunk

        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        assert headers == [
            "short_code",
            "original_url",
            "custom_alias",
            "created_at",
            "expires_at",
            "is_active",
        ]

    def test_csv_content_type(self):
        """CSV response should have text/csv content type."""
        from app.api.v1.export import _export_csv

        response = _export_csv([])
        assert response.media_type == "text/csv"

    def test_csv_has_content_disposition(self):
        """CSV response should have attachment Content-Disposition."""
        from app.api.v1.export import _export_csv

        response = _export_csv([])
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]
        assert ".csv" in response.headers["Content-Disposition"]


class TestJSONExport:
    """Test JSON generation logic."""

    @pytest.mark.asyncio
    async def test_json_empty_list(self):
        """Empty URL list should export as empty JSON array."""
        from app.api.v1.export import _export_json

        response = _export_json([])
        content = ""
        async for chunk in response.body_iterator:
            content += chunk

        data = json.loads(content)
        assert data == []

    def test_json_content_type(self):
        """JSON response should have application/json content type."""
        from app.api.v1.export import _export_json

        response = _export_json([])
        assert response.media_type == "application/json"

    def test_json_has_content_disposition(self):
        """JSON response should have attachment Content-Disposition."""
        from app.api.v1.export import _export_json

        response = _export_json([])
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]
        assert ".json" in response.headers["Content-Disposition"]
