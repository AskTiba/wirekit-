# Error Log — wirekit

> Every non-trivial error (anything that took real diagnosis, not a typo) is logged here
> at the time it's resolved — not reconstructed from memory later.
> Newest entries at top. Last updated: 2026-10-13

---

## Format

```
## ERR-[NNN] — [Date] — [Short title]

| Field | Content |
|---|---|
| **Context** | What task was in progress when this occurred |
| **Symptom** | What was observed — exact error message, stack trace, or behavior |
| **Root cause** | The actual underlying cause, not just the surface symptom |
| **Resolution** | What was changed — file/line references |
| **Prevention** | What would catch this earlier next time (test, lint rule, pre-flight check) |
| **Related** | Links to other ERR entries or DECISIONS.md entries if relevant |
```

---

## Errors

## ERR-001 — 2026-10-12 — Next-network calculation crashes at top of IPv4 space *(retroactively logged 2026-10-13 from git history `0f147f1`)*

| Field | Content |
|---|---|
| **Context** | Adding quiz mode + pytest suite; a test exercised `net 255.255.255.0 /24` |
| **Symptom** | `AddressValueError: 4294967296 (>= 2**32) is not permitted as an IPv4 address` — raw traceback instead of the intended `Next network = beyond IPv4 space` row (reproduced 2026-10-13) |
| **Root cause** | `nxt = nw + total` computed the next network via `IPv4Address + int`. At the top of the address space the sum reaches 2³², and constructing `IPv4Address(4294967296)` raises `AddressValueError` *before* the guard `nxt <= IPv4Address("255.255.255.255")` could ever run. The check guarded the comparison, not the construction. `analyze()` is also called outside `main()`'s `try/except ValueError` (wirekit.py:155-159), so the exception escaped as a traceback. |
| **Resolution** | Switched to integer arithmetic with an explicit bound: `nxt = int(nw) + total; if nxt <= 0xFFFFFFFF: next_net = str(IPv4Address(nxt)) else: "beyond IPv4 space"` — wirekit.py:51-55 (commit `0f147f1`) |
| **Prevention** | Regression test `tests/test_wirekit.py::test_next_network_beyond_ipv4` asserts the sentinel string; it failed-then-passed with the fix. General rule for this codebase: all address math on the edge of 32-bit space goes through `int`, never through `IPv4Address` arithmetic that can overflow mid-expression. |
| **Related** | Interview material: INTERVIEW_QA.md → §D15 Project Deep-Dive; [ROADMAP.md](ROADMAP.md) test strategy |

---

*(No other non-trivial errors logged yet — add newest at the top)*
