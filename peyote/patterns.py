"""Decorative pattern generators for peyote bead patterns.

All generators return list[list[int]] grids. Patterns are peyote-aware:
double-row minimum thickness, offset-aware diagonals.
"""

import math


def stripe_horizontal(columns: int, rows: int,
                      widths: list[int] | None = None,
                      colors: list[int] | None = None) -> list[list[int]]:
    """Horizontal stripes repeating vertically.

    Args:
        widths: Row count per stripe band (default [3, 3]).
        colors: Color index per band (default [1, 0]).
    """
    if widths is None:
        widths = [3, 3]
    if colors is None:
        colors = [1, 0]
    grid = []
    band_idx = 0
    band_row = 0
    for _ in range(rows):
        grid.append([colors[band_idx % len(colors)]] * columns)
        band_row += 1
        if band_row >= widths[band_idx % len(widths)]:
            band_row = 0
            band_idx += 1
    return grid


def stripe_vertical(columns: int, rows: int,
                    widths: list[int] | None = None,
                    colors: list[int] | None = None) -> list[list[int]]:
    """Vertical stripes running lengthwise."""
    if widths is None:
        widths = [2, 2]
    if colors is None:
        colors = [1, 0]
    # Build a single row template
    template = []
    band_idx = 0
    band_col = 0
    for _ in range(columns):
        template.append(colors[band_idx % len(colors)])
        band_col += 1
        if band_col >= widths[band_idx % len(widths)]:
            band_col = 0
            band_idx += 1
    return [list(template) for _ in range(rows)]


def chevron(columns: int, rows: int, width: int = 2,
            color: int = 1, bg: int = 0) -> list[list[int]]:
    """V-shaped chevron pattern repeating vertically.

    Uses double-row thickness for peyote visibility.
    """
    period = columns  # one full V per period
    grid = []
    for r in range(rows):
        row = [bg] * columns
        for w in range(width):
            pos = (r + w) % period
            # V shape: ascending and descending
            mid = columns // 2
            if pos < mid:
                col = pos
            else:
                col = columns - 1 - pos
            if 0 <= col < columns:
                row[col] = color
            mirror = columns - 1 - col
            if 0 <= mirror < columns:
                row[mirror] = color
        grid.append(row)
    return grid


def diamond(columns: int, rows: int, size: int = 4,
            color: int = 1, bg: int = 0) -> list[list[int]]:
    """Diamond/argyle pattern tiling."""
    grid = []
    for r in range(rows):
        row = [bg] * columns
        for c in range(columns):
            # Diamond distance from center of each tile
            cr = r % (size * 2)
            cc = c % (size * 2)
            dr = abs(cr - size)
            dc = abs(cc - size)
            if dr + dc <= size:
                # On the diamond edge
                if dr + dc >= size - 1:
                    row[c] = color
        grid.append(row)
    return grid


def zigzag(columns: int, rows: int, amplitude: int = 3,
           width: int = 2, color: int = 1, bg: int = 0) -> list[list[int]]:
    """Zigzag lines running down the length."""
    period = amplitude * 2
    grid = []
    for r in range(rows):
        row = [bg] * columns
        phase = r % period
        if phase < amplitude:
            center = phase
        else:
            center = period - phase
        # Scale to column range
        col = int(center * (columns - 1) / amplitude)
        for w in range(width):
            c = col + w
            if 0 <= c < columns:
                row[c] = color
        grid.append(row)
    return grid


def checker(columns: int, rows: int, block_size: int = 2,
            color: int = 1, bg: int = 0) -> list[list[int]]:
    """Checkerboard pattern with configurable block size."""
    grid = []
    for r in range(rows):
        row = []
        for c in range(columns):
            block_r = r // block_size
            block_c = c // block_size
            if (block_r + block_c) % 2 == 0:
                row.append(bg)
            else:
                row.append(color)
        grid.append(row)
    return grid


def border(columns: int, rows: int, thickness: int = 2,
           color: int = 1, bg: int = 0) -> list[list[int]]:
    """Border frame around the edges."""
    grid = []
    for r in range(rows):
        row = []
        for c in range(columns):
            if (r < thickness or r >= rows - thickness or
                    c < thickness or c >= columns - thickness):
                row.append(color)
            else:
                row.append(bg)
        grid.append(row)
    return grid


def dots(columns: int, rows: int, spacing: int = 4,
         color: int = 1, bg: int = 0) -> list[list[int]]:
    """Scattered dot pattern."""
    grid = []
    for r in range(rows):
        row = []
        for c in range(columns):
            if r % spacing == 0 and c % spacing == 0:
                row.append(color)
            elif r % spacing == spacing // 2 and c % spacing == spacing // 2:
                row.append(color)
            else:
                row.append(bg)
        grid.append(row)
    return grid


def wave(columns: int, rows: int, amplitude: int = 2,
         period: int = 8, width: int = 2,
         color: int = 1, bg: int = 0) -> list[list[int]]:
    """Sine wave pattern."""
    mid = columns // 2
    grid = []
    for r in range(rows):
        row = [bg] * columns
        offset = int(amplitude * math.sin(2 * math.pi * r / period))
        for w in range(width):
            c = mid + offset + w
            if 0 <= c < columns:
                row[c] = color
        grid.append(row)
    return grid


def gradient_dither(columns: int, rows: int, direction: str = 'vertical',
                    color: int = 1, bg: int = 0) -> list[list[int]]:
    """Dithered gradient from dense to sparse."""
    grid = []
    for r in range(rows):
        row = []
        for c in range(columns):
            if direction == 'vertical':
                density = r / max(rows - 1, 1)
            else:
                density = c / max(columns - 1, 1)
            # Ordered dithering (2x2 Bayer matrix)
            threshold_map = [[0.0, 0.5], [0.75, 0.25]]
            t = threshold_map[r % 2][c % 2]
            if density > t:
                row.append(color)
            else:
                row.append(bg)
        grid.append(row)
    return grid


def greek_key(columns: int, rows: int, size: int = 4,
              color: int = 1, bg: int = 0) -> list[list[int]]:
    """Greek key / meander border pattern."""
    # Build one tile of the meander
    tile_h = size * 2
    tile_w = size * 2
    tile = [[bg] * tile_w for _ in range(tile_h)]

    # Draw the key shape
    for i in range(tile_w):
        tile[0][i] = color                    # top bar
    for i in range(tile_h):
        tile[i][tile_w - 1] = color           # right bar
    for i in range(tile_w - 1):
        tile[tile_h - 1][i] = color           # bottom bar (partial)
    for i in range(2, tile_h):
        tile[i][0] = color                    # left bar (partial)
    for i in range(1, tile_w - 1):
        tile[2][i] = color                    # inner top bar

    # Tile it
    grid = []
    for r in range(rows):
        row = []
        for c in range(columns):
            row.append(tile[r % tile_h][c % tile_w])
        grid.append(row)
    return grid


PATTERN_CATALOG: dict[str, callable] = {
    'stripe-h': stripe_horizontal,
    'stripe-v': stripe_vertical,
    'chevron': chevron,
    'diamond': diamond,
    'zigzag': zigzag,
    'checker': checker,
    'border': border,
    'dots': dots,
    'wave': wave,
    'gradient': gradient_dither,
    'greek-key': greek_key,
}
