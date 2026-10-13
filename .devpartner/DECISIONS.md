# Decisions Log — wirekit

> All non-trivial architectural, technology, process, and scope decisions — including
> disagreements and overrides — are recorded here. Settled decisions are not re-opened.
> Last updated: 2026-10-13

---

## How to Read This Log

- **Decisions** are final choices; they don't need re-discussion
- **Overrides** are logged when Emily disagreed but the developer chose differently; they
  include the accepted risk
- **Process Improvements** come from sprint retrospectives

---

## Architecture Decisions

| ID | Date | Decision | Persona | Options considered | Chosen rationale |
|---|---|---|---|---|---|
| ADR-001 | 2026-10-13 | CI = full-shape scaled pipeline: test matrix (3.11–3.14) → `ci-success` aggregate, separate security workflow (CodeQL + gitleaks + pip-audit + dependency-review), Dependabot (pip + github-actions), pinned `requirements-dev.txt`. Ruff lint/format **deferred** to backlog. | DevOps / Platform Engineer | A) full-shape scaled (chosen) B) full-shape + ruff introduced now C) test-only minimal | Approved by developer. A keeps the ci-partner non-negotiable shape (parallel graph, security stage, least-privilege, aggregate gate) without adding tooling churn to a zero-dependency codebase in the same session as the bootstrap; C was rejected as below the skill's bar (no security stage), B deferred so the first CI run proves green before a new gate is layered on. |
| ADR-002 | 2026-10-13 | **Zero-runtime-dependency stance is a standing convention.** `wirekit.py` stays stdlib-only; dev/test deps allowed only via pinned `requirements-dev.txt`. | Library Evaluation Specialist | (pre-existing practice, ratified) netaddr / click / rich as alternatives | `install.sh` copies one file — no install friction, no supply-chain surface, no version conflicts on user machines. Revisit only if a feature genuinely needs it (e.g. IPv6 edge cases beyond `ipaddress`). |

---

## Technology / Dependency Choices

