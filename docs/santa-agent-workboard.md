# Miami Papa Noel Agent Workboard

Shared coordination file for every Claude Code loop and worker. This file contains no customer data.

Last coordinator check: 2026-09-01 post-242ab86

Coordinator verification: the active workers are sharing the main repository
directory. No separate Git worktrees are currently visible. The workers are
using separate tool areas, so they must continue claiming individual files and
must not edit the same production file at the same time.

## Current state

| Work item | Owner | Status | Files | Verification |
| --- | --- | --- | --- | --- |
| Phase 1: booking and slot state machine | Claude Code / slots worker | VERIFIED | `tools/slots/` | `23 passed` in focused slot suite |
| Phase 2: public availability and operator confirmation | Claude Code / slots worker | IN_PROGRESS | `tools/slots/`, `schedules/`, `scripts/` | Must prevent public requests for HELD and DEPOSIT_SENT slots |
| Phase 3: Mrs. Claus intake | Claude Code / intake worker | VERIFIED | `tools/mrs_claus_office/` | `20 passed`; synthetic bilingual and gate tests |
| Phase 4: call/text adapters and consent | Claude Code / comms worker | VERIFIED-DRY-RUN | `tools/comms/` | `19 passed`; no provider or recording enabled |
| Phase 5a: content queue | Claude Code / content worker | VERIFIED-DRY-RUN | `tools/content/` | `16 passed`; approval required |
| Phase 5b: elf outreach queue | Claude Code / elves worker | VERIFIED-DRY-RUN | `tools/elves/` | `16 passed`; human send required |

Latest coordinator test checkpoint: `python -m pytest -q` -> `166 passed`.

Open coordinator note: the current `tools/slots/slots.py` availability path
still returns HELD and DEPOSIT_SENT slots. The tests pass, but Phase 2 is not
fully verified until the public request path excludes those states, or routes
them to an explicit operator-review path, with a negative test for each one.
BOOKED remains the only sold state for reporting.

Release state: `242ab86` is local and unpushed. The three coordination files
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

Coordinator checkpoint (green-machine-exec, 2026-09-01): ops_check PASS on all 6 steps; pytest battery 195 passed (email-optional intake added); commits e903623 + this cycle's follow-up; all locally achievable lane acceptance items green. Remaining
external actions: (1) operator creates Stripe Payment Link + pastes URL,
(2) push commits to origin, (3) OPN evidence collection per
docs/opn-form-answers.md minimum strong packet.

## Claim protocol## Claim protocol

Before editing, add a claim under the matching work item with the worker name, timestamp, target files, and expected test command. One worker owns a file at a time. If the work is already claimed, choose another item or review the existing worker's completed diff.

Example:

`Claim: Phase 3 | owner: [WORKER] | started: [YYYY-MM-DD HH:MM] | files: [PATHS] | test: [COMMAND]`

After implementation, append:

`Result: [WORKER] | status: READY_FOR_REVIEW | files: [PATHS] | tests: [RESULT] | blockers: [NONE OR EXACT BLOCKER]`

The coordinator then records `VERIFIED` only after independently reviewing the diff and rerunning the tests.

## Acceptance checklist

- [ ] Booking form and slot catalog use one canonical state machine.
- [ ] `BOOKED` is reachable only after human Zelle verification.
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
