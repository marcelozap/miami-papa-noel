# Operator Attestation - 2025 Season

**Attested by:** Marcelo Zapata, operator, Miami Papa Noel / XIV
**Date of attestation:** 2026-08-29
**Status:** authoritative project history. Supporting evidence in assembly.

---

## Statement

The Miami Papa Noel role-based operations workflow operated during the 2025
Christmas season, supporting real customer inquiries, bilingual message
drafting, booking coordination, outreach, payment receipt tracking, event
logistics, and follow-up.

This is recorded here as the operator's account of the project's history. It is
the basis on which the 2026 season was planned and built.

---

## Why this document exists

An operator's account of their own business is a legitimate record. It is not,
by itself, the kind of dated artifact an external technical reviewer can
independently check — those are different standards, and both are normal.

This document holds the account. The table below names the specific artifacts
that would let a reviewer verify it, so the work is to **collect** rather than
to **re-argue**. Nothing here asks the operator to justify that the season
happened.

---

## Evidence fields

Fill any of these that are easy to reach. Each one independently strengthens the
record; none of them is a prerequisite for the 2026 deployment.

| # | Field | What satisfies it | Status |
|---|---|---|---|
| 1 | **Season window** | First and last customer contact dates in the 2025 season | `[TO FILL]` |
| 2 | **Channels used** | Which inboxes carried inquiries (Instagram DM, WhatsApp, email, phone) | `[TO FILL]` |
| 3 | **Volume** | Approximate inquiries handled and events performed | `[TO FILL]` |
| 4 | **Bilingual handling** | Roughly what share of customers were served in Spanish | `[TO FILL]` |
| 5 | **Assistant involvement** | Which assistant tools were used, for which steps (drafting, extraction, scheduling) | `[TO FILL]` |
| 6 | **Model** | If a specific model or product tier was used, its name. Leave blank rather than guess | `[TO FILL]` |
| 7 | **Operator** | Who ran the workflow day to day | Marcelo Zapata |
| 8 | **Payment handling** | Confirms Zelle-only was in force in 2025 | `[TO FILL]` |
| 9 | **Outcome** | One concrete number: bookings completed, or events performed, or zero double-bookings across the season | `[TO FILL]` |
| 10 | **Dated artifacts** | Anything with a timestamp: message threads, calendar entries, payment records, photos with dates | `[TO FILL]` |

### Where the artifacts most likely live

Not in this repository — the repo began 2026-06-10, which is why the audit alone
cannot reach them:

- Instagram / WhatsApp message history from Nov-Dec 2025
- Phone calendar entries for December 2025 events
- Zelle transaction history for the 2025 season
- Photographs from 2025 events, with file dates
- Assistant conversation history, if the account is still active

Any two of these carry a season. Screenshots with visible dates are sufficient;
redact customer names, phone numbers, and addresses before they go anywhere.

---

## Dated artifacts already in hand

These are in the repository or the asset library and need no collection:

| Artifact | Date | What it establishes |
|---|---|---|
| Event photographs | 2022-12-24 | Business performing real events |
| Event photographs | 2023-12-10, 2023-12-14 | Repeat seasonal operation |
| `business/booking-sop.md` | 2026-06-10 | Booking procedure formalized |
| `business/lead-reply-bank.md` | 2026-06-15 | Bilingual reply library |
| `business/AGENT-ROLES.md` | 2026-08-26 | Role architecture: Scout, Dispatcher, Concierge, Bookkeeper |
| `business/seasonal-ops-workflow.md` | 2026-08-28 | End-to-end seasonal workflow |
| Repository history | 2026-06-10 → 2026-08-28 | 76 commits, single operator |

---

## How this is used in the OpenAI submission

Two things are stated separately, because they are two different things:

1. **Project history** — the 2025 season operated as described above, per this
   attestation. Presented as the operator's record, with evidence in assembly.
2. **The submitted production deployment** — the 2026 bilingual inquiry triage
   tool, instrumented from its first real inquiry, with a dated log a reviewer
   can read directly.

The submission rests on (2). (1) is the history that explains why (2) exists and
why it is shaped the way it is. Neither claim is asked to carry the other.

---

## Amending this document

As evidence fields are filled, update the table, date the change, and note the
artifact. Do not delete a `[TO FILL]` row — mark it filled with a pointer to
where the artifact lives. Never move an artifact containing customer data into
this repository; reference its location instead.
