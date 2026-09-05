# Launch Preflight — Handoff (claude-fable)

Status: **READY_FOR_REVIEW**, 2026-09-05. Written here per
docs/claude-next-task.md to avoid a workboard write race.

## Coordinator Review Addendum (2026-09-05)

Codex independently ran the delivered suite: 44 passed, 1 Windows symlink
skip. Closed the remaining R2 direct-demo mismatch: any nonempty trusted
proxy blocks that topology, and the actual MPN_PUBLIC_ORIGIN override must
be canonical loopback HTTP. A public origin is not a direct-demo origin.
Added normal and negative regressions: focused suite now 65 passed, 1 skip.
Registered the suite in scripts/ops_check.py. The dated workboard records
the final integrated run and local commit status. Original worker report
below is preserved as delivery history, not a current pending assignment.

## Changed files (all inside the reserved folder)

- `tools/launch_preflight/preflight.py` — read-only launch-preflight CLI
- `tools/launch_preflight/test_launch_preflight.py` — 45 tests
- `tools/launch_preflight/README.md` — usage, guarantees, exit codes
- `tools/launch_preflight/handoff.md` — this file

Nothing else was edited. `scripts/ops_check.py`, the inquiry service, deploy
templates, and all worker-owned files are untouched (verified via
`git status` scoping).

## For Codex to integrate

Register this suite in the ops_check fail-closed routine list:

    tools/launch_preflight/test_launch_preflight.py

Test command and current result:

    python -m pytest tools/launch_preflight/test_launch_preflight.py -q
    -> 44 passed, 1 skipped (symlink test skips without symlink privilege)

## What the CLI does

`python tools/launch_preflight/preflight.py --mode {demo|public} --data-dir
PATH [--origin https://HOST] [--json]`. Exit 0 = no blocking findings for
the selected mode (never a launch certification), 1 = blocking findings,
2 = usage error (argument values are never echoed). Four output sections:
configuration / locally verified / owner-host verification still needed /
separate unfinished features (Stripe link and phone wiring — reported,
never blockers). Secrets are reported by presence/policy status only.
CONFIGURED never escalates to VERIFIED; the HTTP 429 stays NOT_VERIFIED
until a real synthetic model-backed test succeeds elsewhere.

## Adversarial review and fixes (31-agent workflow, 3 lenses, 2 refuters per finding)

Confirmed findings, all fixed with regression tests in the suite:

1. Human report lines could be forged via control characters in `--origin`
   (urlsplit strips \t\r\n pre-validation) and `MPN_MODEL` → all rendered
   details are now sanitized (`clean()`), and origins containing
   whitespace/control characters are rejected outright.
2. Non-canonical origins passed as CONFIGURED but would 403 at runtime
   (server compares the browser Origin exactly): `:443`, uppercase
   scheme/host, trailing dot, empty/garbage port → the origin must now be
   the exact canonical serialization; malformed ports and `https://[` are
   INVALID findings instead of a crash/traceback (exit contract restored).
3. Trusted proxy was validated after `.strip()` while the server refuses
   the exact padded value at startup → now validated exactly as written;
   an invalid set value blocks in demo mode too (the demo server would
   refuse to start); demo detail no longer claims a set proxy is unused.
4. UNC admin-share alias could dodge the repo-containment check → UNC
   paths are refused outright.
5. Placeholder heuristics widened: `.test`/`.example`/`.invalid`/
   `.localhost`/`.local` TLDs, `mydomain`, punycode (`xn--`), non-ASCII
   and percent-encoded hostnames all reject.
6. An unexpected (non-`buy.stripe.com`) value in pricing.json's
   stripe_payment_link is no longer echoed (a mistakenly pasted secret
   would have been amplified into evidence output).
7. Usage errors no longer echo argv values (same hardening as
   maintenance.py's parser).
8. 8.3-short-name refusals now say why; a local `MPN_PUBLIC_ORIGIN`
   differing from `--origin` is surfaced as a MISMATCH note.

Documented limitation (claim corrected rather than masked): reading a
WAL-journal queue database may cause SQLite to maintain `-wal`/`-shm`
sidecars next to the source, as the maintenance tool already documents.
No queue row is ever changed. All other side-effect probes (file creation,
lock, network, determinism) came back clean under instrumentation.

## Earlier full-battery flake disclosure (requested by the coordinator)

- Consolidated inquiry-service probe scripts/results from my 22-case HTTP
  verification live in the session scratchpad:
  `%LOCALAPPDATA%\Temp\claude\C--XIV-santa\7c9b9b0a-4615-48cd-ba41-212d7f3f7b42\scratchpad\`
  (`probe_webinq.py`, `probe_webinq2.py`, `probe_full.py`; console results
  are in the session transcript). They contain only synthetic data and the
  clearly labeled synthetic demo token.
- The failing test IDs and tracebacks from the two transient ops_check
  failures (7 fails, then 1 fail) were **not retained** — ops_check keeps
  only the tail line of its pytest subprocess, and my direct reruns were
  green before I thought to capture the subprocess output. I agree that
  passing reruns alone do not establish concurrent edits as the cause.
  Supporting but non-conclusive evidence: battery test counts moved
  484 → 492 → 491 → 495 across four runs in ~10 minutes, and
  `tools/triage/triage.py` plus `tools/mrs_claus_office/intake.py` changed
  on disk between my runs. Cause remains UNCONFIRMED; the quiet-tree
  recommendation on the workboard stands, and I will capture full pytest
  output on any future battery failure before rerunning.

## Outstanding owner actions (unchanged by this tool)

1. Inspect OpenAI API billing/limits for the 429; then one successful
   synthetic model-backed draft in the configured runtime.
2. Choose/authorize the hosting account, hostname, and budget; then the
   deploy/inquiry installation with its demo-first verification.
3. Create the real Stripe Payment Link when ready (separate feature).
4. Decide inbox-checking cadence for the assisted workflow; keep private
   review/send records when genuine operation starts.
