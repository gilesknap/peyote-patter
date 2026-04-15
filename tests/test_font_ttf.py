"""Tests for peyote.font_ttf — uses real system fonts (DejaVu)."""

import os

import pytest

from peyote import font_ttf
from peyote.font_ttf import (
    DEFAULT_FONT_NAME,
    FONT_CATALOG,
    _ensure_min_stroke_width,
    _measure_char_widths,
    available_fonts,
    find_default_font,
    render_char_bitmap,
    render_text_rows,
    resolve_font,
)


# Skip the whole module if no system TTF fonts are installed
pytestmark = pytest.mark.skipif(
    not available_fonts(),
    reason="no system TTF fonts available",
)


class TestFontCatalog:
    def test_catalog_nonempty(self):
        assert len(FONT_CATALOG) > 0

    def test_default_font_in_catalog(self):
        assert DEFAULT_FONT_NAME in FONT_CATALOG

    def test_available_fonts_only_returns_existing(self):
        for name in available_fonts():
            paths = FONT_CATALOG[name]
            assert any(os.path.exists(p) for p in paths)


class TestResolveFont:
    def test_resolve_default(self):
        path = resolve_font(DEFAULT_FONT_NAME)
        assert os.path.exists(path)

    def test_resolve_unknown_falls_back(self):
        # Unknown names should still produce *some* available font
        path = resolve_font('TotallyMadeUpFontName')
        assert os.path.exists(path)

    def test_resolve_none_falls_back(self):
        path = resolve_font(None)
        assert os.path.exists(path)

    def test_find_default_font(self):
        assert os.path.exists(find_default_font())

    def test_resolve_raises_when_nothing_available(self, monkeypatch):
        # Repoint catalog to all-missing paths to exercise the error branch.
        monkeypatch.setattr(font_ttf, 'FONT_CATALOG', {
            'Fake': ['/nonexistent/font.ttf'],
        })
        with pytest.raises(FileNotFoundError, match="No suitable TTF font"):
            resolve_font('Fake')


class TestEnsureMinStrokeWidth:
    def test_isolated_pixel_extends_right(self):
        grid = [[0, 1, 0, 0]]
        result = _ensure_min_stroke_width(grid)
        assert result == [[0, 1, 1, 0]]

    def test_isolated_pixel_at_right_edge_extends_left(self):
        grid = [[0, 0, 0, 1]]
        result = _ensure_min_stroke_width(grid)
        assert result == [[0, 0, 1, 1]]

    def test_already_paired_unchanged(self):
        grid = [[0, 1, 1, 0]]
        result = _ensure_min_stroke_width(grid)
        assert result == [[0, 1, 1, 0]]

    def test_empty_grid(self):
        assert _ensure_min_stroke_width([]) == []

    def test_does_not_mutate_input(self):
        grid = [[0, 1, 0]]
        _ensure_min_stroke_width(grid)
        assert grid == [[0, 1, 0]]


class TestRenderCharBitmap:
    def test_basic_shape(self):
        bitmap = render_char_bitmap('A', columns=8, char_height=10)
        assert len(bitmap) == 10
        assert all(len(row) == 8 for row in bitmap)
        assert all(v in (0, 1) for row in bitmap for v in row)

    def test_blank_char_is_all_zero(self):
        bitmap = render_char_bitmap(' ', columns=8, char_height=10)
        assert all(v == 0 for row in bitmap for v in row)

    def test_letter_has_some_pixels(self):
        bitmap = render_char_bitmap('M', columns=10, char_height=12)
        on_pixels = sum(v for row in bitmap for v in row)
        assert on_pixels > 0

    def test_invalid_font_path_raises(self):
        with pytest.raises(FileNotFoundError):
            render_char_bitmap('A', columns=8, char_height=10,
                               font_path='/no/such/font.ttf')

    def test_dilate_increases_or_equals_pixel_count(self):
        normal = render_char_bitmap('I', columns=10, char_height=12)
        dilated = render_char_bitmap('I', columns=10, char_height=12,
                                      dilate=True)
        n_normal = sum(v for row in normal for v in row)
        n_dilated = sum(v for row in dilated for v in row)
        assert n_dilated >= n_normal


class TestMeasureCharWidths:
    def test_returns_one_width_per_char(self):
        path = find_default_font()
        widths = _measure_char_widths('ABC', path, glyph_height=10, avg_width=10)
        assert len(widths) == 3
        assert all(w >= 4 for w in widths)

    def test_proportional_widths_m_wider_than_i(self):
        path = find_default_font()
        widths = _measure_char_widths('IM', path, glyph_height=20, avg_width=20)
        assert widths[1] >= widths[0]


class TestRenderTextRows:
    def test_rotated_render_has_columns_width(self):
        rows = render_text_rows('A', columns=10, rotate=True)
        assert all(len(r) == 10 for r in rows)
        assert len(rows) > 0

    def test_non_rotated_render(self):
        rows = render_text_rows('A', columns=10, rotate=False)
        assert all(len(r) == 10 for r in rows)
        assert len(rows) > 0

    def test_text_uppercased(self):
        # 'a' and 'A' should produce the same output (text is uppercased)
        a_lower = render_text_rows('a', columns=10, rotate=True)
        a_upper = render_text_rows('A', columns=10, rotate=True)
        assert a_lower == a_upper

    def test_spacing_between_chars(self):
        rows = render_text_rows('AB', columns=10, char_spacing=5, rotate=True)
        # there should be at least 5 all-zero rows somewhere (the spacer)
        zero_count = sum(1 for r in rows if all(v == 0 for v in r))
        assert zero_count >= 5

    def test_explicit_char_height(self):
        rows = render_text_rows('A', columns=10, char_height=8, rotate=False)
        assert len(rows) == 8
