# Sprint Log — wirekit

> Chronological history of sprints — planning outcomes, velocity, retrospective actions.
> This is how the team learns and improves over time.
> Last updated: 2026-10-13

---

## Summary Dashboard

| Sprint | Goal | Committed | Completed | Velocity | Completion Rate |
|---|---|---|---|---|---|
| Sprint 1 | Quality gates + scriptable output (`--json`, `--conv`) | 10 | 9 | 9 | 90% (STORY-005 manual/pending developer) |

---

## Sprint 1 — Quality gates + scriptable output

**Period:** 2026-10-13 → 2026-10-20
**Status:** Review — code complete, all commits pushed, CI + Security green on `main`; STORY-005 pending developer action

### Committed

| ID | Story | Pts | Outcome |
|----|-------|-----|---------|
| STORY-002 | Ruff lint+format gate (local + CI) — closes DEBT-001 | 1 | ✅ Done (`9aab8d8`) |
| STORY-006 | Hypothesis property tests for subnet math | 2 | ✅ Done (`b007cf3`) |
| STORY-003 | Coverage floor (pytest-cov + threshold) — closes DEBT-002 | 1 | ✅ Done (`4c4740c`) |
| STORY-001 | `--json` output mode | 2 | ✅ Done (`da66e5a`) |
| STORY-007 | `--conv` base converter (decimal ↔ binary ↔ hex) — new, requested 2026-10-13 | 2 | ✅ Done (`b738f30`) |
| STORY-004 | LICENSE (MIT per README) + README CI badge — closes DEBT-003 | 1 | ✅ Done (`8e923a7`) |
| STORY-005 | Enable branch protection (manual — developer) | 1 | ⏸ Pending developer (GitHub UI) |

Plus unplanned work absorbed: first push + all three workflows green (`44c29ef` pytest 9.0.3 vuln fix from pip-audit finding PYSEC-2026-1845; `122b808` 9.1.1 latest superseding Dependabot PR #1, closed).

**Total committed:** 10 pts
**Total completed:** 9 pts

### Not Delivered (moved to backlog)

- STORY-005 — blocked on manual GitHub settings (developer-only); carries to Sprint 2 as first item

### Retrospective

**What went well:**
- Gate parity (`pytest && ruff check && ruff format --check` local = CI) proved itself immediately: the very first CI run's pip-audit caught a real advisory in our own pin
- Red-first found bugs in *tests*, not code, twice (analyze output contract, hex hand-calc) — the discipline works both directions
- Coverage-floor workflow (measure → fill gaps → set floor at demonstrated baseline) turned a vanity metric into 7 genuinely missing tests
- Row-shaped `analyze()` contract paid off: `--json` and `--conv` each cost ~4 lines of plumbing
- Memory files stayed current every unit — next session can resume cold

**What could improve:**
- Local PEP 668 friction (every new dev dep needs `--user --break-system-packages` dance) — consider a project `.venv` + `uv` workflow
- Hand-computed expected values in tests are a bug source — verify against `python3 -c` ground truth *before* writing asserts
- `git commit` gates are solid, but push/PR flow for Dependabot needs the token to allow comments (cosmetic gap)

**Action items:**
- STORY-005 branch protection — developer, GitHub UI (Sprint 2 item 1)
- Evaluate `.venv` + uv local dev workflow — Sprint 2 (developer preference)
- CI badge/branch protection story belongs in portfolio narrative — feed interview-partner

**Skill Evolution (persisted to SKILL_EVOLUTION.md):**
- Coverage floor rule: measure first, floor = demonstrated baseline, never aspirational (TECH-006 note)
- Subprocess tests don't credit module coverage — dual-layer testing (in-process + E2E) is now the project default

---

## Pre-Skill History (before Skill 6.0 adoption)

Work completed 2026-10-12 without formal sprints — recorded so context isn't lost:

| Commit | What shipped |
|---|---|
| `0d9bd10` | Initial subnet calculator with cross-shell installer |
| `f16ee07` | README + `.gitignore` |
| `0b4662d` | Renamed project to wirekit, updated clone URLs |
| `945890f` | Renamed script and command to wirekit |
| `0f147f1` | Quiz mode + 23-test pytest suite + fix for next-network overflow (ERR-001) |

**Status at Skill 6.0 adoption (2026-10-13):** MVP feature-complete, tests green, working tree clean on `main`.

---

## Sprint Template

Copy this block for each new sprint:

```markdown
## Sprint [N] — [Goal]

**Period:** [Start date] → [End date]
**Status:** Planning / In Progress / Review / Complete

### Committed

| ID | Story | Pts | Outcome |
|----|-------|-----|---------|
| STORY-XXX | [Title] | [N] | ✅ Done / ❌ Not delivered |

**Total committed:** [X] pts
**Total completed:** [Y] pts
**Velocity:** [Y] pts

### Not Delivered (moved to backlog)

- STORY-XXX — [Reason]

### Retrospective

**What went well:**
- [...]

**What could improve:**
- [...]

**Action items:**
- [Action — target sprint]

**Skill Evolution (persisted to SKILL_EVOLUTION.md):**
- [Any AI behavior changes]
```

---

*(Sprints will be added here as they complete — next ceremony: Sprint 1 planning, project-manager skill)*
