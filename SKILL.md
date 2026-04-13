---
name: peyote-pattern
description: >
  Render an even-count flat peyote stitch bead pattern as a PNG with two
  side-by-side views: a finished fabric preview and a flat working pattern.
  Use this skill whenever the user provides beading instructions, a peyote
  pattern, bead counts per row, or a photo of a beading chart and asks to
  display, blow up, visualise, or make it easier to follow. Also trigger when
  the user wants to design a new pattern (e.g. text or motifs). Always use
  this skill for peyote / bead weaving pattern requests — do not attempt to
  render ad-hoc without reading the references first.
---

# Peyote Pattern Skill

Produces a combined PNG with two views side by side:
1. **Fabric view** (right) — the finished interleaved look, used for design work
2. **Pattern view** (left) — the flat working pattern used while beading

---

## Core workflow

1. **Design in fabric space** — define the pattern as a 2D grid (`fabric[][]`),
   10 cols wide, N rows tall. Each cell is 0 (background) or 1 (accent colour).
   This is the ground truth. Do NOT try to design in pattern space.

2. **Render fabric view** — using the interleave geometry in `references/png-renderer.md`

3. **Derive pattern view** — by applying the Y transform to fabric positions.
   X positions NEVER change. See transform rules below.

4. **Combine side by side** using Pillow and save as PNG.

5. **Present** with `present_files`.

---

## Even-count peyote fabric geometry

- **Width**: must be even (e.g. 10 cols, indexed 0–9)
- **Rows**: fabric rows are indexed 0, 1, 2 ... (0 = topmost)
- **Odd fabric rows** (index 0, 2, 4 ...): use cols 0,2,4,6,8
- **Even fabric rows** (index 1, 3, 5 ...): use cols 1,3,5,7,9
- Each row has WIDTH/2 = 5 beads

In the **fabric view**, row N (1-indexed) sits at:
```
y = PT + (N-1) * BH/2
```
Odd rows flush left, even rows x-offset = SLOT (one full bead slot right).

---

## Fabric → Pattern Y transform

`h = BH/2` (half bead height = 11px for BW=BH=22)

Fabric row N (1-indexed) → pattern y:

| Row | dy | Result |
|-----|----|--------|
| N=1 | 0 | stays put |
| N=2 | −h | lifts up to merge with row 1 (forms the "rows 1+2" combined start) |
| N=3 | 0 | stays put |
| N≥4 | +h*(N−3) | pushed progressively down |

```python
def pattern_y(N, h):
    fabric_y = (N-1) * h
    if N == 1:   dy = 0
    elif N == 2: dy = -h
    elif N == 3: dy = 0
    else:        dy = h * (N-3)
    return fabric_y + dy
```

**X positions are NEVER changed** in the transform. Each bead stays at
`x = PL + col * SLOT` where `col` is its fabric column index.

---

## Pattern view labels

- Row 1 → labelled `R1+2` with arrow `→` (rows 1 and 2 are strung together)
- Row 2 → no label (merged visually with row 1)
- Row N (N≥3) → labelled `R{N+1}` (pattern row numbers are offset by +1 vs fabric)
  - Odd N → arrow `←`
  - Even N → arrow `→`

---

## Designing letter/text patterns

Design letters **directly in fabric space** (no rotation needed):
- Each row of the fabric grid = one row of beads in the finished piece
- The fabric reads top-to-bottom as the piece will be worn/read
- Use double-row strokes for visibility (single rows look thin in the fabric)

See `references/png-renderer.md` for the full Python template.

---

## Key gotchas (hard-won)

| Issue | Wrong | Right |
|-------|-------|-------|
| Design space | Design in pattern space, rotate | Design in fabric space directly |
| X in pattern view | Apply offset to even rows | X never changes — use fabric col * SLOT |
| Even row x in fabric view | No offset | x_offset = SLOT (one full bead slot) |
| Bead shape | Rectangular | Square: BW = BH = 22px |
| Row 2 dy | −0.5h | −h (lifts fully to merge with row 1) |
| Row N≥4 dy | h*(N−3)/2 | h*(N−3) |
| Bead label | Letter + col number | Letter only |
| Title/legend overlap | Single PAD_TOP | Title y=16, legend y=24/35, PAD_TOP=46 |
