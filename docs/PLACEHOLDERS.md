# Placeholder checklist

Everything below must be replaced before you publish. Work top to bottom —
the first item blocks the most.

Quick check at any time:

```bash
grep -n '⟦USERNAME⟧\|⟦HANDLE⟧\|⟦TODO⟧' README.md
bash scripts/build.sh
```

`build.sh` prints how many `⟦USERNAME⟧` markers remain.

---

## 1. Repository — do this first

| # | Item | Where | Notes |
|---|---|---|---|
| 1 | Create a **public** repo named exactly your username | GitHub | `YOURNAME/YOURNAME`. The name must match your handle or the README will not appear on your profile. If a same-named repo predates July 2020, use **Share to profile** on its README page. |
| 2 | Copy this repo's contents in | — | `assets/`, `scripts/`, `README.md`. Optional: `docs/`, `DESIGN_SYSTEM.md`. |
| 3 | Confirm images resolve | — | Relative paths (`assets/…`) require this to be the profile repo. If you keep the README elsewhere, switch to `raw.githubusercontent.com` URLs. |

## 2. GitHub username — 20 occurrences

Search-and-replace in `README.md`:

```
⟦USERNAME⟧  →  your-actual-handle
```

Appears in: the profile links, the three top badges, the streak stats URLs,
both stats card links, the "repos / followers / commits" badges, and the
connect row. Run `grep -c '⟦USERNAME⟧' README.md` to confirm you hit them all.

## 3. Intro copy

| Placeholder | Location | Current text |
|---|---|---|
| Headline | `README.md`, under the hero | "Building software, experimenting with AI, and breaking things until they work." |
| Interest line | directly below it | software · AI · web · finance · motorcycles · CS |
| Code × Markets blurb | `README.md` | "systematic thinking applied to price, volume and risk" |
| Garage blurb | `README.md` | "CAD drawings, telemetry and tachometers appeal for the same reason compilers do." |

## 4. Featured projects — `assets/projects/projects.svg`

Six modules. Each is wrapped in `<!-- EDIT:PROJECT:n:BEGIN -->` … `END` markers.
For each: the **category tag**, **name**, **one-line description**, and
**tech line**.

| # | Current placeholder | Category |
|---|---|---|
| 1 | `project-alpha` | DEV TOOLS |
| 2 | `llm-agent-lab` | AI |
| 3 | `app-shell` | WEB |
| 4 | `pipeline-ctl` | AUTOMATION |
| 5 | `roblox-toolkit` | LUAU |
| 6 | `market-sim` | FINANCE |

**Cards are not clickable.** The `repo ↗` label is decorative — SVG `<img>` tags
cannot carry links. To get real links, delete the `<img>` tag for this panel and
use the markdown table below instead:

```markdown
| | Project | What it does | Stack |
|:-:|---|---|---|
| 01 | [repo](https://github.com/YOU/REPO) | one line, plain and specific | TS · Node |
| 02 | [repo](https://github.com/YOU/REPO) | one line | Python · MCP |
```

## 5. Technology stack — `assets/stack/stack.svg`

Four groups, each between `<!-- EDIT:…:BEGIN -->` … `END`:

- `EDIT:LANGUAGES` — TypeScript, JavaScript, Python, Lua / Luau, Java, C++
- `EDIT:RUNTIME` — React, Next.js, Node.js, Docker, Linux
- `EDIT:TOOLING` — Git, GitHub Actions, MCP, Automation, Testing
- `EDIT:AI` — LLMs, AI coding agents, MCP servers, Prompting, Local AI

**Delete what you do not actually use.** An inflated list is the fastest way to
look like a résumé. If you drop a row, delete its name *and* caption line, and
keep the remaining rows on the same 28px pitch.

Prefer native badges? `assets/stack/shields.md` has a matched, colour-consistent
set.

## 6. Contact links — `README.md`

| Placeholder | Replace with | Delete if unused |
|---|---|---|
| `⟦HANDLE⟧` (X / Twitter) | your handle | delete the whole `<a>` block |
| `⟦USERNAME⟧` (LinkedIn) | your profile slug | delete the whole `<a>` block |
| `⟦TODO⟧` personal site | your URL | uncomment and fill |

GitHub keeps `<a>` and `<img>` in READMEs but strips event handlers, so these
are safe.

## 7. Statistics

Default setup needs nothing — committed SVGs, refreshed daily by
`.github/workflows/stats.yml`.

| Situation | Do this |
|---|---|
| First run | **Actions → Update README cards → Run workflow**. Until then the two cards are labelled placeholders (committed on purpose, so nothing looks broken). |
| Prefer zero-config | Uncomment the hotlinked block in the stats section of `README.md`. See the caveat below. |
| Want streak stats | Already wired to `streak-stats.demolab.com`. Replace `⟦USERNAME⟧`. Delete the second, redundant streak badge. |

**On the hotlinked option:** the public `github-stats-extended.vercel.app`
instance is shared and rate-limited, and can return an error card or nothing at
all. That is the reason the default is locally-committed SVGs. The successor to
the now-unmaintained `github-readme-stats` is `github-stats-extended`; the URLs
are otherwise compatible.

---

## 8. Simulated content — leave these alone

These are **intentionally fake** and must never be presented as real:

| Asset | What is invented | Marker shown |
|---|---|---|
| `dashboard.svg` | CPU/memory/disk values, network traffic, uptime, commit dots | `DEMO · simulated telemetry` footer |
| `commit-graph.svg` | the entire activity pattern | `SIM` chip + `not live data` |
| `markets.svg` | every price level, candle, spread, depth figure | `SIMULATED` header + `not investment data · not financial advice` |
| `orderflow.svg` | the pipeline | `SIMULATED` + `synthetic feed · not market data` |
| `garage.svg` | bore/stroke/ratio/mass, pressure trace, load | `hobby · schematic reference · simulated telemetry` |
| `tachometer.svg` | the RPM sweep and readout | `SIM` + `no real instrument data` |

You may restyle these. Do not remove the markers, and do not replace the market
figures with anything that looks like a real balance, return or trade.

The one thing that **is** real in the README: the two cards in
`assets/stats/live/`, generated from public GitHub data.

---

## 9. Final pre-publish check

```bash
bash scripts/build.sh          # all assets valid, no broken README paths
grep -c '⟦USERNAME⟧' README.md # should be 0
```

Then open the repo README on GitHub and confirm:

- [ ] the hero renders and animates
- [ ] the stats cards show real numbers, not the placeholder text
- [ ] no broken image icons
- [ ] project names and links are yours
- [ ] it still looks right in **light mode** — the assets are dark by design
      and will read as dark cards on a white page (that is intentional and
      looks fine, but check it does not jar)
