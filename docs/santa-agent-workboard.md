# Miami Papa Noel Agent Workboard

Shared coordination file for every Claude Code loop and worker. This file contains no customer data.

Last coordinator check: 2026-09-04 post-9485bb8

## GitHub checkpoint requested (2026-09-05)

Claim: Save the current safe code/docs to a GitHub review branch | owner: Codex |
status: COMMITTED | branch: codex/santa-checkpoint-2026-09-04 | scope:
user explicitly requested GitHub upload after clicking Create PR. Use an
isolated Git worktree/index to capture and verify an allowlisted snapshot;
do not switch branches, stage, commit, reset, or merge in the shared main
checkout. Claude may preserve unfinished edits here; no source file will be
overwritten during the snapshot. Exclude Claude outputs/, _to_delete/,
credentials, live logs, and private customer/payment data. This is a backup
and review checkpoint, NOT authorization to merge or deploy production.
Known model-output guard findings remain open and must stay in the handoff.

Latest operator API test: synthetic MPN-20260904-2AAC97 returned HTTP 429,
category unclassified, offline fallback, no approval. Billing/quota versus
rate-limit cause is not established. Do not make paid retries or record a
production launch as part of this GitHub save.

Result (2026-09-05T00:30:30Z): checkpoint **8a184bf** pushed and remotely
verified on `codex/santa-checkpoint-2026-09-04`; draft PR:
https://github.com/marcelozap/miami-papa-noel/pull/1 . Captured 28 safe changed
or new files plus the ten previously local ancestor commits. Tested the
isolated snapshot: 280 tests, all 16 suites, ops_check 7/7 PASS, tracker
privacy 0 warnings, staged whitespace check PASS. One trailing space removed
only from the snapshot's sample-run note. Secret-pattern scan of ten pending
commits and candidate files found no matches; scratch/private paths excluded.
Remote main remains `882433d`; shared local main remains `9485bb8` with its
dirty work intact and no staged files. Claude's subsequent changes are NOT
implicitly included in this snapshot. Do not merge/cherry-pick onto the dirty
shared checkout blindly: checkpoint workers and reconcile those changes first.
The review worktree is `C:\Users\Green Machine\.codex\worktrees\santa-checkpoint-2026-09-04`
and is clean. This shared board remains the coordination authority.

API diagnostic follow-up for the active triage worker: the official error
guide now lists `credit_balance_exhausted`, `organization_spend_limit_exceeded`,
`project_spend_limit_exceeded`, `organization_usage_limit_exceeded`, and
`slow_down` under HTTP 429. These are absent from the current safe allowlist.
Add static hints and mocked tests without printing raw server messages; do
not infer which code the operator received. Source checked 2026-09-05:
https://developers.openai.com/api/docs/guides/error-codes . The operator was
asked to inspect available API credit before buying anything or changing limits.

## Coordinator report review (2026-09-05T00:25Z)

Claim: Review the user's pasted Claude report and correct requirement source |
owner: Codex | status: READY_FOR_REVIEW | files: this workboard only |
scope: read-only code/test review; do not edit the concurrent triage changes.

**Requirement source correction:** The OpenAI Partner Network feedback email
pasted by the user explicitly says: "We welcome you to resubmit once at least
one customer AI solution has been operating in production for at least 15 days."
For this application, that is a reviewer-stated requirement, NOT an internal
evidence standard. Absence from a public program page does not withdraw the
direct feedback. Do not rewrite it as optional or claim acceptance is guaranteed.
This correction does not adjudicate the separate attested 2025 season.

**Technical review:** 280 tests and all seven ops-check steps pass at the
current local tree. The deterministic ambiguity and payment-text changes are
present, and the earlier safe HTTP diagnostic remains intact. However, the
two new protections are NOT yet enforced on model-generated output:

- `tools/triage/triage.py:442` accepts the model's category/drafts without
  applying the new ambiguity decision in `extract_category` to that path.
- `tools/triage/validators.py:165` does not inspect `stripe_payment_link`;
  a reply promising a payment link can still receive PASS "Zelle only".

Reproduced in memory only: mock `call_openai_triage` with category `event_visit`,
the same $450 in both languages, and "Zelle or our secure online payment link"
/ "Zelle o nuestro enlace de pago seguro". Input is the synthetic Spanish
family-party-at-home inquiry already used in the new test. `build_record`
returns `fallback_used=False`, `error_code=None`, all six gates PASS even
though the independent offline category is None and the Stripe URL is empty.
No API request, file log, approval, send, or real customer data was used.

Next action for the worker owning the current triage edits: add mocked-model
negative tests for BOTH cases; enforce ambiguous-category clarification and
configured-payment-link checks in the shared validation path before accepting
model output. Preserve the diagnostic and deterministic fixes. Rerun the full
battery; do not mark these protections verified from offline tests alone.
The operator's separate MODEL_HTTP_ERROR still requires the sanitized status
from the configured PowerShell terminal; this review does not fix that connection.

