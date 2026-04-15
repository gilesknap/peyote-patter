"""Tests for the root-level backward-compat wrappers."""

import importlib


class TestPeyoteWrapper:
    def test_peyote_re_exports_main(self):
        mod = importlib.import_module('peyote')  # the package
        assert mod.__doc__  # package docstring exists


class TestFontWrapper:
    def test_font_module_re_exports(self):
        # Import the root-level font.py wrapper
        import font as font_root
        assert hasattr(font_root, 'text_to_fabric')
        assert hasattr(font_root, 'text_to_fabric_rows')
