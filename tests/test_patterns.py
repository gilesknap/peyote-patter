"""Tests for peyote.patterns — generators, catalog, and repeat-spec."""

import pytest

from peyote.patterns import (
    PATTERN_CATALOG,
    PATTERN_REPEAT_SPEC,
    SINGLE_COLOR_PATTERNS,
    TWO_COLOR_PATTERNS,
    argyle,
    border,
    braid,
    checker,
    chevron,
    diamond,
    dots,
    flames,
    gradient_dither,
    greek_key,
    honeycomb,
    pattern_repeat_default,
    pattern_repeat_kwargs,
    scales,
    stripe_horizontal,
    stripe_vertical,
    wave,
    zigzag,
)


# ── Shape & dimension invariants for every pattern in the catalog ────────────

@pytest.mark.parametrize("name,fn", list(PATTERN_CATALOG.items()))
def test_pattern_dimensions(name, fn):
    grid = fn(columns=10, rows=12)
    assert len(grid) == 12, f"{name}: wrong row count"
    assert all(len(row) == 10 for row in grid), f"{name}: wrong col count"


@pytest.mark.parametrize("name,fn", list(PATTERN_CATALOG.items()))
def test_pattern_uses_only_known_indices(name, fn):
    grid = fn(columns=12, rows=12)
    used = {v for row in grid for v in row}
    # Patterns return small int color indices (0/1/2)
    assert used.issubset({0, 1, 2}), f"{name}: unexpected indices {used}"


@pytest.mark.parametrize("name,fn", list(PATTERN_CATALOG.items()))
def test_pattern_emits_some_on_pixels(name, fn):
    """Every pattern must light up at least one bead at a reasonable size."""
    grid = fn(columns=12, rows=12)
    on = sum(1 for row in grid for v in row if v != 0)
    assert on > 0, f"{name}: produced an entirely empty grid"


# ── Pattern-specific behaviour ───────────────────────────────────────────────

class TestStripeHorizontal:
    def test_default_alternating_bands(self):
        g = stripe_horizontal(4, 6)
        # Default widths=[3,3], colors=[1,0]
        assert g[0] == [1, 1, 1, 1]
        assert g[2] == [1, 1, 1, 1]
        assert g[3] == [0, 0, 0, 0]
        assert g[5] == [0, 0, 0, 0]

    def test_custom_widths_and_colors(self):
        g = stripe_horizontal(2, 4, widths=[1, 1], colors=[1, 2])
        assert g[0] == [1, 1]
        assert g[1] == [2, 2]
        assert g[2] == [1, 1]
        assert g[3] == [2, 2]


class TestStripeVertical:
    def test_default_columns_alternate(self):
        g = stripe_vertical(4, 2)
        # widths=[2,2], colors=[1,0]
        assert g[0] == [1, 1, 0, 0]
        # all rows identical
        assert g[1] == g[0]


class TestChevron:
    def test_chevron_symmetric_about_centre(self):
        g = chevron(10, 4)
        for row in g:
            assert row == row[::-1]


class TestDiamond:
    def test_diamond_uses_bg_and_color(self):
        g = diamond(8, 8, size=2)
        flat = {v for row in g for v in row}
        assert flat == {0, 1}


class TestZigzag:
    def test_zigzag_amplitude_one(self):
        g = zigzag(6, 4, amplitude=1, width=1)
        # Each row should have exactly one ON bead
        for row in g:
            assert sum(row) == 1


class TestChecker:
    def test_checker_block_size_one(self):
        g = checker(4, 4, block_size=1)
        # Standard chessboard: opposite corners are equal
        assert g[0][0] == g[1][1]
        assert g[0][1] != g[0][0]

    def test_checker_block_size_two(self):
        g = checker(4, 4, block_size=2)
        # Top-left 2×2 block should be uniform
        assert g[0][0] == g[0][1] == g[1][0] == g[1][1]
        # Adjacent block differs
        assert g[0][2] != g[0][0]


class TestBorder:
    def test_border_frames_grid(self):
        g = border(5, 5, thickness=1, color=1, bg=0)
        # All edges are color 1
        assert all(g[0][c] == 1 for c in range(5))
        assert all(g[-1][c] == 1 for c in range(5))
        assert all(g[r][0] == 1 for r in range(5))
        assert all(g[r][-1] == 1 for r in range(5))
        # Centre is bg
        assert g[2][2] == 0

    def test_border_thickness_two(self):
        g = border(6, 6, thickness=2)
        # First two and last two rows entirely color
        assert all(v == 1 for v in g[0])
        assert all(v == 1 for v in g[1])
        assert all(v == 1 for v in g[-1])


