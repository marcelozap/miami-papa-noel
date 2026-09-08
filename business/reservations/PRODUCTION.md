# PRODUCTION RECORD — Miami Papa Noel Reservation System

**System:** XIV reservation, logistics, and content workflow for Miami Papa Noel
**Customer:** Miami Papa Noel (bilingual Santa visit business, Miami-Dade & Broward, miamipapanoel.com)
**Operational owner:** The performer (business owner) — takes the bookings, works the schedule the system produces
**Operator / implementer:** Marcelo Zapata, Founder, XIV
**Launch date:** [TO FILL on first real customer operation — never backdated]. System installed locally and 17/17 synthetic tests passed 2026-09-04 13:25 UTC (see OPS-LOG.md) — an installation checkpoint, not a launch.
**Status:** NOT STARTED — built locally and tested synthetically (17/17 gate tests); no real customer inquiry or booking has been processed. Daily ops will be recorded in OPS-LOG.md once real operation begins.

## Built functionality (implemented locally, verified by synthetic tests — not yet serving customers)

Four lanes over one shared source of truth (`data/reservations.json` + append-only `data/events.jsonl`):

1. **Reservation agent** — collects date, time, address, package (validated against the locked rate card), guest details, and deposit status; advances a record only as far as its data allows (inquiry → hold → pending_review).
2. **Logistics agent** — checks every consecutive pair of visits on a date for travel time (10-zone South Florida drive matrix), setup time, and buffer; blocks overlapping or undrivable routes. Encodes the real constraints: Christmas Eve 45-min visits 60 min apart, peak-evening 60-min visits 90 min apart. Drive times are estimates, not live traffic, and are labelled as such.
3. **Operator review** — the ONLY code paths that verify a Zelle deposit or mark a booking confirmed. Enforced in the state machine, not by convention: an agent actor attempting either is refused with an error.
4. **Content lane (MaloSound)** — drafts bilingual EN/ES captions and video briefs from CONFIRMED reservations only; a hold or inquiry can never trigger a public announcement (enforced + tested). Every draft waits for operator approval before publishing. MaloSound.ai is integrated through an adapter interface whose only current implementation is a local dry-run — no invented API, no credentials in the repo.

## Models used

- **Content lane (generative):** when `OPENAI_API_KEY` is configured on the production machine, caption and video-brief drafting runs on an OpenAI model via the API (default `gpt-4o-mini`, overridable with `OPENAI_MODEL`); the model used is recorded in each draft's manifest. Generated text is checked against the copy rules in code (no "insured" claims, no client names or addresses, correct brand) and rejected on violation. Without the key, deterministic bilingual templates run instead — the manifest says which path produced each draft. *(Record the date the key was first configured here: ____________ — model use in production counts from that date, not before.)* As of 2026-09-05 no model-backed run has succeeded on any Santa path — the last live attempt returned HTTP 429 credit_balance_exhausted (gpt-4.1-mini); the only successful call was a raw gpt-5.6-luna haiku outside Santa's gated paths. The OpenAI drafting path is built and mock-tested but unverified against the live API.
- **Build & operations tooling:** Claude (Anthropic), via Claude Code sessions operated by XIV, was used to build the system and will assist in operating it once real operation begins.
- The reservation state machine, logistics feasibility math, rate card, deposit gates, and health monitoring are **deterministic Python — no model in the loop by design**. Booking state can only change through validated code paths; no model output can alter a reservation's status.
- No customer data is used to train or fine-tune any model.

## Release process

A change ships only when: (1) the full pytest gate suite (`tests/`, 17 tests covering every permission boundary and the logistics math) passes, and (2) the operator approves the change. The gate tests are the production contract — a failing gate test is a blocked release. The XIV orchestrator's `miami_papa_noel` node is configured to emit hash-chained receipts into the XIV ledger (external to this repository; no production runs recorded yet).

## Monitoring

`python papanoel.py health` is to run daily once operation begins (one installation-day run recorded so far; see OPS-LOG.md): counts by status, holds older than 48h without a verified deposit, confirmed bookings whose route regressed to tight/impossible after later bookings, drafts pending operator approval, and records failing validation. Every run appends to `data/health.log`.

## Failure handling

Fail-closed everywhere. On out-of-scope input or any gate failure, the lane stops, writes an ESCALATION event to the log, and waits for the operator — it never guesses and never proceeds. An impossible route blocks confirmation; an unverified deposit blocks review; a non-confirmed reservation raises an error if it reaches the content lane. Incidents are written to the event log with what happened, what should have happened, and the fix goes through the release process above.

## Concrete outcome

*(Fill from OPS-LOG.md after the operating window: bookings processed, deposits verified, routes blocked/prevented, drafts produced and approved. Real numbers only.)*
