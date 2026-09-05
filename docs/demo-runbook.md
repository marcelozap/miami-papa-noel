# Live Demonstration Runbook

Six minutes, six commands, one terminal. Everything runs offline on a clean
machine with Python 3.10+. No key, no network, no install — the demo runs the
deterministic path throughout.

**Open in the repository root:**

```powershell
cd "C:\XIV\santa"
```

---

## 0. Frame it in one sentence (15 seconds)

> "This is the inquiry triage step of a seasonal Santa booking business. A real
> customer message comes in, the tool reads it and drafts a bilingual reply
> against a locked price list, and a human approves before anything is sent. The
> tool has no send path at all."

---

## 1. Inquiry intake and bilingual draft (90 seconds)

```powershell
python tools\triage\triage.py --demo
```

**Point at, in the output:**

- **Language detection** — case 1 is English, case 2 is Spanish, detected from
  the message alone.
- **Extraction** — `requested_date: 2026-12-13` parsed from "Dec 13", and
  `2026-12-20` from "el 20 de diciembre". Two languages, two date formats.
- **`missing: phone or email`** — the tool knows what it still needs and the
  draft asks for it.
- **`schedule risk: high`** — Dec 13 is a first-to-fill date, flagged before any
  price is quoted.
- **Both drafts** — English and Spanish, same price, same deposit, same terms.

> "Nothing here was sent. This is a draft on the operator's screen."

---

## 2. The pricing guard and the other gates (90 seconds)

```powershell
python tools\triage\demo_guards.py
```

Two deliberately bad drafts go through the validators.

**Case 1 — every rule broken at once.** 8 blocking failures: a $999 price that
is not on the locked list, "confirmed", "deposit received", the Spanish
"confirmada", two insurance claims, and Venmo.

**Case 2 — the interesting one.** Both prices are individually legal: $325 and
$450 are both real prices. But the English draft says $325 and the Spanish says
$450. Bilingual parity catches it.

> "That second case is the one that matters. A bilingual business can quote two
> different prices to two customers and never notice. The gate makes that
> impossible to send."

---

## 3. Human approval (60 seconds)

```powershell
python tools\triage\triage.py --message "Hi, do you have Dec 13 open for our HOA clubhouse in Doral? About 60 kids." --channel instagram_dm
```

The tool prints the drafts, prints the six gate results, then stops:

```
Nothing has been sent. Type APPROVE to record operator approval,
or anything else to reject.
>
```

**Type `no` first.** Show that it records a rejection.

Run it again and type `APPROVE`. Show the confirmation line and the log path.

> "Approval marks the record. The operator still copies the text into Instagram
> themselves. There is no integration to the customer channel — deliberately."

Note: omitting `--real` keeps this in the synthetic log. **Never pass `--real`
during a demonstration.**

---

## 4. The log and the production clock (60 seconds)

```powershell
python tools\triage\triage.py --status
```

Shows the first real inquiry, days elapsed, and the earliest qualification date.
Before the first real inquiry it reports `NOT STARTED`, which is the honest
answer.

Then show a log line:

```powershell
Get-Content "$env:LOCALAPPDATA\MiamiPapaNoel\triage\synthetic-log.jsonl" -Tail 1
```

**Point out what is *not* in it:** no message text, no draft text, no name, no
phone, no email, no street address. Location is a coarse area;
`contact_status` records whether a phone was given, never the number.

**Point out what is:** `model`, `prompt_version`, `price_list_version`,
`reviewer`, `approved_at`, `fallback_used`, `outcome`, `error_code`.

> "Every metric in the submission comes out of this file. Nothing is tracked
> separately, so nothing can drift from what actually happened."

Redacted sample, if they want to read one without a live run:
`tools/triage/examples/inquiry-redacted.jsonl`.

---

## 5. Manual fallback (45 seconds)

```powershell
python -m pytest tools\triage\test_triage.py -q
```

45 passed — including the negative tests that prove each gate blocks.

Then open `tools/triage/README.md` to the **Manual fallback** section and show
the price table.

> "If the model is unavailable, the tool falls back to a deterministic path
> automatically and logs `fallback_used: true`. If the whole tool is
> unavailable, this section is the procedure — the full price table, the deposit
> terms, the Zelle details, and the rules about what may never be written to a
> customer. The business earns most of its year in six weeks. Nothing here is
> allowed to become load-bearing."

---

## 6. Receipts and payment (30 seconds)

Be precise here, because it is the easiest thing to overstate:

> "Payment is Zelle only, and it is human. The tool never touches money, never
> sees a transfer, and cannot say a deposit arrived — that phrasing is blocked
> in both languages. Payment receipts are reconciled by the operator against the
> booking, following `business/booking-sop.md`. What the tool logs is inquiry
> handling, not payments."

---

## The whole demo, as a script

```powershell
cd "C:\XIV\santa"
python tools\triage\triage.py --demo
python tools\triage\demo_guards.py
python tools\triage\triage.py --message "Hi, do you have Dec 13 open for our HOA clubhouse in Doral?" --channel instagram_dm
python tools\triage\triage.py --status
python -m pytest tools\triage\test_triage.py -q
python scripts\validate_slot_confirmations.py
```

---

## Questions to expect

**"Is this in production?"**
> "Built, tested, and instrumented. The production clock starts on the first
> real customer inquiry, and `--status` reports it. We are not claiming days we
> have not run."

**"Which model?"**
> "The default path is deterministic and logged as `offline-rules-v1` with
> `fallback_used: true`. AI mode is opt-in and the exact model id is written to
> every log line. We do not put a model name in a document before it has run."

**"What happens if the AI is wrong?"**
> "A human reads every draft before it goes anywhere, and six gates run before
> the human sees it. A bad price, a confirmation phrase, an insurance claim, or
> a non-Zelle payment method blocks approval entirely."

**"Can it book a customer?"**
> "No. It has no send path and no calendar write. It cannot confirm a booking or
> acknowledge a deposit — those phrases are blocked in English and Spanish."

**"How big is this?"**
> "One narrow function, deliberately. Four operating roles are documented in
> `business/AGENT-ROLES.md`; one of them has software support. We would rather
> show one thing that genuinely works."

---

## Before the demo

- [ ] `python -m pytest tools\triage\test_triage.py -q` → 45 passed
- [ ] `python tools\triage\triage.py --demo` renders clean
- [ ] `python tools\triage\demo_guards.py` shows 9 blocking failures
- [ ] Terminal font large enough to read
- [ ] `--real` **not** in any command you will run
- [ ] No real customer data on screen
