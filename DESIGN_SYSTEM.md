# Design System — "Terminal Identity"

Shared visual contract. Every asset MUST obey this. Read it before writing SVG.

## 1. Rendering constraints (hard rules)

These assets render inside GitHub's README renderer via `<img>` tags. That means:

- **No `<script>`, no JS, no external CSS.** Blocked.
- **SMIL works** (`<animate>`, `<animateTransform>`, `<animateMotion>`, `<set>`). CSS `<style>` blocks inside SVG also work. Prefer SMIL for portability; use CSS only for static styling.
- **No web fonts.** Use only system stacks: `ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace` and for display text `system-ui, -apple-system, Segoe UI, Roboto, sans-serif`.
- **No external images / xlink href to files.** Self-contained only. Any referenced image must be inlined as a data URI (prefer none).
- **No `<foreignObject>`.** GitHub strips it. Never use it.
- Always set explicit `width`, `height`, AND `viewBox` on the root `<svg>`.
- Root `<svg>` must have a solid `<rect>` background — transparent backgrounds render as white on light-mode GitHub and look broken.

## 2. Color tokens

Use these EXACT values. No other hues.

| Token | Value | Use |
|---|---|---|
| `bg` | `#05070A` | Page / card background |
| `bg-2` | `#0A0E14` | Raised panel, header strip |
| `bg-3` | `#111823` | Inner well, code block, cell fill |
| `line` | `#1C2530` | Hairline borders, grid lines (opacity 0.5–0.9) |
| `line-hi` | `#2A3644` | Emphasised border, active state |
| `text` | `#C9D4E0` | Primary text |
| `text-dim` | `#7A8B9C` | Secondary text, labels |
| `text-faint` | `#46586A` | Ticks, disabled, watermark |
| `cyan` | `#4DD9E8` | PRIMARY accent — terminals, highlights, active |
| `green` | `#3DDC97` | Success, git activity, "OK" states |
| `amber` | `#E8B44D` | Warnings, RPM redline, "caution" |
| `violet` | `#9B7BFF` | Sparing use — AI, secondary data series |
| `red` | `#FF5C7A` | Errors, down candles, "ERR" |

Rules: **cyan is the protagonist.** Green/amber/violet/red are accents on data only, never large fills. Never more than 3 accent hues in one asset. No gradients except `cyan`→`violet` at ≤35% opacity for atmosphere; no rainbow, no glow blobs, no neon.

## 3. Typography

- Monospace for ALL data, labels, code, telemetry. Sizes: `9, 10, 11, 12, 13, 14, 16, 20, 28, 34`.
- Labels/telemetry: `10px`, `letter-spacing="1.2"`, `fill="#7A8B9C"`, usually `UPPERCASE`.
- Values/metrics: `12–14px`, `fill="#C9D4E0"`.
- Headings: system-ui, `font-weight="600"`, `letter-spacing="-0.5"`.
- NEVER below 9px. NEVER more than ~9 words in any one block of prose. This is a dashboard, not an essay.
- Character `▁▂▃▄▅▆▇█ ░▒▓ ─│┌┐└┘├┤┬┴┼ ●○◆◇ ▲▼ ✓✕ ⟳ ⏱` are approved glyphs. Verify they render; prefer the simple ones.

## 4. Grid & geometry

- Base spacing unit: **4px**. Snap all coordinates to it.
- Hairline strokes: `stroke-width="1"` (never <1, never >2 except rare dividers).
- Corner radius: `0` or `2` (2 for cards, 0 for data cells). This is a terminal — **no rounded/friendly shapes**, no circles-as-decoration, no pills.
- Cards: `<rect>` with `fill="#0A0E14"` + `stroke="#1C2530"`.
- Corner tick marks (HUD crop marks) at card corners are encouraged — 6–10px L-shapes in `line-hi`.

## 5. Animation rules

- **Cycle length 4–14s.** All animations on one asset must share a small set of durations (pick 3–5 durations and reuse) so the thing breathes instead of strobing.
- `repeatCount="indefinite"`. Use `keyTimes` + `keySplines` for smooth ease: `calcMode="spline" keySplines="0.4 0 0.2 1"`.
- **Stagger** repeated animations with `begin="-0.3s"`, `begin="-0.6s"` etc. so loops don't march in lockstep. Negative `begin` is the trick — it starts mid-cycle instantly, no blank first frame.
- **Opacity range 0.15–1.** Nothing fully invisible (flickers), nothing fully opaque that shouldn't be (noise).
- Max ~14 animated elements per asset. More reads as noise and hurts performance.
- No flashing faster than ~1.5Hz. No strobing. No `dur` under 700ms on opacity.
- **Cumulative total across the README should feel calm** — if one asset is busy, the next should be quiet.

## 6. Simulation honesty (hard rule)

Anything showing invented numbers MUST carry a visible marker. This is non-negotiable and a legal/credibility issue:

- Finance/market visuals: label `SIMULATED` in `text-faint` 9–10px, near the data. Never fake returns, P&L, portfolio value, or profit.
- Dashboard/telemetry visuals: a `DEMO` or `SIM` chip in a corner, or one line of footnote text.
- Commit hashes, user IDs, file paths, version strings: use obviously-fake but *well-formed* values (`0x7f3a9c21`, `a3f91c4`, `v2.14.0`, `/usr/local/lib/node`). Real-looking but fabricated person names, emails, or company names are banned.

## 7. Easter eggs (the reward for looking closely)

Sprinkle 1–3 per asset, tiny, `fill="#46586A"` or dim cyan, `9–10px`:

- `HTTP 200` · `HTTP 418` · `ETag: "a3f91c4"` · `X-Powered-By: caffeine`
- `sha a3f91c4` · `0x7f3a9c21` · `pid 0x1f4` · `errno 0`
- `$ git push --force-with-lease` · `~ $ make -j$(nproc)`
- `curl -sS https://api.github.com/users/$USER/rate_limit`
- `Δt=0.031s` · `λ=0.0021` · `Σ=1024` · `O(1) amortized` · `n=1024 iterations`
- `BUILD ● OK` · `DEPLOY ○ queued` · `DEBUG ✕` · `UPTIME 41d 07:13:52`
- `nanoseconds since epoch` · `errno 0` · `stddev=0.004`
Never more than 3 per asset, never in a position that hurts the layout.

## 8. File rules

- `assets/<section>/<name>.svg` — lowercase, hyphenated.
- Pretty-print with 1 attribute per line where reasonable. Keep files readable — a human maintains this.
- Target **< 40KB per SVG**. Under 80KB absolute ceiling.
- Always include a `<title>` and `<desc>` for accessibility, and `role="img"`.
- Include `<!-- ... -->` section comments so the user can edit safely.

## 9. Bar for "does this look real"

If it would look out of place on a Linear / Vercel / Tailscale engineering blog, cut it.
Restraint is the entire point. A terminal that a real engineer would actually sit in front of.
