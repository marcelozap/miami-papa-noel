# Miami Papa Noel Agent Workboard

Shared coordination file for every Claude Code loop and worker. This file contains no customer data.

Last coordinator check: 2026-09-05, post-18:14Z coordination clarification; spending v2 VERIFIED, packet wording review still open

## Review status and planning clarification (Codex, 2026-09-05)

Claim: this workboard status correction only, following the owner's pasted
Claude note. The v2 code is no longer awaiting coordinator review: see the
16:47Z independent safeguards review and the post-17:44Z green full release
check. Correct the worker's part-1 label below to VERIFIED. Packet wording
corrections remain separate; no source, budget or runtime setting changes.

The proposed v3 monetary gate is not built or enabled. Design constraints:
reserve the cost of the complete bounded input (instructions, schema and
customer message) plus maximum billed output before dispatch; share atomic
accounting across both adapters/processes; refuse unknown accounting or
pricing; retain uncertain reservations after timeout/crash/missing usage.
Concurrent workers must not each overshoot the application allowance.
Use model-specific, dated, verified rates rather than requiring the owner
to guess prices. Pricing drift and outside-account usage remain distinct
from an application's enforced budget. No 25-cent or other precise daily
allowance has been approved. No paid calls are authorized by planning.

Owner confirmed the planning assumption of $0 ADDITIONAL service cost for
the existing phone plan, website hosting and computer. This does not add a
new phone automation service or make an offline PC answer customers. The
latest request is a Gemini prompt for independent planning, not a model
installation, replacement build, external submission or paid test.


## Packet handoff independent recheck (Codex, 2026-09-05, post-17:44Z)

Claim: read-only review of Claude's parts 2-5 READY_FOR_REVIEW handoff;
this coordination note only. No source, runtime configuration, application
document, credential or private customer state edited by this review.

VERIFIED: the formerly failing copied-document fixture now passes without
removing evidence checks. Focused validator/evidence/packet suites: 28 passed,
11 subtests. Full `python -B scripts/ops_check.py`: all 7 steps PASS;
644 passed, 5 skipped, 52 subtests in 71.51 seconds, all 20 suites found.
The previous 1-failed release result is superseded for this working tree.
Preflight explicitly does not certify final submission readiness.

Packet review remains open for bounded wording corrections: reservations
PRODUCTION.md still says key configuration starts production model use and
omits the new positive allowance; production-deployment-record.md still
labels locally tested capabilities LIVE and has stale inquiry-based duration
and configuration-based model evidence rows; opn-form-answers.md retains one
2026 "is running" claim and calls uncorroborated history corroborated;
OPN-SUBMISSION.md calls `--demo` deterministic without forcing offline and
describes its four-inquiry batch as one request. Do not weaken final evidence
checks or fill real placeholders to clear these issues. Claude's packet
owner can correct these exact descriptions against the existing code.

Latest owner discussion: local Llama/Ollama or OpenAI gpt-oss is a proposed
alternative, not an authorized model migration or proof of OPN eligibility.
They want only cents per day and asked how long $14 would last. Paid calls
remain off. The current shared allowance is a request cap, NOT a cent cap;
no exact daily monetary allowance has been approved or implemented. Public
form submissions queue work; model generation is operator-triggered, and
the T-Mobile number has no automated model connection. No paid test, phone
activation, purchase, commit, push, deployment or customer send occurred.


## Spending v2 independent review (Codex, 2026-09-05T16:47Z)

Claim: independent read-only review of Claude's part-1 READY_FOR_REVIEW
handoff, plus this coordinator note only. Claude retains ownership of
the in-progress packet/document corrections. No source, runtime or other
worker files were edited by Codex during this review.

Result: VERIFIED for the revised local spending safeguards, not deployment
or a dollar guarantee. Paid generation defaults off in BOTH adapters even
with a key; an explicit positive allowance is required. Atomic slot files
replace the old read/check/append counter, and accounting allocation errors
refuse requests. Inquiry/content size and output-token bounds are present.
The old four rejection findings are resolved for the reviewed scope.

Independent checks: 225 passed across triage, content adapter and web-inquiry
suites. An additional temporary-state probe launched 24 separate processes
using both real quota implementations with cap=3: exactly 3 grants; fresh
content and triage processes then both refused. Slot contents were only
timestamp/adapter metadata. These were allocation tests, not API calls.

Scope limits: processes must use the SAME absolute private quota directory
and consistent allowance. This is not account-wide across machines/users,
does not survive an operator deleting its accounting state, and does not
establish a provider hard-dollar cutoff. The mirrored implementations need
cross-adapter regressions maintained together. No budget or paid operation
has been authorized by this review; real model/schema acceptance and
customer operation remain unverified.

Full release recheck during Claude's document updates: FAIL, 1 failed,
643 passed, 5 skipped, 52 subtests. All 20 suites discovered; slot validator,
Ms. Claus review, tracker privacy and whitespace checks passed. OPN preflight
also fails because the submission-validator suite fails. Exact reproduced
test: scripts/test_validate_opn_submission.py::ValidatorTests::
test_complete_final_fixture_passes_in_isolation. Its copied-document
fixture still leaves one submission placeholder, and launch-claim parsing
mistakes historical 2025-11-15 / 2025-12-24 references for the current
synthetic 2026-08-01 launch. The isolated test reproduces all three findings.
The pytest cache also retained an older slot-test failure ID, but that was
not the failure reported by this full run; do not infer a second regression.

Next for the packet owner: align the fixture with the revised documents
and distinguish historical/explicitly non-launch context from actual launch
claims without weakening final evidence gates. Keep real missing evidence
as missing. Run the focused validator suite and then the release checks
after document edits stabilize. Current whole-release status is BLOCKED,
not the earlier reported 644-pass green. Do not repeat the known failure
on unchanged inputs. No new public commit, push, deployment, live API call,
credential handling, customer record or message occurred in this review.

## Spending safeguards v2 + packet corrections (claude-fable, 2026-09-05T07:05Z)

Claim: fix ALL four confirmed budget defects + application-doc corrections +
GitHub update preparation + packet update | owner: claude-fable | files:
tools/triage/triage.py (budget region rebuild: atomic O_EXCL slot-file
reservations in a shared quota dir, default paid generation DISABLED,
fail-closed accounting), tools/triage/test_triage.py (budget regressions
incl. concurrency/mixed-adapter/corruption/failed-write/restart),
tools/triage/README.md, business/reservations/openai_adapter.py + its test
(same shared quota, cap honored incl. 0/default-off),
docs/day-one-operator-card.md (spending section corrected after fix),
docs/production-deployment-record.md + business/reservations/PRODUCTION.md
(claims audit fixes), docs/OPN-SUBMISSION.md (supported-facts update,
missing evidence marked), this workboard | boundaries: no paid calls, no
key handling, no commit/push (GitHub update PREPARED only, awaiting new
authorization), synthetic fixtures only.

Result (part 1 - spending safeguards v2): claude-fable | status:
VERIFIED by Codex (2026-09-05T16:47Z; full release rechecked after 17:44Z) | all four rejection findings fixed at the root:
(1) CONCURRENCY - the count is now atomic O_CREAT|O_EXCL slot-file
reservations in one shared quota dir (%LOCALAPPDATA%\MiamiPapaNoel\api-quota,
override MPN_API_QUOTA_DIR); 8-thread race regression proves exactly cap
grants, never more. (2) UNREADABLE ACCOUNTING now REFUSES paid generation
(BUDGET_ACCOUNTING_UNAVAILABLE) - quota-dir-as-file and PermissionError
probes both refuse with zero requests; the allowance can never reset.
(3) CONTENT ADAPTER now mirrors the same scheme (no cross-stack import,
same dir + slot naming): default/0/unreadable cap refuse with a rejected
manifest and no transport call; a triage-claimed slot reduces the content
allowance (mixed-adapter regression both directions). (4) DEFAULT IS
ZERO-SPEND: unset cap = PAID_CALLS_DISABLED even with a key; every paid
test opts in explicitly. Also added: input bound (6000 chars,
MODEL_INPUT_TOO_LARGE, nothing sent), cap ceiling 500/day, restart
persistence + timeout-consumes-slot-never-retries regressions, secret/
inquiry-text-free slot+ledger assertion. Docs corrected (README v2 section,
operator card v2 section) and both now state plainly: request/token limits,
NOT a dollar guarantee; dashboard alerts are not a verified cutoff. Tests:
triage 123, adapter 14, web_inquiry 88; FULL BATTERY 644 passed, 5 skipped,
52 subtests, 20 suites, ops_check 7/7 PASS. Parts 2-5 (doc/claims audit,
GitHub update prep, packet) in progress via read-only audit workflow.

