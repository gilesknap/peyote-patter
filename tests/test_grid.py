"""Tests for peyote.grid."""

from peyote.grid import (
    blank_grid,
    count_beads,
    mirror_horizontal,
    mirror_vertical,
    overlay,
    tile,
)
from peyote.sizing import BeadConfig


class TestBlankGrid:
    def test_default_zeros(self, small_config):
        g = blank_grid(small_config)
        assert len(g) == small_config.rows
        assert all(len(row) == small_config.columns for row in g)
        assert all(v == 0 for row in g for v in row)

    def test_custom_fill(self, small_config):
        g = blank_grid(small_config, fill=3)
        assert all(v == 3 for row in g for v in row)


class TestCountBeads:
    def test_counts_only_active_columns(self):
        cfg = BeadConfig(columns=4, rows=2)
        # row 0 (N=1): active cols are [0, 2]
        # row 1 (N=2): active cols are [1, 3]
        fabric = [
            [1, 9, 1, 9],   # only cols 0,2 counted → 1, 1
            [9, 2, 9, 2],   # only cols 1,3 counted → 2, 2
        ]
        counts = count_beads(fabric, cfg)
        assert counts == {1: 2, 2: 2}

    def test_blank_grid_count(self, tiny_config):
        g = blank_grid(tiny_config)
        counts = count_beads(g, tiny_config)
        # Half the cells per row are active, total = rows * (cols/2)
        expected = tiny_config.rows * (tiny_config.columns // 2)
        assert counts == {0: expected}

    def test_returns_plain_dict(self, tiny_config):
        # not a defaultdict (so unknown keys raise)
        counts = count_beads(blank_grid(tiny_config), tiny_config)
        assert type(counts) is dict


class TestMirror:
    def test_mirror_horizontal_reverses_each_row(self):
        g = [[1, 2, 3], [4, 5, 6]]
        assert mirror_horizontal(g) == [[3, 2, 1], [6, 5, 4]]

    def test_mirror_vertical_reverses_row_order(self):
        g = [[1, 2], [3, 4], [5, 6]]
        assert mirror_vertical(g) == [[5, 6], [3, 4], [1, 2]]

    def test_mirror_horizontal_palindrome_unchanged(self):
        g = [[1, 2, 2, 1]]
        assert mirror_horizontal(g) == g


class TestTile:
    def test_tile_replicates_pattern(self):
        src = [[1, 2], [3, 4]]
        result = tile(src, 4, 4)
        assert result == [
            [1, 2, 1, 2],
            [3, 4, 3, 4],
            [1, 2, 1, 2],
            [3, 4, 3, 4],
        ]

    def test_tile_smaller_than_source(self):
        src = [[1, 2, 3], [4, 5, 6]]
        result = tile(src, 1, 2)
        assert result == [[1, 2]]

    def test_tile_empty_source_returns_zeros(self):
        result = tile([], 3, 4)
        assert result == [[0] * 4 for _ in range(3)]

    def test_tile_empty_rows_returns_zeros(self):
        # rows present but empty (no cols) → also handled
        result = tile([[]], 2, 3)
        assert result == [[0] * 3 for _ in range(2)]


class TestOverlay:
    def test_nonzero_overwrites(self):
        base = [[0, 0, 0], [0, 0, 0]]
        top = [[1, 0, 2], [0, 3, 0]]
        assert overlay(base, top) == [[1, 0, 2], [0, 3, 0]]

    def test_zero_does_not_overwrite(self):
        base = [[1, 1], [1, 1]]
        top = [[0, 0], [0, 0]]
        assert overlay(base, top) == [[1, 1], [1, 1]]

    def test_offset_positions(self):
        base = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        top = [[5]]
        assert overlay(base, top, offset_row=1, offset_col=1) == [
            [0, 0, 0],
            [0, 5, 0],
            [0, 0, 0],
        ]

    def test_overlay_clips_off_grid(self):
        base = [[0, 0], [0, 0]]
        top = [[7, 7], [7, 7]]
        # offset places top mostly off the grid
        result = overlay(base, top, offset_row=1, offset_col=1)
        assert result == [[0, 0], [0, 7]]

    def test_overlay_returns_copy(self):
        base = [[1, 2], [3, 4]]
        result = overlay(base, [[0, 0], [0, 0]])
        assert result == base
        assert result is not base
        assert result[0] is not base[0]
