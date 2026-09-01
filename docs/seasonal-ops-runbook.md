# Seasonal Operations Runbook

The operator's manual for the Miami Papa Noel tools. Every tool here is local,
standard-library Python, drafts-only (nothing sends itself), and stores
customer-adjacent state OUTSIDE the repository under
`%LOCALAPPDATA%\MiamiPapaNoel\`.

Public contact: **786-975-9557** (call/text/WhatsApp) and
**santa@miamipapanoel.com**. Zelle deposits go ONLY to **305-244-0360**.
The 50% Zelle deposit is a non-refundable retainer; balance due on arrival.

---

## 1. Booking and slot control (`tools/slots/slots.py`)

One canonical state machine. A slot is SOLD only at BOOKED, and BOOKED is
reachable only through a human verifying the Zelle deposit:

```
OPEN --hold--> HELD --deposit-sent--> DEPOSIT_SENT --verify-zelle--> BOOKED
  ^              |                        |                            |
  +---release----+------------release-----+-----------cancel----------+
```

Legacy names `HOLD_48HR` and `CONFIRMED` are accepted as aliases
everywhere. `DEPOSIT_SENT` is deliberately its own state in the tracker
validator too - it means unverified, and is never treated as PAID.

**The normal booking, in order:**

```powershell
# 1. Customer asks for a slot - hold it 48h under a lead ref (never a name)
python tools\slots\slots.py hold --slot EVE-2026-12-24-1700 --ref L-014 --operator Marcelo

# 2. Customer says the Zelle was sent - record it; the slot is still NOT sold
python tools\slots\slots.py deposit-sent --slot EVE-2026-12-24-1700 --operator Marcelo

# 3. YOU check the Zelle account with your own eyes, THEN:
python tools\slots\slots.py verify-zelle --slot EVE-2026-12-24-1700 --operator Marcelo --amount 250 --memo-ref MEMO-014

# 4. Only now does a confirmation draft exist - send it manually:
python tools\slots\slots.py confirmation --slot EVE-2026-12-24-1700
```

The confirmation draft is bilingual, names the verification date, restates the
four visit requirements (chair, air conditioning, designated adult, parking
within 100 feet), and the balance-on-arrival Zelle terms. **The site and the
tools never claim a deposit cleared unless step 3 was performed by a human.**

**Housekeeping:**

```powershell
python tools\slots\slots.py availability          # public view (BOOKED hidden)
python tools\slots\slots.py expire-holds          # release lapsed 48h holds
python tools\slots\slots.py release --slot X --operator Marcelo --reason "no reply"
python tools\slots\slots.py cancel  --slot X --operator Marcelo --retainer FORFEIT
python tools\slots\slots.py status                # every slot's state
python tools\slots\slots.py audit                 # the append-only ledger
python tools\slots\slots.py check-tracker-privacy # committed tracker holds no customers
```

**LOCAL MODE, stated plainly:** the public site is static and cannot share
live state across devices. `export-availability` writes a dated snapshot for a
manual deploy; until deployed, the site shows the previous snapshot and the
operator is the source of truth. Cancellation keeps the retainer (FORFEIT), or
moves it to a new date (TRANSFERRED) - exactly the documented policy, never a
refund promise.

**Manual fallback (no Python):** the paper rule is the same machine - a date
is written in the calendar in pencil at HELD, in pen only after you saw the
Zelle arrive, and the customer gets the confirmation text only after the pen.

## 2. Mrs. Claus Office intake (`tools/mrs_claus_office/intake.py`)

Bilingual intake for website, text, and call inquiries. Collects the booking
facts and the four requirements, drafts the EN+ES reply from the locked price
list, and escalates anything sensitive to the human operator.

```powershell
python tools\mrs_claus_office\intake.py --channel text --name "..." --phone "..." ^
  --date 2026-12-13 --time 6pm --city Doral --event-type "family party" ^
  --guest-details "20 guests, 8 kids" --chair yes --air-conditioning yes ^
  --gift-adult yes --parking yes --notes "..."