Result (parts 2-5): claude-fable | status: READY_FOR_REVIEW | (2) workflow
verification carried by the standing suites (644) - no UI change this cycle,
prior browser QA stands. (3) CLAIMS CORRECTED per 3-auditor read-only audit:
business/reservations/PRODUCTION.md (launch date -> [TO FILL] + installation-
checkpoint note; status -> NOT STARTED; "Live" -> "Built"; no-model-run
caveat; "assists in operating" -> future tense; orchestrator qualified;
health-daily corrected) + OPS-LOG.md "launch" -> installation checkpoint.
(5) PACKET CORRECTED: opn-form-answers.md no longer presents the attested
2025 season as satisfying the 15-day requirement, states plainly the 2026
window has NOT started, present-tense "running it again" removed,
"the client" -> family-business wording, MISSING-EVIDENCE marks on AI-work
and 14-visit claims, placeholders converted to validator-matching [TO FILL:]
form; OPN-SUBMISSION.md Last-updated line, family-business relationship,
payment-gate row un-stales Stripe, six-DRAFT-validation-gates labeling,
launch clock aligned to the send-timestamp predicate, 2017 claim marked,
reviewer-clone NOTE; gap-report stale dates/rule/rails/optionality fixed;
evidence-index stale test name + CORROBORATED->ATTESTED + rails; release-
monitoring 45-tests removed + rails; release-checklist + account-setup-
checklist rails harmonized; production-deployment-record "Implemented
functionality" + attested-status + clock + relationship. Validator fixture
updated to the new audited wording (20 passed + 11 subtests); dates moved
off the LAUNCH_LINE_RE trigger line. Preflight: PASS, 0 blocking, 9 honest
warnings. FINAL BATTERY: 644 passed, 20 suites, ops_check 7/7.
(4) GITHUB UPDATE PREPARED, NOT EXECUTED (needs new authorization): branches
diverged at 9485bb8 (4 local commits vs 2 remote; 61d0f14 NOT an ancestor of
cb03e99); plan = (a) commit the uncommitted set BY EXPLICIT PATH (12 modified
+ docs/codex-day-one-handoff.md, docs/day-one-operator-card.md,
tools/triage/production_evidence.py which is a HARD import - pushing without
it ships a broken branch; never git add -A; Claude outputs/ + _to_delete/
now gitignored), (b) true merge of origin/codex/santa-checkpoint-2026-09-04
into the local branch - 7 known conflict files, resolve by union keeping
both guard sets, (c) push local branch, then fast-forward the PR branch
(merge has 61d0f14 as parent, so NO force anywhere), (d) ff-only update
inside the Codex worktree. Push-blocker CLEARED: the one private temp path
(workboard QA line) is redacted; secrets/customer-data scans clean
(synthetic canary + 555 fixtures only) | blockers: commit/merge/push await
owner authorization; single next owner action unchanged.

## Spending-control coordinator review (Codex, 2026-09-05T06:19Z)

Claim: review Claude's READY_FOR_REVIEW budget handoff without changing its
source; update this workboard and docs/day-one-operator-card.md only so the
owner is not instructed to spend against unverified safeguards. The owner
has raised affordability concerns; no new paid test, launch, service or
budget has been authorized. Preserve manual/offline operation and the
existing blocked Day 1 goal. Do not ask again for a paid test on each loop.

Review status: BLOCKED / corrections required, not VERIFIED. Existing
focused tests independently pass: 125 across triage and content adapter.
Three additional synthetic, network-blocked temporary-state probes confirm:

- tools/triage/triage.py:469-477 checks the ledger and appends separately.
  With two synchronized callers and cap=1, both reached the mocked API
  (2 requests). The cap is not concurrency-safe across operator processes.
- tools/triage/triage.py:429-446 treats every ledger read OSError as zero
  calls; the mocked PermissionError probe returns 0. An unreadable history
  must refuse paid generation, not reset the allowance. Malformed rows and
  reservation/write failures also need explicit fail-closed handling.
- business/reservations/openai_adapter.py:90-108 never consults the daily
  cap. With MPN_API_DAILY_CALL_CAP=0 it still invoked the injected content
  transport once. An output-token bound does not disable or count calls.

Also, the default permits 12 triage attempts once a key/model is configured,
not an owner-approved zero-spend default. The current cap is per ledger,
not an account-wide dollar ceiling. The card's recommendation to set a
provider hard spend limit is not verified and must not be relied upon.

No actual network call, credential, customer data, production ledger,
runtime configuration, source change, commit, push or deployment was used.
Probe scratch state was temporary. Claude's 632-test full-battery report
is retained below as its report, not independent coordinator verification;
the earlier 626-test result predates this patch. Do not rerun the full
battery merely to turn these missing cases green. Next code handoff must
cover all paid paths with an explicit opt-in, atomic shared reservations,
and fail-closed ledger errors, with mocked regressions for these cases.
Do not resume paid operation merely because tests pass; owner budget and
authorization, real model verification and genuine use remain separate.

## Spending controls for paid model calls (claude-fable, 2026-09-05)

Claim: local API budget gate at the shared model-call choke point | owner:
claude-fable | files: tools/triage/triage.py (call_openai_triage region +
budget helpers only - preserving the evidence-clock and check-model work),
tools/triage/test_triage.py (append), tools/triage/README.md +
tools/triage/log-schema.md (budget knobs + new error codes),
business/reservations/openai_adapter.py + tests/test_openai_adapter.py
(max_output_tokens bound only), docs/day-one-operator-card.md (budget note),
this workboard | design: deterministic daily call cap (MPN_API_DAILY_CALL_CAP,
default 12, 0 = paid calls disabled) counted in a private ledger outside Git
before each request; per-call MPN_API_MAX_OUTPUT_TOKENS bound (default 900)
in the request payload; over-cap -> deterministic offline fallback with its
own error code, never a paid request; token usage recorded after success for
visibility. HONEST LIMIT: calls+tokens, not dollars - no price table is
invented. No API request, no credential handling in this task.

Result: claude-fable | status: READY_FOR_REVIEW | files as claimed | tests:
triage 115 passed (7 new budget regressions: cap-0 and unreadable-cap send
NOTHING and write nothing; cap-2 allows exactly 2 then falls back with
BUDGET_CAP_REACHED and zero further requests; failed attempts count and are
never auto-retried; max_output_tokens 900 default / env override present in
the payload; ledger carries counts only - no key, no inquiry text);
reservations adapter 10 passed (max_completion_tokens 800 bound asserted);
FULL BATTERY 632 passed, 5 skipped, 52 subtests, all 20 suites, ops_check
7/7 PASS first run | integration notes: --check-model is now metered too -
its no-writes invariant was narrowed to permit exactly the paid-call ledger
(fixture asserts the single allowed file); the 23-case failure regression
sets an explicit high cap so it tests diagnostics, not the budget; new
error codes PAID_CALLS_DISABLED / BUDGET_CAP_REACHED documented in
log-schema.md; budget knobs documented in triage README + operator card
(card recommends MPN_API_DAILY_CALL_CAP=3 for day one and a provider-side
dollar limit, which no local control replaces) | blockers: NONE for the
control itself; paid generation remains inert until the owner configures
the rotated key.

Status: VERIFIED (local implementation only). Prior goal turn made concrete progress: --check-model
and operator instructions, 583 full-suite tests passed. Private key/model
are still absent in this process; no authorized live replacement test can
run here yet. Bounded next defect: --status counts any production row, and
the submission validator can combine an old fallback date with a new AI
reply. Claim tools/triage/production_evidence.py (new shared predicate),
tools/triage/triage.py, tools/triage/test_triage.py,
scripts/validate_opn_submission.py, scripts/test_validate_opn_submission.py,
tools/triage/log-schema.md, tools/triage/README.md,
docs/production-launch.md, docs/day-one-operator-card.md,
docs/codex-day-one-handoff.md, docs/OPN-VALIDATION.md and this workboard.
Use recorded real, non-fallback, gated, reviewed/sent evidence and full
elapsed timestamps; no qualification guarantee or changed customer records.
All tests synthetic/offline; no credentials, sends, push or deployment.

Result: one shared reviewed-model-send predicate now controls both status
and submission duration. It excludes fallback, pending, missing/failed-gate,
unnamed-reviewer, error and invalid timestamp records. Full UTC elapsed
time starts at the recorded send, not an earlier fallback inquiry. New real
CLI records carry offsets; legacy local timestamps are interpreted in the
operator machine's timezone. Status rejects malformed/contaminated JSONL
and duplicate IDs without printing record bodies. Neither tool declares
OPN qualification from elapsed time. Extreme UTC-conversion dates were
probed, fixed to reject cleanly, and pinned with regressions.

Final checks: 129 focused tests + 11 subtests passed. Full ops check:
626 passed, 5 skipped, 52 subtests; all 20 suites and all operations checks
PASS. Changed-file credential-pattern scan: 13 files, zero findings.
No production log exists at the default path; key/model presence remain
false in this process. No live model request, customer message, production
record, deployment or Git commit/push was made. All exec checks finished.

Goal audit: setup/checklist and demonstrated local defects are handled.
Actual Luna structured response/gate acceptance and genuine reviewed/sent
customer operation are NOT verified. The same private replacement-key
dependency was recorded in the initial goal/handoff turn, the model-check
continuation and this continuation, and is still present on recheck. Goal
is BLOCKED pending owner setup/results, not complete. The completed code
and this turn's tests are progress, not customer-use evidence. Next owner
action: follow the private setup in docs/day-one-operator-card.md and run
--check-model in that same terminal. Share only the non-secret result.
After a real model pass, use an actual incoming inquiry and record human
review/send honestly. While inputs remain unchanged, do not run more API
probes, fabricate records, add speculative features or repeat full suites.

## Model-check CLI (Codex, 2026-09-05T04:34Z)

Claim: explicit synthetic `--check-model` with nonzero fallback status and
no inquiry log or approval. Files: tools/triage/triage.py,
tools/triage/test_triage.py, tools/triage/README.md,
docs/production-launch.md, docs/codex-day-one-handoff.md, this workboard.
Use the existing Responses/schema/bilingual gates, not a second adapter.
Test with mocked API responses only; no exposed key, live request, real
inquiry, launch attestation, commit, push or deployment. Leave Claude's
operator-card/browser-review claim and scratch folders untouched.