| ID | Date | Library/Tool | Version | Why chosen | Rejected alternatives |
|---|---|---|---|---|---|
| TECH-001 | 2026-10-13 | pytest (test runner) | 9.0.3 pinned (bumped from 9.0.2 same day — PYSEC-2026-1845 found by first pip-audit CI run) | De-facto Python standard; `pytest.ini` already drives `testpaths`/`pythonpath`; supports Python ≥3.10 (covers full CI matrix) | `unittest` (more boilerplate, weaker parametrize/monkeypatch/capsys — all three used in `tests/test_wirekit.py`) |
| TECH-002 | 2026-10-13 | `ipaddress` (stdlib) for subnet math | builtin | Correct RFC handling (`strict=False` normalization, `num_addresses`, netmask/broadcast) with zero deps | Raw integer bitmasking by hand (re-implements RFCs, bug-prone); `netaddr` (runtime dep, violates ADR-002) |
| TECH-003 | 2026-10-13 | GitHub Actions + codeql-action@v4 + gitleaks-action@v3 (SHA-pinned) + dependency-review-action@v5 | current as of 2026-10-13 | Remote is GitHub; CodeQL is native SAST; gitleaks v3 **required** — v2's Node 20 runtime was removed from GitHub runners 2026-09-16; personal repo → no gitleaks license needed | GitLab CI/CircleCI (wrong platform); unpinned `gitleaks@v2` (would fail outright); third-party "all-in-one" CI marketplaces (supply-chain risk) |
| TECH-004 | 2026-10-13 | ruff (lint + format + import sort) | 0.17.0 pinned | Single Rust binary, black-compatible formatter, one config for all three jobs, 10-100× faster than the trio; official docs' recommended rule set (`E,F,UP,B,SIM,I`); config in `ruff.toml` to avoid implying packaging metadata (no `pyproject.toml` yet by design) | flake8+black+isort trio (three tools, three configs, much slower); pylint (no formatter, more pedantic, slower) |
| TECH-005 | 2026-10-13 | hypothesis (property-based testing) | 6.169.0 pinned | Subnet math is invariant-driven (alignment, broadcast arithmetic, usable-host formulas) — properties cover all 2^32 × 33 cases vs hand-picked examples; caught edge cases (0.0.0.0/0) the example suite never generates; dev-only (ADR-001) | More example tests (never reach edge space systematically); Hypothesis's `derandomize=True` not needed — CI reruns fresh |
| TECH-006 | 2026-10-13 | pytest-cov (coverage measurement + floor) | 7.1.0 pinned | Measurement first revealed the real baseline (70%: subprocess CLI tests don't credit in-process coverage); after gap-fill tests the floor is set at the demonstrated 100% via `pytest.ini` `addopts` (gate command stays `python3 -m pytest` — CI parity free); escapes only via `# pragma: no cover` on genuinely untestable lines (currently one: `__main__` call) | Setting an aspirational floor with no tests behind it (green-without-meaning); `COVERAGE_PROCESS_START` subprocess tracing (heavy sitecustomize machinery for a 105-line module) |

---

## Research Logged (Universal Research Loop — core-partner §1.6)

### 2026-10-13 — CI pipeline for wirekit (before scaffolding)

**Sources studied (named):**
1. GitHub Docs — *Building and testing Python* (actions/guides/building-and-testing-python)
2. istranin.dev — *GitHub Actions Python Testing: Complete pytest CI Guide* (2026-09)
3. Modern Git Academy — *Lab: Build a Python CI Pipeline*
4. khimananda.com — *CI/CD Pipeline for Python with GitHub Actions: 2026 Guide*
5. GitHub Actions API (`actions/*`, `github/codeql-action`, `gitleaks/gitleaks-action` tags) — live version verification
6. gitleaks-action v3 README (raw.githubusercontent @ v3) — v2→v3 migration + licensing

**Concrete lessons applied:**
- Quote matrix versions (`"3.11"` … `"3.14"`) — YAML mangles unquoted numbers; `fail-fast: false` so one version's failure doesn't hide the others' results.
- `cache: pip` requires a committed dependency file → created `requirements-dev.txt` (also gives CI/local command parity: CI runs exactly what you run).
- Use `python -m pytest` (module form), not bare `pytest` — avoids `ModuleNotFoundError` path failures.
- JUnit report uploaded with **unique per-matrix artifact names** + `if: always()` (upload precisely when tests fail).
- One stable aggregate check (`ci-success`) is the required branch-protection status — not the individual matrix jobs.
- `concurrency` + `cancel-in-progress` on push/PR workflows; `timeout-minutes` on every job; top-level `permissions: contents: read`; `persist-credentials: false` on checkout.
- **gitleaks-action v2 is dead as of 2026-09-16** (Node 20 removed from runners) — v3 is mandatory; personal accounts need no license.
- Coverage thresholds must be chosen deliberately, not copied — hence no `--cov-fail-under` yet (DEBT-002).

---

## Developer Overrides

*(No overrides yet — ADR-001 was approved as recommended.)*

---

## Process Improvements

| Date | Sprint | Improvement | Status |
|---|---|---|---|
| 2026-10-13 | bootstrap | CI scope presented as options-before-decision (core-partner §1.5) before scaffolding — developer picked the recommended option | Adopted |

---

## Tech Debt Register

| ID | Date | Item | Impact | Target sprint to address |
|---|---|---|---|---|
| DEBT-001 | 2026-10-13 | No linter/formatter (ruff) configured — **closed 2026-10-13**: `ruff.toml` + pinned 0.17.0, local gate + CI lint job (STORY-002) | Style drift and silent lint-class bugs as contributors grow; CI shape has the gap flagged (ci-partner §2.8) | ~~Sprint 1~~ closed |
| DEBT-002 | 2026-10-13 | No coverage measurement or threshold (pytest-cov not installed) — **closed 2026-10-13**: pytest-cov 7.1.0, `--cov=wirekit --cov-fail-under=100` in `pytest.ini`; measurement drove 7 new in-process tests (STORY-003) | Coverage regressions go unnoticed; 23 tests may have blind spots (e.g. `show_bits` edge paths) | ~~Sprint 1~~ closed |
| DEBT-003 | 2026-10-13 | No LICENSE file (README states this openly) — **closed 2026-10-13**: MIT `LICENSE` (copyright 2026 Tibamwenda Anthony, from `git config user.name`), README License section links it, CI badge added (STORY-004) | Legally unlicensed — others can't legally reuse; blocks some portfolio reviewers | ~~Sprint 1~~ closed |
