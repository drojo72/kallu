"""Exception hierarchy."""

from __future__ import annotations


class KelluError(Exception):
    """Base class for all Kellu errors."""


class ConfigError(KelluError):
    """Invalid or unreadable configuration."""


class SecurityError(KelluError):
    """A security invariant would be violated (unsafe path, wrong ownership, denied access)."""
