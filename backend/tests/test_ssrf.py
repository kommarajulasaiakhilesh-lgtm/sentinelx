"""Tests for SSRF destination validation. Run with --noconftest."""

import ipaddress

import pytest

from app.core import ssrf
from app.core.ssrf import is_safe_public_ip, validate_destination


SAFE_IPS = ["8.8.8.8", "1.1.1.1", "93.184.216.34", "2606:4700:4700::1111"]

UNSAFE_IPS = [
    "127.0.0.1",          # loopback
    "10.0.0.5",           # private
    "192.168.1.1",        # private
    "172.16.0.1",         # private
    "169.254.169.254",    # cloud metadata / link-local
    "100.64.0.1",         # CGNAT
    "0.0.0.0",            # unspecified
    "224.0.0.1",          # multicast
    "::1",                # IPv6 loopback
    "fd00::1",            # IPv6 unique-local
    "fe80::1",            # IPv6 link-local
    "::ffff:127.0.0.1",   # IPv4-mapped loopback
    "::ffff:10.0.0.1",    # IPv4-mapped private
]


@pytest.mark.parametrize("addr", SAFE_IPS)
def test_safe_ips_allowed(addr):
    assert is_safe_public_ip(ipaddress.ip_address(addr)) is True


@pytest.mark.parametrize("addr", UNSAFE_IPS)
def test_unsafe_ips_rejected(addr):
    assert is_safe_public_ip(ipaddress.ip_address(addr)) is False


@pytest.mark.parametrize("addr", SAFE_IPS)
def test_validate_allows_public_literal(addr):
    validate_destination(f"https://[{addr}]/hook" if ":" in addr else f"https://{addr}/hook")


@pytest.mark.parametrize("addr", UNSAFE_IPS)
def test_validate_rejects_unsafe_literal(addr):
    url = f"https://[{addr}]/hook" if ":" in addr else f"https://{addr}/hook"
    with pytest.raises(ValueError):
        validate_destination(url)


def test_rejects_non_http_scheme():
    for url in ["ftp://example.com", "file:///etc/passwd", "gopher://x"]:
        with pytest.raises(ValueError):
            validate_destination(url)


def test_rejects_credentials_in_url():
    with pytest.raises(ValueError):
        validate_destination("https://user:pass@example.com/hook")


def test_rejects_local_hostnames():
    for host in ["localhost", "api.localhost", "db.internal", "printer.local"]:
        with pytest.raises(ValueError):
            validate_destination(f"https://{host}/hook")


def test_hostname_resolving_to_private_is_rejected(monkeypatch):
    def fake_getaddrinfo(host, port, *a, **k):
        return [(None, None, None, "", ("10.1.2.3", port))]

    monkeypatch.setattr(ssrf.socket, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(ValueError):
        validate_destination("https://rebind.example.com/hook")


def test_hostname_resolving_to_public_is_allowed(monkeypatch):
    def fake_getaddrinfo(host, port, *a, **k):
        return [(None, None, None, "", ("8.8.8.8", port))]

    monkeypatch.setattr(ssrf.socket, "getaddrinfo", fake_getaddrinfo)
    validate_destination("https://good.example.com/hook")
