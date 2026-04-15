"""Tests for peyote.export — actually round-trips PNG/SVG/PDF/JSON via tmp_path."""

import json

import pytest
from PIL import Image

from peyote.colors import ColorPalette
from peyote.export import (
    format_bead_count,
    load_json,
    render_combined_png,
    save_json,
    save_pdf,
    save_png,
    save_svg,
    svg_to_pil,
)
from peyote.grid import blank_grid
from peyote.sizing import BeadConfig


@pytest.fixture
def fabric_and_meta():
    cfg = BeadConfig(columns=4, rows=4)
    palette = ColorPalette.two_color('#ffffff', '#000000')
    fabric = blank_grid(cfg)
    fabric[0][0] = 1  # one foreground bead
    return fabric, cfg, palette


class TestSvgToPil:
    def test_converts_svg_to_image(self):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
               '<rect width="10" height="10" fill="red"/></svg>')
        img = svg_to_pil(svg, scale=1)
        assert isinstance(img, Image.Image)
        assert img.width == 10
        assert img.height == 10

    def test_scale_increases_dimensions(self):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
               '<rect width="10" height="10" fill="red"/></svg>')
        small = svg_to_pil(svg, scale=1)
        large = svg_to_pil(svg, scale=3)
        assert large.width == small.width * 3


class TestRenderCombinedPng:
    def test_view_fabric(self, fabric_and_meta):
        fabric, cfg, palette = fabric_and_meta
        img = render_combined_png(fabric, '', cfg, palette, view='fabric')
        assert isinstance(img, Image.Image)

    def test_view_pattern(self, fabric_and_meta):
        fabric, cfg, palette = fabric_and_meta
        img = render_combined_png(fabric, '', cfg, palette, view='pattern')
        assert isinstance(img, Image.Image)

    def test_view_both_combines_horizontally(self, fabric_and_meta):
        fabric, cfg, palette = fabric_and_meta
        both = render_combined_png(fabric, '', cfg, palette, view='both')
        fabric_img = render_combined_png(fabric, '', cfg, palette, view='fabric')
        pattern_img = render_combined_png(fabric, '', cfg, palette, view='pattern')
        # 'both' should be at least as wide as the two side-by-side
        assert both.width >= fabric_img.width + pattern_img.width


class TestSaveSvg:
    def test_save_fabric_svg(self, fabric_and_meta, tmp_path):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / 'p.svg'
        result = save_svg(fabric, 'T', cfg, palette, output=str(out),
                          view='fabric')
        assert result == str(out)
        content = out.read_text()
        assert content.startswith('<svg')

    def test_save_pattern_svg(self, fabric_and_meta, tmp_path):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / 'p.svg'
        save_svg(fabric, '', cfg, palette, output=str(out), view='pattern')
        assert out.read_text().startswith('<svg')


class TestSavePng:
    def test_save_creates_valid_image(self, fabric_and_meta, tmp_path):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / 'p.png'
        save_png(fabric, '', cfg, palette, output=str(out), view='fabric')
        assert out.exists()
        # Verify it opens as a real PNG
        with Image.open(out) as img:
            assert img.format == 'PNG'

    def test_save_both_view(self, fabric_and_meta, tmp_path):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / 'p.png'
        save_png(fabric, '', cfg, palette, output=str(out), view='both')
        assert out.exists()


class TestSavePdf:
    @pytest.mark.parametrize("view", ['fabric', 'pattern', 'both'])
    def test_save_pdf(self, fabric_and_meta, tmp_path, view):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / f'p_{view}.pdf'
        save_pdf(fabric, '', cfg, palette, output=str(out), view=view)
        assert out.exists()
        # PDF magic header
        assert out.read_bytes()[:4] == b'%PDF'


class TestJsonRoundtrip:
    def test_save_and_load_preserves_state(self, fabric_and_meta, tmp_path):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / 'p.json'
        save_json(fabric, cfg, palette, title='Hello', output=str(out))

        loaded_fabric, loaded_cfg, loaded_palette, loaded_title = load_json(
            str(out)
        )
        assert loaded_fabric == fabric
        assert loaded_cfg.columns == cfg.columns
        assert loaded_cfg.rows == cfg.rows
        assert loaded_cfg.bead_width == cfg.bead_width
        assert loaded_palette.colors == palette.colors
        assert loaded_palette.names == palette.names
        assert loaded_title == 'Hello'

    def test_save_json_structure(self, fabric_and_meta, tmp_path):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / 'p.json'
        save_json(fabric, cfg, palette, title='X', output=str(out))
        data = json.loads(out.read_text())
        assert 'title' in data
        assert 'config' in data
        assert 'palette' in data
        assert 'fabric' in data
        assert data['fabric'] == fabric

    def test_load_missing_title_defaults_empty(self, fabric_and_meta,
                                                tmp_path):
        fabric, cfg, palette = fabric_and_meta
        out = tmp_path / 'p.json'
        save_json(fabric, cfg, palette, title='', output=str(out))
        # Manually rewrite without title
        data = json.loads(out.read_text())
        del data['title']
        out.write_text(json.dumps(data))
        _, _, _, title = load_json(str(out))
        assert title == ''


class TestFormatBeadCount:
    def test_includes_total(self, fabric_and_meta):
        fabric, cfg, palette = fabric_and_meta
        text = format_bead_count(fabric, cfg, palette)
        assert 'Total' in text

    def test_includes_color_names(self, fabric_and_meta):
        fabric, cfg, palette = fabric_and_meta
        text = format_bead_count(fabric, cfg, palette)
        # Background color name should appear
        assert palette.names[0] in text

    def test_total_matches_sum(self):
        cfg = BeadConfig(columns=4, rows=4)
        palette = ColorPalette.two_color('#ffffff', '#000000')
        fabric = blank_grid(cfg)
        fabric[0][0] = 1
        text = format_bead_count(fabric, cfg, palette)
        # 4 rows × 2 active beads = 8
        assert ' 8 beads' in text
