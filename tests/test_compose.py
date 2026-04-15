"""Tests for peyote.compose."""

import pytest

from peyote.compose import (
    Segment,
    _shift_pattern_to_accents,
    compose_pattern_only,
    compose_segmented,
    compose_text_with_background,
    compose_text_with_border,
    default_border_rows,
    text_extent,
)
from peyote.font_ttf import available_fonts
from peyote.sizing import BeadConfig

# Skip text-rendering tests if no font is installed; pure-pattern composition
# does not need a font.
needs_font = pytest.mark.skipif(
    not available_fonts(),
    reason="no system TTF fonts available",
)


class TestTextExtent:
    def test_first_and_last_nonzero_rows(self):
        cfg = BeadConfig(columns=4, rows=6)
        fabric = [
            [0, 0, 0, 0],   # 0
            [0, 0, 0, 0],   # 1
            [0, 1, 0, 0],   # 2  ← first
            [0, 0, 0, 0],   # 3
            [1, 0, 0, 0],   # 4  ← last
            [0, 0, 0, 0],   # 5
        ]
        assert text_extent(fabric, cfg) == (2, 4)

    def test_blank_grid_returns_defaults(self):
        cfg = BeadConfig(columns=4, rows=4)
        fabric = [[0] * 4 for _ in range(4)]
        # Defaults: first_row=0, last_row=rows-1=3
        assert text_extent(fabric, cfg) == (0, 3)


class TestShiftPatternToAccents:
    def test_zero_stays_zero(self):
        assert _shift_pattern_to_accents([[0, 0]]) == [[0, 0]]

    def test_one_becomes_two(self):
        assert _shift_pattern_to_accents([[1, 1]]) == [[2, 2]]

    def test_two_becomes_three(self):
        assert _shift_pattern_to_accents([[1, 2, 0]]) == [[2, 3, 0]]


class TestComposePatternOnly:
    def test_pattern_only_dimensions(self, small_config):
        fabric = compose_pattern_only('checker', small_config)
        assert len(fabric) == small_config.rows
        assert all(len(r) == small_config.columns for r in fabric)

    def test_pattern_only_unknown_raises(self, small_config):
        with pytest.raises(ValueError, match="Unknown pattern"):
            compose_pattern_only('not-a-pattern', small_config)

    def test_pattern_only_passes_kwargs(self, small_config):
        f1 = compose_pattern_only('checker', small_config, block_size=1)
        f2 = compose_pattern_only('checker', small_config, block_size=4)
        assert f1 != f2


@needs_font
class TestDefaultBorderRows:
    def test_returns_at_least_one(self, small_config):
        rows = default_border_rows('HI', small_config)
        assert rows >= 1


@needs_font
class TestComposeTextWithBorder:
    def test_dimensions(self):
        cfg = BeadConfig(columns=10, rows=80)
        fabric = compose_text_with_border('HI', cfg, border_pattern='checker')
        assert len(fabric) == cfg.rows
        assert all(len(r) == cfg.columns for r in fabric)

    def test_explicit_border_rows(self):
        cfg = BeadConfig(columns=10, rows=80)
        fabric = compose_text_with_border('HI', cfg, border_pattern='checker',
                                           border_rows=4)
        # The first 4 rows should not be all-zero (border painted)
        assert any(v != 0 for v in fabric[0])

    def test_unknown_pattern_raises(self):
        cfg = BeadConfig(columns=10, rows=80)
        with pytest.raises(ValueError, match="Unknown pattern"):
            compose_text_with_border('HI', cfg, border_pattern='nope')

    def test_border_uses_accent_slot(self):
        cfg = BeadConfig(columns=10, rows=80)
        fabric = compose_text_with_border('HI', cfg, border_pattern='checker',
                                           border_rows=2)
        # Borders are shifted to accent slots so values >= 2
        flat = {v for row in fabric for v in row}
        assert any(v >= 2 for v in flat)

    def test_border_rows_larger_than_grid_truncates(self):
        # Force border_rows to exceed config.rows so the truncation guard
        # in compose_text_with_border fires.
        cfg = BeadConfig(columns=10, rows=4)
        fabric = compose_text_with_border(
            'X', cfg, border_pattern='checker',
            border_rows=10,  # > rows=4
        )
        assert len(fabric) == cfg.rows

    def test_wrap_border_paints_sides(self):
        cfg = BeadConfig(columns=20, rows=80)
        fabric = compose_text_with_border(
            'HI', cfg, border_pattern='stripe-v',
            border_rows=4, margin=4, gap=1, wrap_border=True,
        )
        # With wrap_border=True and margin > gap, the side strips outside the
        # top/bottom band rows must contain at least one non-zero bead.
        side_cols = [0, 1, 18, 19]
        mid_rows = range(10, 70)
        side_pixels = sum(
            1 for r in mid_rows for c in side_cols if fabric[r][c] != 0
        )
        assert side_pixels > 0


