# peyote-pattern

A pattern generator for **even-count flat peyote stitch** beadwork. Design rings, bracelets, and bookmarks with text, decorative patterns, and freeform pixel editing — from a full CLI or an interactive NiceGUI visual designer with live preview.

Output fabric and pattern charts as PNG, SVG, PDF, or reloadable JSON.

## Features

- **Even-count peyote aware** — staggered columns respect the real thread path, with single beads at the start and doubled beads at the turnaround.
- **Text rendering** — any system TTF font, proportional widths, automatic stroke-width normalisation so narrow letters survive at low bead resolution.
- **17 decorative patterns** — 11 single-colour (stripes, chevron, diamond, zigzag, checker, border, dots, wave, gradient, Greek key, …) plus 6 two-colour (argyle, scales, flames, braid, honeycomb, kinetic).
- **Five layout modes** — Text Only, Text + Border, Text + Border Wrap (frames text on all four sides), Text + Background, Pattern Only.
- **Size presets** — ring, wide ring, bracelet, wide bracelet, bookmark — plus fully custom column / row counts.
- **10 named palettes** and 20 Miyuki Delica bead-code colour references.
- **Interactive editor** — click individual beads to customise, with zoom, pan, and row-by-row progress tracking.
- **Persistent state** — settings, custom edits, and row progress survive browser refresh via localStorage.
- **Save / load** — round-trip JSON files preserving the full design.

## Installation

Requires Python ≥ 3.12 and [`uv`](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/gilesknap/peyote-pattern.git
cd peyote-pattern
uv sync
```

System fonts used by the default catalogue: DejaVu Serif (preferred), DejaVu Sans, Liberation, Ubuntu. On Debian / Ubuntu:

```bash
sudo apt install fonts-dejavu fonts-liberation fonts-ubuntu
```

## Usage

### Visual designer (recommended)

```bash
uv run peyote-gui
```

Opens a browser-based designer with a settings panel and live preview. Features side-by-side fabric and pattern charts, per-colour bead counts, a pixel editor for custom tweaks, and save / load.

For development with hot-reload:

```bash
uv run python -m peyote.gui
```

### Command line

```bash
# A ring that says GILES
uv run peyote "GILES"

# Bracelet-sized HELLO with an ocean palette
uv run peyote "HELLO" --preset bracelet --palette ocean

# Text framed by a chevron border on all four sides
uv run peyote "LOVE" --border chevron --wrap-border --gap 2

# Pattern only, no text
uv run peyote --pattern kinetic --palette berry --preset wide-ring

# Export as PDF for printing
uv run peyote "JOY" --format pdf --output joy.pdf

# Print bead counts per colour
uv run peyote "HI" --bead-count
```

Full CLI help:

```bash
uv run peyote --help
```

## Concepts

### Layouts

| Layout                | Slots                                 | Description                                                                                  |
| --------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------- |
| Text Only             | Background · Text                     | Just the text.                                                                               |
| Text + Border         | Background · Text · Accent 1 · Accent 2 | Text with a decorative band above and below, auto-sized to fit.                              |
| Text + Border Wrap    | Background · Text · Accent 1 · Accent 2 | As above but the pattern wraps the side margins too, framing text on all four sides.         |
| Text + Background     | Background · Text · Accent 1 · Accent 2 | Text sits on top of a full-grid decorative pattern.                                          |
| Pattern Only          | Background · Accent 1 · Accent 2      | No text — the entire grid is the pattern.                                                    |

Pattern colour slots are shifted automatically so Accent 1 / 2 are never confused with the Text colour.

### Size presets

| Preset           | Columns | Rows | Notes                    |
| ---------------- | ------- | ---- | ------------------------ |
| `ring`           | 10      | 72   | Finger ring (default).   |
| `wide-ring`      | 20      | 72   | Chunkier ring.           |
| `bracelet`       | 40      | 180  | Standard cuff.           |
| `wide-bracelet`  | 50      | 200  | Wide cuff.               |
| `bookmark`       | 20      | 200  | Long bookmark strip.     |

Columns must always be even (required by even-count peyote). Row counts are approximate — ~0.9 mm per row of 11/0 Delicas, with wrist bracelets typically 2.5–3× the length of a finger ring.

### Margin, border, and gap

- **Margin** — blank background beads on the two long sides of the text (shrinks letter height).
- **Border** — decorative pattern bands at the strip ends (short sides). Auto-sized to land `gap` rows before the text.
- **Gap** — blank background rows between text and border (and, in Border Wrap mode, between text and the side strips).

### Colour palettes

Named palettes populate the four colour pickers (Background / Text / Accent 1 / Accent 2). You can then freely edit any picker — nothing locks the colour to the palette name.

Built-in palettes: `classic`, `ocean`, `earth`, `forest`, `sunset`, `monochrome`, `berry`, `gold`, `teal`, `day-to-night`.

The `MIYUKI_DELICA` dictionary in `peyote/colors.py` maps common 11/0 Delica bead codes to approximate hex colours for reference.

## Output formats

| Format | Notes                                                    |
| ------ | -------------------------------------------------------- |
| PNG    | Default. High-resolution raster.                         |
| SVG    | Vector, scalable, editable in Inkscape.                  |
| PDF    | Print-ready, fits both fabric and pattern views.         |
| JSON   | Round-trip format — reload into the GUI or CLI via `--fabric`. |

The CLI can emit `fabric` only, `pattern` only, or `both` via `--view`.

## Project layout

```
peyote/
├── sizing.py       # BeadConfig + presets
├── colors.py       # Palettes and Miyuki Delica reference
├── grid.py         # Grid primitives (blank, mirror, tile, overlay, count_beads)
├── font_ttf.py     # TTF-to-bitmap via Pillow, stroke normalisation
├── font.py         # text_to_fabric composition
├── patterns.py     # 17 decorative pattern generators
├── compose.py      # Layer composition: text + border, pattern only, wrap_border
├── renderer.py     # SVG renderers for fabric and pattern views
├── editor.py       # Pixel editor (GUI)
├── export.py       # PNG / SVG / PDF / JSON output
├── cli.py          # Command-line entry point
└── gui.py          # NiceGUI visual designer
```

## Development

```bash
uv sync
uv run pytest              # run the test suite
uv run python -m peyote.gui  # dev GUI with hot-reload
```

The NiceGUI server hot-reloads on file save — no need to restart it during development.

## Contributing

Issues and pull requests are welcome. The project uses `uv` for dependency management and `pytest` for testing.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.

Copyright 2026 Giles Knap.