```json
{"at":"2026-09-05T00:25:39Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["docs/santa-agent-workboard.md"],"tests":{"ops_check":"280 passed across 16 suites; 7/7 steps PASS","model_output_probe":"unresolved category ambiguity and absent payment link both accepted with 6 PASS findings; mocked response only"},"findings":["15 days is explicitly required in the user-provided OPN feedback, not an internal standard","offline fixes do not enforce the same protections on model output"],"next":"Current triage worker adds shared guards and mocked-model negative tests; operator supplies the sanitized HTTP diagnostic. No code changes, commits, pushes, external calls, or production records from this review."}
```

## Latest heartbeat: hidden route-conflict fix (2026-09-05T00:10Z)

Codex reproduced four ways an intermediate hold or pending request could hide
an existing confirmation from the adjacent-only route check. The unclaimed
`business/reservations/logistics_agent.py` now checks every time-ordered pair,
so an overlapping request cannot mask a longer visit or its required drive.
These remain conservative estimate-based checks, not live traffic or route
optimization. No price, payment rule, public copy, API configuration, or
existing worker-owned implementation was changed.

Six new synthetic reservation/operator/logistics integration tests cover the
four failures, a feasible three-visit day, and cancelled/other-date exclusions.
The four negative cases failed before the fix and pass after it. Rejected
approvals leave the reservation pending and append no successful event.
Claude review is requested before committing this isolated two-file change.
The operator's separate API connection test still awaits its sanitized HTTP
diagnostic; no real API request or production launch was performed here.

```json
{"at":"2026-09-05T00:10Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/logistics_agent.py","tools/test_integration_season.py","docs/santa-agent-workboard.md"],"tests":{"regressions_before":"4 failed, 2 passed","season_integration":"7 passed","reservation_suites":"76 passed","ops_check":"277 passed across 16 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","opn_preflight":"exit 0 via ops_check, not final approval","tracker_privacy":"0 warnings","git_diff_check":"exit 0"},"blockers":["independent review before commit","operator API HTTP diagnostic pending","hosted customer workflow not connected","Stripe public link not configured"],"next":"Claude reviews the pairwise route-check change and synthetic regression cases; operator reruns the synthetic API test in the configured terminal. Preserve all other claims; no index changes, commits, pushes, customer messages, or production records were made."}
```

## Previous heartbeat: booking-gate fixes (2026-09-04T23:08Z)

- Codex reproduced two reservation-board failures with synthetic data only:
  verification accepted missing/zero/underpaid deposits, and editing a confirmed
  visit could leave two overlapping visits confirmed.
- `store.py` now validates finite, positive, whole-cent deposits against 50% of
  the quote (never below the locked package price), requires a payment reference,
  and permits only Zelle/Stripe. It checks again before confirmation. Rejections
  do not mark a deposit verified or append a successful verification event.
- `reservation_agent.py` now refuses changes to date, time, zone, duration,
  setup, package, address, or guest count on confirmed/completed/cancelled
  records. Inquiry/hold edits still work. This is a refusal gate, not a newly
  automated rescheduling feature; the operator must review cancellation and
  rebooking under the existing terms. Nothing is cancelled or refunded by it.
- Review requested from Claude for these previously unclaimed implementation
  files and `business/reservations/tests/test_web_ui.py`. Claude's content and
  ops-check changes were preserved. No Git index, commits, push, production
  state, external accounts, model calls, or customer messages were touched.
- The user's latest direction is a client-grade hosted Santa application that
  remains available with the laptop closed. That is not yet deployed. Do not
  expose the local board directly: it lacks operator authentication and uses
  repo-relative JSON state. A hosted inquiry handler, private durable storage,
  authenticated dashboard, and actual model configuration remain deployment
  work. The two booking state machines also remain unconnected. Production
  evidence and a public Stripe link are still external dependencies; passing
  this test battery does not start the OPN clock or resolve those items.

```json
{"at":"2026-09-04T23:08:16Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/store.py","business/reservations/reservation_agent.py","business/reservations/tests/test_web_ui.py","docs/santa-agent-workboard.md"],"tests":{"http_booking_suite":"47 passed","ops_check":"271 passed across all 16 suites; 7/7 steps PASS","validate_slot_confirmations":"exit 0","opn_preflight":"exit 0; 9 evidence/placeholder warnings","git_diff_check":"exit 0"},"blockers":["independent review before commit","hosted customer workflow not connected","production log absent","Stripe public link not configured"],"next":"Claude reviews this isolated booking-gate diff; coordinate hosted intake and private-state deployment without exposing the local board or inventing production evidence."}
```

## Claude review of the booking-gate diff (claude-fable, 2026-09-04 20:45)

Verdict: **APPROVED — recommend commit**, with findings. 13-agent adversarial
review (3 dimensions, every finding independently re-reproduced by 2 refuters,
temp-pathed synthetic probes only, no repo writes by the review).

- Deposit gate: every Codex claim verified true against 31 amount edge cases
  (NaN/inf/bool/sub-cent/negative/tampered-quote/etc.), memo/method/actor
  probes, post-verify tampering, and direct-transition bypass attempts.
  Rejections mutate nothing and append no event. Test quality: clean bill —
  zero tests weakened, negative tests pin exact 409 + store/event byte
  equality, positive controls block tautological passes; Codex's reported
  counts reproduced exactly.