```

- Missing facts become questions in the draft, in both languages.
- **Escalates** (never answers alone): payment questions, discount requests,
  complaints, unclear requests, final availability, operator-marked
  exceptions, and dates whose slots are all BOOKED (`date_fully_booked_review`
  - an internal flag; the customer is never told a date is gone by the tool).
- The draft always says the coordinator must confirm the date - it never
  promises availability, never confirms, never verifies payment, never
  discounts, and runs through all six triage validation gates; a failing draft is printed only with a BLOCKED banner and is never offered for sending.
- Deterministic: works with no model, no key, no network.
- Intake records: `%LOCALAPPDATA%\MiamiPapaNoel\intake\intake-log.jsonl`
  (override `MPN_INTAKE_DIR`). Customer data never enters the repository.

**Preserved review tools:** `tools/ms_claus/ms_claus.py` (public-page review)
and `business/december-slot-board.html` (display board) are untouched;
`tools/slots/slots.py` is now the only write path for slot state.

## 3. Calls and texts (`tools/comms/`)

See `tools/comms/README.md`. Provider adapters only - **no provider is
connected**; there is no automated calling, no recording (consent-gated and
impossible without a live tested provider), and 786-975-9557 stays answered by
a human. `simulate-inbound-sms` / `simulate-inbound-call` exercise the event
log locally with redacted summaries.

**External account still required:** an SMS/voice provider (e.g. Twilio)
account with its credentials in environment variables - one manual setup step,
documented in the adapter. Until then everything is dry-run and labeled so.

## 4. Content queue (`tools/content/`)

See `tools/content/README.md`. Performer-recorded videos are referenced by
path; the tool drafts deterministic bilingual scripts/captions, requires
`approve --operator`, and schedules DRY-RUN only. **Publishing is blocked in
code** until social credentials exist AND the operator approves at publish
time. A stem filter refuses topics that smell like fabricated social proof or
affiliations (partner, sponsor, review, customer, guarantee, ...) at
draft time; mandatory human approval remains the real gate.

**External account still required:** social platform credentials, plus the
operator's explicit go-ahead per post.

## 5. Elf outreach (`tools/elves/`)

See `tools/elves/README.md`. Public-prospect research for schools, HOAs,
businesses, nonprofits, and community events - public contact paths only,
personal-looking emails refused, job boards refused, a cap of 15 outstanding unsent messages (drafted OR approved) so
outreach is sent and recorded rather than stockpiled, `DO_NOT_CONTACT` is
sticky, and every message requires `approve --operator` before a HUMAN sends
it via the public path. Affiliation claims are refused at draft time.

---

## Daily loop, in season

```powershell
python tools\slots\slots.py expire-holds
python tools\slots\slots.py status
# work the inquiries through Mrs. Claus Office, escalations first
# verify any Zelle that arrived, then send the confirmations it unlocks
python tools\ms_claus\ms_claus.py            # weekly: public-page review
python scripts\validate_slot_confirmations.py
```

## One command for everything

```powershell
python scripts\ops_check.py        # battery + validators + privacy + preflight
python scripts\ops_check.py --fast # same, minus the OPN preflight
```

## The whole test battery

```powershell
python -m pytest tools\triage\test_triage.py scripts\test_validate_opn_submission.py scripts\test_evidence_index.py scripts\test_build_opn_packet.py tools\ms_claus\test_ms_claus.py tools\slots\test_slots.py tools\mrs_claus_office\test_intake.py tools\comms\test_comms.py tools\content\test_content.py tools\elves\test_elves.py tools\test_integration_season.py -q
```

## What is real vs. simulated

| Lane | Status |
|---|---|
| Slot state machine, Zelle verification, confirmations | **Working locally** - operator-driven, external state |
| Mrs. Claus intake, drafts, escalation | **Working locally** - deterministic |
| Public site | Static; availability via manually deployed snapshots (LOCAL MODE) |
| Calls/texts | **Simulated** - adapter skeleton, no provider connected |
| Call recording | **Off** - requires consent AND a live tested provider; neither exists |
| Content posting | **Dry-run** - no social credentials connected |
| Outreach sending | **Manual by design** - human sends every approved draft |
