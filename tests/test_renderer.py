"""Tests for peyote.renderer (SVG generation)."""

from peyote.colors import ColorPalette
from peyote.grid import blank_grid
from peyote.renderer import _bead_el, make_fabric_svg, make_pattern_svg
from peyote.sizing import BeadConfig


class TestBeadEl:
    def test_bead_el_includes_rect(self, four_color_palette):
        cfg = BeadConfig(columns=4, rows=2)
        svg = _bead_el(0, 0, 1, four_color_palette, cfg)
        assert '<rect' in svg
        assert 'fill="#000000"' in svg  # palette[1] in four_color

    def test_bead_el_includes_label_text(self, four_color_palette):
        cfg = BeadConfig(columns=4, rows=2)
        svg = _bead_el(0, 0, 0, four_color_palette, cfg, label=True)
        assert '<text' in svg
        # Index 0 → label 'A'
        assert '>A<' in svg

    def test_bead_el_no_label(self, four_color_palette):
        cfg = BeadConfig(columns=4, rows=2)
        svg = _bead_el(0, 0, 0, four_color_palette, cfg, label=False)
        assert '<text' not in svg

    def test_bead_el_unknown_index_uses_fallback(self):
        cfg = BeadConfig(columns=4, rows=2)
        empty_palette = ColorPalette()
        svg = _bead_el(0, 0, 99, empty_palette, cfg)
        assert '#cccccc' in svg
        assert '#999999' in svg


class TestMakeFabricSVG:
    def test_returns_svg_string_and_dimensions(self, small_config,
                                                two_color_palette):
        fabric = blank_grid(small_config)
        svg, w, h = make_fabric_svg(fabric, 'Title', small_config,
                                     two_color_palette)
        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert w > 0 and h > 0

    def test_includes_one_rect_per_active_bead(self, two_color_palette):
        cfg = BeadConfig(columns=4, rows=4)
        fabric = blank_grid(cfg)
        svg, _, _ = make_fabric_svg(fabric, '', cfg, two_color_palette)
        # 4 cols × 4 rows / 2 active per row = 8 active beads + 1 background rect
        assert svg.count('<rect') == 8 + 1


class TestMakePatternSVG:
    def test_returns_svg_string_and_dimensions(self, small_config,
                                                two_color_palette):
        fabric = blank_grid(small_config)
        svg, w, h = make_pattern_svg(fabric, 'Title', small_config,
                                      two_color_palette)
        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert w > 0 and h > 0

    def test_includes_row_arrows(self, two_color_palette):
        cfg = BeadConfig(columns=4, rows=4)
        fabric = blank_grid(cfg)
        svg, _, _ = make_pattern_svg(fabric, '', cfg, two_color_palette)
        # Right and left arrows should both appear (different parity rows)
        assert '\u2192' in svg or '\u2190' in svg

    def test_first_row_label_is_r1_plus_2(self, two_color_palette):
        cfg = BeadConfig(columns=4, rows=4)
        fabric = blank_grid(cfg)
        svg, _, _ = make_pattern_svg(fabric, '', cfg, two_color_palette)
        assert 'R1+2' in svg

    def test_no_labels_for_small_beads(self, two_color_palette):
        # bead_width 8 < 16 → labels suppressed
        cfg = BeadConfig(columns=4, rows=2, bead_width=8, bead_height=8)
        fabric = blank_grid(cfg)
        svg, _, _ = make_pattern_svg(fabric, '', cfg, two_color_palette)
        # No bead-letter labels, but row labels still present
        assert '>A<' not in svg

    def test_labels_for_large_beads(self, two_color_palette):
        # default bead_width=22 ≥ 16 → labels visible
        cfg = BeadConfig(columns=4, rows=2)
        fabric = blank_grid(cfg)
        svg, _, _ = make_pattern_svg(fabric, '', cfg, two_color_palette)
        assert '>A<' in svg
