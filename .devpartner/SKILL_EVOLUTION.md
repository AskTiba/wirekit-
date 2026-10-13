# Skill Evolution — wirekit

> This file is how Emily learns and adapts to this specific project over time.
> It is read at the START of every session (before anything else) and updated at the
> END of every session and every sprint retrospective.
>
> These entries OVERRIDE the defaults in BOOT.md and the individual SKILL.md files
> for this project. They are the highest-priority configuration source.
>
> Last updated: 2026-10-13

---

## How This Works

1. **Session start:** Emily reads this file FIRST, before BOOT.md or any SKILL.md
2. **Session end:** Emily updates this file with corrections, new conventions, and learnings
3. **Sprint retrospective:** Developer and Emily explicitly discuss what to add here
4. **Evolution is cumulative:** entries are never deleted, only superseded
   (add a "Superseded by:" note if a rule changes)

---

## Developer Preferences

| Date | Preference | Context |
|---|---|---|
| 2026-10-13 | Accepted recommended options when presented as a comparison table (CI scope question) — keep presenting options, lead with a clear recommendation | Skill 6.0 bootstrap, ADR-001 |

---

## Project-Specific Conventions

| Date | Convention | Established in |
|---|---|---|
| 2026-10-13 | **Runtime stays stdlib-only** — any new runtime dependency needs a DECISIONS.md entry first (ADR-002) | ADR-002 |
| 2026-10-13 | **Dev/test deps live only in pinned `requirements-dev.txt`** — CI installs exactly that file (command parity: CI runs what you run) | ADR-001 |
| 2026-10-13 | **Local commit gate = `python3 -m pytest && ruff check . && ruff format --check .`** (ruff 0.17.0 pinned in `requirements-dev.txt`, config `ruff.toml`, target py311; CI lint job mirrors the same commands — gate + CI landed together per convention) | ci-partner §1.1 mirror; STORY-002 |
| 2026-10-13 | All address arithmetic at the edges of IPv4 space goes through `int`, never `IPv4Address` arithmetic (can overflow mid-expression) | ERR-001 |
| 2026-10-13 | Commits before 2026-10-13 predate the protocol; from bootstrap onward: conventional commits ≤12 words, test-first, commit only on developer trigger | core-partner §8 |
| 2026-10-13 | This is a terminal tool — WCAG/browser conventions don't apply; keep output plain-text ordered key/value lines and meaningful exit codes | PROJECT_STATE → Conventions |

---

## Corrections Logged

| Date | Session # | Was about to do | Should do instead |
|---|---|---|---|
| *(none yet)* | | | |

---

## What Worked Well

| Date | Pattern | Why it worked |
|---|---|---|
| 2026-10-13 | Research pass (6 named sources) before scaffolding CI caught that gitleaks-action v2 is dead on current runners (Node 20 removed 2026-09-16) and verified live action majors (checkout@v7, setup-python@v7, codeql@v4) — generated pipeline uses current, working versions | Would have shipped a failing pipeline from stale memory |

---

## Standing Technical Decisions (Project-Level)

| Decision | Settled | Date | Reference |
|---|---|---|---|
| CI scope: full-shape scaled (no ruff yet) | Yes | 2026-10-13 | [DECISIONS.md](DECISIONS.md) ADR-001 |
| Zero runtime dependencies | Yes | 2026-10-13 | [DECISIONS.md](DECISIONS.md) ADR-002 |
| pytest as test runner, pinned 9.0.3 (vuln bump from 9.0.2, PYSEC-2026-1845) | Yes | 2026-10-13 | [DECISIONS.md](DECISIONS.md) TECH-001 |
| Python support claim = 3.11–3.14 (CI matrix is the source of truth) | Yes | 2026-10-13 | [ROADMAP.md](ROADMAP.md) NFR |