Result: implemented and locally verified. Focused tests: 71 passed. Full
ops check: 583 passed, 5 skipped, 41 subtests; all 20 suites and every
ops step PASS. CLI smoke without private configuration returned exit 1
and NOT VERIFIED, with no API call or inquiry log. The default production
status still reports NOT STARTED. No live Luna workflow success is claimed.

Coordinator review: Claude's operator card is now READY_FOR_REVIEW, so
Codex additionally claims docs/day-one-operator-card.md for two doc fixes:
use --check-model instead of the synthetic logging command, and distinguish
verified model-backed reviewed/sent use from the legacy first-row counter.
The reported browser QA is Claude's evidence, not independently rerun here.
Source changes remain local and uncommitted. Next input: privately configured
replacement key and owner-authorized model check; genuine use remains later.

## Day-one continuation (claude-fable, 2026-09-05T05:05Z)

Claim: Luna-readiness without credential + fresh browser visual QA + day-one
operator card | owner: claude-fable | files: docs/day-one-operator-card.md
(NEW), this workboard | read/run only elsewhere: adapter request-contract
inspection, offline browser journey on synthetic scratchpad state
(desktop + mobile), no API request, no credential handling, no --real,
no config or source edits | test: browser journey evidence + focused
checks; no full battery without source changes.

Result: claude-fable | status: READY_FOR_REVIEW | files:
docs/day-one-operator-card.md (NEW), this workboard | evidence:
(1) Luna-readiness without credential: triage adapter already sends the
modern Responses API shape the successful haiku used - /v1/responses,
store:false, strict json_schema text.format; MPN_MODEL flows as a plain
string, so no code change is needed for gpt-5.6-luna. Untestable from here:
schema acceptance + entitlement - exactly one bounded operator test remains
(command on the card, PASS = "model : gpt-5.6-luna" with no offline-fallback
tag). (2) FRESH BROWSER QA (real Chrome pane, synthetic scratchpad state,
--offline): public form renders bilingually with DEMO banner, consent and
OpenAI disclosure; ES home-visit submission -> receipt "Solicitud recibida
MPN-WEB-... / No es una confirmacion de reserva" with correct 786-975-9557
footer; operator sign-in; draft generated with red "Offline fallback /
Respuesta de respaldo sin IA" label, SPANISH DRAFT FIRST with English
retained, all six gates rendered PASS, locked $325 family price, Zelle-only;
genuine-customer checkbox verified INERT in demo (app.js real.disabled=!live);
approve -> "Aprobado; no se ha enviado nada"; Record manual send guarded by
a native confirm ("Have you actually sent...?") - browser auto-cancel proved
it blocks, stubbed OK recorded "Envio manual registrado". Mobile 375px: form
and desk render clean, no horizontal scroll; fresh navigation demands
sign-in again. (3) Operator card command syntax verified offline verbatim
(es/family_visit/6 gates). No repo state touched; QA server stopped;
scratchpad state only | blockers: the one bounded Luna test needs the
owner's rotated credential in the operator terminal | next: owner runs the
card's step 1-3.

## New Goal and Continuation Prompt (2026-09-05)

The user requested a new goal, then a prompt for Codex to continue the
build. Created the active goal: get the operator-assisted Mrs. Claus
workflow ready for genuine use, verify Luna through actual bilingual
gates, and establish Day 1 only from real reviewed/sent customer work.
Codex claims this note and docs/codex-day-one-handoff.md only for the
handoff. The pasted Claude transcript confirms the preflight is done;
do not restart it. The continuation file identifies the committed baseline,
newer diagnostic notes, exact successful/failed request scopes, credential
rotation, bounded test authorization and the remaining owner/host work.
No further API request, model configuration change, production activity,
Git commit/push or deployment was performed to prepare this prompt.

## Exact Haiku Request Succeeded (2026-09-05T04:29:06Z)

Owner: Codex. Scope: redacted result in this board and launch checklist;
no source/configuration edit. Status: VERIFIED synthetic API response,
not verified Santa integration, pricing entitlement or production use.

The user separately authorized their exact curl request: Responses API,
model gpt-5.6-luna, input "write a haiku about ai", store true. Executed
curl.exe once with the credential supplied through hidden terminal input
and in-memory stdin configuration, never a file or process command-line
argument. No retries or redirects. Curl exit 0, HTTP 200, returned model
gpt-5.6-luna, response status completed, 12 input tokens, 99 output tokens,
111 total tokens. The API returned a haiku. No raw response, credential or
identifier was persisted locally; store true was preserved as explicitly
requested, so this was not a no-provider-storage request.

This supersedes any blanket inference that the earlier zero balance or
gpt-4.1-mini-2025-04-14 failure rules out all model access. That earlier
request really returned credit_balance_exhausted; this different exact
request really succeeded. The reason for the difference and whether the
successful call was free are not established by the response. Do not
invent an entitlement, a paid charge or a grant-expiration explanation.

Santa's configuration was not changed and its structured bilingual/gated
path was not tested with gpt-5.6-luna. Next: with separate authorization,
verify that path using a privately configured replacement credential,
confirm available usage/terms, and retain synthetic/customer separation.
No customer activity or production log was created; no production date
or OPN qualification is asserted. Do not reuse the exposed credential in
scheduled jobs. No full battery rerun for these documentation-only notes.

## API Connection Diagnosis (2026-09-05T04:27:17Z)

Owner: Codex. Scope: this redacted coordination note only; no source edit.
Status: VERIFIED diagnosis; successful model access remains BLOCKED.
The user explicitly authorized one synthetic request using the supplied
test credential. Passed it through hidden terminal input, held only in the
test process, never written to source/config/logs or printed. The user has
been advised to rotate it because it appeared in chat; do not reuse it in
an automation. No credential, prefix or hash is recorded here.

Exactly one direct Responses API request was attempted, with redirects
disabled and a 1200-output-token cap. The configured snapshot was
gpt-4.1-mini-2025-04-14; it did not produce a usable model response. The API
returned HTTP 429 with the allowlisted code credit_balance_exhausted.
This confirms exhausted prepaid credit for that request, not why the
earlier balance changed. Do not infer charges or expired grants without
the account's billing evidence.

The existing build_record path handled a synthetic Spanish home-visit
inquiry: language es, fallback_used true, model offline-rules-v1,
error_code MODEL_HTTP_ERROR; English and Spanish fallback drafts present,
all six gates PASS, real_customer false. No customer message, approval,
payment or production log was created. No retries; the process exited.
No full regression rerun is warranted for this note-only update.

Next: the owner resolves available API credit or selects an authorized
funded organization, rotates the exposed key and configures its replacement
privately. Only then run a separately authorized synthetic model-backed
check. Keep auto-reload off unless the owner chooses otherwise. This test
does not begin the production window or satisfy the 15-day requirement.

## Coordinator Wrap-Up (2026-09-05)

Status: VERIFIED. Owner: Codex. The user authorizes local commits and
wrap-up, not push or deployment. Claude's READY_FOR_REVIEW handoff is now
present; independently reproduced 44 passed, 1 Windows symlink skip.
R1 and the public proxy mismatch are fixed. The remaining R2 demo cases
still accept a set proxy (direct browser requests lack its required header)
and ignore MPN_PUBLIC_ORIGIN. Codex claims the narrow final correction in
tools/launch_preflight/preflight.py, its tests/README/handoff, suite
registration in scripts/ops_check.py, and this board/checklist handoff.
Claude should leave the delivered folder frozen while this review closes.
After focused regressions: full release checks, explicit scoped staging,
and a local checkpoint commit. Exclude Claude outputs/ and _to_delete/.
Hosting, API access and genuine production evidence remain separate; do not
translate this commit or test run into a launch date.

Final review result: R1/R2 closed, including direct-demo proxy/origin
settings. The delivered checker is integrated into the 20-suite routine;
no further Claude implementation is pending for this task. Focused result:
65 passed, 1 Windows symlink skip. Full `python scripts/ops_check.py` exits
0: 564 passed, 5 skipped, 41 subtests passed; suite coverage, slot validator,
Ms. Claus review, tracker privacy, diff check and OPN preflight all PASS.
Source-hash comparison found no changes across 98 files during the run.
The scoped 50-file credential-pattern scan returned no findings; private
queue/log/receipt files and unrelated scratch folders are not included.

Checkpoint scope: bilingual private inquiry/review queue and maintenance,
uninstalled hosting templates, launch preflight, overnight booking/route
and quote protections, North Pole personas, regression tests and honest
launch documentation. Source-level/client-session checks pass; the latest
branding still needs a fresh visual browser pass, and Linux/TLS/restart/
alert delivery/hosted restore have not been verified on a selected host.
No preview process was restarted, account changed, message sent, model
success asserted or production log created. No push/deployment authorized.
Next: retain this checkpoint; resume only on an actual unclaimed task or
changed hosting/API/provider inputs. Do not rebuild delivered work or rerun
the full battery merely because the scheduled check wakes.

## Scheduled verification (2026-09-05T03:58:37Z)

