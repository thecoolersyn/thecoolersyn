#!/usr/bin/env python3
"""
Render assets/dashboard/commit-graph.svg from REAL GitHub contribution data.

Fetches the public contribution calendar over the GraphQL API and renders it in
the project design system. There is no synthetic fallback: if the fetch fails
this script exits non-zero and leaves the previous SVG untouched, so a failed
run can never publish a fabricated graph.

Usage:
    # local / CI — needs a token with read:user
    GITHUB_TOKEN=... python3 scripts/gen_commit_graph.py

    # render from a saved payload (no network, used for testing)
    python3 scripts/gen_commit_graph.py --from-json contribs.json

Output is deterministic for a given payload: same data in, byte-identical SVG
out, so the weekly workflow only commits when the data actually changed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

# ── Design system tokens (keep in sync with DESIGN_SYSTEM.md) ────────────────
BG = "#0A0E14"
BORDER = "#1C2530"
LINE_HI = "#2A3644"
TEXT_DIM = "#7A8B9C"
TEXT_FAINT = "#46586A"
CYAN = "#4DD9E8"

# Activity ramp: empty -> 5 levels, dim cyan. Deliberately NOT GitHub's green.
LEVELS = ["#0E1A20", "#123039", "#17495A", "#1E6E86", CYAN]
EMPTY = "#0A0E14"

W, H = 900, 200
ROWS = 7
CELL, GAP = 11, 3
PAD_X, PAD_Y = 40, 58
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    """Fetch the public contribution calendar via the GraphQL API."""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "git-profile-readme",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:                      # noqa: PERF203
        sys.exit(f"error: GitHub API returned HTTP {exc.code}")
    except urllib.error.URLError as exc:
        sys.exit(f"error: cannot reach GitHub API: {exc.reason}")

    if payload.get("errors"):
        msgs = "; ".join(e.get("message", "?") for e in payload["errors"])
        sys.exit(f"error: GraphQL error: {msgs}")

    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    if not cal["weeks"]:
        sys.exit("error: empty contribution calendar")
    return cal


def flatten(cal: dict) -> list[dict]:
    """Weeks -> a flat, chronologically ordered list of days."""
    days = []
    for wk in cal["weeks"]:
        for d in wk["contributionDays"]:
            days.append(
                {
                    "count": d["contributionCount"],
                    "date": d["date"],
                    "weekday": d["weekday"],   # 0 = Sunday
                }
            )
    return days


def levels_for(counts: list[int]) -> tuple[int, int, int]:
    """Quartile thresholds over non-zero days, so the ramp adapts to the
    account's own distribution instead of assuming fixed cut-offs."""
    nz = sorted(c for c in counts if c > 0)
    if not nz:
        return 0, 0, 0

    def pct(p: float) -> int:
        idx = min(len(nz) - 1, int(round(p * (len(nz) - 1))))
        return nz[idx]

    return pct(0.25), pct(0.5), pct(0.75)


def level_of(count: int, q1: int, q2: int, q3: int) -> int:
    if count <= 0:
        return 0
    return 1 + (count >= q1) + (count >= q2) + (count >= q3)


