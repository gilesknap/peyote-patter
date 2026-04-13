Generate a peyote bead pattern: $ARGUMENTS

Use the Python tools in this project to generate peyote stitch bead patterns.

## Quick reference

```bash
cd /home/giles/code/peyote-pattern

# Text on a ring (10 columns, sideways reading)
uv run peyote "TEXT"

# Text on a bracelet (40 columns, TTF font)
uv run peyote "HELLO WORLD" --preset bracelet

# Pattern only
uv run peyote --pattern chevron --palette ocean

# Text with decorative borders
uv run peyote "GILES" --border chevron --border-rows 8

# Bead shopping list
uv run peyote "HELLO" --bead-count

# Launch GUI
uv run python -m peyote.gui
```

## Size presets

| Preset | Columns | Rows | Use |
|--------|---------|------|-----|
| ring | 10 | 72 | Standard ring (default) |
| wide-ring | 20 | 72 | Wider ring / thin cuff |
| bracelet | 40 | 120 | Standard bracelet |
| wide-bracelet | 50 | 150 | Wide cuff |
| bookmark | 20 | 200 | Tall narrow piece |
| custom | any even | any | Use --columns and --rows |

## Character capacity (ring, sideways text)

Each char = 7 rows + 2 spacing = 9 rows:
- 72 rows -> ~8 characters
- 100 rows -> ~11 characters

## All CLI options

- `--preset NAME` — size preset
- `--columns N` — bead columns (must be even)
- `--rows N` — fabric rows
- `--font auto|ttf|bitmap` — font engine
- `--font-path PATH` — custom TTF font
- `--orientation sideways|straight` — text direction
- `--pattern NAME` — decorative pattern (no text)
- `--border NAME` — border pattern around text
- `--border-rows N` — rows per border band
- `--bg-color HEX` / `--fg-color HEX` — bead colors
- `--palette NAME` — named palette (classic, ocean, earth, forest, sunset, monochrome, berry, gold, teal)
- `--format png|svg|pdf|json` — output format
- `--view both|pattern|fabric` — which view to render
- `--bead-count` — print bead count summary
- `--no-open` — don't open result

## Patterns available

stripe-h, stripe-v, chevron, diamond, zigzag, checker, border, dots, wave, gradient, greek-key

## GUI

Run `uv run python -m peyote.gui` to launch the visual designer at http://localhost:8080 with live preview, color pickers, pattern selection, and download buttons.