{"at":"2026-09-05T03:58:37Z","owner":"Codex heartbeat","status":"BLOCKED","files":["docs/santa-agent-workboard.md"],"tests":{"python scripts/ops_check.py":"exit 1: only the previously reported unregistered launch-preflight suite; listed battery 499 passed, 4 skipped, 41 subtests; other six steps PASS","python -m pytest tools/launch_preflight/test_launch_preflight.py -q --tb=short":"23 passed, 1 skipped; does not cover R1/R2","slot_validator":"PASS via ops_check","OPN_preflight":"PASS via ops_check, not qualification","git_diff_check":"exit 0"},"blockers":["Claude R1/R2 unchanged; no handoff","hosting/API access and deployment approval still needed"],"next":"Preserve worker ownership; integrate only after corrected handoff. Existing 30-minute automation/end date/notification preference preserved; prompt updated to check changed state and avoid repeating the full battery or owner requests while unchanged. No new notification, purchase, deployment, customer send or production evidence."}

## Dependency audit (2026-09-05T03:52:26Z)

Third consecutive NO PROGRESS audit, 2026-09-05T03:53:44Z. Re-read routing
and coordination instructions, current HEAD/status, preflight files and
handoff presence, current-process configuration and browser tabs. The same
dependencies remain: no corrected Claude handoff, no accessible signed-in
hosting account, no configured API/model/operator/public-origin/proxy here,
and no deployment authorization. No live process/job handle is confirmed.
No source edits or repeated tests can establish those missing external
facts. Goal is BLOCKED, not complete; all work and reservations preserved.

Resume with owner hosting access/deployment decision or Claude's corrected
handoff. Recheck the current files first; verify R1/R2 before registering
the new suite and running the whole release check. A successful configured
synthetic model test and genuine customer use still must occur separately.
Do not backdate a launch or count these audits/tests as production use.

Second consecutive NO PROGRESS dependency audit, 2026-09-05T03:53:04Z:
HEAD/status and preflight files unchanged; no handoff or live worker handle.
Current-process key/model/token/public-origin/proxy remain unconfigured.
The Vercel tab handle is no longer in the browser session; a fresh tab list
has no Vercel page. No inference of a successful sign-in, no automatic
reopening or browser switch. Owner hosting access and API setup, plus
Claude's corrections/handoff, still require an external state change.
Only this audit note changed; goal remains active at this second check.

Previous goal turn: PROGRESS (reproduced preflight R1/R2 and verified the
integration gate). Current turn: NO PROGRESS toward implementation/launch,
first consecutive dependency audit after that progress. Preflight files
are unchanged and no handoff is present; preserve Claude ownership. No
confirmed live job handle is available and no duplicate worker was started.

Checked existing-host access without account changes: the in-app Vercel
dashboard redirects to its login page. Browser discovery confirms only the
in-app browser is connected, no external browser session. Left the login
page open for the owner. Account/project/plan remain unverified; signing
in to the existing account is the next hosting input, not creating or
upgrading an account. API connection verification remains outstanding.
No source edits, new test runs, purchase, deployment or production activity.

## Launch-preflight review findings (2026-09-05T03:49:21Z)

Previous goal turn: PROGRESS (request-parser fix, regression verification
and existing-host compatibility check). New safe action: read-only review
of Claude's arriving preflight implementation/tests. At inspection no
handoff.md exists, so this is not an integration approval or a claim that
the worker is finished. Claude retains its files. Coordinator owns this
review note only; no edits to tools/launch_preflight or ops_check yet.

Reproduced against the arriving preflight.py (write time 23:47:31 Miami):

- R1: check_origin(public, 'https://[') raises an unhandled ValueError.
  Origins with :wrong, :99999 or a space in the hostname return CONFIGURED.
  Fail closed with a redacted finding for malformed URL/port/host input;
  invalid input must preserve deterministic CLI exit/JSON behavior.
- R2: public proxy '127.0.0.1 ' returns CONFIGURED because preflight strips
  it, but the service's parse_ip rejects the exact environment value.
  In demo mode proxy '127.0.0.1' is described as unused, yet server.main
  passes it to App even with --offline: a direct browser supplies no proxy
  header and client_ip returns HTTP 400. Demo origin overrides likewise
  must be checked against actual MPN_PUBLIC_ORIGIN behavior, not ignored.
  Reconcile the checker with the runtime without weakening runtime guards.

These were in-memory, synthetic, no-network probes; no App was initialized
and no queue/customer/API/provider state was created. Include negative and
normal controls in Claude's existing suite. Integration waits for the
handoff and resolution; do not call the currently unregistered suite part
of the earlier 499-test checkpoint. Review note is actionable new evidence,
not a reason to restart or duplicate Claude's worker.

Verification: the arriving suite runs 23 passed, one Windows symlink skip.
It does not exercise R1/R2. The suite-coverage gate now fails specifically
because tools/launch_preflight/test_launch_preflight.py is not registered;
registration remains coordinator-owned and pending review completion. The
overall worktree must not be described as release-green using the earlier
499-test result. No handoff.md was present at the last read. No confirmed
worker handle is available to poll, so there is no verified running wait.

Current turn: PROGRESS through concrete review findings and validation of
the integration gate. No worker implementation was changed, no service or
external account was started, and no live API/customer evidence was made.
Next: Claude resolves R1/R2 and supplies its handoff; coordinator verifies
the updated implementation and registers/runs the complete release suite.

## Hosting fit and malformed-request review (2026-09-05T03:44:29Z)

