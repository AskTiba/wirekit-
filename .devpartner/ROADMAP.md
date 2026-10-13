# Roadmap — wirekit

> Vision, milestones, NFR targets, backlog snapshot, and tech debt register.
> Last updated: 2026-10-13

---

## Vision

**One-sentence product vision:**
> The single-command IPv4 answer key for anyone learning or practicing subnetting — mask in any real-world format, every exam-relevant field out, zero install friction.

**Core problem solved:**
> Learning subnetting requires checking your work constantly, but existing calculators either demand strict CIDR-only syntax or dump a wall of numbers with no context. `wirekit` takes the mask exactly as it appears in the real world (`ipconfig`, router page, CIDR block) and reports exactly the values you're practicing — with `--bits` showing *why* the network ID is what it is.

---

## MVP Scope (MoSCoW)

| Priority | Feature | Status | Sprint |
|---|---|---|---|
| **Must Have** | Subnet calculation (network, netmask, broadcast, host range, counts, next network) | ✅ Done | pre-skill (2026-10-12) |
| | Three mask input forms + glued CIDR | ✅ Done | pre-skill |
| | Edge cases `/31` `/32`, host normalization, clear errors (no tracebacks) | ✅ Done | pre-skill |
| | `--bits` teaching mode | ✅ Done | pre-skill |
| | Test suite | ✅ Done (23 tests) | pre-skill |
| | Cross-shell installer + README | ✅ Done | pre-skill |
| **Should Have** | `--quiz` practice mode | ✅ Done | pre-skill (2026-10-12) |
| | CI + security pipeline (this bootstrap) | ✅ Files created 2026-10-13, first run pending push | Sprint 1 |
| | JSON output for scripting | ⏸ Not started | Sprint 1 |
| **Could Have** | More quiz question types (subnetting from scratch, VLSM decomposition) | ⏸ Not started | Sprint 2+ |
| | Coverage gate (pytest-cov + threshold) | ⏸ Not started ([DECISIONS.md](DECISIONS.md) DEBT-002) | Sprint 1 |
| | IPv6 support | ⏸ Undecided — PO decision needed (changes core data model; `ipaddress` supports it, but output schema and quiz logic are IPv4-shaped) | TBD |
| **Won't Have (v1)** | GUI / web version | ❌ Excluded | — | 
| | Network scanning / host discovery | ❌ Excluded — out of product definition (calculator, not scanner) | — |

---

## Milestones

| # | Milestone | Target date | Status | Key features |
|---|---|---|---|---|
| M1 | Working CLI + tests | 2026-10-12 | ✅ Complete | calculator, edge cases, `--bits`, `--quiz`, installer, README |
| M2 | Skill 6.0 bootstrap + CI | 2026-10-13 | 🟡 In progress | `.devpartner/`, skills installed, CI + security workflows (first run pending push) |
| M3 | v1.1 — scripting + quality gates | TBD (Sprint 1) | ⏸ Not started | JSON output, ruff gate, coverage gate, LICENSE |

---

## Non-Functional Requirements (NFR Targets)

> Concrete, measurable targets. "Fast" and "scalable" are not targets.

| Requirement | Target | Measurement method | Current baseline |
|---|---|---|---|
| CLI startup + calc latency | < 100 ms per invocation | `time python3 wirekit.py 192.168.1.26 /24` | not yet measured (pure stdlib math — expected well under) |
| Test suite runtime | < 5 s full suite | `python3 -m pytest` (timed) | **1.98 s / 23 tests (2026-10-13)** |
| Runtime dependencies | 0 (stdlib only) | `grep '^import' wirekit.py` vs stdlib | **0 (2026-10-13)** — standing rule, ADR-002 |
| Python support | 3.11 – 3.14 | CI matrix (4 jobs) | enforced once CI first runs |
| CI wall-clock | < 5 min per push | GitHub Actions run duration | not yet measured (first run pending) |
| Accessibility | N/A (terminal tool) — plain-text ordered output, meaningful exit codes | manual + subprocess tests assert stderr/exit codes | met by design |
| Bundle/install footprint | single ≤ 20 KB script | `wc -c wirekit.py` | 4.8 KB |

### Performance Log

| Date | Metric | Value | Notes |
|---|---|---|---|
| 2026-10-13 | Test suite runtime | 1.98 s | 23 tests incl. subprocess CLI tests |

---

## Backlog Snapshot

### Ready for next sprint (Sprint 1 candidates)

| ID | Story | Points | Priority |
|---|---|---|---|
| STORY-001 | JSON output mode (`--json`) for scripting | 2 | Should Have |
| STORY-002 | Ruff lint + format gate (local + CI) — close DEBT-001 | 1 | Should Have |
| STORY-003 | Coverage measurement + threshold — close DEBT-002 | 1 | Could Have |
| STORY-004 | LICENSE file (developer picks MIT/Apache-2.0) — close DEBT-003 | 1 | Should Have |
| STORY-005 | Enable branch protection (manual GitHub settings, documented in PROJECT_STATE.md) | 1 | Must Have |

---

## Tech Debt Register

> Full register in [DECISIONS.md](DECISIONS.md) → Tech Debt Register. Highest priority:

| ID | Item | Impact | Target sprint |
|---|---|---|---|
| DEBT-001 | No ruff lint/format gate | Style drift, silent lint-class bugs | Sprint 1 |
| DEBT-002 | No coverage threshold | Test blind spots undetected | Sprint 1 |
| DEBT-003 | No LICENSE | Legally unlicensed code | Sprint 1 |

---

## Risks

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| RISK-001 | CI exists but branch protection never enabled → `ci-success` is advisory, red merges possible | Medium | High | STORY-005; settings documented in PROJECT_STATE.md → Branch Protection |
| RISK-002 | CI first run reveals environment-only failure (matrix version, junit path, cache config) | Medium | Low | Command-match check done at scaffold (ci-partner §5.1); fix-forward on first push, log in ERROR_LOG.md |
