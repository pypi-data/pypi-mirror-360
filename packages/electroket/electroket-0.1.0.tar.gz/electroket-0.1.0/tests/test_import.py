"""Tests for the electroket package."""

import importlib.metadata as metadata
import electroket


def test_show_version():
    """Ensure ``show_version`` returns electroket's version."""

    assert electroket.show_version() == metadata.version("electroket")
