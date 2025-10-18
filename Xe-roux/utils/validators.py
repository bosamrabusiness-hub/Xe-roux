"""URL validation utilities for ClipX security.

Raises HTTPException(400) for invalid or disallowed URLs.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from fastapi import HTTPException, status

# Patterns for allowed schemes
_ALLOWED_SCHEMES = {"http", "https"}

# RFC 1918 private networks, loopback, link-local, multicast ranges handled via ipaddress module

_private_networks = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]

_reserved_networks = [
    ipaddress.ip_network("127.0.0.0/8"),  # loopback
    ipaddress.ip_network("0.0.0.0/8"),  # "this" network
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("224.0.0.0/4"),  # multicast
    ipaddress.ip_network("240.0.0.0/4"),  # reserved
]

_blocked_networks = _private_networks + _reserved_networks

_host_regex = re.compile(r"^[A-Za-z0-9.-]+$")


def _is_ip_address(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _ip_in_blocked_ranges(ip_str: str) -> bool:
    ip_obj = ipaddress.ip_address(ip_str)
    return any(ip_obj in net for net in _blocked_networks)


def validate_url(url: str) -> str:
    """Validate a user-supplied URL.

    Ensures scheme is http/https and host is not private or reserved.
    Returns the normalized URL string if valid, otherwise raises HTTP 400.
    """

    parsed = urlparse(url)

    # Check scheme
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must start with http:// or https://",
        )

    # Validate host presence
    host = parsed.hostname
    if not host:
        raise HTTPException(status_code=400, detail="URL missing host component")

    # Simple host format validation
    if not _host_regex.match(host):
        raise HTTPException(status_code=400, detail="Invalid host format")

    # If host is IP, block private/reserved ranges
    if _is_ip_address(host) and _ip_in_blocked_ranges(host):
        raise HTTPException(status_code=400, detail="URL points to a disallowed IP range")

    # All good – return original (or reconstructed) URL
    return url