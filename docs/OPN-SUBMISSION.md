# OpenAI Partner Network — Submission

**Applicant:** Marcelo Zapata / XIV
**Deployment:** Miami Papa Noel — AI-assisted bilingual inquiry triage
**Date:** 2026-08-29

---

## Summary

Miami Papa Noel is a bilingual seasonal service business in Miami-Doral,
operating since 2017, with a public booking site at `miamipapanoel.com` and a
documented role-based operations workflow. It runs under XIV, the operator's
business. **It is the operator's own business, not an external third-party
customer**, and is not presented as one.

The role-based workflow operated during the 2025 Christmas season — inquiries,
bilingual drafting, booking coordination, outreach, payment receipt tracking,
logistics, and follow-up — per the operator attestation at
`docs/operator-attestation-2025-season.md`. Supporting artifacts for that season
are being assembled and are labeled as such throughout.

**What is submitted for review is the 2026 deployment:** a real, runnable,
instrumented tool that performs bilingual inquiry triage with mandatory human
approval. It is built, tested, and documented, and is ready to enter production
on its first real customer inquiry. It reaches 15 days of continuous operation
15 days after that first real record.

---

## What is live

The tool at `tools/triage/triage.py`. Run the deterministic path with:

```powershell
python tools\triage\triage.py --demo
```

With `MPN_MODEL` and `OPENAI_API_KEY` configured, the same command makes one
OpenAI Responses API request for structured extraction and bilingual drafting.
If the request is unavailable or the model output fails a local safety gate,
the deterministic path is used and the fallback is logged.

For each inquiry it:

- detects English or Spanish
- extracts requested date, service category, location, and contact status
- identifies missing information, and never guesses a date from a bare month
- flags schedule and capacity risk against the season's first-to-fill dates
- drafts a short reply in **both** English and Spanish
- quotes only from a locked, versioned price list
- states Zelle-only payment terms
- writes a structured log line

**It cannot send anything.** There is no network egress to a customer channel.
The operator types `APPROVE`, then copies the draft into the channel by hand.

### Enforced safety gates

Six, each with negative tests proving it blocks rather than warns:

| Gate | Blocks |
|---|---|
| Pricing | Any figure outside the locked list `2026-08-28.1` |
| Bilingual parity | EN and ES stating different prices; an empty draft |
| Missing information | Required fields absent with no question asked |
| Unsafe confirmation | "confirmed", "booked", "deposit received", "reservado", "depósito recibido" — accent-insensitive |
| Insurance claim | Any insurance language while the policy is unverified |
| Payment method | Venmo, Cash App, Stripe, Square, PayPal, card, wire |

The tool is structurally incapable of confirming a booking or acknowledging a
deposit. Only a human does either, and only after funds clear.

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
| **Active customer AI deployment** | Built and ready; the production clock starts on the first real inquiry |
| **Launch date / status** | `[TO FILL]` — recorded automatically as the first `--real` log line. Never backdated |
| **Operational owner** | **Marcelo Zapata — built and operated.** Sole operator and sole committer in the repository history |
| **Live AI functionality** | Configured Responses API path for structured extraction and bilingual drafting, with deterministic extraction and drafting as the tested fallback; six enforced gates |
| **Concrete outcome** | `[TO FILL]` — derives from the log: inquiries handled, median first-response time, share approved unedited, rejection rate, fallback rate |
| **Production model** | `[TO FILL]` — written verbatim only after a configured model produces a validated draft. The default remains `offline-rules-v1` with `fallback_used: true` |
| **How components work together** | `docs/agent-workflow-architecture.md` — state graph with per-step build state |
| **Testing and release approval** | 45 passing tests; `docs/release-checklist.md`; local submission preflight in `scripts/validate_opn_submission.py`. Single-operator approval, stated plainly |
| **Production monitoring** | Logging layer built and tested; `tools/triage/log-schema.md` |
| **Failure handling** | Automatic fallback to deterministic mode; full manual procedure if the tool is unavailable |
| **≥15 days production** | **Not yet met.** Real production records, model/outcome fields, external evidence, and elapsed time remain to be collected |

---

## Verification a reviewer can run

```powershell
git clone https://github.com/marcelozap/miami-papa-noel
cd miami-papa-noel
python -m pytest tools\triage\test_triage.py -q      # 45 passed
python tools\triage\triage.py --demo                 # 4 synthetic inquiries, end to end
python scripts\validate_slot_confirmations.py        # Slot validation passed.
python tools\triage\triage.py --status               # production clock
python scripts\validate_opn_submission.py --preflight # package and safety preflight
```

No install, no key, and no network required — those commands exercise the
deterministic path. Everything above runs on a clean machine with Python 3.10+.
AI mode is opt-in and is the only path that makes a network call.

---

## Honest limitations

Listed because a reviewer should not have to discover them:

- No telephony or messaging integration. Phone and WhatsApp are human.
- No payment processing, card handling, or online payment acceptance. **Zelle only**, human-initiated and human-verified.
- No calendar integration. The slot board is read by a person.
- The deployment is one narrow function, not the full role architecture.
- The business served is the operator's own, not an external customer.
- 2025 season artifacts are in assembly; that history is presented as operator attestation, not as the submitted deployment.

---

## Timeline

| Date | Milestone |
|---|---|
| 2026-08-29 | Tool built, tested, documented. Ready for first real inquiry |
| `[TO FILL]` | First real customer inquiry — production clock starts |
| `[TO FILL + 15]` | 15 days continuous operation reached |
| Then | Resubmission with production log, launch date, model, and measured outcomes |

---

## Package contents

| Document | Purpose |
|---|---|
| `docs/OPN-SUBMISSION.md` | This response |
| `docs/production-deployment-record.md` | Factual deployment record |
| `docs/agent-workflow-architecture.md` | State graph, roles, approval points, failure states |
| `docs/release-monitoring-and-failure-handling.md` | Testing, approval, gates, outage fallback, privacy |
| `docs/evidence-index.md` | Every claim traced to source and date |
| `docs/gap-report.md` | Blockers and how each closes |
| `docs/operator-attestation-2025-season.md` | Prior-season history of record |
| `docs/release-checklist.md` | Pre-release gate |
| `docs/15-day-evidence-checklist.md` | Daily evidence discipline |
| `tools/triage/` | The deployment itself |