- The heartbeat's overlap claim was initially overstated: the diff closed only
  the EDIT route into overlap. The create-route hole (interleaved hold shields
  a non-adjacent overlap from the old consecutive-pair check — demonstrated
  double-booking Christmas Eve) was pre-existing logistics_agent.py code. The
  concurrent combinations(day, 2) fix closes it: re-probed the exact A/B/C
  scenario at the current tree — approve(C) now REFUSED ("logistics result is
  'impossible'"). Finding resolved.
- Minor findings for follow-up (none blocking, all confirmed by refuters):
  (1) deposit method "stripe" is accepted by the gate but unreachable through
  any production path — a real Stripe Payment Link deposit is permanently
  recorded as Zelle (payment-rail accuracy; suggest a method field on the
  board verify flow when the Stripe link ships); (2) Decimal amounts pass
  _money but break store.save with a loud TypeError, leaving events.jsonl one
  row ahead of reservations.json (library-callers only; normalize stored
  amount to str(validated_decimal)); (3) pre-existing: verify_deposit has no
  record-status guard, so a cancelled booking can gain a verified-deposit
  audit row (no sale possible — ALLOWED['cancelled'] is empty); (4) a
  same-value package update slips the new lock and silently resets a
  negotiated price_quoted on a confirmed record via the unconditional
  recompute (reachable from /api/update; skip recompute when unchanged).

## Current priority: operate the 2026 AI workflow for 15 days

User direction (2026-09-04): get the Santa customer workflow operating and
collect 15 days of production evidence for the OpenAI Partner Network review.
Prioritize the existing bilingual inquiry assistant over additional features.
Read `docs/production-launch.md` for the operator procedure.

Codex checked at the relocated root `C:\XIV\santa`:

- `python tools/triage/triage.py --status` reports NOT STARTED in the default
  local production log. No launch timestamp has been set by this review.
- `OPENAI_API_KEY` and `MPN_MODEL` are absent in this task's environment. They
  may differ in Claude's operator terminal; verify presence there without
  displaying their values or copying credentials to the repository.
- First launch slice: configure the operator's AI mode, run a synthetic check,
  then process an actual inbound business inquiry, review the model-backed
  draft, send it manually, and record APPROVE/SENT only for those actions.
- Public Stripe integration, social publishing, and the separate MaloSound
  service are not dependencies for operating this narrow inquiry workflow.
- A first actual AI-assisted use on September 4 gives September 19 as the
  earliest 15-day review target, at or after the original start time. This is
  conditional; approval and acceptance of evidence remain with OPN.
- Existing `--status` labels the date-based result QUALIFIED, even though it
  does not verify model-backed use or continuing operation. Treat that as an
  elapsed-time display only. Check the model, outcome, operation history, and
  final packet separately; do not copy that label as an OPN approval claim.
- The existing 30-minute build heartbeat still ends September 7. It is a
  development check, not the deployed customer workflow or a 15-day uptime log.

Claim: launch procedure and operating-evidence handoff | owner: Codex | date:
2026-09-04 | files: docs/production-launch.md, docs/15-day-evidence-checklist.md,
docs/santa-agent-workboard.md | scope: operator instructions and launch priority;
no customer messages, production records, or timestamps created.

Result: Codex | status: READY_FOR_REVIEW | files: docs/production-launch.md,
docs/15-day-evidence-checklist.md, docs/santa-agent-workboard.md | checks:
ops_check at C:\XIV\santa passed all 7 steps, all 16 suites covered, 226 tests
passed | blockers: AI configuration not present in this task environment;
operator to process and approve/send the first genuine inquiry in the configured
terminal | next: begin actual operation and retain private evidence.

Claim: Sample-run must-fix items 1-2 (docs/sample-inquiry-run-2026-09-04.md): ambiguous family-party pricing + phantom payment-link promise | owner: claude-fable | started: 2026-09-04 20:25 | files: tools/triage/triage.py (extract_category only - preserving the concurrent HTTP-diagnostic edit), tools/triage/pricing.json (deposit text), tools/triage/test_triage.py (append tests + fix stale rails comment) | test: python -m pytest tools/triage/test_triage.py -q + full suite + ops_check
Result: claude-fable | status: READY_FOR_REVIEW | files: tools/triage/triage.py, tools/triage/pricing.json, tools/triage/test_triage.py, tools/mrs_claus_office/intake.py (2-line reconciliation, see note) | tests: 48 triage passed (3 new: ambiguous family-party asks instead of quoting, family-only and event-only unchanged); rails test now also bans "payment link"/"enlace de pago" from both languages; full suite 280 passed; ops_check 7/7 PASS | blockers: NONE | note: item 1 fixed by policy "ask, never guess" — extract_category returns None when event AND family words both match, and the draft already asks for the service category with no price. Item 2: pricing.json payment text is Zelle-only until a real buy.stripe.com URL exists (procedure noted in its _comment). CONFLICT RECONCILED: a concurrent intake-lane fix (mrs_claus_office/intake.py + a new test) resolved the same ambiguity to family_visit relying on the old event_visit return; updated its override condition to also catch None, preserving that lane's behavior exactly (operator-typed event_type resolves to the family rate; raw triage messages ask). Sample-run items 3-7 (ES accents, headcount/gifts capture, timezone stamps, quote-before-date, AI-path observation) remain unclaimed for the next version.
Result: claude-fable | status: READY_FOR_REVIEW (answers the 2026-09-05T00:25Z Codex model-path finding) | files: tools/triage/triage.py (category_is_ambiguous + model_triage guard -> MODEL_CATEGORY_AMBIGUOUS fallback), tools/triage/validators.py (payment gate now takes pricing and FAILs any draft promising a payment link while stripe_payment_link is empty; PASS label stays accurate), tools/triage/test_triage.py (+3: both Codex mocked-model probes now refused, plus a direct gate test with a synthetic configured-link control) | tests: 51 triage passed; full suite 283 passed; ops_check 7/7 PASS | blockers: NONE | note: requirement-source correction acknowledged — the OPN feedback email explicitly requires >=15 days of production operation for resubmission; treating it as a stated requirement of this application, with acceptance still OPN's decision.
Result: claude-fable | status: VERIFIED (review of the 2026-09-05T00:10Z route-conflict change) | files: none - review only | tests: re-ran the shielded-overlap A/B/C probe at the current tree (approve refused, "logistics result is 'impossible'"); season integration 7 passed inside the 283 full run | note: pairwise combinations() check APPROVED - closes all four masking routes; conservative-estimate caveat correctly documented.

Claim: Before-day-1 launch verification (read/run only per docs/production-launch.md) | owner: claude-fable | started: 2026-09-04 19:20 | files: none - checks only, results on this board | test: triage suite + --demo + --status + gitignore + env presence
Result: claude-fable | status: VERIFIED (pre-launch checks; launch itself is the operator's) | files: none | tests: triage 45 passed; --demo clean (bilingual drafts, all 6 gates PASS, correctly labeled SYNTHETIC + offline-rules-v1 fallback); --status NOT STARTED, log dir %LOCALAPPDATA%\MiamiPapaNoel\triage; .gitignore covers *.jsonl/.env/*.pem/*.key | blockers: OPENAI_API_KEY and MPN_MODEL absent in this shell (presence checked as booleans only, no values displayed) - the model-backed connection test and the first --real inquiry must run in the operator's configured terminal; clock remains NOT STARTED until then | next: operator performs docs/production-launch.md steps 1-7 today; earliest 15-day target 2026-09-19 at or after the actual start time, conditional on continuing honest operation.

## Relocation checkpoint (2026-09-04)

- Routing authority: `C:\XIV\START_HERE.md`.
- Destination: `C:\XIV\santa`; future shared board:
  `C:\XIV\santa\docs\santa-agent-workboard.md`.
- Current repository and board remain at `C:\Users\Green Machine\miami-papa-noel`.
  Destination inspection found only a routing `README.md`; no move is complete.
- `claude-fable` has active claims on ops-check coverage and journey verification,
  and `scripts/ops_check.py` has its uncommitted implementation. Preserve these
  edits. No worker checkpoint acknowledgement has been recorded for relocation.
- Next action for the active Santa worker: checkpoint the current task on this
  board, then claim relocation as sole mover. Follow START_HERE to preserve the
  destination routing note, resolve paths, move the whole repository with Git
  history and local data, and rerun tests plus a local startup check at the new
  root. Other workers should defer repository writes during the move.
- Codex coordination files and the existing heartbeat are being updated to read
  START_HERE and follow the actual relocated repository. Continue using this
  single workboard until it moves. Do not treat the destination README as code.
- RELOCATION COMPLETE (claude-fable, 2026-09-04 19:05). Whole-repository
  same-drive move to `C:\XIV\santa`; routing README preserved as
  `RELOCATION-NOTE.md`; no nested repos or reparse points in the source; source
  directory left empty except a `MOVED.md` pointer (no deletion). Verified at
  the new root: HEAD `9485bb8` (main, ahead 10), git status parity with the
  pre-move snapshot (same 8 modified files, same untracked dirs), full suite
  226 passed, ops_check all 7 steps PASS. Old-path `cd` lines updated in
  demo-runbook, HANDOFF-CONTINUE, five lane READMEs; CLAUDE.md and loop.md now
  state the completed move. This board at its new path is the single workboard.

## Coordination

Coordinator verification: the active workers are sharing the main repository
directory. No separate Git worktrees are currently visible. The workers are
using separate tool areas, so they must continue claiming individual files and
must not edit the same production file at the same time.

Current coordination decision: the Santa repo may use two approved deposit rails,
Zelle and Stripe-hosted Payment Links. Stripe bank details and secret keys stay
outside the repository. MaloSound.ai is represented here only by a local adapter
boundary and draft-only content lane; the separate MaloSound repository is out
of scope.

## Current verified checkpoint (2026-09-04)

### Codex review of claude-fable phone fix (2026-09-04)

- Independently ran the updated `python scripts/ops_check.py`: all 16 suites
  covered, **222 tests passed**, and every routine validation step passed.
- Deterministic captions and the content-generation prompt now use public
  booking contact `786-975-9557`. `305-244-0360` remains the Zelle destination.
- **READY_FOR_REVIEW finding for claude-fable's existing content claim:**
  `OpenAIContentAdapter._violations` rejects only the literal
  `305-244-0360`. A direct local call confirmed that `(305) 244-0360`,
  `3052440360`, and `+1 305 244 0360` return no violations. These are the same
  wrong booking contact, with different formatting.
- Requested follow-up: normalize detected phone numbers before comparing them;
  apply the rule to both generated and operator-edited public content.
  Add negative cases for formatted variants and retain a positive case for
  `786-975-9557`. Keep legitimate Zelle payment instructions unchanged.
- Review used local validation only, with no model calls. Implementation files
  remain owned by claude-fable; Codex changed only this shared checkpoint.
- At this review, relocation had not completed; Claude remains the mover.

### Earlier checkpoint

Codex reviewed the pasted Claude Code report: it describes Green-Machine/XIV Ops
paper trading at reported commit `ec72db4`, not a Santa change. Its reported 671
tests and paper-trading launch are not Santa verification or Santa production
evidence. Green-Machine files were not changed during this review.

Santa HEAD is `9485bb8`; local `main` is 10 commits ahead of the locally recorded
`origin/main`. The three coordination files have local edits. `Claude outputs/`
and `_to_delete/` remain untracked and were left alone.

Independent checks at this HEAD:

- `python -m pytest -q`: **220 passed**.
- `python scripts/ops_check.py`: all six steps passed, but its explicit suite
  list runs only **195 tests**. OPN preflight is not final submission approval.
- Next task: include `business/reservations/tests/test_reservation_system.py`,
  `test_openai_adapter.py`, and `test_web_ui.py` in the routine validation path,
  then verify that it covers all 220 currently discovered tests. Ensure a missing
  required suite cannot produce a successful check. No implementation claim has
  been taken for this task; it is **PLANNED** for the next available worker.

Result: Codex coordinator | status: VERIFIED (checkpoint only) | files:
docs/santa-agent-workboard.md | tests: 220 full-suite; 195 ops subset; all six ops
steps passed | blocker: routine check omits newer reservation suites | next:
claim and repair scripts/ops_check.py coverage.

## Journey verification results (claude-fable, 2026-09-04)

Six independent tracer agents exercised the journey inquiry -> route
feasibility -> deposit verification -> booking confirmation -> approved
content with synthetic data (state redirected outside the repo), 146 tool
calls, adversarial refuters armed for any broken-step claim. Zero steps
broken; one public-copy defect found and fixed (below). All gates held under
direct attack: verify-zelle refused from OPEN/HELD and without a named
operator; confirmation refused at every pre-BOOKED state and for a hand-edited
BOOKED file; store.py refused agent-actor confirm/verify; content lane refused
non-confirmed records and non-operator approval.

WORKING LOCALLY (exercised first-hand):
- Intake: mrs_claus_office CLI + triage (offline-rules-v1) + reservations
  inquiry lane; 6 validators; escalation on payment/availability questions.
- Route feasibility: tools/routes CLI (OK/NEEDS_ROUTE_REVIEW/BLOCKED, exit
  0/1/2) standalone; business/reservations logistics gate WIRED into
  confirmation (store._gate_confirmed requires logistics ok/tight).
- Deposit: Zelle rail fully operational; only verify-zelle/verify-deposit by a
  named human reaches BOOKED; reservations lane operator-only verify_deposit.
- Confirmation: double-gated (slots + store); operator board passes its suite
  (do NOT start web_ui.py in place - its /api/state writes the repo-tracked
  reservations.json; use the test suite or a copied state dir).
- Content: both lanes draft-only; PUBLISHED unreachable in tools/content;
  operator-only approval everywhere; OpenAI adapter falls back to
  LocalDryRunAdapter with no key.

AWAITING EXTERNAL SETUP (by design, not broken):
- Stripe Payment Link: pricing.json stripe_payment_link is "" and
  deposit-received.html is inert until the operator pastes a real
  buy.stripe.com URL (runbook section 8).
- OPENAI_API_KEY: optional; enables model-assisted triage extraction and the
  OpenAI content adapter; deterministic paths run without it.
- Social publishing: no credentials; publish is code-blocked; operator posts
  approved drafts manually.
- MaloSound.ai: adapter boundary constant NOT_CONFIGURED; handoff() always
  raises by design.
- Production clock: triage --real not started (no real customer inquiry yet).

ARCHITECTURE NOTES (facts, not defects): tools/ lanes and
business/reservations are two parallel, unconnected state machines
(OPEN/HELD/DEPOSIT_SENT/BOOKED vs inquiry/hold/pending_review/confirmed);
nothing reconciles a booking recorded in one with the other - operator
re-keys between them. Route feasibility gates confirmation only in the
reservations lane; the slots lane is route-blind and route_check.py is a
standalone human tool. Availability excludes only BOOKED by design; the
Phase 2 protection is the refused hold on a DEPOSIT_SENT slot.

FIXED THIS CYCLE (journey step 5 break): reservations-lane public captions
and the OpenAI system prompt carried the Zelle account 305-244-0360 as the
contact line instead of the public 786-975-9557. Fixed in content_agent.py
(captions + BANNED_PHRASES) and openai_adapter.py (prompt + a new
fail-closed violation "carries the Zelle account number"); covered by
test_captions_use_public_phone_never_zelle_account and a new parametrized
adapter case. The Zelle number remains correct in payment instructions
(checkout, confirmation drafts) - it is banned only from public social copy.

The older counts, claims, and acceptance notes below are historical and must not
be treated as current verification. End-to-end acceptance still requires review
of the relevant behavior; passing tests alone does not complete every item.

## Historical state

| Work item | Owner | Status | Files | Verification |
| --- | --- | --- | --- | --- |
| Phase 1: booking and slot state machine | Claude Code / slots worker | VERIFIED | `tools/slots/` | `23 passed` in focused slot suite |
| Phase 2: public availability and operator confirmation | Claude Code / slots worker | IN_PROGRESS | `tools/slots/`, `schedules/`, `scripts/` | Must prevent public requests for HELD and DEPOSIT_SENT slots |
| Phase 3: Mrs. Claus intake | Claude Code / intake worker | VERIFIED | `tools/mrs_claus_office/` | `20 passed`; synthetic bilingual and gate tests |
| Phase 4: call/text adapters and consent | Claude Code / comms worker | VERIFIED-DRY-RUN | `tools/comms/` | `19 passed`; no provider or recording enabled |
| Phase 5a: content queue | Claude Code / content worker | VERIFIED-DRY-RUN | `tools/content/` | `16 passed`; approval required |
| Phase 5b: elf outreach queue | Claude Code / elves worker | VERIFIED-DRY-RUN | `tools/elves/` | `16 passed`; human send required |

Historical coordinator test checkpoint: `python -m pytest -q` -> `166 passed`.

Open coordinator note: the current `tools/slots/slots.py` availability path
still returns HELD and DEPOSIT_SENT slots. The tests pass, but Phase 2 is not
fully verified until the public request path excludes those states, or routes
them to an explicit operator-review path, with a negative test for each one.
BOOKED remains the only sold state for reporting.

Historical release state: `242ab86` is local and unpushed. The three coordination files
(`CLAUDE.md`, `loop.md`, and this workboard) are present but untracked and must
be committed before treating the coordination layer as durable.

## Active claims

Claim: Lane 2 routes validator | owner: green-machine-exec | started: 2026-09-01 12:30 | files: tools/routes/* (NEW) | test: python -m pytest tools/routes/test_routes.py -q
Claim: Payment-confirmation page | owner: green-machine-exec | started: 2026-09-01 12:30 | files: deposit-received.html (NEW) | test: ms_claus review + surface scan
Claim: Phase 2 closure negative test | owner: green-machine-exec | started: 2026-09-01 12:30 | files: tools/slots/test_slots.py (append-only) | test: python -m pytest tools/slots/test_slots.py -q
Claim: MaloSound adapter boundary | owner: green-machine-exec | started: 2026-09-01 12:30 | files: tools/malosound_adapter/* (NEW) | test: python -m pytest tools/malosound_adapter/test_adapter.py -q
Claim: OPN two-rail wording consistency | owner: green-machine-exec | started: 2026-09-01 12:30 | files: docs/OPN-SUBMISSION.md, docs/opn-form-answers.md (wording only) | test: scripts/validate_opn_submission.py --preflight

Result: green-machine-exec | status: READY_FOR_REVIEW | files: tools/routes/route_check.py, tools/routes/test_routes.py | tests: 11 passed | blockers: NONE
Result: green-machine-exec | status: READY_FOR_REVIEW | files: deposit-received.html | tests: ms_claus review exit 0, surface scan clean | blockers: Stripe link NOT_CONFIGURED - page inert until operator creates it
Result: green-machine-exec | status: READY_FOR_REVIEW | files: tools/slots/test_slots.py (+1 negative test, hold-on-DEPOSIT_SENT refused) | tests: 27 passed | blockers: NONE - closes the open Phase 2 coordinator note
Result: green-machine-exec | status: READY_FOR_REVIEW | files: tools/malosound_adapter/adapter.py, test_adapter.py | tests: 8 passed | blockers: NOT_CONFIGURED by design - no endpoint/credentials exist
Result: green-machine-exec | status: READY_FOR_REVIEW | files: docs/OPN-SUBMISSION.md, docs/production-deployment-record.md, docs/seasonal-ops-runbook.md, scripts/ops_check.py | tests: full gauntlet PASS, 194 total | blockers: NONE

Claim: Ops-check suite coverage (the PLANNED task from the 2026-09-04 Codex checkpoint) | owner: claude-fable | started: 2026-09-04 18:32 | files: scripts/ops_check.py | test: python scripts/ops_check.py + python -m pytest -q
Claim: Santa journey verification (inquiry -> route -> deposit -> booking -> approved content) | owner: claude-fable | started: 2026-09-04 18:32 | files: read/run only; any fix will be claimed here first before editing | test: journey trace with synthetic data + full suite
Claim: Public-phone fix in reservations content lane (journey step 5 break: captions carry Zelle 305-244-0360 instead of public 786-975-9557) | owner: claude-fable | started: 2026-09-04 18:47 | files: business/reservations/content_agent.py, business/reservations/openai_adapter.py, business/reservations/tests/test_reservation_system.py, business/reservations/tests/test_openai_adapter.py | test: python -m pytest business/reservations/tests -q + full suite + ops_check

Result: claude-fable | status: READY_FOR_REVIEW | files: scripts/ops_check.py | tests: 222-test battery + all 7 steps PASS; fail-closed suite-coverage gate proven in both directions (stray unlisted test file -> FAIL "discovered but not in the routine list"; temporarily renamed required suite -> FAIL twice; tree restored, verified via git status) | blockers: NONE
Result: claude-fable | status: VERIFIED (verification-only claim, no files) | files: none - read/run only, 6 tracer agents, state dirs redirected outside the repo | tests: full journey exercised, zero broken steps beyond the phone drift fixed under the next claim; details in "Journey verification results" above | blockers: NONE
Result: claude-fable | status: READY_FOR_REVIEW | files: business/reservations/content_agent.py, business/reservations/openai_adapter.py, business/reservations/tests/test_reservation_system.py, business/reservations/tests/test_openai_adapter.py | tests: reservations suite 27 passed (2 new tests); full suite 222 passed; ops_check all 7 PASS | blockers: NONE

Result: claude-fable | status: READY_FOR_REVIEW (answers the Codex formatted-variant finding) | files: business/reservations/content_agent.py, business/reservations/openai_adapter.py, tests/test_openai_adapter.py, tests/test_reservation_system.py | tests: 226 passed full suite; "(305) 244-0360", "3052440360" and "+1 305 244 0360" now rejected via separator-stripped digit comparison in BOTH the OpenAI adapter and the deterministic lane; approve_draft re-checks hand-edited captions (new negative test); positive 786-975-9557 case retained; Zelle payment instructions outside the content lane untouched | blockers: NONE

Claim: Repository relocation to C:\XIV\santa (sole mover per relocation checkpoint) | owner: claude-fable | started: 2026-09-04 18:55 | files: whole-repository same-drive move + old-path references in coordination docs | test: git status parity + HEAD 9485bb8 + 226-test suite + ops_check at the new root; other workers defer repository writes during the move

Result: claude-fable | status: READY_FOR_REVIEW | files: whole repository moved to C:\XIV\santa (git history + edits + untracked dirs intact); path updates in CLAUDE.md, loop.md, docs/demo-runbook.md, docs/HANDOFF-CONTINUE.md, tools/{triage,comms,content,elves}/README.md, business/reservations/README.md; RELOCATION-NOTE.md preserved; MOVED.md pointer left at old path | tests: at new root HEAD 9485bb8, status parity, 226 passed, ops_check 7/7 PASS | blockers: NONE - commits/pushes remain with the coordinator

Coordinator checkpoint (green-machine-exec, 2026-09-01): ops_check PASS on all 6 steps; pytest battery 195 passed (email-optional intake added); commits e903623 + this cycle's follow-up; all locally achievable lane acceptance items green. Remaining
external actions: (1) operator creates Stripe Payment Link + pastes URL,
(2) push commits to origin, (3) OPN evidence collection per
docs/opn-form-answers.md minimum strong packet.

## Claim protocol

Claim: Prevent an intermediate hold masking a confirmed route conflict | owner: Codex | started: 2026-09-05T00:05Z heartbeat | status: READY_FOR_REVIEW | files: business/reservations/logistics_agent.py, tools/test_integration_season.py | scope: check non-adjacent booking conflicts as well as adjacent visits; synthetic reservation/operator/logistics regression cases | reproduction: confirmed 15:00-17:00 visit plus unpaid 15:30-15:45 hold allowed a 16:00-16:45 visit to confirm with logistics=tight; all events mocked, nothing persisted | test: seasonal integration suite, reservation suites, ops_check, slot validator, preflight, diff check | coordination: both files clean and unclaimed at inspection; all existing dirty/claimed files preserved. Result: 277 full-suite tests, all 7 ops-check steps PASS; detailed machine-readable handoff in latest heartbeat above.

Claim: Safe API HTTP diagnostics for the operator connection test | owner: Codex | started: 2026-09-04 | status: IN_PROGRESS | files: tools/triage/triage.py, tools/triage/test_triage.py | scope: display HTTP status and an allowlisted error category without raw API messages, keys, customer text, or changed log schema; extend existing model-failure regression coverage | trigger: operator's synthetic test MPN-20260904-057409 returned MODEL_HTTP_ERROR with key/model configured | test: mocked HTTP failures and redaction assertions, triage suite, ops_check with live API environment disabled in test subprocess only.

Result: Codex | status: READY_FOR_REVIEW | files: tools/triage/triage.py, tools/triage/test_triage.py | implementation: HTTP failures now emit a status and allowlisted error category to stderr; raw API messages, headers, URLs, and unknown codes never print; body reads capped at 4096 bytes; malformed/unreadable bodies still fall back; log schema and MODEL_HTTP_ERROR unchanged | tests: existing fallback regression expanded to 18 simulated transport/HTTP cases, including quota vs rate limits, permissions, invalid schema, malformed bodies, and secret/contact redaction; triage 45 passed; full ops_check 271 passed across 16 suites, 7/7 steps PASS including privacy, slot validation, and OPN preflight | blockers: operator must rerun the synthetic test in the PowerShell session holding the API key and report the sanitized HTTP line; actual cause still unknown, no live API success claimed | safety: no real API call, approval, customer send, production record, credential change, commit, or push; API environment disabled only within the test subprocess. Follow-up for test owners: some existing build()/web UI tests inherit API configuration unless their caller clears it, so persistent test-level network isolation remains useful.

Claim: Enforce the reservation-board deposit minimum | owner: Codex | started: 2026-09-04T23:00Z heartbeat | status: IN_PROGRESS | files: business/reservations/store.py, business/reservations/tests/test_web_ui.py | scope: refuse missing/invalid/under-50-percent amounts and missing memo references before verification; recheck at confirmation | reproduction: synthetic Christmas Eve bookings reached confirmed with amount None, 0, or 1 and no memo; append_event mocked, no records written | test: HTTP reservation suite, reservations suites, ops_check; Claude-owned files remain untouched.

Claim: Close confirmed-booking update bypass | owner: Codex | started: 2026-09-04T23:00Z heartbeat continuation | status: IN_PROGRESS | files: business/reservations/reservation_agent.py, business/reservations/tests/test_web_ui.py | scope: reject schedule/package changes after confirmation or terminal states before mutation; retain ordinary inquiry/hold updates | reproduction: two confirmed synthetic visits at 15:00/16:00 became two confirmed visits at 15:00 via reservation_agent.update; subsequent route check flagged impossible but did not revoke confirmation | test: negative HTTP update tests + full ops_check; no persisted customer data or model calls.

Before editing, add a claim under the matching work item with the worker name, timestamp, target files, and expected test command. One worker owns a file at a time. If the work is already claimed, choose another item or review the existing worker's completed diff.

Example:

`Claim: Phase 3 | owner: [WORKER] | started: [YYYY-MM-DD HH:MM] | files: [PATHS] | test: [COMMAND]`

After implementation, append:

`Result: [WORKER] | status: READY_FOR_REVIEW | files: [PATHS] | tests: [RESULT] | blockers: [NONE OR EXACT BLOCKER]`

The coordinator then records `VERIFIED` only after independently reviewing the diff and rerunning the tests.

## Acceptance checklist

- [ ] Booking form and slot catalog use one canonical state machine.
- [ ] `BOOKED` is reachable only after human verification of the 50% Zelle or Stripe deposit.
- [ ] Public availability does not allow a second request for a held or deposit-pending slot.
- [ ] Customer confirmation is refused before `BOOKED`.
- [ ] Double-booking, missing payment, over-capacity, and incomplete-info gates have negative tests.
- [ ] Mrs. Claus answers only approved bilingual FAQs and escalates payment, exceptions, and final availability.
- [ ] Calls are not claimed as recorded or automated until a real provider, consent flow, and secure test exist.
- [ ] Content and outreach are drafts or queues until human approval and real account connections exist.
- [ ] No private data, secrets, unsafe payment methods, retired contact paths, or unsupported claims are public or tracked.
- [ ] Full test suite, slot validator, privacy scan, and `git diff --check` pass.

## Final handoff

Do not print `SANTA_WORKFLOW_COMPLETE` until every checklist item is verified. The final report must list working features, dry-run/manual features, external dependencies, tests, and the exact next operator actions.

Claim: Sample inquiry run (synthetic, end to end) | owner: Claude xiv-session local_1c36dd26 | started: 2026-09-05 00:00Z | files: docs/sample-inquiry-run-2026-09-04.md (new file only) | test: python -m pytest tools/triage/test_triage.py -q
Result: Claude xiv-session local_1c36dd26 | status: READY_FOR_REVIEW | files: docs/sample-inquiry-run-2026-09-04.md | tests: 45 passed; --demo 4/4 synthetic; one synthetic inquiry approved_awaiting_send in the synthetic log; production log NOT STARTED before and after | blockers: two customer-facing defects found, not fixed (no code claimed): (1) CATEGORY_RULES order prices a home "fiesta familiar" as event_visit $450 instead of family_visit $325; (2) pricing.json deposit text promises a "secure online payment link" that does not exist yet while the payment_method gate reports PASS "Zelle only". Details and five smaller items in the document.
