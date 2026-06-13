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

CODE_LENGTH = 6
MODULUS = BASE ** CODE_LENGTH        # 62^6 = 56,800,235,584
PRIME_MULTIPLIER = 2147483647  # Must be coprime with MODULUS (62 = 2 * 31)
PRIME_MULTIPLIER_INV = pow(PRIME_MULTIPLIER, -1, MODULUS)  # modular inverse, Python 3.8+

OFFSET = 100000  # keeps small IDs from mapping to 0


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


# Fixed permutation of indices 0 to 5 to scatter sequential patterns in the output string
PERMUTATION = [3, 0, 5, 1, 4, 2]


def encode_id(db_id: int) -> str:
    """
    Shuffle DB id using modular multiplication before encoding.
    shuffled = (db_id + OFFSET) * PRIME_MULTIPLIER  mod MODULUS
    Result is zero-padded to CODE_LENGTH, and characters are permuted
    so that sequential inputs do not produce sorted/sequential codes.
    Limit: Up to 56.8 billion unique IDs (62^6) can be shuffled without collisions.
    """
    if db_id < 0:
        raise ValueError("Cannot encode negative IDs")
    val = (db_id + OFFSET) % MODULUS
    shuffled = (val * PRIME_MULTIPLIER) % MODULUS
    code = encode(shuffled)
    padded = code.rjust(CODE_LENGTH, CHARSET[0])  # left-pad with '0'
    return "".join(padded[i] for i in PERMUTATION)


def decode_id(code: str) -> int:
    """Inverse of encode_id."""
    if len(code) != CODE_LENGTH:
        raise ValueError(f"Code must be exactly {CODE_LENGTH} characters long")
    # Reconstruct the padded string using the inverse permutation mapping:
    # padded[3] = code[0], padded[0] = code[1], padded[5] = code[2]
    # padded[1] = code[3], padded[4] = code[4], padded[2] = code[5]
    padded = [code[1], code[3], code[5], code[0], code[4], code[2]]
    shuffled = decode("".join(padded))
    val = (shuffled * PRIME_MULTIPLIER_INV) % MODULUS
    return val - OFFSET
