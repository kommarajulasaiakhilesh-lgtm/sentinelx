"""Threat detection primitives for OWASP LLM Top 10 enforcement.

Covers the enforceable items:
- LLM01 Prompt Injection & LLM07 System-Prompt Leakage — input normalization
  (unicode, zero-width, leetspeak, spacing/punctuation obfuscation) plus a
  categorized signature set, so obfuscated attacks that defeat naive substring
  matching are still caught.
- LLM02 Sensitive Information Disclosure — PII / secret pattern detection for
  data-loss-prevention policies.

This is deterministic pattern detection, not an ML classifier: it meaningfully
raises coverage and closes obvious evasion gaps, but is not a guarantee. A
trained classifier is the natural next step.
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

_ZERO_WIDTH = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF], None
)

# Common leetspeak / homoglyph substitutions attackers use to evade filters.
_LEET = str.maketrans(
    {
        "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
        "7": "t", "@": "a", "$": "s", "!": "i", "|": "i",
    }
)


def normalize(text: str) -> str:
    """NFKC-normalize, lowercase, strip zero-width chars, collapse whitespace."""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_ZERO_WIDTH)
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def _deleet(text: str) -> str:
    return text.translate(_LEET)


def _despace(text: str) -> str:
    """Keep only letters/digits — defeats spacing and punctuation obfuscation
    (e.g. 'i g n o r e', 'ig-nore', 'ign0re')."""
    return re.sub(r"[^a-z0-9]", "", text)


# ---------------------------------------------------------------------------
# Prompt-injection signatures (LLM01 / LLM07)
# ---------------------------------------------------------------------------

INJECTION_SIGNATURES: dict[str, list[str]] = {
    "INSTRUCTION_OVERRIDE": [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore the above",
        "ignore your instructions",
        "disregard previous instructions",
        "disregard all instructions",
        "disregard the earlier directives",
        "set aside the earlier directives",
        "forget previous instructions",
        "forget everything",
        "forget safety",
        "override your instructions",
        "override your guidelines",
    ],
    "SYSTEM_PROMPT_EXTRACTION": [
        "reveal system prompt",
        "show system prompt",
        "print system prompt",
        "your system prompt",
        "the system prompt",
        "repeat the system prompt",
        "what is your system prompt",
        "reveal your instructions",
        "show your instructions",
        "print your instructions",
        "disclose hidden rules",
        "disclose your hidden",
        "repeat the text above",
    ],
    "JAILBREAK": [
        "you are dan",
        "do anything now",
        "developer mode",
        "no restrictions",
        "without restrictions",
        "has no restrictions",
        "ignore safety",
        "bypass safety",
        "bypass your instructions",
        "jailbreak",
    ],
}

# Precompute de-leeted, de-spaced signature forms for robust matching.
_SIG_FORMS: list[tuple[str, str]] = [
    (category, _despace(_deleet(sig)))
    for category, sigs in INJECTION_SIGNATURES.items()
    for sig in sigs
]


def detect_prompt_injection(text: str) -> dict | None:
    """Return {category, signature} if the input matches an injection signature."""
    base = normalize(text)
    candidate = _despace(_deleet(base))
    for category, sig_form in _SIG_FORMS:
        if sig_form and sig_form in candidate:
            return {"category": category, "signature": sig_form}
    return None


# ---------------------------------------------------------------------------
# Sensitive-data detection (LLM02)
# ---------------------------------------------------------------------------

_SENSITIVE_PATTERNS: dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "AWS_ACCESS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "API_KEY": re.compile(r"\b(?:sk|pk|rk)[-_][A-Za-z0-9]{16,}\b"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
}


def detect_sensitive_data(text: str) -> list[str]:
    """Return the list of sensitive-data categories found in ``text``."""
    found = []
    for name, pattern in _SENSITIVE_PATTERNS.items():
        if pattern.search(text):
            found.append(name)
    return found
