"""Progressbar style module."""

from .style import TProgressbar

# pylint: disable=too-few-public-methods


class Vertical(TProgressbar):
    """Vertical progressbar style, override using same class name to set
    configuration."""


class Horizontal(TProgressbar):
    """Horizontal progressbar style, override using same class name to set
    configuration."""
