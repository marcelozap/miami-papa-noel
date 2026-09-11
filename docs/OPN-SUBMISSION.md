# OpenAI Partner Network — Submission

**Applicant:** Marcelo Zapata / XIV
**Deployment:** Miami Papa Noel — AI-assisted bilingual inquiry triage
**Date:** 2026-08-29
**Last updated:** 2026-09-10 America/New_York (2026-09-11 UTC).
**Status:** DRAFT PREPARATION; NOT READY FOR FINAL RESUBMISSION.

The current answers are in `docs/opn-form-answers.md`. A successful owner-run
synthetic check is recorded separately in `docs/model-check-2026-09-10.md`;
it is not a production record. Read-only status still reports NOT STARTED.
No application submission, publication or new paid call occurred in this pass.

---

## Summary

Miami Papa Noel is a bilingual seasonal service business in Miami-Doral,
operating since 2017 per the owner's account [MISSING EVIDENCE: no dated
artifact before 2022-12-24], with a public booking site at `miamipapanoel.com`
and a documented role-based operations workflow. It runs under XIV, the
operator's business. Miami Papa Noel is a family business with distinct
principals: Walter Zapata owns and operates the Santa visit service; Marcelo
Zapata (XIV) designed, built, and operates the AI workflow. **It is not an
arms-length external enterprise customer**, and the packet says so plainly.

The role-based workflow operated during the 2025 Christmas season — inquiries,
bilingual drafting, booking coordination, outreach, payment receipt tracking,
logistics, and follow-up — per the operator attestation at
`docs/operator-attestation-2025-season.md`. Supporting artifacts for that season
are being assembled and are labeled as such throughout.

**What is being prepared for review is the 2026 operator-assisted workflow:**
a runnable bilingual inquiry tool with human approval and manual sending.
It is not yet an active customer AI deployment. The documented evidence
window starts at the send timestamp of the first valid genuine,
model-backed, reviewed-and-sent record; fallback, unsent and synthetic records
do not start it (`tools/triage/production_evidence.py`). Actual launch,
operating duration and outcomes must be supported by real records, not inferred
from that timer or the successful model check. Final acceptance belongs to OPN.

---

## What is implemented

The tool at `tools/triage/triage.py`. Run the deterministic path with:

```powershell
Set-Location 'C:\XIV\santa'
$env:MPN_API_DAILY_CALL_CAP = '0'
python tools\triage\triage.py --demo
```

With the cap explicitly zero, no model request is dispatched. Enabling model
drafting separately requires a key, exact model, positive call allowance and
valid private cost policy. Each generated draft may then request the API;
`--demo` contains four inquiries, not one paid check. Errors or rejected output
fall back to local rules with explicit provenance. Demo logs are synthetic.

For each inquiry it:

- detects English or Spanish
- extracts requested date, service category, location, and contact status
- identifies missing information, and never guesses a date from a bare month
- flags schedule and capacity risk against the season's first-to-fill dates
- drafts a short reply in **both** English and Spanish
- quotes only from a locked, versioned price list
- states the official deposit terms (Zelle; a Stripe Payment Link rail
  was adopted 2026-08-30 and activates once the operator creates the link)
- writes a structured log line

**It cannot send anything.** There is no network egress to a customer channel.
The operator types `APPROVE`, then copies the draft into the channel by hand.

### Enforced safety gates

Six draft-validation gates (all software-enforced, applied to deterministic
AND model output), each with negative tests proving it blocks rather than
warns:

| Gate | Blocks |
|---|---|
| Pricing | Any figure outside the locked list `2026-08-28.1` |
| Bilingual parity | EN and ES stating different prices; an empty draft |
| Missing information | Required fields absent with no question asked |
| Unsafe confirmation | "confirmed", "booked", "deposit received", "reservado", "depósito recibido" — accent-insensitive |
| Insurance claim | Any insurance language while the policy is unverified |
| Payment method | Venmo, Cash App, Square, PayPal, card, Apple Pay, wire, Zinli; and any payment-link promise while no real buy.stripe.com link is configured |

The draft gates reject detected booking/payment-confirmation language, and
the tool has no booking or payment mutation path. A human still reviews every
reply and verifies the required deposit before confirming a booking.

---

## What is manual

By design, and documented in `tools/triage/README.md`:

- Sending every message
- Reading the slot board and deciding availability
- Verifying the Zelle deposit and confirming the booking
- Route and logistics planning
- Event execution
- Follow-up, referral, and review requests

## What is designed but not built

Software support for the Scout, Dispatcher, and Bookkeeper roles defined in
`business/AGENT-ROLES.md`. Each has a documented procedure; none has a running
component. The Concierge role is the one now tool-assisted.

## What is planned

Automated analytics over the production log, and prompt-regression testing
against real inquiry samples once enough have accumulated.

---

## Requirement responses