def build(cal: dict) -> str:
    days = flatten(cal)
    cols = (len(days) + ROWS - 1) // ROWS
    grid_w = cols * (CELL + GAP) - GAP

    counts = [d["count"] for d in days]
    q1, q2, q3 = levels_for(counts)
    total = sum(counts)
    first = days[0]["date"]
    last = days[-1]["date"]

    def month_ticks() -> list[tuple[int, str]]:
        """Label a column when its first day opens a new month.

        The window rarely starts on the 1st, so the first two labels can land
        one column apart and collide. Enforce a minimum gap.
        """
        out, seen, last_col = [], set(), -99
        for i, d in enumerate(days):
            col, row = divmod(i, ROWS)
            if row != 0:
                continue
            m = d["date"][5:7]
            if m in seen or col - last_col < 3:
                continue
            seen.add(m)
            last_col = col
            out.append((col, datetime.strptime(d["date"], "%Y-%m-%d").strftime("%b")))
        return out

    out: list[str] = []
    add = out.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">')
    add('  <title id="t">Contribution activity — last 12 months</title>')
    add('  <desc id="d">A seven-row activity heatmap of public GitHub contributions over the '
        f'{first} to {last} window, showing {total} contributions. Generated from real GitHub data.</desc>')
    add(f'  <rect width="{W}" height="{H}" fill="{BG}"/>')

    # ── header ──
    window = f"{first} → {last}"
    add(f'  <text x="{PAD_X}" y="26" font-family="{MONO}" font-size="10" fill="{TEXT_DIM}" '
        f'letter-spacing="1.3">COMMIT ACTIVITY \u00b7 last 12 months</text>')
    add(f'  <text x="{W - PAD_X}" y="26" text-anchor="end" font-family="{MONO}" font-size="10" '
        f'fill="{TEXT_FAINT}" letter-spacing="0.8">{total:,} contributions \u00b7 {window}</text>')

    # ── legend on its own row ──
    lx = W - PAD_X - 5 * (CELL + GAP) + GAP
    ly = 40
    add(f'  <text x="{lx - 10}" y="{ly + CELL - 2}" text-anchor="end" font-family="{MONO}" '
        f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">less</text>')
    for i, col in enumerate(LEVELS):
        add(f'  <rect x="{lx + i * (CELL + GAP)}" y="{ly}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{col}" stroke="{BORDER}" stroke-width="1"/>')
    add(f'  <text x="{lx + 5 * (CELL + GAP) + 2}" y="{ly + CELL - 2}" font-family="{MONO}" '
        f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">more</text>')

    # ── grid ──
    add(f'  <g transform="translate({PAD_X} {PAD_Y})">')
    for row in range(ROWS):
        y = row * (CELL + GAP)
        cells = []
        for col in range(cols):
            i = col * ROWS + row
            if i >= len(days):
                break
            x = col * (CELL + GAP)
            lvl = level_of(days[i]["count"], q1, q2, q3)
            if lvl == 0:
                cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                             f'fill="{EMPTY}" stroke="{BORDER}" stroke-width="1"/>')
            else:
                cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                             f'fill="{LEVELS[lvl]}"/>')
        add("    " + "".join(cells))
    add('  </g>')

    # ── weekday axis ──
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        add(f'  <text x="{PAD_X - 8}" y="{PAD_Y + row * (CELL + GAP) + 9}" text-anchor="end" '
            f'font-family="{MONO}" font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">'
            f'{label}</text>')

    # ── month ticks ──
    for col, label in month_ticks():
        add(f'  <text x="{PAD_X + col * (CELL + GAP)}" y="{H - 30}" font-family="{MONO}" '
            f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.6">{label}</text>')

    # ── provenance note: this graph is real, and says so ──
    add(f'  <rect x="{W - PAD_X - 42}" y="{H - 26}" width="42" height="14" rx="1" '
        f'fill="none" stroke="{LINE_HI}" stroke-width="1"/>')
    add(f'  <text x="{W - PAD_X - 21}" y="{H - 15}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="9" fill="{TEXT_FAINT}" letter-spacing="0.9">LIVE</text>')
    add(f'  <text x="{PAD_X}" y="{H - 15}" font-family="{MONO}" font-size="9" fill="{TEXT_FAINT}" '
        f'letter-spacing="0.6">public GitHub contribution data \u00b7 regenerated weekly</text>')

    add('</svg>')
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--login", default=os.environ.get("GITHUB_ACTOR", ""),
                    help="GitHub login (defaults to $GITHUB_ACTOR)")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", "")
                    or os.environ.get("GH_TOKEN", ""))
    ap.add_argument("--from-json", help="render from a saved GraphQL payload instead of the API")
    ap.add_argument("--out", default="assets/dashboard/commit-graph.svg")
    args = ap.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as fh:
            payload = json.load(fh)
        cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    else:
        if not args.login:
            sys.exit("error: no login (pass --login or set GITHUB_ACTOR)")
        if not args.token:
            sys.exit("error: no token (pass --token or set GITHUB_TOKEN)")
        cal = fetch(args.login, args.token)

    svg = build(cal)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(svg)

    total = sum(d["count"] for d in flatten(cal))
    print(f"wrote {args.out} ({len(svg):,} bytes, {total:,} real contributions)")


if __name__ == "__main__":
    main()