@needs_font
class TestComposeTextWithBackground:
    def test_dimensions(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = compose_text_with_background('A', cfg,
                                               background_pattern='checker')
        assert len(fabric) == cfg.rows
        assert all(len(r) == cfg.columns for r in fabric)

    def test_unknown_background_raises(self):
        cfg = BeadConfig(columns=10, rows=40)
        with pytest.raises(ValueError, match="Unknown pattern"):
            compose_text_with_background('A', cfg,
                                          background_pattern='nope')

    def test_background_present(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = compose_text_with_background('A', cfg,
                                               background_pattern='checker')
        # Background pixels are accent (>=2), text uses 1 — both must appear
        flat = {v for row in fabric for v in row}
        assert 1 in flat  # text
        assert any(v >= 2 for v in flat)  # background


class TestComposeSegmented:
    def test_blank_segment_pads_zero(self):
        cfg = BeadConfig(columns=4, rows=10)
        out = compose_segmented([Segment(kind='blank', rows=10)], cfg)
        assert len(out) == 10
        assert all(v == 0 for row in out for v in row)

    def test_pattern_segment(self, small_config):
        out = compose_segmented(
            [Segment(kind='pattern', pattern='checker', rows=small_config.rows)],
            small_config,
        )
        assert len(out) == small_config.rows
        # Some non-zero pixels expected
        assert any(v != 0 for row in out for v in row)

    def test_pattern_unknown_raises(self, small_config):
        with pytest.raises(ValueError, match="Unknown pattern"):
            compose_segmented([Segment(kind='pattern', pattern='nope')],
                              small_config)

    def test_truncates_when_too_many_rows(self, small_config):
        # Two pattern segments that together exceed config.rows
        out = compose_segmented([
            Segment(kind='pattern', pattern='checker', rows=small_config.rows),
            Segment(kind='pattern', pattern='checker', rows=small_config.rows),
        ], small_config)
        assert len(out) == small_config.rows

    def test_pads_when_too_few_rows(self, small_config):
        out = compose_segmented(
            [Segment(kind='blank', rows=2)],
            small_config,
        )
        assert len(out) == small_config.rows

    def test_default_blank_rows(self, small_config):
        # Segment(blank) with rows=None should default to 4
        out = compose_segmented([Segment(kind='blank')], small_config)
        # All-zero, padded to config.rows
        assert len(out) == small_config.rows
        assert all(v == 0 for row in out for v in row)

    def test_pattern_kwargs_pass_through(self):
        cfg = BeadConfig(columns=8, rows=8)
        a = compose_segmented([
            Segment(kind='pattern', pattern='checker', rows=8,
                    pattern_kwargs={'block_size': 1}),
        ], cfg)
        b = compose_segmented([
            Segment(kind='pattern', pattern='checker', rows=8,
                    pattern_kwargs={'block_size': 4}),
        ], cfg)
        assert a != b

    @needs_font
    def test_text_segment_default_rows(self):
        cfg = BeadConfig(columns=10, rows=120)
        out = compose_segmented(
            [Segment(kind='text', text='HI')], cfg,
        )
        assert len(out) == cfg.rows
        # Text segment should produce some non-zero pixels
        assert any(v != 0 for row in out for v in row)

    @needs_font
    def test_text_segment_explicit_rows(self):
        cfg = BeadConfig(columns=10, rows=80)
        out = compose_segmented(
            [Segment(kind='text', text='A', rows=20)], cfg,
        )
        assert len(out) == cfg.rows
