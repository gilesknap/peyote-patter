"""Unit tests for peyote.editor — pure logic, no NiceGUI."""

from peyote.colors import ColorPalette
from peyote.editor import (
    EditorState, add_palette_color, bead_center, clear_fabric,
    cut, fabric_from_json, fabric_to_json, flood_fill, get_selection,
    hit_test, paint_circle, paint_line, paint_pencil, paint_rect,
    paste_at, push_history, redo, undo, use_color,
)
from peyote.grid import blank_grid
from peyote.sizing import BeadConfig


def _make_state(columns=20, rows=40, active_color=1):
    config = BeadConfig(columns=columns, rows=rows)
    fabric = blank_grid(config, fill=0)
    palette = ColorPalette.from_pairs([("#ffffff", "White"), ("#000000", "Black")])
    state = EditorState(
        fabric=fabric, config=config, palette=palette, title="t",
        snapshot=[r[:] for r in fabric],
        snapshot_palette=ColorPalette.from_pairs([("#ffffff", "White")]),
        active_color=active_color,
    )
    return state


# ─── hit_test ──────────────────────────────────────────────────────────

def test_hit_test_dead_center():
    config = BeadConfig(columns=20, rows=40)
    fabric = blank_grid(config)
    # Row 0 (N=1, odd), fabric col 0 — center should hit
    cx, cy = bead_center(0, 0, config)
    assert hit_test(cx, cy, fabric, config) == (0, 0)
    # Row 1 (N=2, even), fabric col 1 — center should hit
    cx, cy = bead_center(1, 1, config)
    assert hit_test(cx, cy, fabric, config) == (1, 1)


def test_hit_test_all_quadrants():
    config = BeadConfig(columns=20, rows=40)
    fabric = blank_grid(config)
    # Row 0,N=1 odd → even fcs active; row 39,N=40 even → odd fcs active.
    for ri, fc in [(0, 0), (0, 18), (39, 1), (39, 19)]:
        cx, cy = bead_center(ri, fc, config)
        assert hit_test(cx, cy, fabric, config) == (ri, fc)


def test_hit_test_just_inside_edge():
    config = BeadConfig(columns=20, rows=40)
    fabric = blank_grid(config)
    # Row 5 is N=6, even → odd fcs active. Use fc=5.
    cx, cy = bead_center(5, 5, config)
    eps = 0.1
    hw, hh = config.bead_width / 2 - eps, config.bead_height / 2 - eps
    for dx, dy in [(hw, 0), (-hw, 0), (0, hh), (0, -hh)]:
        assert hit_test(cx + dx, cy + dy, fabric, config) == (5, 5)


def test_hit_test_gutter_returns_none():
    config = BeadConfig(columns=20, rows=40)
    fabric = blank_grid(config)
    # A click midway between row-0 beads at fc=0 and fc=2, at y=PT (top edge
    # of row 0), is above row 1 and between beads on row 0 — a true gutter.
    cx_0, _ = bead_center(0, 0, config)
    cx_2, _ = bead_center(0, 2, config)
    gx = (cx_0 + cx_2) / 2
    from peyote.editor import PT
    assert hit_test(gx, PT, fabric, config) is None


def test_hit_test_outside_both_parities():
    config = BeadConfig(columns=20, rows=40)
    fabric = blank_grid(config)
    # Y midway between rows 0 and 1, X at a position that's in a gutter
    # for both parities (halfway between their bead centers).
    _, y0 = bead_center(0, 0, config)
    _, y1 = bead_center(1, 1, config)
    cy = (y0 + y1) / 2
    # This cy should still be valid (rows overlap), but choose x far off-grid
    assert hit_test(-50, cy, fabric, config) is None


def test_hit_test_single_row_edge():
    config = BeadConfig(columns=10, rows=1)
    fabric = blank_grid(config)
    cx, cy = bead_center(0, 0, config)
    assert hit_test(cx, cy, fabric, config) == (0, 0)
    cx, cy = bead_center(0, 8, config)
    assert hit_test(cx, cy, fabric, config) == (0, 8)


