# Project State — wirekit

> **Single source of truth for project continuity across sessions.**
> The AI reads this file at the start of every session. Keep it current — it IS the memory.
> Last updated: 2026-10-13

---

## What Currently Works

| Feature / Component | Verified by | Date |
|---|---|---|
| Subnet calculator core (`normalize_mask`, `build_network`, `analyze`) — network, netmask, CIDR, broadcast, host range, counts, next network | `python3 -m pytest` → 23 passed | 2026-10-13 |
| Three mask input forms (`/24`, `24`, `255.255.255.0`) + glued CIDR (`10.0.3.77/21`) | `tests/test_wirekit.py::test_mask_formats_are_equivalent`, `test_glued_cidr_form` | 2026-10-13 |
| Edge cases: `/31` (RFC 3021), `/32`, host-in-larger-network normalization, next network beyond IPv4 space | `test_slash31_point_to_point`, `test_slash32_single_host`, `test_host_address_is_normalized`, `test_next_network_beyond_ipv4` | 2026-10-13 |
| `--bits` teaching mode (binary IP AND MASK) | `test_cli_bits_mode` | 2026-10-13 |
| `--quiz` interactive practice mode (random problems, scoring, `q` to quit) | `test_quiz_question_is_well_formed`, `test_run_quiz_scores_answers` | 2026-10-13 |
| CLI error paths — invalid IP, `/33`, missing mask, no args → exit code 2, no traceback | `test_cli_invalid_ip_fails`, `test_cli_invalid_prefix_fails`, `test_cli_missing_mask_fails`, `test_cli_no_args_fails` | 2026-10-13 |
| Cross-shell installer (`install.sh` → `~/.local/bin` + `net` alias, zsh/bash detection) | Manual run (pre-skill); code review 2026-10-13 | 2026-10-12 |
| GitHub Actions CI (test matrix 3.11–3.14 + security workflow) | Files generated 2026-10-13 — **activates on first push; not yet run** | 2026-10-13 |

---

## In Progress (Exact Next Step)

| Story/Task | Current Unit | Exact Next Action | Files |
|---|---|---|---|
| Skill 6.0 self-bootstrap (BOOT.md Step 0) | All 7 items produced | Developer decides: stage bootstrap files (`git add .devpartner/ AGENTS.md .opencode/ .github/ requirements-dev.txt .gitignore`) | `.devpartner/*`, `AGENTS.md`, `.opencode/skills/*`, `.github/*`, `requirements-dev.txt` |

> **Granularity rule:** "Exact Next Action" means the precise command, function name, or
> file — not "working on auth." A new session must be able to pick up from this without
> asking what to do next.

---

## Broken / Blocked

| Issue | Symptom | Blocking what | Owner |
|---|---|---|---|
| Branch protection not yet enforced | `ci-success` check exists in CI but GitHub repo settings don't require it | Merge gate is advisory only | Developer (manual GitHub settings — see Branch Protection below) |

---

## Planned Next (Prioritized)

1. Stage + commit the Skill 6.0 bootstrap (awaiting developer go-ahead)
2. Push and confirm first CI run goes green (matrix + security workflow)
3. Enable branch protection per settings below
4. Sprint 1 planning ceremony (project-manager skill) — backlog in [ROADMAP.md](ROADMAP.md)
5. Ruff lint/format gate ([DECISIONS.md](DECISIONS.md) → DEBT-001)

---

## Architecture & Conventions

### Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Runtime | Python (CPython) | 3.11–3.14 (dev on 3.14.4) | CI matrix is the support claim |
| Runtime dependencies | **none** | — | stdlib only: `argparse`, `ipaddress`, `random`, `sys` |
| Framework | none | — | single-file CLI (`wirekit.py`) |
| Database | none | — | stateless calculator |
| Auth | none | — | local tool, no network I/O |
| Testing | pytest | 9.0.2 (dev-only, pinned in `requirements-dev.txt`) | includes subprocess CLI integration tests |
| CI | GitHub Actions | checkout@v7, setup-python@v7, codeql-action@v4, gitleaks-action@v3 (SHA-pinned) | generated 2026-10-13 by ci-partner |
| Packaging | none (script copy) | — | `install.sh` copies `wirekit.py` → `~/.local/bin/wirekit` |

### Project Structure

```
wirekit/
├── wirekit.py                 # entire application (single file, stdlib only)
├── install.sh                 # cross-shell installer (zsh/bash)
├── tests/test_wirekit.py      # 23 tests: unit + subprocess CLI integration
├── pytest.ini                 # testpaths=tests, pythonpath=.
├── requirements-dev.txt       # pinned dev/test deps (pytest)
├── README.md                  # hiring-manager-facing (portfolio-partner owns)
├── .github/workflows/ci.yml   # test matrix → ci-success aggregate check
├── .github/workflows/security.yml  # CodeQL + gitleaks + dependency audit/review
├── .github/dependabot.yml     # pip + github-actions weekly updates
├── .devpartner/               # project memory (this directory) — committed
├── .opencode/skills/          # project-local Skill 6.0 skills
└── AGENTS.md                  # opencode entry point → BOOT.md protocol
```

### Key Commands

```bash
# Run without installing
python3 wirekit.py 192.168.1.26 /24

# Install (adds `net` alias)
./install.sh

# Test
python3 -m pytest            # 23 tests, ~2s

# Test with CI-style JUnit report
python3 -m pytest -q --junitxml=test-results/pytest.xml
```

### Conventions

- **Commit message format:** conventional commits — `<type>: <description>`, ≤12 words, imperative (core-partner §8.6)
- **Branch strategy:** GitHub Flow — `main` + `feature/*`, `fix/*`, `refactor/*`, `chore/*`
- **Test strategy:** single suite mixing pure-function unit tests and subprocess CLI integration tests (the CLI *is* the product surface — exit codes and stderr are asserted). E2E = the subprocess tests. No coverage threshold yet (DEBT-002).
- **Accessibility conformance target:** N/A — terminal tool. Keep output plain-text ordered key/value lines (screen-reader friendly); never ship ANSI-only meaning.
- **Runtime dependency policy:** stdlib only. Any new runtime dependency requires a DECISIONS.md entry (dependency vetting, core-partner §1.2).
- **No browser/breakpoints:** not a UI project.

### Branch Protection (pending manual setup — ci-partner §3.7)

Recommended GitHub settings (repo → Settings → Branches → `main`):

| Setting | Value |
|---|---|
| Required status check | `ci-success` (stable aggregate name) |
| Require branches up to date | Yes |
| Require pull request before merge | Yes (1 review, solo-friendly) |
| Require linear history / no force-push | Yes |
| `main` direct pushes | Blocked (docs/chore excepted if desired) |

---

## Environment Setup

- **Required env vars:** none (tool reads no configuration)
- **Services required locally:** none
- **Secrets:** none — repo has no credentials; gitleaks scans to keep it that way

---

## Checkpoints / Rollback Points

| Tag | What it marks | Date |
|---|---|---|
| *(none yet)* | pre-bootstrap state = commit `0f147f1` on `main` | 2026-10-12 |

---

## Active Sprint

| Field | Value |
|---|---|
| Sprint # | — (pre-skill work completed 2026-10-12; no formal sprints yet) |
| Sprint goal | — |
| End date | — |
| See also | [SPRINT_LOG.md](SPRINT_LOG.md) |