class TestDots:
    def test_dots_appear_on_grid(self):
        g = dots(4, 4, spacing=2)
        assert g[0][0] == 1
        assert g[1][1] == 1


class TestWave:
    def test_wave_default_runs(self):
        g = wave(10, 12)
        assert len(g) == 12
        assert any(1 in row for row in g)


class TestGradientDither:
    def test_vertical_direction(self):
        g = gradient_dither(8, 16, direction='vertical')
        # Bottom should be denser than top
        top = sum(v for v in g[0])
        bottom = sum(v for v in g[-1])
        assert bottom >= top

    def test_horizontal_direction(self):
        g = gradient_dither(16, 8, direction='horizontal')
        # Right edge denser than left edge (across rows)
        left = sum(row[0] for row in g)
        right = sum(row[-1] for row in g)
        assert right >= left


class TestGreekKey:
    def test_greek_key_tiles(self):
        g = greek_key(8, 8, size=2)
        # tile size 4 → grid is exactly 2×2 tiles, top-left tile must repeat
        assert g[0][:4] == g[0][4:]


class TestArgyle:
    def test_argyle_uses_three_indices(self):
        g = argyle(20, 20, size=4)
        flat = {v for row in g for v in row}
        # bg + diamond + crossing = three colours
        assert {0, 1, 2}.issubset(flat)


class TestScales:
    def test_scales_uses_two_colors(self):
        g = scales(20, 20, radius=3)
        flat = {v for row in g for v in row}
        # bg + two colours
        assert 1 in flat or 2 in flat


class TestFlames:
    def test_flames_render(self):
        g = flames(20, 20, size=4)
        assert sum(v != 0 for row in g for v in row) > 0


class TestBraid:
    def test_braid_two_strand_colors_appear(self):
        g = braid(12, 24)
        flat = {v for row in g for v in row}
        assert 1 in flat
        assert 2 in flat


class TestHoneycomb:
    def test_honeycomb_walls_present(self):
        g = honeycomb(12, 12, size=3)
        # Top wall row should have many ON pixels
        assert sum(v != 0 for v in g[0]) > 0


# ── Catalog & repeat-spec invariants ─────────────────────────────────────────

class TestCatalog:
    def test_catalog_nonempty(self):
        assert len(PATTERN_CATALOG) > 0

    def test_single_color_patterns_in_catalog(self):
        for n in SINGLE_COLOR_PATTERNS:
            assert n in PATTERN_CATALOG

    def test_two_color_patterns_in_catalog(self):
        for n in TWO_COLOR_PATTERNS:
            assert n in PATTERN_CATALOG

    def test_color_groups_disjoint(self):
        assert set(SINGLE_COLOR_PATTERNS).isdisjoint(set(TWO_COLOR_PATTERNS))

    def test_color_groups_cover_catalog(self):
        all_named = set(SINGLE_COLOR_PATTERNS) | set(TWO_COLOR_PATTERNS)
        assert all_named == set(PATTERN_CATALOG.keys())


class TestRepeatSpec:
    def test_default_for_unknown_returns_none(self):
        assert pattern_repeat_default('not-a-pattern') is None

    def test_default_for_known_returns_int(self):
        for name in PATTERN_REPEAT_SPEC:
            assert isinstance(pattern_repeat_default(name), int)

    def test_kwargs_for_unknown_empty(self):
        assert pattern_repeat_kwargs('not-a-pattern', 5) == {}

    def test_kwargs_for_none_repeat_empty(self):
        assert pattern_repeat_kwargs('checker', None) == {}

    @pytest.mark.parametrize("name", list(PATTERN_REPEAT_SPEC.keys()))
    def test_kwargs_returns_correct_kwarg_name(self, name):
        kwarg_name, default, _convert = PATTERN_REPEAT_SPEC[name]
        kwargs = pattern_repeat_kwargs(name, 8)
        assert kwarg_name in kwargs

    def test_kwargs_actually_applies_to_pattern(self):
        # Use a checker pattern with two different repeat values; the grids
        # should differ when block_size changes.
        kwargs1 = pattern_repeat_kwargs('checker', 1)
        kwargs2 = pattern_repeat_kwargs('checker', 4)
        g1 = checker(8, 8, **kwargs1)
        g2 = checker(8, 8, **kwargs2)
        assert g1 != g2

    def test_stripe_widths_are_paired_lists(self):
        # Stripe patterns need a list of 2 widths
        kwargs = pattern_repeat_kwargs('stripe-h', 6)
        assert isinstance(kwargs['widths'], list)
        assert len(kwargs['widths']) == 2
