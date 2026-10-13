# Interview Q&A — wirekit

> **Personal software-engineering study bank.** Generated live during development plus
> post-hoc project scans — every entry maps a real design decision, file, or code pattern
> to the question an interviewer would ask, with a teaching-grade model answer written for
> an intermediate developer working toward interview readiness.
> Last updated: 2026-10-13

---

## Index

| Domain | Section | Question count |
|---|---|---|
| System Design & Architecture | [§Scan.1](#d1-system-design--architecture) | 2 |
| Algorithms & Data Structures | [§Scan.2](#d2-algorithms--data-structures) | 2 |
| Language Fundamentals (Python) | [§Scan.3](#d3-language-fundamentals-python) | 3 |
| Frontend / React | — | 0 (not a web project) |
| Backend / API Design | — | 0 (CLI has no API surface) |
| Database & Queries | — | 0 (stateless, no persistence) |
| Security | [§Scan.7](#d7-security) | 3 |
| Performance & Scalability | [§Scan.8](#d8-performance--scalability) | 1 |
| Testing & QA | [§Scan.9](#d9-testing--qa) | 3 |
| CI/CD & DevOps | [§Scan.10](#d10-cicd--devops) | 3 |
| Accessibility | [§Scan.11](#d11-accessibility) | 1 |
| Mobile / Native | — | 0 |
| Data / ML | — | 0 |
| Behavioral & Decisions | [§D14](#behavioral--decision-trail) | 3 |
| Project Deep-Dive | [§D15](#d15-project-deep-dive) | 4 |
| **Total** | | **25** |

**Scan metadata (interview-partner §7):** scanned 2026-10-13 at Skill 6.0 bootstrap — sources read: `wirekit.py`, `tests/test_wirekit.py`, `install.sh`, `README.md`, `pytest.ini`, git history (5 commits), `.devpartner/*` (freshly written), `.github/workflows/*`.
**Research (interview-partner §1):** questions calibrated against rungcode.io FDE Python question bank (2026-06) — small-CLI rubric: argparse, clean usage, non-zero exit on bad input, edge-case correctness first; probeinterview.com senior-Python guide (2026-06) — senior signal is judgment/tradeoffs, not trivia; datadriven.io take-home rubrics (2026-07) — "single 600-line script" and "tests that pass regardless" are scored failure modes; Understanding Recruitment Python framework (2025-08) — four-axis rubric (accuracy, code quality, problem solving, communication).

---

## Story Entries (Chronological)

### STORY-002 — Ruff lint+format gate (local + CI) — 2026-10-13

**Q (T1):** Why ruff over the flake8 + black + isort trio?

**A:** One Rust binary does linting, formatting, and import sorting with one config (`ruff.toml`), runs 10–100× faster than the Python trio, and its formatter is black-compatible so output style is familiar. Tradeoff: smaller plugin ecosystem than flake8 — accepted because the official rule set (`E,F,UP,B,SIM,I`) covers this codebase's needs, and ruff is dev-only so ADR-002 (zero *runtime* deps) is untouched. Rejected installing all three tools: three configs, three version pins, three CI steps.

**Q (T1):** Your local ruff (0.15.15) was older than the pin (0.17.0) — why does that matter?

**A:** Version drift is the classic "passes locally, fails in CI" trap — different ruff versions enable different rules (0.17.0 even changed defaults and `target-version`). Fix: pin `ruff==0.17.0` in `requirements-dev.txt`, upgrade the local tool via `pipx upgrade ruff`, and have CI install from the same file — one source of truth for both environments (in this project: `requirements-dev.txt:2`, gate verified green on both after alignment).

**Q (T1):** Why configure ruff in `ruff.toml` instead of the conventional `pyproject.toml`?

**A:** `pyproject.toml` signals "this is a packaged project" — wirekit deliberately has no packaging metadata (single-file `install.sh` distribution, ADR-002), so `ruff.toml` keeps tool config from implying a packaging decision that hasn't been made. Equivalent schema, no `[tool.ruff]` header needed. When packaging lands (pipx/PyPI scale item), config can migrate into `pyproject.toml` in one commit. Edge case: ruff discovers `ruff.toml` automatically — no `--config` flag needed, so CI commands stay identical to local.

---

### STORY-006 — Hypothesis property tests (subnet math) — 2026-10-13

**Q (T1):** Example tests passed 23/23 — why add property-based tests?

**A:** Examples prove *specific* cases; properties prove *universal invariants*. Subnet math is all invariants: every network must be prefix-aligned, broadcast must equal network+total−1, usable hosts must follow the /31 vs /32 rule — for all 2³² addresses × 33 prefixes, not the dozen an author imagines. Hypothesis generates edge space automatically (its first find was `0.0.0.0/0`, which no human example covered), plus shrinking turns failures into a minimal repro. Cost: one dev dependency (`hypothesis==6.169.0`, dev-only so ADR-002 untouched).

**Q (T1):** The first red run failed — was that a bug in wirekit?

**A:** No — it was a bug in the *test*: I assumed `analyze()` returned integer-ish values and called `int("0.0.0.1")`. Property tests find test-specification bugs too: the failure forced a precise decision about `analyze()`'s output contract (dotted strings), documented in `rows["HostMin"]` parsing via `ipaddress.ip_address()`. Lesson: red-first applies to property tests equally — triage the failure into (code bug | test bug | property bug) before touching implementation; the other 4 properties passed immediately, so code was correct.

**Q (T1):** What properties did you pick, and why these five?

**A:** Chose independent invariants covering each output dimension: (1) alignment `nw % total == 0` + ip-in-block, (2) broadcast arithmetic, (3) internal consistency of all 9 `analyze` rows incl. usable formula, (4) next-network one-block-past with the `> 0xFFFFFFFF` → "beyond IPv4 space" edge, (5) all four mask input forms (`24`, `/24`, dotted, slash-IP) build the same network. Deliberately avoided: "ip is inside HostMin..HostMax" (false for network-address IPs — a property that must hold by design, not intuition) and quiz randomness (covered by seeded example tests).

---

### STORY-003 — Coverage floor (pytest-cov, fail-under=100) — 2026-10-13

**Q (T1):** Your subprocess CLI tests exercise `main()` end-to-end, yet coverage showed `main()` at 0%. How?

**A:** Coverage instruments *the process it runs in*. `subprocess.run([sys.executable, "wirekit.py", ...])` spawns a fresh interpreter with no coverage tracer — those lines execute, but nothing records them. Fix was dual-layer testing: keep subprocess tests as E2E (they assert real exit code 2 and stderr, which in-process can't prove), add in-process tests calling `wirekit.main()` with `monkeypatch.setattr(sys, "argv", ...)` + `capsys` for coverage. Alternative `COVERAGE_PROCESS_START`/sitecustomize tracing — rejected as heavy machinery for a 105-statement module (TECH-006).

**Q (T1):** Where did `--cov-fail-under=100` come from — vanity metric?

**A:** Measured first: initial baseline was 70% (missing: `show_bits`, quiz EOF handler, all of `main()`). Filled gaps with 7 targeted tests → re-measured 100% of 105 statements → set the floor at the *demonstrated* baseline, not an aspiration (an aspirational floor with nothing behind it just teaches people to game it). 100% is affordable here because the module is tiny and pure-function-heavy; the documented escape is `# pragma: no cover` (used once, on the `__main__` call). On a larger codebase the same method would land at 80–90 — the method is measure→justify→set, never "pick a round number."

**Q (T1):** What did the measurement actually find — was it worth it?

**A:** Three real gaps: (1) quiz EOF handler — the path users hit pressing Ctrl-D daily, never tested; (2) `show_bits` — only reached through a subprocess, so no in-process assertions on its format; (3) `main()` error paths had subprocess coverage only. Each got a test in `tests/test_wirekit.py` matching existing style (monkeypatch argv, capsys, `pytest.raises(SystemExit)` for `parser.error`). Score: 35 tests, 100% coverage, suite still ~2.5s.

---

### STORY-001 — `--json` output mode — 2026-10-13

**Q (T1):** Why keep the human keys (`"Hosts/Net"`, `"Next network"`) in JSON instead of `snake_case` machine keys?

**A:** One data source, two renderings — `analyze()` returns rows, text mode formats them, JSON mode `dict(rows)` + `json.dumps`. Mapping to `snake_case` would add a second schema to invent, test, and keep in sync; drift risk with zero user benefit since `jq` handles any key (`.["Hosts/Net"]`). Values stay strings for the same reason: honest 1:1 mirror of the table; callers can `tonumber` if they need ints. Tradeoff accepted and documented — if a real consumer ever needs typed/aliased output, that's a versioned schema change, not a silent rename.

**Q (T1):** `--json --bits` errors with "not allowed with" — why not just ignore `--bits`?

**A:** Silent ignoring is how scriptable CLIs rot: a user's pipe gets half-JSON half-binary-dump and the bug surfaces three steps downstream with no attribution. `add_mutually_exclusive_group()` turns it into exit code 2 with a clear stderr message at parse time — same failure style as every other CLI error (consistent exit-code contract). Also tightened `--quiz` into the same group: one mode per invocation.

**Q (T1):** Implementation detail: why is `json` importable in stdlib relevant here?

**A:** Project rule ADR-002: runtime stays stdlib-only — any new *runtime* dependency needs a DECISIONS entry. `json` is stdlib, so zero governance overhead and zero supply-chain surface; the flag is ~4 lines (`if args.json: print(json.dumps(dict(rows))); return`). Interview signal: knowing which batteries are included (`json`, `argparse`, `ipaddress`) is table stakes; the judgment is in the output contract, not the import.

---

### STORY-007 — `--conv` base converter — 2026-10-13

**Q (T1):** `--conv 11111111` returns 255, not eleven-million-one-hundred-eleven-thousand. Why?

**A:** Documented ambiguity rule: strings of only `0`/`1` digits (no underscores) are read as **binary** — that's the conversion people want in an IPv4 tool (`--conv 11111111` = the /8 mask). Underscores opt out into decimal (`1_000_000` → 1000000 — underscores signal thousand-grouping, i.e. decimal intent). Prefixes (`0x`, `0b`, `0o`) always win via `int(text, 0)`. Every rule has a test naming the behavior (`test_parse_number_bare_zeroes_and_ones_read_as_binary`) so the surprise is at least a documented, tested surprise.

**Q (T1):** Your first test run failed 6 cases — what actually broke?

**A:** Two different failures, both mine: (1) a hand-arithmetic slip — I asserted `0xC0A8011A == 3232235786` when the correct value is `3232235802` (verified: `192·2²⁴ + 168·2¹⁶ + 1·2⁸ + 26`); the implementation was right and the *test* was wrong. (2) A real design flaw: `1_000_000` was being parsed as binary 64 after underscore-stripping — fixed by only taking the binary path when the input has no underscores. Lesson: when code and test disagree, verify the test against ground truth (`python3 -c 'print(...)'`) before touching code.

**Q (T1):** Why a separate `parse_number()` instead of inline in `main()`?

**A:** Purity + the 100% coverage floor: `parse_number` is a deterministic string→int function with ~12 meaningful inputs — parametrized unit tests cover every branch cheaply; `main()` stays a thin argparse shell. Also `convert()` returns rows in the same `(key, value)` shape as `analyze()`, so the existing table printer and `--json` branch work unchanged — adding a mode cost one flag, one 12-line function, zero changes to output plumbing. That's the payoff of the row-shaped contract from STORY-001.

---

### STORY-004 — MIT LICENSE + README CI badge — 2026-10-13

**Q (T1):** Why MIT over Apache-2.0 or GPL for a portfolio CLI?

**A:** The audience is portfolio reviewers and casual tinkerers — MIT's one condition (keep the copyright notice) is the lowest friction possible, which is the point of a permissive license on a small tool. Apache-2.0 adds a patent grant — valuable for companies shipping products, overkill for a 200-line calculator. GPL would *restrict* reuse, directly opposing the README's goal ("if you want others to reuse this"). Copyright holder sourced from `git config user.name` — not guessed.

**Q (T1):** Why put the *full local gate* commands in the README's Contributing section?

**A:** The README's job is to make contribution frictionless and honest — telling people "run `pytest`" when the real gate is `pytest && ruff check && ruff format --check` guarantees their first PR fails CI on style alone. The line "the same three commands run in CI" also communicates engineering discipline in one sentence: local/parity is enforced, not aspirational (ci-partner §1.1 mirror). Badge at the top gives the instant health signal; the gate commands make the signal maintainable.

---

## Project Scan (Post-Hoc) — 2026-10-13

### D1. System Design & Architecture

**Q: Walk me through wirekit end to end — draw the data flow from `argv` to stdout. Where do `--json` and IPv6 plug in?** (T3)

**Direct answer:** It's a four-stage pipeline in one file: `main()` parses argv with argparse → `normalize_mask`/`build_network` canonicalize input into an `ipaddress.IPv4Network` → `analyze()` computes all nine fields as a pure function → a formatting loop prints aligned `key = value` rows; `--bits` and `--quiz` are sibling modes that branch off `main()` before or after that pipeline.

**Concept:** Parse at the boundary, compute in a pure core, present at the edge. `analyze()` takes a network object and returns data — it never prints, never reads input — so presentation and input concerns can change without touching the math.

**Why / tradeoffs:** Single file vs. package layout: at 172 lines, splitting into `wirekit/{parse,compute,cli}.py` adds indirection with no reuse to justify it. Rejected the package split *for now*; the right trigger is a second consumer (an HTTP wrapper, a library import) — then the pure core moves out unchanged. Take-home rubrics call single-file scripts a rejection signal (datadriven.io) — that rule bites at 600+ lines with mixed concerns, not at 172 lines with one concern.

**In this project:** parse `wirekit.py:135-169` (`main`) · normalize `wirekit.py:18-34` · compute `wirekit.py:37-67` (`analyze`) · present `wirekit.py:161-164` · modes `wirekit.py:70-76` (`show_bits`), `wirekit.py:109-131` (`run_quiz`). `--json` replaces only the print loop (rows are already `(key, value)` pairs — serialize to `dict`). IPv6 plugs into `build_network` (`ipaddress.ip_network` is version-agnostic) but the output schema, `analyze`'s `/31`/`/32` branches, and the quiz are IPv4-shaped — that's the real cost.

**Edge cases:** `nargs="?"` means `ip`/`mask` default to `None` — the missing-mask path (`wirekit.py:152-153`) must be handled before parse; only *parsing* sits inside `try/except ValueError` — `analyze()` at `wirekit.py:161` runs outside it (the exact hole ERR-001 escaped through).

**At scale:** As an HTTP service, `analyze()` needs no refactor — it's pure and O(1). Add a transport layer that validates at the boundary and serializes the row list; horizontal scaling is trivial because there's no shared state.

**Interviewer's intent:** Can they see the boundaries in someone else's code and name where new features belong — comprehension is the senior bottleneck (probeinterview).

**Follow-ups:**
- Q: How do you add `--json` without touching the math? → A: change only the presentation loop — `analyze()` already returns structured pairs.
- Q: What breaks if `analyze()` grows a side effect? → A: quiz mode and any future API reuse lose their pure core; tests would need mocking.
- Q: Draw the equivalent for a service version. → A: route handler → same parse/compute/serialize stages, validation returns 400 instead of exit 2.

---

**Q: If this calculator were an HTTP API serving 10k requests/second, what changes?** (T2)

**Direct answer:** Almost nothing in the core — `analyze()` is O(1) integer math with zero I/O and no shared state, so you add a transport layer (route + serialization) and boundary validation; the work per request is microseconds and Python handles 10k/s of that comfortably.

**Concept:** Stateless pure functions scale linearly with replicas; bottlenecks come from I/O, locks, and shared resources — none exist here. Scaling questions are answered by finding the *actual* constraint, not by rewriting the hot path speculatively.

**Why / tradeoffs:** Rejected "rewrite in Go/C for performance" — premature; it trades development speed and the stdlib-only install story (ADR-002) for speed you won't measure. The rewrite becomes right only if profiling showed interpreter overhead dominating *after* the transport was efficient — it wouldn't.

**In this project:** `wirekit.py:37-67` — no globals mutated, no randomness (except quiz mode), no clock; `next network` already guards the 32-bit boundary (`wirekit.py:51-55`).

**Edge cases:** malformed input must fail at the boundary with 400 (mirroring `parser.error` → exit 2 at `wirekit.py:153,159`); never let `ipaddress` exceptions leak as 500s.

**At scale:** 10k/s → several gunicorn/uvicorn workers, stateless, cache nothing; 1M/s → measure serialization first (`orjson`), still no algorithmic change.

**Interviewer's intent:** Do they measure before optimizing, or reach for a rewrite reflex?

**Follow-ups:**
- Q: What would you cache? → A: nothing — the computation is cheaper than a cache lookup.
- Q: Where's the first real bottleneck? → A: HTTP overhead/serialization, not the math.

---

### D2. Algorithms & Data Structures

**Q: What's the arithmetic behind "Network = IP AND mask", and how do broadcast and the next network follow from it?** (T2)

**Direct answer:** The network address is the bitwise AND of the 32-bit IP and the 32-bit mask — AND zeroes every host bit; broadcast is the network OR the inverted mask (set all host bits to 1); the next network is the current network plus `2^host_bits`, guarded against overflowing the 32-bit space.

**Concept:** A mask is a bitmask of ones (network part) and zeros (host part). AND keeps only network bits; OR NOT fills the host part. Every field in the output is a derived quantity from that one operation.

**Why / tradeoffs:** wirekit delegates the AND to `ipaddress` (`IPv4Network` computes it internally) rather than hand-rolling bitmasking — stdlib correctness (RFCs, edge cases) over visible arithmetic. The trade: learners can't see the operation in `analyze()` — which is exactly why `--bits` exists (`show_bits` prints `addr & mask` explicitly).

**In this project:** `wirekit.py:70-76` prints `IP`, `MASK`, `NETWORK` in binary — `172.30.197.206 /20` → mask `11111111111111111111000000000000` zeroes the low 12 bits → `172.30.192.0`. Next network: `wirekit.py:51-55` (`int(nw) + total`, bound `0xFFFFFFFF`).

**Edge cases:** `/0` → network `0.0.0.0`, broadcast `255.255.255.255`, next = beyond space (the guard path); top-of-space overflow is the ERR-001 case (walked through in [§D15](#d15-project-deep-dive)).

**At scale:** unchanged — the operation is a single CPU instruction at any "scale"; the concept is what matters for interviews, not throughput.

**Interviewer's intent:** Can they derive the algorithm from first principles, or do they only know the API call?

**Follow-ups:**
- Q: Why is `192.168.1.26` in `192.168.1.0/26` reported as network `.0`? → A: AND with `255.255.255.192` clears the low 6 bits.
- Q: Compute usable hosts for /26 by hand. → A: 2^6 − 2 = 62.

---

**Q: How many usable hosts are in a prefix, and why do /31 and /32 break the formula?** (T1)

**Direct answer:** `2^(32−prefix) − 2` — subtracting the network and broadcast addresses — but /31 counts **both** addresses as usable (RFC 3021 point-to-point links) and /32 is a single host with 1 usable address.

**Concept:** The −2 rule exists because traditional subnets reserve the first and last addresses. RFC 3021 realized a /31 has exactly two addresses and wasting both would halve point-to-point link efficiency.

**In this project:** `wirekit.py:44-49` branches on `prefix >= 31`: `host_min, host_max = nw, bc; usable = total`, else `nw + 1, bc - 1; total - 2`. Tests pin both: `tests/test_wirekit.py:64-79`.

**Edge cases:** forgetting the branch reports 0 usable hosts on every /31 — the classic interview trap.

**Interviewer's intent:** Do they know the rule *and* its documented exceptions?

**Follow-ups:**
- Q: Who uses /31 in practice? → A: router point-to-point subinterfaces.
- Q: What does `Hosts/Net` mean for /32? → A: 1 — the address itself.

---

### D3. Language Fundamentals (Python)

**Q: In wirekit, why can an exception fire *inside* an expression before your guard runs? What's the lesson?** (T2)

**Direct answer:** Because `IPv4Address + int` is an overloaded operator that **validates on construction** — at the top of the address space `nw + total` builds `IPv4Address(2**32)` and raises `AddressValueError` during evaluation, so the subsequent `if nxt <= ...` guard is never reached.

**Concept:** Python operator overloading (`__add__`) can do arbitrary work — including raising. Guarding the *result* of an expression is useless if evaluating the expression itself throws. Related: `AddressValueError` subclasses `ValueError`, which is why the bug could masquerade as a handled input error.

**Why / tradeoffs:** The fix chose explicit `int` arithmetic with a literal bound (`0xFFFFFFFF`) over wrapping the expression in `try/except AddressValueError` — catching would treat the symptom and silently absorb future overflow sites; `int` in Python is unbounded, so no overflow can occur *during* the computation, only at the deliberate conversion back to `IPv4Address` — which the guard now precedes.

**In this project:** reproduced 2026-10-13: `IPv4Address('255.255.255.0') + 256` → `AddressValueError: 4294967296 (>= 2**32) is not permitted as an IPv4 address`; fixed at `wirekit.py:51-55`; [ERR-001](ERROR_LOG.md).

**Edge cases:** the guard must run *before* constructing `IPv4Address(nxt)` — order matters; `main()`'s `try` (`wirekit.py:155-159`) only wraps parsing, so any future compute-time `ValueError` still escapes as a traceback — a known narrowing worth fixing.

**At scale:** irrelevant to throughput; relevant to correctness forever — one of the few bug classes that doesn't self-heal.

**Interviewer's intent:** Can they reason about *evaluation order* and exception timing, not just what the code looks like?

**Follow-ups:**
- Q: Why not `try/except OverflowError`? → A: the raise is `AddressValueError`, not `OverflowError` — wrong except-clause would still crash.
- Q: Where should compute-time errors be caught? → A: widen `main()`'s try to cover `analyze()`, or keep `analyze` total (it now is).

---

**Q: How does wirekit turn bad input into a clean error instead of a traceback?** (T1)

**Direct answer:** `parser.error(msg)` from argparse — it prints usage + message to **stderr** and exits with status **2**, and wirekit funnels every input failure (`ValueError` from `ipaddress`/`normalize_mask`, missing mask, no args) into it.

**Concept:** The exit-code contract: 0 = success, 2 = bad usage (argparse's convention), non-zero for anything script callers must detect. Tracebacks are developer-facing; usage errors are user-facing — the boundary decides which.

**In this project:** `wirekit.py:153` (no IP), `wirekit.py:158-159` (parse failures), `wirekit.py:22-23` (prefix range), asserted by four CLI tests (`tests/test_wirekit.py:139-161`) checking `returncode == 2` and stderr content.

**Edge cases:** the one hole — `analyze()` runs outside the try (see D3.1); tests would catch any new traceback path because they assert stderr, not just exit codes.

**Interviewer's intent:** Do they treat exit codes as a real API? (rungcode CLI rubric: "non-zero exit on bad input, no crash.")

**Follow-ups:**
- Q: Why exit 2 and not 1? → A: argparse reserves 2 for usage errors; callers can distinguish misuse from runtime failure.
- Q: What goes to stderr vs stdout? → A: errors/usage to stderr, results to stdout — pipelines depend on it.

---

**Q: What does `token.strip().lstrip("/")` do — and what's the classic `lstrip` trap it avoids?** (T1)

**Direct answer:** It strips surrounding whitespace, then removes **leading slash characters** so `"/24"` → `"24"`; the classic trap is that `lstrip` removes a *set of characters*, not a prefix — `lstrip("/")` would happily eat any number of slashes, and a careless `lstrip("0")` on numbers silently corrupts them (`"024".lstrip("0")` → `"24"`).

**Concept:** `str.lstrip(chars)` treats `chars` as a character set to discard from the left — the opposite of what the name suggests to many devs. Prefix-removal wants slicing (`token[1:]` if `token.startswith("/")`) or `removeprefix` (3.9+).

**In this project:** `wirekit.py:19` — safe here because mask tokens never start with a digit that's also in the strip set (only `/` is stripped, and digits follow), verified by `tests/test_wirekit.py:109-113`.

**Edge cases:** `normalize_mask("///24")` → `"24"` (arguably lenient); a mask of `"/"` alone → `""` → falls to `ipaddress` and errors cleanly.

**Interviewer's intent:** Classic string-API gotcha probe — separates people who've been bitten from people who've only read the docs.

**Follow-ups:**
- Q: Rewrite with `removeprefix`. → A: `token.strip().removeprefix("/")`.
- Q: Why `.isdigit()` first? → A: distinguishes bare prefixes from dotted masks, with a clear range error for `/33`.

---

### D7. Security

**Q: Threat-model wirekit. Where's the attack surface?** (T2)

**Direct answer:** Three surfaces only: CLI argument parsing (validated by `ipaddress`/argparse — no injection primitive exists since nothing is `eval`'d, formatted into shells, or written to disk), the `install.sh` privileged path (copies a binary and appends to your shell rc), and the test suite's `subprocess` usage.

**Concept:** Attack surface = trust boundaries × privileged operations. A pure calculator with no network, no files, no secrets, no deserialization has a near-empty threat model — the danger concentrates in the *installer* (it edits `~/.bashrc`/`~/.zshrc`) and in supply chain (what code you run at all).

**Why / tradeoffs:** Zero runtime dependencies (ADR-002) is itself the security decision: no PyPI code executes on end-user machines. Cost: you reimplement conveniences click/rich would give — accepted, because a 172-line stdlib file is reviewable in one sitting (reviewability *is* a control).

**In this project:** input boundary `wirekit.py:155-159`; `install.sh:7-20` — `cp`/`chmod`/`printf` append with a `grep -q 'alias net='` idempotence guard, `case` selects rc file from `$SHELL`; tests spawn the CLI with a **list** of args, `shell=False` by default (`tests/test_wirekit.py:22-27`) — no shell injection seam.

**Edge cases:** `install.sh` assumes `$HOME` paths without spaces (`printf ... >> "$RC"` is quoted, but the suggested `source $RC` line and alias content would misbehave with spaces); `alias net="wirekit"` depends on `~/.local/bin` PATH ordering — a PATH-hijack window if a writable dir precedes it.

**At scale:** as a service, the boundary validation becomes the WAF-equivalent — return 400 on parse failure, never interpolate input into shell commands, rate-limit (cheap O(1) handler).

**Interviewer's intent:** Can they produce a *bounded* threat model instead of reciting OWASP generically? (Security review of code with user input — standing Security Reviewer hat.)

**Follow-ups:**
- Q: You add config-file loading — what format? → A: TOML/JSON (data, not code) — never pickle, never import of user paths.
- Q: Biggest real risk here? → A: the installer editing shell rc files.

---

**Q: You ship zero runtime dependencies — what does that buy you security-wise, and what does CI still audit?** (T1)

**Direct answer:** No third-party code runs on user machines at all — the PyPI-compromise and transitive-dependency-vulnerability classes don't exist for `wirekit` users; CI still audits the *dev* toolchain because that's what runs on the runner.

**Concept:** Separate the runtime trust boundary (users) from the build trust boundary (CI). Users get stdlib; CI installs pinned `pytest` (9.1.1 — chain: 9.0.2 vulnerable, 9.0.3 minimum fix for PYSEC-2026-1845 found by the first pip-audit run, then 9.1.1 latest superseding Dependabot's PR) — audited by `pip-audit`, PR-time `dependency-review-action` fails on high severity, Dependabot keeps pins and actions current, gitleaks scans history for secrets.

**In this project:** `requirements-dev.txt` (only pinned dep) → `security.yml` dependencies job; `dependabot.yml` (pip + github-actions weekly).

**Edge cases:** dev-dep compromise still yields malicious CI (runs with `GITHUB_TOKEN`, read-only by the workflow's least-privilege `permissions: contents: read`).

**Interviewer's intent:** Do they distinguish runtime vs build supply chain?

**Follow-ups:**
- Q: Why SHA-pin gitleaks? → A: tags are mutable; the SHA is not (ci-partner §3.9).
- Q: What if CI needed a runtime dep later? → A: vet it (DECISIONS.md), pin it, audit it.

---

**Q: Where would secrets go in this project if you ever needed them?** (T1)

**Direct answer:** Environment variables or GitHub Encrypted Secrets — never source, never `.devpartner/`, never comments; and right now the repo has *none*, which gitleaks (security workflow) and GitHub secret scanning enforce continuously.

**Concept:** Secrets belong in the environment layer, gitignored (`.env`/`.env.*` added to `.gitignore` at bootstrap 2026-10-13), referenced by name in code/docs — a leaked key is an incident requiring rotation, not a config fix.

**In this project:** workflow uses `${{ secrets.GITHUB_TOKEN }}` only (`security.yml` gitleaks job) — auto-scoped, never echoed; no hardcoded credentials anywhere (scan passes).

**Edge cases:** writing a secret into `.devpartner/` "just for now" — blocked by convention (core-partner §10.2) and caught by gitleaks if committed.

**Interviewer's intent:** Baseline secrets hygiene — non-negotiable in every backend interview.

**Follow-ups:**
- Q: A key lands in git history — now what? → A: rotate first, then purge history; alerts may show resolved while history still leaks (gitleaks README warns exactly this).

---

### D8. Performance & Scalability

**Q: Where does time actually go in wirekit and its test suite?** (T1)

**Direct answer:** In the CLI, Python interpreter startup (~5–15 ms) dominates — the subnet math is microseconds; in the suite, the 7 subprocess-based tests each pay a fresh interpreter start, which is why 23 tests take ~0.7–2 s rather than milliseconds.

**Concept:** Micro-benchmarks must measure the whole invocation. Process spawn = fork + exec + interpreter init + imports (`ipaddress`, `argparse`) — orders of magnitude above the computation. This is also why *not* caching or precomputing anything is correct here.

**In this project:** measured 2026-10-13: full suite 1.98 s cold / 0.74 s warm (`ROADMAP.md` Performance Log); subprocess layer `tests/test_wirekit.py:22-27`; pure-function tests run in microseconds.

**Edge cases:** if the suite grows 10×, the subprocess layer becomes the wall-clock wall — options: reduce CLI cases to one representative happy path + keep error cases (they're the contract), or accept ~5 s (still within the <5 s NFR).

**At scale:** CLI NFR is <100 ms per invocation — currently ~an order of magnitude under; nothing to optimize, and profiling before assuming is the point (core Core Driver: Performance).

**Interviewer's intent:** Do they know *where* time goes before proposing optimizations?

**Follow-ups:**
- Q: Would pytest-xdist help? → A: partially — subprocess tests parallelize fine, but at 23 tests the overhead of distributing exceeds the gain.
- Q: Could you make the CLI faster? → A: drop the `ipaddress` import cost? No — it's stdlib and correct; not worth it.

---

### D9. Testing & QA

**Q: Explain wirekit's test strategy — what's unit, what's integration, and why this mix?** (T2)

**Direct answer:** One suite, two layers: **pure-function unit tests** calling `analyze`/`build_network`/`normalize_mask` directly, and **black-box CLI integration tests** that spawn the real script via `subprocess` and assert exit codes, stdout, and stderr — integration-weighted, because the CLI *is* the product.

**Concept:** The Testing Trophy: invest most in how units work together. For a CLI, the process boundary is the integration surface — argument parsing, exit codes, stderr routing, and interpreter invocation (`sys.executable`, not a bare `python`) are exactly where "works locally" bugs live, and only subprocess tests see them.

**Why / tradeoffs:** Subprocess tests are slower (interpreter per test) and env-sensitive — accepted because they catch packaging/path bugs (e.g. `pythonpath` issues, shebang problems) invisible to unit tests. Rejected mocking the CLI functions instead: every mock moves the test away from real usage (mocking discipline).

**In this project:** unit examples `tests/test_wirekit.py:30-93`; integration `:125-161` (`run_cli` helper at `:22-27`); parametrized contract `:95-101` — one test proving all three mask spellings produce identical results.

**Edge cases:** tests must assert *stderr* content and `returncode`, not just stdout — asserting only happy output would let tracebacks slip through (the ERR-001 class).

**At scale:** suite growth strategy — keep integration as the gate, move slow/edge-heavy exploration to fewer CLI cases; add coverage measurement before trusting the mix blind (DEBT-002).

**Interviewer's intent:** Can they justify a test *strategy*, not just write assertions?

**Follow-ups:**
- Q: What's missing? → A: coverage data (DEBT-002), EOFError/KeyboardInterrupt branch in quiz (D9.2).
- Q: Why `sys.executable`? → A: runs under the same interpreter as pytest — no PATH ambiguity across the 3.11–3.14 matrix.

---

**Q: `test_run_quiz_scores_answers` monkeypatches both `make_quiz_question` and `input`. What does it verify — and what does it miss?** (T2)

**Direct answer:** It verifies the **scoring and formatting logic** given a controlled question/reply stream (asserting `Correct!`, `Not quite`, and the exact `Score: 1/2`); it misses the random-question generation path, the quit-path scoring, and the `EOFError`/`KeyboardInterrupt` handler — those live (or don't) elsewhere.

**Concept:** Test seams: injecting a fake `input` and a fixed question iterator turns an interactive loop into a deterministic unit test. The danger probeinterview names is a "test that passes whether or not the bug is fixed" — this one doesn't: break `_clean` or the scoring increment and `Score: 1/2` fails.

**Why / tradeoffs:** Monkeypatching `builtins.input` trades realism for determinism — right call for scoring math; the realism gap is covered by *separate* tests: `test_quiz_question_is_well_formed` (`:168-174`) hammers the generator with a seeded `random.Random(0)` over 100 draws (reproducible, not flaky).

**In this project:** `tests/test_wirekit.py:176-193`; the third reply `"q"` exercises quit-before-increment — which is *why* the score is `1/2`, not `1/3`.

**Edge cases:** **Real gap:** the `except (EOFError, KeyboardInterrupt)` branch (`wirekit.py:117-120`) has no test — piped-input death (`` `net --quiz` </dev/null ``) is untested. Also untested: `run_quiz`'s zero-question exit (`if asked:` guard, `wirekit.py:129`).

**At scale:** as the suite grows, seeded RNG keeps generator tests deterministic — never use the global `random` directly in assertions.

**Interviewer's intent:** Can they audit a test suite for what it *doesn't* cover? (Senior signal: verification over green checkmarks.)

**Follow-ups:**
- Q: How would you test the EOF path? → A: monkeypatch `input` to raise `EOFError`, assert clean score-less exit.
- Q: Why not drive the real `input` with subprocess + stdin? → A: would work for integration coverage; unit is cheaper for scoring logic.

---

**Q: Why is the three-mask-forms check one parametrized test instead of three tests?** (T1)

**Direct answer:** Because it asserts a single contract — *"all accepted mask spellings are equivalent"* — and parametrize makes each failing form an explicit case (`/26` vs `26` vs `255.255.255.192`) while keeping one set of expected values to maintain.

**Concept:** Test shape follows the claim. Equivalence is one claim about three inputs; separate tests would duplicate the assertions and let them drift apart, hiding a real regression (e.g. dotted-mask handling breaking while prefix form still passes).

**In this project:** `tests/test_wirekit.py:95-101` — `@pytest.mark.parametrize("mask", [...])`, all asserting `CIDR == "/26"`, `Hosts/Net == "62"`.

**Edge cases:** the glued form `10.0.3.77/21` is *not* equivalent-input — it's a different parse path, so it correctly gets its own test (`:103-106`).

**Interviewer's intent:** Do they use parametrization deliberately rather than copy-paste tests?

**Follow-ups:**
- Q: Add a fourth form — where? → A: add to the parametrize list; zero new assertions.
- Q: When would you split them? → A: if the forms began having form-specific error behavior.

---

### D10. CI/CD & DevOps

**Q: Walk me through the CI pipeline for this repo — and why it's shaped this way.** (T2)

**Direct answer:** Two workflows: **CI** runs pytest as a matrix over Python 3.11–3.14 (`fail-fast: false`, pip cache keyed on `requirements-dev.txt`, JUnit report uploaded per-version) feeding a single `ci-success` aggregate job; **Security** runs CodeQL SAST, gitleaks secret scan (SHA-pinned), `pip-audit` on the pinned dev deps, and PR-time dependency review failing on high severity — with a weekly cron re-scan.

**Concept:** CI mirrors the local commit gate (format → lint → test → build) — here only the test stage exists because no linter is configured yet. Parallel jobs + an explicit `needs:` graph + one stable aggregate check: branch protection requires `ci-success`, so changing the matrix later never reconfigures the rule. Least-privilege `permissions: contents: read`, `concurrency` cancels superseded runs, every job has a timeout.

**Why / tradeoffs:** Scaled breadth for a 172-line script: no build job (ships as a single script — nothing to package), no SBOM/container scan (no dependencies, no Dockerfile), no lint stage yet (DEBT-001 — deliberately deferred so the first run proves a green baseline before a new gate lands). Rejected test-only minimal: below the ci-partner bar — a pipeline without a security stage is the shape that leaks (ADR-001).

**In this project:** `.github/workflows/ci.yml` (matrix `3.11–3.14`, aggregate at the bottom), `.github/workflows/security.yml`, `.github/dependabot.yml`.

**Edge cases:** gitleaks **v2 is dead** — Node 20 was removed from GitHub runners 2026-09-16 — so v3 (SHA `e0c47f4…`) is mandatory, not stylistic; first run itself is a risk (RISK-002: cache/config surprises), mitigated by a local dry-run of the exact CI test step (done 2026-10-13).

**At scale:** matrix grows with supported versions; the aggregate check name stays stable forever — that's the whole trick.

**Interviewer's intent:** Can they design a pipeline a senior platform engineer would defend — not just a green run? (ci-partner §1.0 bar.)

**Follow-ups:**
- Q: Why is cache keyed on a requirements file? → A: hash-based invalidation — change deps, get a fresh cache; a never-changing key serves stale packages forever.
- Q: What's the first thing you'd add? → A: ruff stage in *both* the local gate and CI (DEBT-001) — together, never one side.

---

**Q: Why one `ci-success` job instead of requiring all four matrix jobs by name?** (T1)

**Direct answer:** A single aggregate job with a stable name is the one status check branch protection requires — so adding or dropping Python versions later never touches the branch-protection config, and the required check can't silently stop matching.

**Concept:** Required checks are matched by literal job name; `Test (Python 3.13)`-style names couple repo settings to matrix internals. The aggregate `needs: [test]` + fail-on-`failure|cancelled` pattern gates the whole graph behind one contract.

**In this project:** `ci.yml` `ci-success` job (`if: always()` so it runs even when the matrix fails, then exits 1).

**Edge cases:** `if: always()` is load-bearing — without it, a failed dependency would skip the aggregator and the required check would never report.

**Interviewer's intent:** Do they know how required status checks actually bind to jobs?

**Follow-ups:**
- Q: Matrix job cancelled by concurrency? → A: aggregator sees `cancelled` → fails → merge blocked. Correct.

---

**Q: Cache correctness — what does `cache: pip` actually buy here, and what would make it wrong?** (T1)

**Direct answer:** It reuses pip's *download* cache between runs (keyed on the hash of `requirements-dev.txt`) — install still runs every time; it becomes wrong if keyed on nothing (stale forever) or if it cached an installed venv (works until the Python version in the matrix changes underneath it).

**Concept:** Cache keys must track the inputs that can invalidate the output — dependency file hash for pip, matrix Python version for interpreters. A cache miss must never be a correctness failure: `pip install -r requirements-dev.txt` runs regardless.

**In this project:** `ci.yml` setup-python step: `cache: pip` + `cache-dependency-path: requirements-dev.txt` — one pinned dep (`pytest==9.1.1`), so savings are seconds, correctness is the point (CI runs what you run).

**Edge cases:** typo in `cache-dependency-path` silently disables caching (research lesson — validated at scaffold); this repo's local PEP 668 environment doesn't apply to CI runners (setup-python's interpreter isn't externally managed).

**Interviewer's intent:** Caching questions are a proxy for "do they understand invalidation?"

**Follow-ups:**
- Q: Would you cache `.pytest_cache`? → A: no — per-run artifact, no cross-run value.

---

### D11. Accessibility

**Q: Is a CLI "accessible"? What does that mean without a browser?** (T1)

**Direct answer:** Yes — accessibility is information perceivable through any medium: wirekit's stdout is ordered `key = value` plain text (screen-reader friendly), failures go to stderr with non-zero exit codes (non-visual failure signal), and no meaning is encoded in color or ANSI alone (none is used).

**Concept:** WCAG applies to human-computer interaction broadly; terminal precedent is man pages — linear, textual, structured. The failure mode for CLIs is meaning carried only in layout or color (e.g. red/green without text).

**In this project:** fixed-order rows printed by `wirekit.py:161-164`; exit-code contract (D3.2); future `--json` (STORY-001) improves machine *and* AT consumption by replacing column alignment with structure.

**Edge cases:** space-aligned columns can read awkwardly ("HostMin = ..." vs table semantics); `--bits` output is long unbroken binary strings — screen readers will spell them out; mitigation is structure, not visuals.

**Interviewer's intent:** Do they think about a11y beyond browsers — a differentiator most candidates skip.

**Follow-ups:**
- Q: What would break it? → A: adding color-only status indicators or requiring mouse/interactive TUI.

---

## Behavioral & Decision Trail

**Q: Tell me about a time you had to choose between shipping fast and adding engineering rigor. How did you decide?** (STAR)

**Answer (STAR):**
- **Situation:** During the Skill 6.0 bootstrap of wirekit (2026-10-13), CI had to be scaffolded; the full-quality option (add ruff lint/format *and* pipeline) competed against shipping the pipeline alone.
- **Task:** Deliver CI that a senior platform engineer would defend, without stalling the baseline.
- **Action:** Presented a three-option comparison table (full-shape scaled / full-shape + ruff / test-only) against the core drivers, recommended deferring ruff so the *first* CI run proves a green baseline, and tracked the gap explicitly as DEBT-001 with a target sprint — rigor deferred *with a receipt*, not dropped. Kept the non-negotiables (security stage, aggregate gate, least privilege) intact in every option.
- **Result:** Developer picked the recommendation; pipeline scaffolded with current action majors and validated locally; the lint gate now has an owner and a date (DECISIONS.md ADR-001).
- **Learning:** "Ship fast vs. be rigorous" is often a false binary — split the decision so the cheap part ships now and the expensive part gets tracked accountability.

---

**Q: Tell me about a time you rejected a popular dependency. What was the tradeoff?** (STAR)

**Answer (STAR):**
- **Situation:** wirekit could have used `netaddr` (richer IP manipulation), `click` (nicer CLI ergonomics), or `rich` (pretty output) — all standard choices.
- **Task:** Decide the dependency posture for a tool whose install story is "copy one file."
- **Action:** Ran the dependency vetting checklist (necessity / maintenance / license / security / footprint / alternatives), then ratified the pre-existing stdlib stance as ADR-002: runtime stays zero-dependency; dev deps go in pinned `requirements-dev.txt`. Documented the trigger to revisit (IPv6/VLSM complexity beyond `ipaddress`).
- **Result:** End users execute a 4.8 KB file with no PyPI trust requirement; the supply-chain attack surface for consumers is zero; CI still audits the dev toolchain.
- **Risk accepted:** re-implementing conveniences costs time — accepted while the surface is small; the rejected alternatives become correct the moment a feature genuinely needs them.
- **Learning:** The strongest dependency decision isn't "which library" — it's proving you don't need one, with a written re-evaluation trigger.

---

**Q: Walk me through a hard bug you fixed. How did you find it?** (STAR)

**Answer (STAR):**
- **Situation:** While adding the quiz mode and first test suite to wirekit (2026-10-12), a test case on `255.255.255.0 /24` crashed with `AddressValueError: 4294967296 (>= 2**32) is not permitted as an IPv4 address` instead of printing "beyond IPv4 space."
- **Task:** Fix the crash without breaking the nine-field output contract.
- **Action:** Reproduced it (still reproducible — confirmed 2026-10-13), then traced *evaluation order*: `nxt = nw + total` constructed `IPv4Address(2**32)` **during evaluation**, so the guard `if nxt <= IPv4Address("255.255.255.255")` below it could never run — the check guarded the wrong thing. Rewrote the computation as unbounded `int` math with an explicit `0xFFFFFFFF` bound before any `IPv4Address` construction (`wirekit.py:51-55`), and pinned it with a regression test asserting the sentinel string (`tests/test_wirekit.py:90-92`).
- **Result:** `net 255.255.255.0 /24` now prints `Next network = beyond IPv4 space`; the regression test failed-then-passed with the fix; logged as ERR-001 with the prevention rule ("edge-of-space address math goes through `int`").
- **Learning:** The guard was visible in the code — but it guarded a value whose *construction* was the failure point. Reading for evaluation order, not control flow, found it.

---

## D15. Project Deep-Dive

**Q: Reproduce and diagnose wirekit's one historical production bug — live, as if I've never seen it.** (T3)

**Direct answer:** It's an overflow-at-the-boundary bug: computing the next network for a block at the top of IPv4 space raised `AddressValueError` during *expression evaluation*, crashing the CLI with a traceback instead of printing `beyond IPv4 space`.

**Concept:** The old code computed `nxt = nw + total` (an `IPv4Address + int` operation whose `__add__` **validates on construction**) and *then* compared against `255.255.255.255`. For `255.255.255.0 /24`, `total = 256`, so the sum is `2**32` — `IPv4Address(4294967296)` raises **before** the comparison line exists in execution order. The guard inspected a value that could never be produced.

**Why / tradeoffs:** Fix options: (a) wrap in `try/except AddressValueError` — treats the symptom, hides future overflow sites, and catches outside `main()`'s existing narrow try anyway; (b) check *before* constructing — but where does the bound live? (c) **chosen:** do the arithmetic in Python `int` (unbounded — cannot overflow) and only convert to `IPv4Address` behind an explicit `0xFFFFFFFF` bound. (c) makes the invariant visible and total.

**In this project:** reproduced with `IPv4Address('255.255.255.0') + 256` → `AddressValueError: 4294967296 (>= 2**32) is not permitted as an IPv4 address`; fix `wirekit.py:51-55`; full log [ERR-001](ERROR_LOG.md); commit `0f147f1`.

**Code — how it works here:**
```python
# before (crash — construction raises before the guard runs)
nxt = nw + total
if nxt <= ipaddress.IPv4Address("255.255.255.255"):
    next_net = str(nxt)
else:
    next_net = "beyond IPv4 space"

# after (wirekit.py:51-55 — int math can't overflow; guard precedes conversion)
nxt = int(nw) + total
if nxt <= 0xFFFFFFFF:
    next_net = str(ipaddress.IPv4Address(nxt))
else:
    next_net = "beyond IPv4 space"
```

**Edge cases / failure modes:** the same class hides anywhere address arithmetic touches the boundary (`broadcast + 1`, subnet iteration near `255.255.255.255`); `main()`'s `try` still only wraps parsing (`wirekit.py:155-159`) — a compute-time `ValueError` would still traceback (narrowing worth closing). Also note `AddressValueError ⊂ ValueError` — a careless broad `except ValueError` in the parse layer would misroute it as an input error.

**At scale:** this bug never self-heals with load — it's input-dependent, not rate-dependent; the mitigation is property-style edge tests (top-of-space, `/0`, `/32`) which the suite now has.

**Interviewer's intent:** Live-debugging ability: reproduce → isolate → explain *timing* of the failure → minimal correct fix → regression test. (Matches probeinterview's "verification: tests the actual failure mode, doesn't trust green.")

**Follow-ups:**
- Q: How do you know the test would fail without the fix? → A: it was written alongside — failed on the old code, passed after (classic red-green).
- Q: What other inputs hit this? → A: any block whose `network + size > 2**32` — only the final `/24`-and-above ranges at the top.
- Q: Should `analyze` raise or return the sentinel? → A: sentinel keeps it total (no exceptions to catch at the boundary) — chosen.

---

**Q: Why do `/31` and `/32` need special-casing? Take me through the RFC and the code.** (T3)

**Direct answer:** The standard formula (usable = total − 2) reserves network and broadcast addresses — but a /31 has exactly two addresses, so subtracting both would report **zero** usable hosts on every point-to-point link; RFC 3021 legalized /31 by making both addresses usable, and /32 is by definition a single host with itself as "broadcast."

**Concept:** Host-address reservation is a convention of classful-era subnetting, not a law of the math. RFC 3021 ("Using 31-Bit Prefixes on IPv4 Point-to-Point Links") documented what operators already did: assign both ends of a /31 to the interfaces. For /32, `network == broadcast == the address`.

**Why / tradeoffs:** Branching on `prefix >= 31` at the *field-computation* layer (one branch, in `analyze`) versus special-casing per caller — chosen at the source so every consumer (CLI, future `--json`, quiz) inherits correct values. The rejected alternative: computing `total - 2` everywhere and clamping — would report 0 and confuse users.

**In this project:** `wirekit.py:44-49`; pinned by two dedicated tests: `tests/test_wirekit.py:64-70` (`/31` → HostMin `.0`, HostMax `.1`, 2 usable) and `:72-79` (`/32` → all three fields equal the address, 1 usable); the quiz generator mirrors the same branch (`wirekit.py:87-92`).

**Code — how it works here:**
```python
if prefix >= 31:
    host_min, host_max = nw, bc  # /31: both addresses usable (RFC 3021)
    usable = total  # /32: the address itself
else:
    host_min, host_max = nw + 1, bc - 1
    usable = total - 2
```

**Edge cases / failure modes:** the quiz path duplicates this branch (`make_quiz_question`) — if one copy is fixed and not the other, the tool would teach wrong answers; a refactor extracting `usable_range(net)` would DRY them. `/30` is the boundary where the old rule still holds (2 usable of 4).

**At scale:** irrelevant to load; *relevant to correctness at network scale* — automation scripting against `Hosts/Net` on /31 fabrics breaks if this is wrong (router configs are generated from such output).

**Interviewer's intent:** Do they know their RFCs beyond the happy path — and can they point at the branch that implements the exception?

**Follow-ups:**
- Q: Why does the quiz exclude first/last-host questions for /31? → A: `if prefix < 31` (`wirekit.py:99`) — the concepts differ at the boundary.
- Q: How would you test the duplication risk? → A: shared fixture asserting `analyze` and quiz answers agree on the same network.

---

**Q: What does `strict=False` do in `build_network` — when would you want `strict=True`?** (T2)

**Direct answer:** `ipaddress.ip_network(value, strict=False)` **normalizes** a host address into its containing network — `172.30.197.206/20` becomes `172.30.192.0/20` — instead of raising; `strict=True` (the default) rejects any address with host bits set.

**Concept:** `172.30.197.206/20` has host bits set (`.206` isn't aligned to the /20 boundary `…192.0`). Strict mode is a *correctness lint*: it catches fat-fingered input like `192.168.1.1/24` when the caller meant a subnet. Non-strict is user-facing ergonomics: people paste the address they're sitting on (from `ipconfig`) and want its network.

**Why / tradeoffs:** `strict=False` trades input strictness for the tool's core promise (README: "host addresses passed inside a larger network" are handled). Rejected `strict=True` + manual strip: would re-implement normalization and *worse* — a typo'd mask would no longer produce the obvious answer, breaking the "answer key" use case.

**In this project:** `wirekit.py:34`; test `tests/test_wirekit.py:82-88` asserts `172.30.197.206 /20` → `Network 172.30.192.0`, `CIDR /20`, `Netmask 255.255.240.0`.

**Edge cases:** non-strict silently accepts genuinely wrong input (`10.0.0.5/8` → `10.0.0.0/8`) — the tool can't distinguish "host in a network" from "typo"; a `--strict` flag would let callers demand the lint (good `--json`-era backlog candidate).

**At scale:** as a library used by automation, default flip to `strict=True` would be the safe choice — APIs should reject; CLIs should normalize.

**Interviewer's intent:** Do they understand a stdlib default that's deliberately overridden, and the security/UX trade it encodes (normalize vs. validate)?

**Follow-ups:**
- Q: Why is normalization *more* correct for this product? → A: the product is a learning answer key — it must answer, not scold.
- Q: Where does strictness belong in the future API? → A: at the boundary as an explicit option — normalize by default for humans, strict for machines.

---

**Q: "Your whole app is one 172-line script." Some rubrics reject single-file take-homes outright. Defend it — or refactor it.** (T2)

**Direct answer:** Defend it *with a boundary*: one file is correct at this size because there is exactly one concern (calculate + print) and one consumer (the CLI) — but I'd name the explicit trigger for splitting (a second consumer, or crossing ~400 lines), and I'd already enforce internal layering so the split is a move, not a rewrite.

**Concept:** Structure by change-coupling, not by convention. Package layout pays off when independent things change independently — parser vs. math vs. presentation haven't diverged yet. The rubric rule ("single 600-line script = rejection") targets *mixed concerns that already diverge*; the counter-error is premature `src/` scaffolding with one module in it.

**Why / tradeoffs:** What's traded: import-time isolation (can't import just the math without `argparse`), and reviewer navigation. What's gained: `install.sh` stays a one-file `cp`, the whole product fits in one review, stdlib-only distribution (ADR-002) survives. The alternative (split now) was rejected until a real second consumer exists — the documented re-evaluation trigger.

**In this project:** layering *is* visible despite one file: pure compute `wirekit.py:18-67` (zero I/O), I/O modes `:70-131`, orchestration `:135-169` — a mechanical `git mv` split later. Evidence the boundary holds: 16 of 23 tests import the module and never touch I/O.

**Edge cases:** the actual smell to watch isn't length — it's `import random` (quiz) sitting next to pure math: mixed testability. Extracting quiz first would be the highest-value split, higher than the ceremonial `src/` layout.

**At scale:** team growth (2+ contributors) or an HTTP wrapper is the trigger — at that point `wirekit/{core,cli,quiz}.py` with a stable `analyze()` API.

**Interviewer's intent:** Can they argue structure from coupling and change-cost instead of repeating "one class per file"? (Senior judgment signal — probeinterview.)

**Follow-ups:**
- Q: What splits first when you do split? → A: `run_quiz`/`make_quiz_question` — the only stateful, interactive, non-deterministic code.
- Q: What does the single file cost you in CI? → A: nothing yet — no lint stage to slow (DEBT-001), and coverage mapping stays trivial.

---

## Coverage Checklist (interview-partner §11)

- [x] System design: "draw this system" (D1.1) + "scale it" (D1.2)
- [x] Every non-trivial function has ≥1 Q tied to real code: `normalize_mask` (D3.3), `build_network` (D15.3), `analyze` (D2.1, D15.2), `show_bits` (D2.1), `make_quiz_question`/`run_quiz` (D9.2), `main` (D3.2)
- [x] Data model / migration questions — **N/A**: stateless calculator, no persistence (documented in Index)
- [x] User-input + secrets surface → security questions (D7.1–D7.3); no auth to probe — explicitly noted as absent, not skipped
- [x] Test suite produced "why this test" questions (D9.1–D9.3)
- [x] CI/CD produced pipeline questions (D10.1–D10.3)
- [x] Performance question (D8.1)
- [x] A11y question for the user-facing surface (D11.1)
- [x] Dependency decisions → "why this library/not" (D7.2, D14.2, TECH-001..003)
- [x] Logged decisions → behavioral/STAR (D14.1–D14.3)
- [x] ≥3 project-specific deep-dives (D15.1–D15.4 — four)
- [x] Index updated; no duplicate questions across sections (overflow covered once in D15.1; language angle D3.1 cross-links rather than repeats)

---

## Sprint Reviews

*(None — no formal sprints yet. This bank was produced by the §7 post-hoc scan at bootstrap, 2026-10-13.)*

---

## Personal Study Queue

| Question | Domain | Status (strong / weak / repeat) | Last drilled |
|---|---|---|---|
| D15.1 — Reproduce/diagnose the overflow bug | Deep-Dive | untested | — |
| D10.1 — Walk through the CI pipeline | CI/CD | untested | — |
| D9.2 — What does the monkeypatched quiz test miss? | Testing | untested | — |
| D3.1 — Exception fires inside the expression | Language | untested | — |
| D14.1 — Fast vs. rigorous (STAR) | Behavioral | untested | — |
