"""Grid utilities for peyote fabric manipulation."""

from collections import defaultdict

from .sizing import BeadConfig


def blank_grid(config: BeadConfig, fill: int = 0) -> list[list[int]]:
    """Create a blank fabric grid filled with a single color index."""
    return [[fill] * config.columns for _ in range(config.rows)]


def count_beads(fabric: list[list[int]], config: BeadConfig) -> dict[int, int]:
    """Count beads by color index, only counting active columns per row."""
    counts: dict[int, int] = defaultdict(int)
    for ri, row in enumerate(fabric):
        for col in config.cols_for_row(ri):
            counts[row[col]] += 1
    return dict(counts)


def mirror_horizontal(grid: list[list[int]]) -> list[list[int]]:
    """Mirror a grid left-to-right."""
    return [row[::-1] for row in grid]


def mirror_vertical(grid: list[list[int]]) -> list[list[int]]:
    """Mirror a grid top-to-bottom."""
    return grid[::-1]


def tile(grid: list[list[int]], target_rows: int, target_cols: int) -> list[list[int]]:
    """Tile a pattern to fill target dimensions."""
    src_rows = len(grid)
    src_cols = len(grid[0]) if grid else 0
    if src_rows == 0 or src_cols == 0:
        return [[0] * target_cols for _ in range(target_rows)]
    result = []
    for r in range(target_rows):
        row = []
        for c in range(target_cols):
            row.append(grid[r % src_rows][c % src_cols])
        result.append(row)
    return result


def overlay(base: list[list[int]], top: list[list[int]],
            offset_row: int = 0, offset_col: int = 0) -> list[list[int]]:
    """Overlay top grid onto base. Non-zero values in top overwrite base."""
    result = [row[:] for row in base]
    base_rows = len(base)
    base_cols = len(base[0]) if base else 0
    for r, row in enumerate(top):
        tr = r + offset_row
        if 0 <= tr < base_rows:
            for c, val in enumerate(row):
                tc = c + offset_col
                if val != 0 and 0 <= tc < base_cols:
                    result[tr][tc] = val
    return result
