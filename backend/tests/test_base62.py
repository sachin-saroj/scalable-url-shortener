"""
Tests for Base62 Encoder
─────────────────────────
Unit tests for the core encoding algorithm.
"""

import pytest

from app.utils.base62 import decode, decode_id, encode, encode_id


class TestBase62Encode:
    """Test Base62 encoding."""

    def test_encode_zero(self):
        assert encode(0) == "0"

    def test_encode_single_digit(self):
        assert encode(1) == "1"
        assert encode(9) == "9"

    def test_encode_double_digit(self):
        assert encode(10) == "a"
        assert encode(35) == "z"
        assert encode(36) == "A"
        assert encode(61) == "Z"

    def test_encode_62_is_10(self):
        """62 in Base62 = '10' (like 10 in decimal = '10')"""
        assert encode(62) == "10"

    def test_encode_large_number(self):
        assert encode(100000) == "q0U"

    def test_encode_negative_raises(self):
        with pytest.raises(ValueError, match="negative"):
            encode(-1)


class TestBase62Decode:
    """Test Base62 decoding."""

    def test_decode_zero(self):
        assert decode("0") == 0

    def test_decode_single_char(self):
        assert decode("a") == 10
        assert decode("Z") == 61

    def test_decode_multi_char(self):
        assert decode("10") == 62
        assert decode("q0U") == 100000

    def test_decode_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            decode("")

    def test_decode_invalid_char_raises(self):
        with pytest.raises(ValueError, match="Invalid character"):
            decode("hello!")


class TestBase62Roundtrip:
    """Verify encode(decode(x)) == x for various values."""

    @pytest.mark.parametrize("num", [0, 1, 61, 62, 100, 1000, 100000, 56800235583])
    def test_roundtrip(self, num):
        encoded = encode(num)
        decoded = decode(encoded)
        assert decoded == num, f"Roundtrip failed for {num}: encode={encoded}, decode={decoded}"


class TestBase62WithOffset:
    """Test the ID-specific encoding with offset."""

    def test_encode_id_1(self):
        code = encode_id(1)
        assert decode_id(code) == 1

    def test_encode_id_large(self):
        code = encode_id(999999)
        assert decode_id(code) == 999999

    def test_encode_id_minimum_length(self):
        """Offset ensures codes are always at least a few chars long."""
        code = encode_id(1)
        assert len(code) >= 3