| Requirement | Response |
|---|---|
| **Active customer AI deployment** | NOT STARTED; software and a synthetic check are not active customer operation |
| **Launch date / status** | `[TO FILL]` — Launch date = the first real inquiry record (never backdated); the 15-day evidence window is measured from the send timestamp of the first valid real, model-backed, reviewed-and-sent record - fallback or unsent records never start it (shared predicate: `tools/triage/production_evidence.py`) |
| **Operational owner** | **Marcelo Zapata — built and operated.** Sole operator and sole committer in the repository history |
| **Live AI functionality** | Structured extraction and bilingual drafting passed an owner-run synthetic check; no current production AI functionality is asserted |
| **Concrete outcome** | `[TO FILL]` — supported real inquiry outcome and counts. Time saved or customer first-response time require additional baseline/arrival evidence |
| **Production model** | `[TO FILL]` — written verbatim only after a configured model produces a validated draft. The default remains `offline-rules-v1` with `fallback_used: true` |
| **How components work together** | `docs/agent-workflow-architecture.md` — state graph with per-step build state |
| **Testing and release approval** | Passing synthetic regression tests; dated results in `docs/santa-agent-workboard.md`; `docs/release-checklist.md`; local submission preflight in `scripts/validate_opn_submission.py`. Single-operator approval, stated plainly |
| **Production monitoring** | Logging layer built and tested; `tools/triage/log-schema.md` |
| **Failure handling** | Automatic fallback to deterministic mode; full manual procedure if the tool is unavailable |
| **≥15 days production** | **Not yet met.** Real production records, model/outcome fields, external evidence, and elapsed time remain to be collected |

---

## Verification a reviewer can run

NOTE (2026-09-10): this working tree contains uncommitted changes on top of
c14b896. A clone at that commit does not include this draft's latest changes.
Identify the eventual reviewed release before claiming reproducibility.
The following commands do not authorize a push or deployment.

```powershell
git clone https://github.com/marcelozap/miami-papa-noel
cd miami-papa-noel
$env:MPN_API_DAILY_CALL_CAP = '0'
$env:MPN_CHAT_ALLOW_MODEL = '0'
$env:OPENAI_API_KEY = ''
python -m pytest tools\triage\test_triage.py -q      # synthetic triage regression suite
python tools\triage\triage.py --demo                 # 4 synthetic inquiries, end to end
python scripts\validate_slot_confirmations.py        # Slot validation passed.
python tools\triage\triage.py --status               # production clock
python scripts\validate_opn_submission.py --preflight # package and safety preflight
```

Python 3.10+ runs the tool; pytest must already be installed to run the tests.
The clone needs network access, while the local checks run without paid model
requests under the settings above. The demo writes synthetic records outside
Git. For read-only evidence status, run only `--status`.

---

## Honest limitations

Listed because a reviewer should not have to discover them:

- No telephony or messaging integration. Phone and WhatsApp are human.
- No payment processing or card handling runs in this system. Deposits are **Zelle, human-initiated and human-verified**; a Stripe Payment Link rail was adopted 2026-08-30 but is **not yet live** (no link exists until the operator creates one in the Stripe dashboard). Either way, the tools never move money - a named human verifies every deposit before a booking exists.
- No calendar integration. The slot board is read by a person.
- The deployment is one narrow function, not the full role architecture.
- The business served is the operator's own, not an external customer.
- 2025 season artifacts are in assembly; that history is presented as operator attestation, not as the submitted deployment.

---

## Timeline

| Date | Milestone |
|---|---|
| 2026-08-29 | Tool implementation documented; not production-use evidence |
| 2026-09-10 | Owner supplied a successful synthetic check; separate test evidence only |
| `[TO FILL]` | First valid genuine model-backed, reviewed-and-sent record |
| `[TO FILL + 15]` | Earliest elapsed-window review, with actual operating evidence still required |
| Then | Resubmission with production log, launch date, model, and measured outcomes |

---

## Package contents

| Document | Purpose |
|---|---|
| `docs/OPN-SUBMISSION.md` | This response |
| `docs/opn-form-answers.md` | Current draft answers and final resubmission gates |
| `docs/model-check-2026-09-10.md` | Owner-supplied synthetic test result, not production evidence |
| `docs/production-deployment-record.md` | Factual deployment record |
| `docs/agent-workflow-architecture.md` | State graph, roles, approval points, failure states |
| `docs/release-monitoring-and-failure-handling.md` | Testing, approval, gates, outage fallback, privacy |
| `docs/evidence-index.md` | Every claim traced to source and date |
| `docs/gap-report.md` | Blockers and how each closes |
| `docs/operator-attestation-2025-season.md` | Prior-season history of record |
| `docs/release-checklist.md` | Pre-release gate |
| `docs/15-day-evidence-checklist.md` | Daily evidence discipline |
| `tools/triage/` | The deployment itself |
