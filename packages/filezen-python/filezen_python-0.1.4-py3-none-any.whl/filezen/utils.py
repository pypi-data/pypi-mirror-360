"""Utility functions for the FileZen Python SDK."""

import base64
import re
from urllib.parse import urlparse


def is_url(source: str) -> bool:
    """Check if source is a URL."""
    try:
        result = urlparse(source)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_base64(source: str) -> bool:
    """Check if source is base64 encoded."""
    # Check for data URL format
    if source.startswith("data:"):
        return True

    # Check for plain base64
    try:
        # Base64 should only contain valid characters
        base64_pattern = re.compile(r"^[A-Za-z0-9+/]*={0,2}$")
        if not base64_pattern.match(source):
            return False

        # Base64 should be reasonably long (at least 16 characters for meaningful data)
        # and typically doesn't contain common English words
        if len(source) < 16:
            return False

        # Try to decode to verify it's valid base64
        if len(source) % 4 == 0:  # Valid base64 length
            base64.b64decode(source)
            return True
        return False
    except Exception:
        return False


def generate_local_id() -> str:
    """Generate a unique local ID."""
    import random
    import time

    return f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