def test_hit_test_last_row():
    config = BeadConfig(columns=10, rows=5)
    fabric = blank_grid(config)
    cx, cy = bead_center(4, 0, config)  # N=5, odd
    assert hit_test(cx, cy, fabric, config) == (4, 0)


# ─── paint_* ────────────────────────────────────────────────────────────

def test_paint_pencil_writes_and_idempotent():
    state = _make_state()
    assert paint_pencil(state, 0, 0) is True
    assert state.fabric[0][0] == 1
    # Second call returns False (no change)
    assert paint_pencil(state, 0, 0) is False


def test_paint_pencil_rejects_inactive_cell():
    state = _make_state()
    # Row 0 (N=1, odd) — fc=1 is inactive
    assert paint_pencil(state, 0, 1) is False
    assert state.fabric[0][1] == 0


def test_paint_line_horizontal_active_only():
    state = _make_state()
    # Horizontal line across row 0 (odd): active fcs are 0,2,4,...
    paint_line(state.fabric, state.config, (0, 0), (0, 10), color=1)
    # Every even fc from 0..10 should be 1
    assert all(state.fabric[0][fc] == 1 for fc in (0, 2, 4, 6, 8, 10))
    # Odd cells should remain 0
    assert all(state.fabric[0][fc] == 0 for fc in (1, 3, 5, 7, 9))


def test_paint_line_diagonal():
    state = _make_state()
    paint_line(state.fabric, state.config, (0, 0), (4, 4), color=1)
    # At least the endpoints should be painted
    assert state.fabric[0][0] == 1
    assert state.fabric[4][4] == 1


def test_paint_rect_outline_vs_fill():
    state = _make_state()
    # Outline rect, ri 2..4, fc 0..4 (all active — odd rows have even fc, even rows have odd fc)
    paint_rect(state.fabric, state.config, (2, 0), (4, 4), color=1, fill=False)
    outlined = sum(row.count(1) for row in state.fabric)

    state2 = _make_state()
    paint_rect(state2.fabric, state2.config, (2, 0), (4, 4), color=1, fill=True)
    filled = sum(row.count(1) for row in state2.fabric)

    assert outlined > 0
    assert filled > outlined


def test_paint_circle_writes_pixels():
    state = _make_state()
    # Circle on a 20x40 grid
    paint_circle(state.fabric, state.config, (20, 10), (20, 14), color=1)
    written = sum(row.count(1) for row in state.fabric)
    assert written > 0


def test_flood_fill_respects_adjacency():
    state = _make_state()
    # Paint an isolated cell; flood fill should only fill reachable region
    state.fabric[0][0] = 0  # already 0
    flood_fill(state.fabric, state.config, 0, 0, color=1)
    # All active cells should flip to 1 (fully connected blank fabric)
    total_active = 0
    for ri in range(state.config.rows):
        for fc in state.config.cols_for_row(ri):
            total_active += 1
            assert state.fabric[ri][fc] == 1


def test_flood_fill_stops_at_boundary():
    state = _make_state()
    # Draw a horizontal barrier on row 5
    for fc in state.config.cols_for_row(5):
        state.fabric[5][fc] = 2
    # Also block row 4 — peyote neighbours are (ri±1, fc±1); barrier on
    # adjacent rows above and below row 6 isolates row 6+.
    # Actually: flood from (0,0). Neighbours include (1, fc±1). The barrier
    # on row 5 blocks traversal through any row-5 cell (since color != orig).
    flood_fill(state.fabric, state.config, 0, 0, color=1)
    # Row 6+ should remain 0
    for ri in range(6, state.config.rows):
        for fc in state.config.cols_for_row(ri):
            assert state.fabric[ri][fc] == 0, f"leak at ({ri},{fc})"
    # Rows 0..4 should be 1
    for ri in range(5):
        for fc in state.config.cols_for_row(ri):
            assert state.fabric[ri][fc] == 1


