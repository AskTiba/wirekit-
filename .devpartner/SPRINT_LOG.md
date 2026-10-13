# Sprint Log — wirekit

> Chronological history of sprints — planning outcomes, velocity, retrospective actions.
> This is how the team learns and improves over time.
> Last updated: 2026-10-13

---

## Summary Dashboard

| Sprint | Goal | Committed | Completed | Velocity | Completion Rate |
|---|---|---|---|---|---|
| Sprint 1 | Quality gates + scriptable output (`--json`, `--conv`) | 10 | — | — | — |

---

## Sprint 1 — Quality gates + scriptable output

**Period:** 2026-10-13 → 2026-10-20
**Status:** In Progress

### Committed

| ID | Story | Pts | Outcome |
|----|-------|-----|---------|
| STORY-002 | Ruff lint+format gate (local + CI) — closes DEBT-001 | 1 | ✅ Done |
| STORY-006 | Hypothesis property tests for subnet math | 2 | ⏸ Not started (U3) |
| STORY-003 | Coverage floor (pytest-cov + threshold) — closes DEBT-002 | 1 | ⏸ Not started (U4) |
| STORY-001 | `--json` output mode | 2 | ⏸ Not started (U5) |
| STORY-007 | `--conv` base converter (decimal ↔ binary ↔ hex) — new, requested 2026-10-13 | 2 | ⏸ Not started (U6) |
| STORY-004 | LICENSE (MIT per README) + README CI badge — closes DEBT-003 | 1 | ⏸ Not started (U7) |
| STORY-005 | Enable branch protection (manual — developer) | 1 | ⏸ Not started |

**Total committed:** 10 pts

### Not Delivered (moved to backlog)

- *(none yet)*

### Retrospective

*(to be filled at sprint close)*

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
