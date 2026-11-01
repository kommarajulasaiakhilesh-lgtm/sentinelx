"""SSRF destination validation for outbound webhook requests.

This is a defense-in-depth control, not a complete SSRF boundary. It rejects
non-HTTP(S) schemes, credential-bearing authorities, obviously local
hostnames, and any literal or DNS-resolved IP that is not globally routable
(loopback, private, link-local, unique-local, CGNAT, multicast, reserved, and
cloud metadata addresses).

A small time-of-check/time-of-use window remains between DNS resolution here
and the connection made by the HTTP client (DNS rebinding). Fully closing it
requires network-level egress restrictions in the hosting environment, so the
production webhook worker stays disabled until those are in place. The worker
additionally disables redirects and environment proxies.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

# Cloud instance metadata endpoints (link-local, but blocked explicitly too).
METADATA_IPS = {
    ipaddress.ip_address("169.254.169.254"),  # AWS/GCP/Azure IMDS
    ipaddress.ip_address("fd00:ec2::254"),  # AWS IMDS over IPv6
}

_LOCAL_SUFFIXES = (".localhost", ".local", ".internal")


def is_safe_public_ip(ip: ipaddress._BaseAddress) -> bool:
    """Return True only for globally routable, non-sensitive addresses."""
    # Normalize IPv4-mapped/compatible IPv6 (e.g. ::ffff:127.0.0.1) so a
    # mapped private/loopback address cannot slip through.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped

    if ip in METADATA_IPS:
        return False

    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or not ip.is_global
    )


def _resolve(host: str, port: int) -> list[str]:
    try:
        results = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (OSError, socket.gaierror) as exc:
        raise ValueError("Webhook hostname could not be safely resolved.") from exc
    if not results:
        raise ValueError("Webhook hostname did not resolve.")
    return [result[4][0].split("%", 1)[0] for result in results]


def validate_destination(url: str) -> None:
    """Raise ValueError if ``url`` is not a safe public HTTP(S) destination."""
    parsed = urlsplit(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS webhook URLs are allowed.")

    if (
        not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            "Webhook URL has an invalid or credential-bearing authority."
        )

    host = parsed.hostname.rstrip(".").lower()

    if host == "localhost" or host.endswith(_LOCAL_SUFFIXES):
        raise ValueError("Local webhook destinations are not allowed.")

    # Literal IP: validate directly, no DNS.
    try:
        literal_ip = ipaddress.ip_address(host)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if not is_safe_public_ip(literal_ip):
            raise ValueError("Webhook destination IP is not publicly routable.")
        return

    # Hostname: resolve and validate every candidate address.
    port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    for address in _resolve(host, port):
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise ValueError(
                "Webhook hostname resolved to an invalid address."
            ) from exc
        if not is_safe_public_ip(ip):
            raise ValueError(
                "Webhook hostname resolves to a non-public IP address."
            )
