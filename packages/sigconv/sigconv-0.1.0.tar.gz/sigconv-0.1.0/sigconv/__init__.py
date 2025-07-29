"""
sigconv — Signature format converter.

This package provides tools to parse and convert between binary signature formats:
- spaced format: "48 8B 05 ? ? ? ? 41"
- escaped format: "\\x48\\x8B\\x05....\\x41"
- bytesmask format: ("488B050000000041", "xxx????x")
"""

from .main import SignatureConverter, detect_format

__all__ = ["SignatureConverter", "detect_format"]