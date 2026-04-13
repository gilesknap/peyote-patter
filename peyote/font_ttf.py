"""TTF-to-bitmap font rendering engine for scalable peyote patterns."""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Search paths for monospace fonts
_FONT_SEARCH = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
    '/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf',
]


def find_default_font() -> str:
    """Find a suitable monospace font on the system."""
    for path in _FONT_SEARCH:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "No suitable TTF font found. Install dejavu or liberation fonts, "
        "or specify a font path with --font-path."
    )


def render_char_bitmap(
    char: str,
    columns: int,
    char_height: int,
    font_path: str | None = None,
    threshold: int = 128,
    dilate: bool = False,
) -> list[list[int]]:
    """Render a single character to a binary bitmap grid.

    Args:
        char: Single character to render.
        columns: Target width in bead columns.
        char_height: Target height in bead rows.
        font_path: Path to TTF font file. Auto-detected if None.
        threshold: Binarization threshold (0-255).
        dilate: Apply morphological dilation for thicker strokes.

    Returns:
        char_height x columns grid of 0/1 values.
    """
    if font_path is None:
        font_path = find_default_font()

    # Render at ~10x target size for quality
    render_size = max(columns, char_height) * 10
    font_size = int(render_size * 0.8)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except (IOError, OSError):
        raise FileNotFoundError(f"Cannot load font: {font_path}")

    # Draw character on grayscale canvas
    canvas_size = render_size * 2
    img = Image.new('L', (canvas_size, canvas_size), color=0)
    draw = ImageDraw.Draw(img)
    draw.text((canvas_size // 4, canvas_size // 8), char, font=font, fill=255)

    # Crop to tight bounding box
    bbox = img.getbbox()
    if bbox is None:
        # Blank character (e.g., space)
        return [[0] * columns for _ in range(char_height)]
    img = img.crop(bbox)

    # Resize to target dimensions
    img = img.resize((columns, char_height), Image.Resampling.LANCZOS)

    # Optional dilation for thicker strokes
    if dilate:
        img = img.filter(ImageFilter.MaxFilter(size=3))

    # Threshold to binary
    grid = []
    for y in range(char_height):
        row = []
        for x in range(columns):
            pixel = img.getpixel((x, y))
            row.append(1 if pixel > threshold else 0)
        grid.append(row)

    return grid


def render_text_rows(
    text: str,
    columns: int,
    char_height: int | None = None,
    char_spacing: int = 2,
    font_path: str | None = None,
    rotate: bool = True,
    dilate: bool = False,
) -> list[list[int]]:
    """Render text to pixel rows using TTF rendering.

    Args:
        text: Text to render.
        columns: Bead column count of the piece.
        char_height: Rows per character. Auto-calculated if None.
        char_spacing: Blank rows between characters.
        font_path: Path to TTF font. Auto-detected if None.
        rotate: If True, render upright then rotate 90 CW (for sideways reading).
        dilate: Apply morphological dilation.

    Returns:
        List of rows, each `columns` wide.
    """
    text = text.upper()

    if rotate:
        # Render upright: glyph is columns-tall x char_width-wide
        # After 90 CW rotation: char_width rows x columns cols
        glyph_height = columns  # reading height = strip width
        if char_height is None:
            char_height = max(5, int(columns * 0.7))  # reading width
        glyph_width = char_height
    else:
        # Render straight: glyph fills columns width
        glyph_width = columns
        if char_height is None:
            char_height = max(7, int(columns * 1.4))
        glyph_height = char_height

    if font_path is None:
        font_path = find_default_font()

    rows: list[list[int]] = []
    for i, ch in enumerate(text):
        if i > 0:
            if rotate:
                for _ in range(char_spacing):
                    rows.append([0] * columns)
            else:
                for _ in range(char_spacing):
                    rows.append([0] * columns)

        glyph = render_char_bitmap(ch, glyph_width, glyph_height,
                                   font_path=font_path, dilate=dilate)

        if rotate:
            # Rotate 90 CW: H rows x W cols -> W rows x H cols
            h = len(glyph)
            w = len(glyph[0]) if glyph else 0
            rotated = []
            for c in range(w):
                row = []
                for r in range(h - 1, -1, -1):
                    row.append(glyph[r][c])
                rotated.append(row)
            rows.extend(rotated)
        else:
            rows.extend(glyph)

    return rows
