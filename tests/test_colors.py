"""Tests for peyote.colors."""

import pytest

from peyote.colors import (
    MIYUKI_DELICA,
    PALETTE_DEFS,
    ColorPalette,
    darken,
    get_palette,
    text_color_for,
)


class TestDarken:
    def test_darken_white_default_factor(self):
        # 255 * 0.65 = 165 → 0xa5
        assert darken('#ffffff') == '#a5a5a5'

    def test_darken_with_hash(self):
        assert darken('#ff0000', factor=0.5) == '#7f0000'

    def test_darken_without_hash(self):
        assert darken('ff0000', factor=0.5) == '#7f0000'

    def test_darken_black_returns_black(self):
        assert darken('#000000') == '#000000'

    def test_darken_factor_one_is_identity(self):
        assert darken('#abcdef', factor=1.0) == '#abcdef'

    def test_darken_factor_zero_is_black(self):
        assert darken('#ffffff', factor=0.0) == '#000000'


class TestTextColorFor:
    def test_white_for_dark_background(self):
        assert text_color_for('#000000') == '#ffffff'

    def test_dark_for_light_background(self):
        assert text_color_for('#ffffff') == '#333333'

    def test_white_for_dark_red(self):
        assert text_color_for('#400000') == '#ffffff'

    def test_dark_for_light_yellow(self):
        # high luminance yellow
        assert text_color_for('#ffff00') == '#333333'


class TestColorPalette:
    def test_from_pairs_assigns_indices(self):
        pal = ColorPalette.from_pairs([('#ff0000', 'Red'), ('#00ff00', 'Green')])
        assert pal.colors == {0: '#ff0000', 1: '#00ff00'}
        assert pal.names == {0: 'Red', 1: 'Green'}

    def test_from_pairs_computes_strokes(self):
        pal = ColorPalette.from_pairs([('#ffffff', 'White')])
        # strokes use darken()
        assert pal.strokes[0] == darken('#ffffff')

    def test_from_pairs_computes_text_colors(self):
        pal = ColorPalette.from_pairs([('#000000', 'Black'), ('#ffffff', 'White')])
        assert pal.text_colors[0] == '#ffffff'
        assert pal.text_colors[1] == '#333333'

    def test_two_color_factory(self):
        pal = ColorPalette.two_color('#000000', '#ffffff')
        assert pal.num_colors == 2
        assert pal.names[0] == 'Background'
        assert pal.names[1] == 'Accent 1'

    def test_two_color_custom_names(self):
        pal = ColorPalette.two_color('#000000', '#ffffff',
                                     bg_name='BG', fg_name='FG')
        assert pal.names == {0: 'BG', 1: 'FG'}

    def test_three_color_factory(self):
        pal = ColorPalette.three_color('#000000', '#ffffff', '#ff0000')
        assert pal.num_colors == 3

    def test_four_color_factory(self):
        pal = ColorPalette.four_color('#000000', '#ffffff', '#ff0000', '#00ff00')
        assert pal.num_colors == 4
        assert pal.names[1] == 'Text'
        assert pal.names[2] == 'Accent 1'
        assert pal.names[3] == 'Accent 2'

    def test_label_alphabetical(self):
        pal = ColorPalette.from_pairs(
            [('#000000', 'A'), ('#ffffff', 'B'), ('#ff0000', 'C')]
        )
        assert pal.label(0) == 'A'
        assert pal.label(1) == 'B'
        assert pal.label(25) == 'Z'

    def test_num_colors_property(self):
        pal = ColorPalette.from_pairs([('#000000', 'A')])
        assert pal.num_colors == 1
        empty = ColorPalette()
        assert empty.num_colors == 0

    def test_default_dataclass_is_empty(self):
        pal = ColorPalette()
        assert pal.colors == {}
        assert pal.names == {}
        assert pal.strokes == {}
        assert pal.text_colors == {}


class TestGetPalette:
    def test_known_palette_returns_instance(self):
        pal = get_palette('classic')
        assert isinstance(pal, ColorPalette)
        assert pal.colors[0] == '#E8A0A8'
        assert pal.colors[1] == '#C82020'

    def test_unknown_palette_raises(self):
        with pytest.raises(ValueError, match="Unknown palette"):
            get_palette('totally-not-a-palette')

    @pytest.mark.parametrize("name", list(PALETTE_DEFS.keys()))
    def test_all_builtin_palettes_load(self, name):
        pal = get_palette(name)
        assert pal.num_colors == len(PALETTE_DEFS[name])
        # every entry must have a matching label/stroke/text-color slot
        for i in range(pal.num_colors):
            assert i in pal.colors
            assert i in pal.names
            assert i in pal.strokes
            assert i in pal.text_colors


class TestMiyukiCatalog:
    def test_catalog_nonempty(self):
        assert len(MIYUKI_DELICA) > 0

    def test_entries_are_hex_name_pairs(self):
        for code, entry in MIYUKI_DELICA.items():
            assert code.startswith('DB')
            hex_color, name = entry
            assert hex_color.startswith('#')
            assert len(hex_color) == 7
            assert isinstance(name, str)
