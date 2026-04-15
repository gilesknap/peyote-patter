"""Tests for peyote.font (high-level text-to-fabric API)."""

import pytest

from peyote.font import _center_in_grid, text_to_fabric
from peyote.font_ttf import available_fonts
from peyote.sizing import BeadConfig

pytestmark = pytest.mark.skipif(
    not available_fonts(),
    reason="no system TTF fonts available",
)


class TestTextToFabric:
    def test_returns_correct_dimensions(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = text_to_fabric('HI', cfg)
        assert len(fabric) == cfg.rows
        assert all(len(row) == cfg.columns for row in fabric)

    def test_pixels_are_binary(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = text_to_fabric('A', cfg)
        assert all(v in (0, 1) for row in fabric for v in row)

    def test_some_pixels_are_set(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = text_to_fabric('A', cfg)
        assert any(v == 1 for row in fabric for v in row)

    def test_margin_clears_outer_columns(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = text_to_fabric('M', cfg, margin=2)
        # Outermost columns (0, 1 and 8, 9) must be all zero with margin=2
        for row in fabric:
            assert row[0] == 0 and row[1] == 0
            assert row[8] == 0 and row[9] == 0

    def test_no_margin_can_use_outer_columns(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = text_to_fabric('M', cfg, margin=0)
        # Without a margin, an "M" should reach the edges in at least one row.
        any_edge = any(row[0] == 1 or row[-1] == 1 for row in fabric)
        assert any_edge

    def test_non_rotate_orientation(self):
        cfg = BeadConfig(columns=10, rows=40)
        fabric = text_to_fabric('A', cfg, rotate=False)
        assert len(fabric) == cfg.rows
        assert all(len(row) == cfg.columns for row in fabric)

    def test_empty_text_yields_blank_fabric(self):
        cfg = BeadConfig(columns=10, rows=20)
        fabric = text_to_fabric('', cfg)
        # Empty text → no glyphs → all-zero output
        assert all(v == 0 for row in fabric for v in row)


class TestCenterInGrid:
    def test_centers_short_pattern(self):
        cfg = BeadConfig(columns=4, rows=10)
        # 2-row pattern in 10-row grid → top_pad = (10-2)//2 = 4
        pattern = [[1, 1, 1, 1], [1, 1, 1, 1]]
        result = _center_in_grid(pattern, cfg)
        assert len(result) == 10
        # rows 0-3 are blank, 4-5 contain pattern, 6-9 blank
        for r in (0, 1, 2, 3, 6, 7, 8, 9):
            assert all(v == 0 for v in result[r])
        for r in (4, 5):
            assert result[r] == [1, 1, 1, 1]

    def test_pads_short_rows(self):
        cfg = BeadConfig(columns=6, rows=4)
        pattern = [[1, 1]]  # only 2 wide → needs padding to 6
        result = _center_in_grid(pattern, cfg)
        assert all(len(row) == 6 for row in result)

    def test_truncates_wide_rows(self):
        cfg = BeadConfig(columns=4, rows=4)
        pattern = [[1, 1, 1, 1, 1, 1]]  # 6 wide → truncates to 4
        result = _center_in_grid(pattern, cfg)
        assert all(len(row) == 4 for row in result)

    def test_truncates_too_many_rows(self):
        cfg = BeadConfig(columns=4, rows=2)
        pattern = [[1] * 4 for _ in range(10)]
        result = _center_in_grid(pattern, cfg)
        assert len(result) == 2
