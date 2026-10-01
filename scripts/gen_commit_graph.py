#!/usr/bin/env python3
"""
Generate assets/dashboard/commit-graph.svg — a contribution-style activity grid
with SMIL animation, rendered in the project design system.

The pattern is a fixed seed so the layout is stable across runs (GitHub caches
images; you do not want the graph reshuffling every time you regenerate).

Usage:
    python3 scripts/gen_commit_graph.py
    python3 scripts/gen_commit_graph.py --seed 7 --out assets/dashboard/commit-graph.svg
"""

from __future__ import annotations

import argparse
import random

# ── Design system tokens (keep in sync with DESIGN_SYSTEM.md) ────────────────
BG = "#0A0E14"
BORDER = "#1C2530"
LINE = "#1C2530"
LINE_HI = "#2A3644"
TEXT = "#C9D4E0"
TEXT_DIM = "#7A8B9C"
TEXT_FAINT = "#46586A"
CYAN = "#4DD9E8"

# Activity ramp: empty -> 5 levels, dim cyan. Deliberately NOT GitHub's green.
LEVELS = ["#0E1A20", "#123039", "#17495A", "#1E6E86", CYAN]
EMPTY = "#0A0E14"

W, H = 900, 200
COLS, ROWS = 53, 7
CELL, GAP = 11, 3
PAD_X, PAD_Y = 40, 58
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Cells that periodically "pop" to a new level: (col, row, to_level, begin)
# Hand-picked so the motion feels organic rather than random per load.
POPS = [
    (6, 2, 3, "-3.0s"), (11, 5, 4, "-7.5s"), (14, 1, 2, "-1.5s"),
    (19, 4, 4, "-9.0s"), (23, 0, 1, "-5.0s"), (26, 6, 3, "-11.0s"),
    (30, 3, 4, "-2.0s"), (34, 2, 2, "-8.0s"), (37, 5, 3, "-4.0s"),
    (41, 1, 4, "-10.0s"), (45, 3, 2, "-0.5s"), (48, 6, 3, "-6.0s"),
]


def build(seed: int) -> str:
    rng = random.Random(seed)
    cells: list[tuple[int, int, int]] = []
    # A believable activity profile: a weekday rhythm with bursty weeks.
    for c in range(COLS):
        week_energy = rng.uniform(0.15, 1.0)
        for r in range(ROWS):
            is_weekend = r >= 5
            # Real contribution graphs are sparse; this keeps empty cells
            # readable as "no activity" rather than a solid block of colour.
            base = 0.10 if is_weekend else 0.30
            p = min(0.86, base + week_energy * 0.42)
            if rng.random() < p:
                level = min(4, 1 + int(rng.random() * 4 * week_energy))
            else:
                level = 0
            cells.append([c, r, level])

    grid_w = COLS * (CELL + GAP) - GAP

    out: list[str] = []
    add = out.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">')
    add('  <title id="t">Contribution activity graph</title>')
    add('  <desc id="d">A seven-row by fifty-three-column activity heatmap for the last '
        'twelve months. The pattern is simulated for visual demonstration and is not '
        'live GitHub data.</desc>')
    add(f'  <rect width="{W}" height="{H}" fill="{BG}"/>')

    # ── header strip ────────────────────────────────────────────────────────
    add(f'  <text x="{PAD_X}" y="26" font-family="{MONO}" font-size="10" fill="{TEXT_DIM}" '
        f'letter-spacing="1.3">COMMIT ACTIVITY \u00b7 last 12 months</text>')
    add(f'  <text x="{W - PAD_X}" y="26" text-anchor="end" font-family="{MONO}" font-size="10" '
        f'fill="{TEXT_FAINT}" letter-spacing="0.8">1,284 contributions \u00b7 sha a3f91c4</text>')

    # ── legend, on its own row so it never collides with the grid ───────────
    lx = W - PAD_X - 5 * (CELL + GAP) + GAP
    ly = 40
    add(f'  <text x="{lx - 10}" y="{ly + CELL - 2}" text-anchor="end" font-family="{MONO}" '
        f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">less</text>')
    for i, col in enumerate(LEVELS):
        add(f'  <rect x="{lx + i * (CELL + GAP)}" y="{ly}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{col}" stroke="{BORDER}" stroke-width="1"/>')
    add(f'  <text x="{lx + 5 * (CELL + GAP) + 2}" y="{ly + CELL - 2}" font-family="{MONO}" '
        f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">more</text>')

    # ── grid ────────────────────────────────────────────────────────────────
    add(f'  <g transform="translate({PAD_X} {PAD_Y})">')
    for r in range(ROWS):
        y = r * (CELL + GAP)
        parts = []
        for c in range(COLS):
            level = next(lvl for (cc, rr, lvl) in cells if cc == c and rr == r)
            x = c * (CELL + GAP)
            if level == 0:
                parts.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                             f'rx="2" fill="{EMPTY}" stroke="{BORDER}" stroke-width="1"/>')
            else:
                parts.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                             f'rx="2" fill="{LEVELS[level]}"/>')
        add("    " + "".join(parts))

    # ── animated pops, drawn over their base cell ───────────────────────────
    for (c, r, to_lvl, begin) in POPS:
        x, y = c * (CELL + GAP), r * (CELL + GAP)
        add(f'    <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{LEVELS[to_lvl]}">')
        add(f'      <animate attributeName="opacity" values="0.16;0.16;1;1;0.16" '
            f'keyTimes="0;0.52;0.66;0.86;1" dur="12s" begin="{begin}" '
            f'calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1;0.4 0 0.2 1;0.4 0 0.2 1" '
            f'repeatCount="indefinite"/>')
        add('    </rect>')

    add('  </g>')

    # ── legend (drawn above, immediately before the grid) ──────────────────
    _ = grid_w

    # ── weekday axis (left), one label every other row ──────────────────────
    for i, label in enumerate(["Mon", "Wed", "Fri"]):
        add(f'  <text x="{PAD_X - 8}" y="{PAD_Y + i * 2 * (CELL + GAP) + 9}" text-anchor="end" '
            f'font-family="{MONO}" font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">'
            f'{label}</text>')

    # ── month ticks (own row below the grid) ────────────────────────────────
    months = [(0, "Jan"), (9, "Mar"), (18, "May"), (26, "Jul"), (35, "Sep"), (44, "Nov")]
    for (c, label) in months:
        add(f'  <text x="{PAD_X + c * (CELL + GAP)}" y="{H - 30}" font-family="{MONO}" '
            f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">{label}</text>')

    # ── honesty marker ──────────────────────────────────────────────────────
    add(f'  <rect x="{W - PAD_X - 36}" y="{H - 26}" width="36" height="14" rx="1" '
        f'fill="none" stroke="{LINE_HI}" stroke-width="1"/>')
    add(f'  <text x="{W - PAD_X - 18}" y="{H - 15}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.9">SIM</text>')
    add(f'  <text x="{PAD_X}" y="{H - 15}" font-family="{MONO}" font-size="9" fill="{TEXT_FAINT}" '
        f'letter-spacing="0.6">simulated activity pattern \u00b7 not live data</text>')

    add('</svg>')
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=1337, help="deterministic pattern seed")
    ap.add_argument("--out", default="assets/dashboard/commit-graph.svg")
    args = ap.parse_args()

    svg = build(args.seed)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {args.out} ({len(svg):,} bytes, seed={args.seed})")


if __name__ == "__main__":
    main()
