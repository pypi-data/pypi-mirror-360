"""Shinobi - Enhanced project initialization tool built on top of uv."""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # backport for Python <3.8

__version__ = version("shinobi")
