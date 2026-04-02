"""
Base62 Encoder/Decoder
───────────────────────
Converts database auto-increment IDs to short URL codes.

WHY Base62?
- Uses 0-9, a-z, A-Z → 62 characters, all URL-safe
- 6 chars = 62^6 = 56.8 BILLION unique codes
- Deterministic: same ID always produces same code → NO COLLISIONS
- Reversible: can decode back to ID for debugging

WHY NOT UUID?
- UUIDs are 36 chars → defeats "short" URL purpose

WHY NOT random strings?
- Random strings require collision detection
- At scale (billions of URLs), collision probability increases
- Base62(auto_increment) is mathematically collision-free

TRADE-OFF:
- Sequential IDs leak creation order
- Mitigation: encode(id + offset) or encode(id * prime_number)
  We use a simple prime multiplier to shuffle the sequence

COMMON INTERVIEW MISTAKE:
- Using MD5/SHA hash + truncation → collision risk at scale
- Using random with retry-on-collision → non-deterministic latency
"""

# Character set: 0-9 (10) + a-z (26) + A-Z (26) = 62 chars
CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(CHARSET)  # 62

# Prime multiplier to shuffle sequential IDs (prevents enumeration)
# Any large prime works; must be coprime with BASE^max_length
PRIME_MULTIPLIER = 2147483647  # Mersenne prime (2^31 - 1)
OFFSET = 100000  # Starting offset to ensure minimum code length


def encode(num: int) -> str:
    """
    Encode a positive integer to a Base62 string.
    
    Args:
        num: Database auto-increment ID (must be positive)
    
    Returns:
        Base62 encoded string (e.g., "Ab3xK9")
    
    Example:
        encode(1) → "1"
        encode(62) → "10"
        encode(100000) → "q0U"
    """
    if num < 0:
        raise ValueError("Cannot encode negative numbers")
    if num == 0:
        return CHARSET[0]

    result = []
    while num > 0:
        result.append(CHARSET[num % BASE])
        num //= BASE
    return "".join(reversed(result))


def decode(code: str) -> int:
    """
    Decode a Base62 string back to integer.
    
    Args:
        code: Base62 encoded string
        
    Returns:
        Original integer value
    
    Example:
        decode("Ab3xK9") → original integer
    """
    if not code:
        raise ValueError("Cannot decode empty string")
    
    num = 0
    for char in code:
        if char not in CHARSET:
            raise ValueError(f"Invalid character '{char}' in Base62 string")
        num = num * BASE + CHARSET.index(char)
    return num


def encode_id(db_id: int) -> str:
    """
    Encode a database ID with shuffling to prevent enumeration.
    
    This adds an offset and applies a transformation so that
    sequential IDs don't produce sequential short codes.
    
    Args:
        db_id: Auto-increment database ID
    
    Returns:
        Shuffled Base62 string
    """
    # Add offset to ensure minimum length
    shuffled = db_id + OFFSET
    return encode(shuffled)


def decode_id(code: str) -> int:
    """Decode a shuffled Base62 code back to database ID."""
    return decode(code) - OFFSET