def test_clear_fabric_sets_all_cells():
    state = _make_state()
    clear_fabric(state.fabric, 3)
    assert all(v == 3 for row in state.fabric for v in row)


# ─── Palette ───────────────────────────────────────────────────────────

def test_add_palette_color_dedupes():
    palette = ColorPalette.from_pairs([("#ffffff", "W"), ("#000000", "B")])
    idx_a = add_palette_color(palette, "#ff0000", "Red")
    assert idx_a == 2
    # Same hex (different case) returns existing
    idx_b = add_palette_color(palette, "#FF0000")
    assert idx_b == idx_a
    assert len(palette.colors) == 3


def test_add_palette_color_generates_stroke_and_text_color():
    palette = ColorPalette.from_pairs([("#ffffff", "W")])
    idx = add_palette_color(palette, "#ff0000")
    assert idx in palette.strokes
    assert idx in palette.text_colors
    assert palette.names[idx] == "Custom 1"


def test_use_color_bumps_recent_mru():
    state = _make_state()
    use_color(state, 1)
    use_color(state, 2)
    use_color(state, 1)  # re-select
    assert state.recent_colors[0] == 1
    assert state.recent_colors[1] == 2
    assert state.active_color == 1


# ─── History ───────────────────────────────────────────────────────────

def test_push_history_and_undo_roundtrip():
    state = _make_state()
    for i in range(5):
        push_history(state)
        paint_pencil(state, i, i * 2 if (i + 1) % 2 == 1 else i * 2 + 1)
    # Current: 5 mutations done, history has 5 entries
    for _ in range(5):
        assert undo(state) is True
    # After 5 undos, fabric should be empty again
    assert all(v == 0 for row in state.fabric for v in row)


def test_redo_replays_mutations():
    state = _make_state()
    push_history(state)
    paint_pencil(state, 0, 0)
    assert state.fabric[0][0] == 1
    undo(state)
    assert state.fabric[0][0] == 0
    redo(state)
    assert state.fabric[0][0] == 1


def test_new_mutation_clears_redo_stack():
    state = _make_state()
    push_history(state)
    paint_pencil(state, 0, 0)
    undo(state)
    push_history(state)  # starts a new branch — redo should be cleared
    assert state.redo_stack == []


# ─── Selection / clipboard ─────────────────────────────────────────────

def test_get_selection_inactive_cells_are_none():
    state = _make_state()
    paint_pencil(state, 0, 0)
    paint_pencil(state, 1, 1)
    sel = get_selection(state.fabric, state.config, (0, 0, 1, 1))
    # Row 0 (odd-N): fc 0 active, fc 1 inactive → None
    assert sel[0][0] == 1
    assert sel[0][1] is None
    # Row 1 (even-N): fc 0 inactive → None, fc 1 active → 1
    assert sel[1][0] is None
    assert sel[1][1] == 1


def test_cut_and_paste_roundtrip():
    state = _make_state()
    paint_pencil(state, 0, 0)
    paint_pencil(state, 0, 2)
    state.selection = (0, 0, 0, 2)
    cut(state)
    # After cut, those cells are 0
    assert state.fabric[0][0] == 0
    assert state.fabric[0][2] == 0
    # Paste back at origin
    paste_at(state.fabric, state.config, state.clipboard, 0, 0)
    assert state.fabric[0][0] == 1
    assert state.fabric[0][2] == 1


# ─── JSON I/O ──────────────────────────────────────────────────────────

def test_json_roundtrip_identity():
    state = _make_state()
    # Make a non-trivial pattern
    paint_pencil(state, 0, 0)
    paint_pencil(state, 5, 5)
    paint_pencil(state, 10, 8)

    s = fabric_to_json(state)
    fabric2, config2, palette2, title2 = fabric_from_json(s)
    assert fabric2 == state.fabric
    assert config2.columns == state.config.columns
    assert config2.rows == state.config.rows
    assert palette2.colors == state.palette.colors
    assert title2 == state.title