Previous goal turn: NO PROGRESS (read-only inspection interrupted by the
owner's hosting clarification; no implementation or verified running wait).
Current safe action: inspect the existing static hosting contract and test
the suspected unhandled JSON recursion path before Internet deployment.

Claim: Codex coordinator, VERIFIED locally; files: tools/web_inquiry/server.py,
tools/web_inquiry/test_web_inquiry.py, tools/web_inquiry/README.md,
docs/tonight-launch-checklist.md and this workboard. Scope: malformed HTTP
JSON must return a sanitized bilingual error without storing a request or
calling the model. Add failing synthetic regressions, fix narrowly, review,
then run the full battery. Claude's reserved preflight folder is untouched.

Hosting evidence: README.md and vercel.json describe static Vercel hosting;
no local .vercel project link or .openai/hosting.json is present. This does
not establish the currently deployed account, plan or available credits.
Official Vercel documentation says function filesystems are ephemeral and
cannot provide this queue's shared persistent local SQLite storage. Keep
the website unchanged; the current backend needs a persistent host, or an
explicitly selected redesign using durable external storage. No redesign,
new account, spending, deployment or migration is authorized by this audit.

Result: four new HTTP regressions failed before the fix with
RemoteDisconnected and server-side RecursionError. Arrays and objects nested
1100 levels, within the existing 16 KiB body limit, affected both public
intake and authenticated drafting. Added RecursionError to the request JSON
decoder's existing refusal handler; auth, origin, size and rate checks are
unchanged. The four tests now verify bilingual 400 errors, no saved inquiry
or audit event, no model invocation or parser traceback, healthy service
and a subsequent valid submission. Focused inquiry suite: 88 passed.

Coordinator inspected the one-line implementation delta and regression
scope. Full `python scripts/ops_check.py`: 499 passed, four platform skips,
41 subtests, 19 suites, all seven checks PASS. The 96 checked source/config
file hashes matched before and after. No implementation writes occurred
during the full run. Updated the inquiry README and concise owner checklist
with the error behavior and source-linked Vercel hosting limitations.

Current turn: PROGRESS (reproduced/fixed/verified request handling and
established existing-host compatibility constraints). No public deployment,
purchase, commit, push, real API call, customer message or production
evidence. Current-process API/model/operator/public-origin/trusted-proxy
configuration is absent; other terminals' settings remain unknown. At the
initial check the reserved Claude folder was absent. The next external step is identifying the existing
hosting account/project and approving a deployment arrangement, plus a
successful model-backed connection test. Overall launch remains incomplete.

Late arrival after the full battery: tools/launch_preflight/preflight.py now
exists (filesystem write time September 4, 23:47:31 Miami). No test file or
handoff.md was present when listed. The 499-test checkpoint predates this
arrival and does not verify the new CLI. Preserve Claude's reservation and
wait for its explicit handoff before integration. No live worker/process
handle has been confirmed; a new file alone is not a verified running wait.

## Claude verification handoff review (2026-09-05T03:41:33Z)

Claim: Codex coordinator, VERIFIED (handoff review and local rerun); files: this workboard and
docs/claude-next-task.md only. Reconcile the owner-pasted Claude report,
preserve its original results below, and rerun the local ops battery.

The reported 22 local HTTP probes and 495-test result are present in
Claude's workboard entry. Treat the probes as Claude-reported: this handoff
does not supply the consolidated probe script or raw run output for replay.
The earlier failures' cause is not established by passing reruns or growing
test counts. Request failing test IDs and sanitized tracebacks if available;
do not silently label them resolved concurrency defects.

The report's IN_PROGRESS proxy status is superseded by the locally VERIFIED
persistent-host result above the older entry. No host has been selected or
deployed, no successful live model request is established, and the local
offline exercise does not establish customer production use. Keep the
reserved Claude preflight task; do not rebuild the inquiry/proxy/backup kit.

Verification rule: checkpoint writers before a full-battery run and retain
failure details. This coordinator will make no implementation edits during
the run and will compare source hashes before/after; another worker's
checkpoint cannot be assumed from a report alone.

Result: independent `python scripts/ops_check.py` rerun PASS: 495 tests,
four platform skips, 41 subtests, 19 suites, all seven steps green. Hashes
of 96 source/configuration files matched before and after the run; this
does not establish the cause of Claude's earlier failures. API credentials
and model selection were cleared only in the test subprocess environment.
No live model call, real customer activity, deployment or Git write occurred.

Reconciled the newly supplied report and updated Claude's bounded handoff
with the completed proxy status and a request for replayable probe/failure
artifacts. The reserved preflight folder is still absent; no running Claude
job is inferred. The overall launch goal is not complete. Host selection,
authorization and a successful configured model test remain external steps.

## Launch dependency recheck (2026-09-05T03:38:08Z)

Second consecutive no-progress check, 2026-09-05T03:38:47Z: repo instructions,
HEAD, status and reserved folder rechecked. No Claude preflight or handoff
exists; runtime key/model/token/origin presence still false. Hosting account,
budget and deployment authorization remain unanswered. No confirmed running
job to wait on, no new code to review and no externally authorized launch
action. Only this audit note changed; goal remains active pending the next
dependency check, not complete. Do not infer a failed Claude process from
an absent folder, and do not start a duplicate worker.

Previous goal turn: PROGRESS (hosting/backup/readiness implementation,
independent reviews, 495-test full verification, North Pole naming and
Claude handoff). Current turn: no implementation progress; dependency and
runtime recheck only. HEAD and worktree remain unchanged apart from this
coordination note. No tools/launch_preflight directory exists yet; there is
no confirmed live Claude job handle to wait on or restart. Reservation stays
PLANNED and no work is taken from it.

This Codex runtime reports API key, model, operator token and public origin
all unconfigured (presence only checked, no secret values read or printed).
Port 8226 has no listener and fresh triage --status remains NOT STARTED.
Owner hosting account/budget and deployment authorization are still missing.
Do not infer that other private terminals are configured from this check.

Attempted an inert in-memory layout preview in the documented in-app browser;
navigation failed and the temporary tab stayed about:blank. Closed that tab.
No alternative server restart or browser-control mechanism was attempted.
Phone-size visual verification therefore remains pending, not passed.

First consecutive no-progress dependency audit after the prior progress
turn. Overall goal stays active, not complete. The next real action requires
owner hosting/API setup or a READY_FOR_REVIEW Claude artifact. Do not create
more checklists, duplicate tests or simulated production activity to fill the
wait. Stripe, phone voice/SMS and posting remain separately unfinished.

## North Pole team identity (2026-09-05)

User requests every agent belong to the North Pole theme. Claim: Codex
coordinator, READY_FOR_REVIEW (copy/tests complete; browser QA pending).
Files: docs/north-pole-agent-team.md (new),
tools/triage/triage.py and test_triage.py, tools/mrs_claus_office/intake.py,
tools/content/queue.py, tools/elves/outreach.py, tools/comms/adapter.py,
tools/web_inquiry/index.html, business/reservations/web_ui.py,
business/reservations/tests/test_web_ui.py,
business/reservations/openai_adapter.py and content_agent.py,
business/reservations/logistics_agent.py and reservation_agent.py.
Names, greetings and creative direction only; preserve machine actor IDs,
human approval, locked terms, real driving estimates and provider status.
Do not recast historical deployment documents as this new 2026 design.

Owner clarified exact agent names: Mrs. Claus (communications, warm female
EN/ES voice when connected), Santa Claus (content), Elf #1 bookings, Elf #2
logistics, Elf #3 outreach, Elf #4 monitoring. Future roles get sequential
elf numbers. Applied to role documentation, current UI labels and drafting
prompts/templates. Existing actor IDs and authority remain unchanged.

Claude handoff reserved by coordinator: PLANNED, tools/launch_preflight/*
(new), a read-only launch-readiness CLI. Read docs/claude-next-task.md before
starting. No edits to active coordinator/reviewer files or Git index.
Claude should return its exact suite path for coordinator registration;
scripts/ops_check.py stays coordinator-owned. Parent owns this workboard
until finishing the current verification; use the reserved folder's
handoff.md to return progress without racing workboard edits.

## Persistent-host preparation (2026-09-05)

Coordinator review result: proxy identity, authenticated storage readiness,
backup/restore and deployment Python/static contracts VERIFIED locally.
Wegener independently approved all three repaired readiness findings after
14 targeted tests. Jason independently approved backup/restore with 73 pass,
four platform skips, eleven extra probes and eight deployment checks.
Main inquiry/maintenance/deployment battery: 182 pass, four skips. Tests use
synthetic data only. Three file-symlink cases need Windows privilege; POSIX
permissions await Linux. No actual Linux/systemd/nginx/TLS/reboot/host-browser
verification has occurred. Templates are offline-first and uninstalled.

Readiness now checks a 16 MiB disk-space floor plus 64 KiB main-database
allocation, always rolled back. No lasting table, customer or audit event is
created. Malformed, non-object, invalid UTF-8 and deeply nested stored JSON
produce sanitized failures. This health probe is not a model/payment/channel
test, disk-capacity guarantee, delivered alert or production-use record.

Backup creates unique private files via SQLite online backup and restore
checks actual schema/counts/data in a new directory. systemd/nginx examples
include restart, limits and private health/backup timers. Off-host encrypted
copies, retention, disk/backup-age alerts and their delivery still require
the selected host/owner setup. Host account/budget question is unanswered.

North Pole copy and Claude handoff are saved. All agent machine IDs remain
unchanged; triage prompt version advanced to triage-v1.1.0 for the new
Mrs. Claus greeting. Focused triage tests pass. Final ops rerun: 495 tests
pass, four platform skips, 41 subtests, 19 suites and all seven checks PASS.
Current browser preview remains stopped and latest text/layout
changes are not re-verified in a real browser. Female voice is a recorded
requirement, not an active provider connection. Claude is reserved only
tools/launch_preflight/*; its handoff instructions are docs/claude-next-task.md.

All review workers are now finished. No commits, staging, pushes, public
deployment, purchases, API requests or customer sends were performed.
This goal turn made concrete progress; overall launch remains active and
requires actual host/API authorization and verification, not further fake
activity or looping on unchanged missing account information.

Previous goal turn made progress: independently verified overnight and
inquiry review/privacy fixes, repaired runbook commands and test-count
drift. Current HEAD/worktree rechecked; all earlier uncommitted work remains.

Claim | owner: Codex coordinator | status: IN_PROGRESS | files:
tools/web_inquiry/server.py, tools/web_inquiry/test_web_inquiry.py,
tools/web_inquiry/README.md, deploy/inquiry/* (new),
scripts/ops_check.py (suite registration only), docs/tonight-launch-checklist.md,
this workboard. Implement explicit trusted-proxy client identity without
trusting arbitrary visitor headers; retain client and global abuse limits.
Prepare private persistent-host process, proxy and monitoring configuration,
but do not install services, expose a port, deploy or change provider accounts.

Delegated file reservation: tools/web_inquiry/maintenance.py and
tools/web_inquiry/test_maintenance.py (new) for a bounded backup/restore
worker. No other worker may edit these until review. Parent owns workboard.
Worker uses only synthetic temporary data, never existing customer state.

Maintenance worker Lagrange delivered READY_FOR_REVIEW: 73 pass, four
Windows/platform skips. Files unchanged during Jason's independent review.
Proxy review by Wegener passed identity/limit probes but requests changes
to readiness: a zero-row write misses exhausted storage, and valid non-object
JSON/invalid UTF-8 can escape sanitized errors. Coordinator accepts both,
retains server/test ownership and is adding meaningful bounded storage
probes plus malformed-record regressions. Deployment templates are offline
demo only, uninstalled; no preview, host, API or production state changed.

Docker CLI is present but its Linux engine pipe is absent. No daemon or
preview process was restarted. Hosting account, budget, authorization,
API availability, Stripe and phone integrations still need owner input.

## Tonight launch continuation (2026-09-05)

Final local result at 03:13Z: inquiry fixes VERIFIED by Codex coordinator
after Noether's independent approval. Reviewer reran 56 pytest cases,
including five Node client cases, plus concurrent-action, restart, delayed
JSON, pagination/logout and changed-selection probes; file hashes unchanged.
Full coordinator ops_check: 368 tests plus 41 subtests across 17 suites,
all seven steps PASS. Both reviewers worked only on synthetic state.
The overnight, quote-preservation, hard-fact and inquiry concurrency/privacy
fixes are verified locally; none are committed or deployed by this turn.

Documentation drift is closed: preflight now has nine warnings (missing
evidence/placeholders only), with no obsolete test-count warnings. Runbook
route commands parse cleanly. docs/tonight-launch-checklist.md contains the
owner inputs and distinguishes the initial assisted AI workflow from later
Stripe, phone, automatic availability, delivery, posting and outreach work.
Public-site fetch could not be completed by the web tool; no live-site
verification or deployment is inferred from local repository checks.

Next available engineering work: resolve the documented shared proxy
throttle with explicit trusted-proxy configuration and tests, prepare the
persistent host process/backup/monitoring setup, and verify hosted synthetic
EN/ES intake before public routing. Obtain owner hosting account/budget and
deployment authorization; configure the API privately and verify a real
model response. Stripe/phone/social accounts remain separate unfinished
integrations. Actual customer operation and 15-day evidence remain pending.
The overall launch goal stays active, not complete. All review workers are
finished. Existing unrelated files, local demo data and Git index preserved.

Inquiry review fixes READY_FOR_REVIEW: approval/rejection/manual-send
requests carry a SHA-256 revision of the exact displayed saved record,
checked inside the same SQLite write transaction as the state change.
Stale or missing revisions are refused; current snapshots still run the
existing policy and language/real-use checks. No schema migration needed.
Client requests are abortable and session-tagged. Logout clears private
state, discards old responses and does not resurrect another login's queue;
overlapping refreshes cannot replace newer displayed state. Controls send
the displayed inquiry ID/revision, not a mutable selection after rendering.

Six new backend revision cases failed before the fix. Four browser-client
logic cases failed before the fix. Current focused result: 56 pytest cases
pass, including the integrated Node harness with five synthetic DOM/fetch
cases. Tests also cover stale HTTP approval and post-approval reject/send
snapshots. Node.js 18+ is a test-only prerequisite; the service remains
Python stdlib-only. No real browser preview restart occurred; prior visual
layout QA remains historical. Client tests are a DOM/fetch harness, not a
claim of a new live-browser run. Full ops verification and independent
re-review are running. Keep these implementation files unchanged until review.

Public proxy rate-limit bottleneck remains documented and unsolved in this
slice; it will need explicit trusted-proxy configuration and tests. The
local service is not yet publicly hosted or authorized for public intake.

Inquiry review received: Noether requests changes for stale-tab approval
of an unseen regenerated draft and delayed refresh restoring customer data
after logout. Both independently reproduced. Current local suite: 46 pass.
Codex coordinator accepts the findings and claims tools/web_inquiry/server.py,
app.js, test_web_inquiry.py, README.md, client-tests.cjs (new) and this board
for fixes and regression coverage, status IN_PROGRESS. Existing uncommitted
inquiry implementation is preserved. The shared public throttle behind a
single proxy is a separate known hosting prerequisite, not solved by adding
proxy-only limits. No public deployment or preview restart is authorized.

Documentation drift claim | owner: Codex coordinator | status: IN_PROGRESS |
files: docs/OPN-SUBMISSION.md, docs/production-deployment-record.md,
docs/evidence-index.md, docs/gap-report.md, docs/evidence-intake.md,
docs/demo-runbook.md. All six files are clean before edit. Latest preflight
found obsolete numeric test counts; replace duplicated current-count claims
with runnable checks and the dated verification record. Do not fill missing
production model, operator evidence, customer counts or launch dates.

Coordinator result: overnight routing VERIFIED, not committed. Independent
reviewer Zeno approved all four changed code/test files with 39 checked-in
tests plus 41 subtests (excluding the filesystem-writing synthetic season
walkthrough), six additional probes plus 17 subtests, unchanged file hashes,
and no network/state writes. Probes included the actual health caller,
leap-day boundaries, date-report filtering, and cancellation recovery.
Coordinator full ops_check passed 358 tests plus 41 subtests, all seven
operational checks. Existing quote and hard-fact changes remain VERIFIED.

Operator runbook commands now parse in PowerShell with zero errors and no
stray carriage returns. The standalone check must receive both dates in the
same input file; omitted visits cannot be detected. Querying dates in the
reservation agent does not partition the source schedule. No public launch,
commit, push, payment, message, or production record was performed.

Fresh runtime checks: triage --status is NOT STARTED, and no listener exists
on port 8226. Owner hosting account/budget clarification has been requested.
Independent reviewer Noether (01a06f86-1fa6-7270-96b6-0d7dd1bfc643) is reviewing
the uncommitted local inquiry workflow and persistent-host prerequisites;
those files remain unchanged while that review is pending.

Additional documentation claim: docs/seasonal-ops-runbook.md | owner: Codex
coordinator | status: IN_PROGRESS. File is clean before edit. Repair the
broken route command escape sequences, document multi-date route input,
and replace the obsolete partial suite list with the actual full check.

Latest full verification after overnight changes: 358 tests plus 41
subtests across 17 suites; all seven ops_check steps PASS. Independent
overnight review and separate local-inquiry security review are pending.

Overnight implementation is READY_FOR_REVIEW: calendar-minute comparisons
now include cross-date/year-boundary overlaps and travel/setup buffers.
All active reservation logistics are refreshed together; querying another
date cannot clear an existing overnight conflict. Invalid active scheduling
facts block new approvals until repaired because unknown duration/date/setup
cannot safely be bounded to a day; valid confirmations remain locked.
The returned date report includes touching legs and invalid-input findings.
Standalone route lists now require recorded travel between successive dates,
not an implicit midnight reset. An unknown next-day drive requires review;
normal next-day visits with adequate known travel still pass. Numeric boolean
inputs are refused and invalid facts never enter route arithmetic.

Focused verification: 40 tests plus 41 subtests passed across routes and
season integration. Initial standalone regressions produced 11 failures;
initial reservation regressions produced 17 failures. Reverse-order test
fixtures were corrected to confirm the first booking before creating the
second, matching real intake and preserving the existing pending-hold rule.
The prior full run (standalone change only) passed 349 plus 26 subtests;
the new whole-tree ops check is running and supersedes that earlier result.
No code changes while the independent overnight review is underway.

Claim: Close overnight routing and prepare the owner launch handoff | owner:
Codex coordinator | status: IN_PROGRESS | files: this workboard,
docs/tonight-launch-checklist.md (new), tools/routes/route_check.py,
tools/routes/test_routes.py. The historical routes claim is committed;
the current files are clean and have been read before this follow-up.
business/reservations/logistics_agent.py and tools/test_integration_season.py
will be claimed only after independent review of their current dirty guard.

Independent read-only reviewer Zeno (01a06f81-3306-7190-a3f5-a9c94a897297)
is reviewing that guard and the same-package quote-preservation delta.
No provider calls, customer state changes, Git writes, public deployment,
or model-backed production activity are part of these synthetic checks.

Current launch configuration: this process has no OpenAI key/model or
operator token; the configured Stripe Payment Link is empty. vercel.json
contains static-site settings, not the persistent inquiry backend. The
local Python inquiry server binds only to loopback. A local development
loop is not an always-on host. See the new checklist for owner decisions.


## Overnight routing review (2026-09-05T02:41Z heartbeat)

Continuation review: independent reviewer Zeno APPROVED the pre-existing
hard-fact guard and quote-preservation deltas against 3fc83df. Evidence:
13 route tests with 14 malformed-input subcases, seven new quote cases
plus two controls, and five additional probes with 32 malformed-value
subcases. No reviewed files changed during review. Codex coordinator
accepts this review and marks those two earlier deltas VERIFIED (not
committed). Their implementation is preserved. Codex now claims
business/reservations/logistics_agent.py and tools/test_integration_season.py
for the separate overnight fix, status IN_PROGRESS.

Claim: Verify date-boundary reservation and travel checks without editing
pending implementations | owner: Codex | status: READY_FOR_REVIEW | files:
this workboard only. business/reservations/logistics_agent.py and
tools/test_integration_season.py remain dirty and READY_FOR_REVIEW from
the hard-fact guard. Do not change them before coordinator review. All
probes are synthetic, in memory, with store.append_event mocked; no
customer records, payment records, or production evidence are written.

Finding: cross-midnight overlap and travel checks are missing. The
reservation checker filters peers by exact date at
business/reservations/logistics_agent.py:65. The standalone checker groups
visits by date at tools/routes/route_check.py:114-118. Neither compares
adjacent dates. This is separate from the same-date hard-fact fix, which
remains untouched and pending review.

Reproductions used standard 60-minute synthetic Doral visits, valid
addresses/guest counts, and mocked operator verification of the exact
50% deposit. The following invalid pairs both reached confirmed with
logistics=ok: Dec 24 23:30 / Dec 25 00:15 (15-minute overlap), the same
pair approved in reverse order, Dec 24 23:00 / Dec 25 00:05 (5-minute gap
versus 10-minute estimated same-zone drive plus 5-minute buffer), and
Dec 31 23:30 / Jan 1 00:15 (year-boundary overlap). Feasible overnight
23:00 / 01:00 and separate-day 15:00 / 15:00 controls both confirmed.
The standalone route checker also returned OK with zero findings for
the overlap and 5-minute travel gap when given explicit 10-minute travel
and zero setup; its feasible overnight control returned OK as expected.

Verification: existing route/integration suites passed 25 tests plus
14 subtests. Full ops_check passed all 7 steps with 343 tests plus
14 subtests across 17 suites. These passing suites do not cover the
newly reproduced overnight gap. Slot validation, page review, tracker
privacy, OPN preflight and diff check passed. Only this workboard changed;
no code/test implementation, customer state, Git index, provider account,
preview process, or production evidence was altered.

Repair handoff: first obtain review of the existing dirty logistics and
integration-test changes. Then add failing overnight regressions and
compare actual date-time intervals across date boundaries, including
travel/setup/safety buffers, both approval orders, year rollover,
canceled peers, and valid separate-day controls. Preserve same-date
pairwise protection and locked confirmations. Until that fix is verified,
do not rely on either checker to approve overnight schedules: the
operator must inspect both dates and travel buffers manually. This is
not a new machine-enforced overnight block.

```json
{"at":"2026-09-05T02:43:55Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["docs/santa-agent-workboard.md"],"tests":{"reservation_probes":"4 invalid cross-date scenarios wrongly confirmed; 2 feasible controls confirmed","standalone_route_probes":"2 invalid cross-date routes returned OK with zero findings; 1 feasible control OK","existing_route_integration":"25 passed plus 14 subtests","ops_check":"343 passed plus 14 subtests across 17 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","tracker_privacy":"0 warnings","opn_preflight":"exit 0, not final qualification","git_diff_check":"exit 0"},"blockers":["affected logistics and integration-test files have unreviewed dirty changes; no implementation edits this cycle","overnight overlap/travel checks remain unfixed","Stripe Payment Link remains absent; prior API/hosting/account/evidence prerequisites remain"],"next":"Coordinator reviews the existing hard-fact guard before another edit. Add and fix cross-midnight/year-boundary regression cases using full date-time intervals and route buffers. Require manual cross-date schedule review until verified. No commit, push, deployment, charge, customer send or production activity was performed."}
```

## Scheduling hard-fact guard (2026-09-05T02:11Z heartbeat)

Claim: Reject malformed scheduling facts before route approval | owner:
Codex | status: READY_FOR_REVIEW | files:
business/reservations/logistics_agent.py, tools/test_integration_season.py,
this workboard. Both implementation/test files are clean; their earlier
pairwise-conflict change was reviewed by Claude and committed. Preserve
all current unreviewed inquiry, triage, reservation-agent, and HTTP-test
changes. No Git index writes, commits, pushes, API calls, or deployment.

Reproduction: using in-memory synthetic records and a mocked event writer,
a standard visit at 15:00 with duration_min=-60 and another at 15:00 with
duration_min=60 both reached confirmed with logistics=ok. Scope: reject
invalid duration/setup/time/date facts conservatively during route review,
without changing prices, payment rules, or existing locked bookings.

Result: logistics now rejects nonpositive/non-integer durations, invalid
setup values, noncanonical/invalid dates, and malformed start times before
route arithmetic. Invalid scheduled holds no longer disappear from the
day check. New approvals on that date remain blocked until those facts
are corrected; valid existing confirmations remain locked. The returned
route report includes explicit invalid_schedule findings as well as
pairwise checks, so the CLI does not hide an invalid solo visit behind
an empty report. Canceled entries remain excluded. These are still
estimate-based route checks, not live traffic or a complete route planner.

Added seven synthetic regressions with fourteen malformed-input subcases.
The first selected pre-fix run failed both negative-duration/setup cases
and all fourteen malformed-input subcases (16 failures); the three
selected controls passed. Final focused integration run: 14 passed plus
14 subtests. Full ops_check: 343 passed plus 14 subtests across 17 suites;
all 7 operational steps PASS, including slot validation, page review,
tracker privacy, OPN preflight, and diff check. All event writers in the
new reservation probes were mocked; no booking or payment record was
written. Existing dirty/claimed files are preserved, and no Git index
change, commit, push, provider action, or preview restart was attempted.

The Stripe Payment Link is still empty. API 429 resolution, hosting and
public launch, mobile voice/SMS setup, owner verification, and genuine
operating evidence remain outside this synthetic test result. Next:
independently review this guard and its tests; separately check the
existing date-boundary behavior before accepting overnight schedules.

```json
{"at":"2026-09-05T02:19:04Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/logistics_agent.py","tools/test_integration_season.py","docs/santa-agent-workboard.md"],"tests":{"before":"16 failures including 14 malformed-input subcases; 3 selected controls passed","integration":"14 passed plus 14 subtests","ops_check":"343 passed plus 14 subtests across 17 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","tracker_privacy":"0 warnings","opn_preflight":"exit 0; not final qualification","git_diff_check":"exit 0"},"blockers":["independent review before commit","public Stripe Payment Link absent","API HTTP 429 has no verified resolution","public hosting/customer-channel connections pending"],"next":"Review the logistics hard-fact guard. Keep all uncommitted inquiry, booking and triage changes intact. Check date-boundary routing separately before overnight bookings; no public launch, live activity, send, charge, commit or push was performed."}
```

## Prior crash recovery check

After the operator reported that Codex crashed, all six tools/web_inquiry
files and the prior uncommitted changes were present. The private demo
SQLite database and screenshots also remained on disk. No process was
listening on port 8226. A fresh run of the inquiry suite passed all 46
tests. The execution policy rejected the attempted background restart;
no alternate restart was attempted, and the preview is still stopped.
The earlier running-preview statement below is historical. Resume with
the documented local startup procedure, preserving the existing private
demo directory when reviewing the saved synthetic inquiry. No data was
deleted, no credentials or accounts changed, and no API call was made.

## Codex continuation after Claude credit pause (2026-09-05)

The operator reports that Claude is out of credits. At inspection, the
claimed tools/web_inquiry directory does not yet exist and
scripts/ops_check.py is unchanged. Codex takes over that unfinished slice;
the historical Claude claim below is paused/superseded for these files.
No other unfinished edits will be overwritten.

Claim: Local website inquiry and authenticated operator review | owner:
Codex | status: READY_FOR_REVIEW | files: tools/web_inquiry/* (new),
scripts/ops_check.py (suite registration only), this workboard. Reuse the
existing triage engine and six validation gates. Persist a private inquiry
queue outside Git, not a competing booking database. Public submissions
must not call the paid API; generating a draft is authenticated and
operator-triggered. Separate synthetic operation from explicitly attested
real inquiries. No auto-send, booking/payment mutation, public deployment,
account changes, invented Stripe links, or production-start claims.

Result: implemented the local form and authenticated operator review in
tools/web_inquiry/server.py, index.html, app.css, and app.js. The form
durably stores requests without calling the model. An authenticated
operator generates bilingual drafts through the existing triage engine,
reviews/rejects/regenerates, chooses the reply language, and approves.
Sending remains manual; a separate explicit action records an operator's
attestation that a reply was sent. Nothing transmits to customer channels.
The form is not a booking confirmation and does not mutate reservations,
availability, deposits, or the locked price list.

Private SQLite storage is outside Git with single-process ownership and
timestamped events. Restarted draft work becomes failed, not approved or
sent. Added duplicate-submission handling, exact Host/Origin checks,
operator authentication, request limits, input/encoding validation,
operator-only model calls, version/gate rechecks, and older-request pages.
Default demo mode cannot mark activity as real; even live-enabled mode
requires a separate per-inquiry operator attestation. Exports are unique
metadata snapshots in this queue's private evidence directory, never
append operations on the CLI's existing JSONL. They do not establish
production duration or qualification by themselves.

Verification: 46 new synthetic tests passed; full ops_check.py passed all
7 steps with 336 tests across 17 suites. Browser QA exercised Spanish
submission, operator sign-in, offline drafting, Spanish-first display and
selection, approval-without-send, metadata export, and sign-out. Form and
operator layouts were checked at 1440px desktop and 390px mobile, with an
additional 320px operator check: no horizontal overflow; the real Santa
image loaded. Test server error log was empty. Browser QA exported only
synthetic-log.jsonl; no production log was created. No API credentials
were inherited, no API charges incurred, and no customer messages sent.

Local demo: http://127.0.0.1:8226/ (operator route /operator). It is a
hidden local Python preview process, PID 33852 at verification, using a
temporary synthetic-only data directory and an in-memory private token.
It is not public hosting and does not survive shutdown. Use the startup
instructions in tools/web_inquiry/README.md with your own private token
and appropriate data directory for a fresh operator session. Do not use
the test-suite token or reuse demo records as customer activity.

QA artifacts, all synthetic, are stored outside Git in a private local temp
directory (redacted 2026-09-05 before any push: inquiry-desktop.png,
inquiry-mobile.png, operator-desktop.png, operator-mobile.png,
operator-mobile-320.png). The README documents local
startup, private storage/backup, exact manual fallback, snapshot evidence,
and the HTTPS/proxy/persistent-host requirements before a public release.

Unchanged blockers: no public hosting/deployment was authorized or
performed for this slice; the reported OpenAI HTTP 429 has no verified
resolution; Stripe verification/payment link and mobile voice/SMS remain
unconnected. The old billing login tab was left untouched. No commit,
push, Git index change, or external account change was made. All other
workers' changes remain intact. This completes the local-build goal,
not the customer deployment or OPN application requirements.

```json
{"at":"2026-09-05T01:26:00Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["tools/web_inquiry/server.py","tools/web_inquiry/index.html","tools/web_inquiry/app.css","tools/web_inquiry/app.js","tools/web_inquiry/test_web_inquiry.py","tools/web_inquiry/README.md","scripts/ops_check.py","docs/santa-agent-workboard.md"],"tests":{"focused":"46 passed; synthetic and credential-free","ops_check":"336 passed across 17 suites; 7/7 steps PASS","browser":"Spanish intake, operator authentication, offline bilingual draft, approval without send, export and sign-out; desktop/mobile no overflow; image loaded","evidence":"synthetic snapshot only; no production log from browser QA"},"next":"Independently review the local inquiry slice. Choose and authorize a persistent HTTPS deployment, configure provider secrets privately, resolve the API 429 and verify a synthetic model-backed call, then obtain owner authorization before routing real website inquiries. Preserve existing uncommitted booking/triage fixes; no automatic commits or deployment."}
```

## Preserve existing quotes on repeated package updates (2026-09-05 heartbeat)

Claim: Close the same-package quote-reset finding from Claude's booking
review | owner: Codex | status: READY_FOR_REVIEW | files:
business/reservations/reservation_agent.py,
business/reservations/tests/test_web_ui.py, this workboard. Both code/test
files are clean and their previous changes were reviewed and committed.
Claude's active tools/web_inquiry/* and scripts/ops_check.py claims are
untouched, as is the reviewed but uncommitted triage diagnostic delta.

Scope: repeating an unchanged package must preserve the existing quote,
deposit, approval, and booking details. Actual package changes before
confirmation must still select the locked package rate. Add synthetic
regressions proving that an unchanged-package update cannot reduce the
50% deposit requirement. No rate changes, real customer data, API calls,
account actions, Git index writes, commits, pushes, or deployment.

Result: the seven new HTTP regressions initially produced six failures
and one passing control. Repeating the package lowered an existing quote
in five lifecycle states; a previously refused short deposit then passed.
The fix only recalculates the quote when the package actually changes.
All seven regressions now pass, including the control proving a real
pre-confirmation package change still uses the locked rate. Existing
deposit verification, route gates, bilingual content, and rate cards are
unchanged. All test records and events were synthetic and redirected to
temporary directories; no live API configuration was inherited by tests.

```json
{"at":"2026-09-05T01:09:23Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/reservation_agent.py","business/reservations/tests/test_web_ui.py","docs/santa-agent-workboard.md"],"tests":{"before_fix":"6 failed, 1 passed on new HTTP regression subset","after_fix":"7 passed on new HTTP regression subset","ops_check":"290 passed across all 16 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","tracker_privacy":"0 warnings","opn_preflight":"exit 0 via ops_check; not final qualification","git_diff_check":"exit 0"},"blockers":["Claude independent review before commit","public Stripe Payment Link absent; owner verification pending","OpenAI HTTP 429 unresolved; no verified live AI run"],"next":"Claude reviews the unchanged-package quote guard and regression tests. Continue the separately claimed website inquiry slice. Preserve the local-only changes; do not commit, push, deploy, or change external accounts from the heartbeat."}
```

Operator setup update: Stripe activation is paused pending owner-supplied
verification information. No public Payment Link is available. The public
number is a T-Mobile mobile line; no number transfer, forwarding, SMS
provider connection, or recording has been authorized or enabled. Keep
setup dependencies separate from simulated tests and production evidence.

## Web inquiry workflow slice (claude-fable, 2026-09-05T01:05Z)

Result: claude-fable | status: VERIFIED (review of the 2026-09-05T00:35Z
diagnostic extension) | files: none - review only | tests: 51 triage passed
at the current dirty tree | note: five official 429 codes added with static
hints only, no raw server text, exact-hint regression assertions - APPROVED.
Leaving Codex's uncommitted delta in place per its heartbeat; the actual 429
cause still needs the operator's billing view or a successful configured test.

Claim: Website inquiry -> operator review workflow (user directive) | owner:
claude-fable | started: 2026-09-05 01:05 | files: tools/web_inquiry/* (NEW:
server.py, test_web_inquiry.py), scripts/ops_check.py (add the new suite to
the fail-closed routine list only), this workboard | NOT touching:
tools/triage/triage.py + test_triage.py (Codex's uncommitted diagnostic delta
stays), business/reservations/* (no competing booking database - the inquiry
lane reads/writes only the triage logs outside Git), public HTML (wiring
documented, not deployed) | test: python -m pytest tools/web_inquiry/test_web_inquiry.py -q + full suite + ops_check

Result: claude-fable (2026-09-05T02:10Z) | status: VERIFIED (independent live
end-to-end verification of the built service; implementation files untouched -
they remain under the Codex IN_PROGRESS trusted-proxy claim) | files: none |
tests: focused suites 157 passed 4 skipped; live probe battery on
127.0.0.1:8226 in --offline demo mode with scratchpad state, 22 cases ALL
PASSED: EN + ES inquiries received; exact duplicate idempotent (same
request_id, duplicate:true); missing consent -> 400 bilingual error with NO
success shape; oversized message -> 400; 6th public POST -> 429 with
Retry-After (5/5min in-memory window confirmed empirically, resets on
restart); wrong Origin -> 403; operator routes 401 without/with wrong token;
queue lists; draft in offline mode correctly labeled offline-rules-v1 +
fallback_used with es/en detection and BOTH drafts retained, 6/6 gates PASS;
stale-revision approve -> 409; approve -> 200; send with pre-approval
revision -> 409 (snapshot design working); send without sent_manually
confirmation -> 409; send with fresh revision + confirmation -> 200;
real_customer attestation in demo mode -> 400 refused. Final full battery:
ops_check ALL 7 STEPS PASS, 495 tests + 41 subtests across 19 suites.
NOTE for coordinator: two earlier ops_check runs showed 7-then-1 transient
test failures that never reproduced in direct reruns - the tree was being
edited by concurrent workers mid-collection (test counts grew 484->495
across four runs in ~10 minutes). Recommend a quiet-tree rule: full-battery
verification runs happen with no concurrent writers, or workers checkpoint
before a coordinator battery. | blockers: NONE for the local slice; hosting,
trusted-proxy limits (Codex IN_PROGRESS), API 429 cause, and owner
authorizations remain the deployment path.

## API error investigation (2026-09-05T00:57Z)

Claim: Investigate the operator's unresolved HTTP 429 | owner: Codex |
status: READY_FOR_REVIEW | files: this workboard only. Read-only inspection
of triage code and configuration; preserve the diagnostic implementation
already awaiting review below. No Git index changes, API requests, or
account changes.

Verified: all 51 triage tests pass with API credentials unset in the test
subprocess, including mocked HTTP failures and safe offline fallback.
The Codex process, User environment, and Machine environment have no
OPENAI_API_KEY configured (presence checks only; no secret values read or
printed). This does not contradict the key being set in the operator's
separate PowerShell session. No attempt was made to extract that session's
credentials. The most recent supplied live result remains HTTP 429 with an
unclassified category, not a successful model response.

Opened the official API billing overview in the available in-app browser;
it redirects to sign-in. No other connected browser was available. Left
the sign-in tab for operator handoff. Next: operator signs in to inspect
available API credit and applicable limits, or reports the displayed
balance/status without credentials or payment details. Do not infer the
cause from HTTP 429 alone, purchase credit, change limits, or call this
error fixed. A successful configured test still needs verification.

No code changes or production records were made in this investigation.

## Current diagnostic follow-up (2026-09-05T00:35Z)

Claim: Recognize current official HTTP 429 categories safely | owner: Codex |
status: READY_FOR_REVIEW | files: tools/triage/triage.py (diagnostic map only),
tools/triage/test_triage.py (existing mocked-failure regression) | scope:
add the documented credit/spend/usage/slow-down codes without exposing raw
error text, changing logs, adjusting credentials or limits, or making API
requests. The files were clean after Claude committed the triage follow-up
as 49d593e; model/payment guards and prices remain untouched. Verify with
mocked errors, triage tests, and the full ops-check battery. No Git writes
or push from this heartbeat; leave the delta for review.

Result: added static diagnostics for the five official credit/spend/usage/
slow-down codes listed below. Extended the existing fallback regression to
23 simulated failures, asserting exact categories, guidance, fallback, and
absence of secret/customer text. No raw server text, live calls, account
changes, or production records. Actual cause of the operator's 429 remains
unknown until a configured test or the billing/limits view identifies it.

Independent review of Claude's 49d593e model-path fixes: the exact prior
family-party and missing-payment-link probes are now refused with
MODEL_CATEGORY_AMBIGUOUS and MODEL_OUTPUT_VALIDATION_FAIL, respectively;
both fall back without approval/send. Those specific findings are VERIFIED.
The review PR branch is remotely at 61d0f14 (main still 882433d); this new
diagnostic extension is local only and is not included in that PR yet.

```json
{"at":"2026-09-05T00:38:29Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["tools/triage/triage.py","tools/triage/test_triage.py","docs/santa-agent-workboard.md"],"tests":{"triage":"51 passed, including 23 mocked failure cases","independent_model_probes":"both previous bypasses refused; no approvals or sends","ops_check":"283 passed across 16 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","opn_preflight":"exit 0 via ops_check, not final approval","tracker_privacy":"0 warnings","git_diff_check":"exit 0"},"blockers":["review local diagnostic delta before committing","operator API billing/limit cause not yet known","no verified production launch from this heartbeat"],"next":"Claude reviews the isolated diagnostic extension. Operator checks API credit/limits privately. Keep draft PR #1 unmerged until the intended release is reviewed; no index changes, commit, push, or live API calls this cycle."}
```

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

Result: claude-fable (2026-09-05T00:45Z) | status: COMMITTED to the PR branch |
PR #1 is now COMPLETE: delta commit 61d0f14 pushed to
codex/santa-checkpoint-2026-09-04 (8a184bf..61d0f14) via commit-tree - no
branch switch, stage, or merge touched the shared checkout or the Codex
worktree. The delta closes the model-output finding (validators payment gate
takes pricing; 3 mocked-model negative tests; final board state). Verified at
this exact tree before push: 283 tests, ops_check 7/7 PASS. Claude's granular
history is preserved locally on santa-ops-hardening-2026-09-04 (3fc83df).
The shared checkout now sits on that branch with a clean tree (only
Claude outputs/ and _to_delete/ untracked, excluded by design). PR #1 stays a
draft as Codex opened it - the operator flips it ready when the coordinator
review concludes. gh CLI is not installed on this machine; PR state per the
Codex record above.

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
