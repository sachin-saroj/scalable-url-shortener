"""
QR Code Service
────────────────
Generates QR codes for short URLs.

WHY server-side QR generation?
- Consistent quality across all clients
- Can cache generated QR codes
- No client-side JavaScript dependency
- Can embed logos or branding in future
"""

import io
import qrcode
from qrcode.constants import ERROR_CORRECT_H


def generate_qr_code(url: str, size: int = 10) -> bytes:
    """
    Generate a QR code PNG image for a URL.
    
    Args:
        url: The full URL to encode
        size: Box size in pixels (default 10)
    
    Returns:
        PNG image as bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,  # High error correction (30%)
        box_size=size,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer.getvalue()
