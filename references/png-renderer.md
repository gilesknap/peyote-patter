# Peyote Pattern PNG Renderer

Full working Python template. Install deps if needed:
```bash
pip install cairosvg Pillow --break-system-packages
```

---

## Complete template

```python
import cairosvg
from PIL import Image
import io

P='P'; R='R'  # add more colour codes as needed

# ── Colours ───────────────────────────────────────────────────────────────
colors    = {'P':'#E8A0A8', 'R':'#C82020', 'B':'#3a3c42'}
strokes_c = {'P':'#c07080', 'R':'#8a1010', 'B':'#111111'}
txtcol    = {'P':'#7a2a34', 'R':'#ffffff', 'B':'#e8e8e8'}

# ── Layout constants ──────────────────────────────────────────────────────
BW=22; BH=22; BM=1; RX=5
SLOT = BW + BM*2   # = 24px, one bead slot
WIDTH=10; HALF=5

# ── Fabric definition ─────────────────────────────────────────────────────
# Design here. Each row = one fabric row, 10 cols wide (0–9).
# Odd-indexed rows (0,2,4...) use cols 0,2,4,6,8
# Even-indexed rows (1,3,5...) use cols 1,3,5,7,9
# Double up rows for visible strokes (single rows look thin).
fabric = [
    # Example: full crossbar
    [1,1,1,1,1,1,1,1,1,1],  # row 0 — odd cols active
    [1,1,1,1,1,1,1,1,1,1],  # row 1 — even cols active
    # ... etc
]

# ── Bead element ──────────────────────────────────────────────────────────
def bead_el(x, y, ck, label=True):
    f,s,t = colors[ck], strokes_c[ck], txtcol[ck]
    el = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{BW}" height="{BH}" rx="{RX}" '
          f'fill="{f}" stroke="{s}" stroke-width="1"/>')
    if label:
        el += (f'<text x="{x+BW/2:.1f}" y="{y+BH/2+4:.1f}" text-anchor="middle" '
               f'font-size="9" font-weight="600" fill="{t}" '
               f'font-family="Arial,sans-serif">{ck}</text>')
    return el

def legend_els(codes_names, lx, PL):
    """codes_names = [('P','Pink'), ('R','Red'), ...]"""
    els = []
    x = PL
    for code, name in codes_names:
        els.append(f'<rect x="{x}" y="24" width="12" height="12" rx="3" '
                   f'fill="{colors[code]}" stroke="{strokes_c[code]}" stroke-width="1"/>'
                   f'<text x="{x+16}" y="35" font-size="10" fill="#555" '
                   f'font-family="Arial,sans-serif">{code}={name}</text>')
        x += 72
    return ''.join(els)

# ── FABRIC VIEW ───────────────────────────────────────────────────────────
# Interleaved brick-like finished fabric appearance.
# Row N (1-indexed): y = PT + (N-1)*BH/2
# Odd rows (N=1,3,5...): cols 0,2,4,6,8, x flush left
# Even rows (N=2,4,6...): cols 1,3,5,7,9, x_offset = SLOT (one full slot right)
def make_fabric_svg(fabric, title):
    PL=30; PT=46; PB=20; PR=30
    nrows = len(fabric)
    last_y = PT + (nrows-1) * BH/2
    SH = int(last_y + BH + PB)
    SW = PL + WIDTH*SLOT + SLOT + PR  # +SLOT for even row offset

    el = []
    el.append(f'<text x="{SW//2}" y="16" text-anchor="middle" font-size="13" '
              f'font-weight="600" fill="#333" font-family="Arial,sans-serif">'
              f'{title} — finished fabric</text>')
    el.append(legend_els([('P','Pink'),('R','Red')], PL, PL))

    for ri in range(nrows):
        N = ri + 1
        is_odd = (N % 2 == 1)
        fab_cols = [0,2,4,6,8] if is_odd else [1,3,5,7,9]
        x_offset = 0 if is_odd else SLOT
        y = PT + (N-1) * BH/2
        for fc in fab_cols:
            ck = R if fabric[ri][fc] else P
            bx = PL + x_offset + (fab_cols.index(fc)) * SLOT*2
            # IMPORTANT: use fabric col position directly, not bi*SLOT*2
            bx = PL + x_offset + fab_cols.index(fc) * SLOT * 2
            el.append(bead_el(bx, y, ck, label=False))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW}" height="{SH}" '
            f'viewBox="0 0 {SW} {SH}"><rect width="{SW}" height="{SH}" fill="white"/>'
            + ''.join(el) + '</svg>'), SW, SH

# ── PATTERN VIEW ──────────────────────────────────────────────────────────
# Flat working pattern. Y transform from fabric positions.
# X positions NEVER change — bead stays at x = PL + col*SLOT always.
#
# h = BH/2
# Row N dy:
#   N=1: 0        (no change)
#   N=2: -h       (lifts to merge with row 1 → "rows 1+2" combined start row)
#   N=3: 0        (no change)
#   N≥4: +h*(N-3) (pushed progressively down, spreading rows apart)
def make_pattern_svg(fabric, title):
    LABEL_W=52; ARROW_W=22
    PL = LABEL_W + ARROW_W + 8
    PT=46; PB=40
    SW = PL + WIDTH*SLOT + 40
    h = BH / 2.0

    def pattern_y(N):
        fabric_y = (N-1) * h
        if N == 1:   dy = 0
        elif N == 2: dy = -h
        elif N == 3: dy = 0
        else:        dy = h * (N-3)
        return fabric_y + dy

    nrows = len(fabric)
    SH = int(PT + pattern_y(nrows) + BH + PB)

    el = []
    el.append(f'<text x="{SW//2}" y="16" text-anchor="middle" font-size="13" '
              f'font-weight="600" fill="#333" font-family="Arial,sans-serif">'
              f'{title} — working pattern</text>')
    el.append(legend_els([('P','Pink'),('R','Red')], PL, PL))

    for ri in range(nrows):
        N = ri + 1
        py = PT + pattern_y(N)
        cy = py + BH/2 + 4
        is_odd = (N % 2 == 1)
        fab_cols = [0,2,4,6,8] if is_odd else [1,3,5,7,9]
        beads = [R if fabric[ri][c] else P for c in fab_cols]

        # Row label
        if N == 1:
            label, arrow = 'R1+2', '→'
        elif N == 2:
            label, arrow = '', ''        # merged with row 1, no separate label
        else:
            label = f'R{N+1}'            # pattern row number = fabric row + 1
            arrow = '←' if is_odd else '→'

        if label:
            el.append(f'<text x="{LABEL_W-4}" y="{cy:.1f}" text-anchor="end" '
                      f'font-size="10" font-weight="500" fill="#666" '
                      f'font-family="Arial,sans-serif">{label}</text>'
                      f'<text x="{LABEL_W+ARROW_W//2+4}" y="{cy:.1f}" '
                      f'text-anchor="middle" font-size="13" fill="#888" '
                      f'font-family="Arial,sans-serif">{arrow}</text>')

        # X: NEVER changes — use actual fabric column position
        for bi, b in enumerate(beads):
            col = fab_cols[bi]
            bx = PL + col * SLOT
            el.append(bead_el(bx, py, b))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW}" height="{SH}" '
            f'viewBox="0 0 {SW} {SH}"><rect width="{SW}" height="{SH}" fill="white"/>'
            + ''.join(el) + '</svg>'), SW, SH

# ── COMBINE AND SAVE ──────────────────────────────────────────────────────
def svg_to_pil(svg_str):
    png = cairosvg.svg2png(bytestring=svg_str.encode(), scale=2)
    return Image.open(io.BytesIO(png))

TITLE = 'My Pattern'
svg1, _, _ = make_pattern_svg(fabric, TITLE)
svg2, _, _ = make_fabric_svg(fabric, TITLE)
img1 = svg_to_pil(svg1)
img2 = svg_to_pil(svg2)

max_h = max(img1.height, img2.height)
def pad_h(img, h):
    if img.height == h: return img
    new = Image.new('RGBA', (img.width, h), (255,255,255,255))
    new.paste(img, (0,0))
    return new

img1 = pad_h(img1, max_h)
img2 = pad_h(img2, max_h)

GAP = 40
out = Image.new('RGBA', (img1.width + GAP + img2.width, max_h), (255,255,255,255))
out.paste(img1, (0,0))
out.paste(img2, (img1.width + GAP, 0))

PNG_PATH = '/mnt/user-data/outputs/peyote-pattern.png'
out.save(PNG_PATH)
print(f"Saved: {PNG_PATH}")
```

After saving, call `present_files([PNG_PATH])`.
