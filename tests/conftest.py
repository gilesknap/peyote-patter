"""Shared pytest fixtures for peyote tests."""

import pytest

from peyote.colors import ColorPalette
from peyote.sizing import BeadConfig


@pytest.fixture
def small_config():
    """Tiny BeadConfig for fast tests (10 cols x 12 rows)."""
    return BeadConfig(columns=10, rows=12)


@pytest.fixture
def tiny_config():
    """Minimum-width even-column config."""
    return BeadConfig(columns=4, rows=6)


@pytest.fixture
def two_color_palette():
    """Background + Foreground palette (two slots)."""
    return ColorPalette.two_color('#ffffff', '#000000')


@pytest.fixture
def four_color_palette():
    """Background + Text + Accent1 + Accent2 palette (four slots)."""
    return ColorPalette.four_color(
        '#ffffff', '#000000', '#ff0000', '#00ff00'
    )
