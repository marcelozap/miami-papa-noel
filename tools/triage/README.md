# Inquiry Triage - Setup and Manual Fallback

AI-assisted bilingual inquiry triage with mandatory human approval.

**What it does:** the operator pastes a real customer inquiry. The tool detects
English or Spanish, extracts the date, service category, location and contact
status, flags schedule risk, and drafts a short reply in both languages using
only the locked price list and Zelle-only terms.

**What it never does:** send anything, confirm a booking, say a deposit was
received, promise insurance, or quote a price that is not in `pricing.json`.

---

## Setup

Nothing to install. Python 3.10+ and the standard library.

```powershell
cd "C:\Users\Green Machine\miami-papa-noel"
python tools\triage\triage.py --demo
```

That runs four synthetic inquiries end to end. **Synthetic runs never count
toward the 15-day production requirement** and are written to a separate log.

### Optional: model-assisted mode

The tool is fully functional offline. Model assistance is opt-in:

```powershell
$env:MPN_MODEL = "<exact model id>"
$env:OPENAI_API_KEY = "<key>"
```

No install required — the call goes over `urllib` from the standard library to
the OpenAI Responses API, with a strict JSON schema and `store: false`.

Rules:

- **The key lives in an environment variable or an ignored local `.env`. Never
  in the repository.** `.gitignore` covers `.env`, `*.pem`, `*.key`.
- **No customer-facing API key.** Customers never touch this tool; the operator
  runs it locally.
- **In AI mode the customer's inquiry text is sent to the OpenAI API.** The
  request sets `store: false`. In deterministic mode nothing leaves the machine.
  Decide this deliberately — it is the one privacy difference between the two
  modes.
- If `MPN_MODEL` or the key is unset, the tool runs deterministically and
  records `fallback_used: true`.
- If the API errors, times out, returns unparseable output, or returns a draft
  that **fails any validation gate**, the tool falls back to the deterministic
  path and records the reason in `error_code`
  (`MODEL_HTTP_ERROR`, `MODEL_UNAVAILABLE`, `MODEL_PARSE_ERROR`,
  `MODEL_SCHEMA_ERROR`, `MODEL_OUTPUT_VALIDATION_FAIL`).
- **A model id is recorded only when its output passed every gate.** The model
  cannot put an unsafe draft in front of the operator.
- Whatever actually ran is written to `model` on every line. **Never edit that
  field by hand.**

### Optional environment variables

| Variable | Effect |
|---|---|
| `MPN_LOG_DIR` | Log directory. Default `%LOCALAPPDATA%\MiamiPapaNoel\triage` |
| `MPN_REVIEWER` | Name recorded as reviewer on approval |
| `MPN_MODEL` | Exact model id for AI mode |

---

## Daily use

**A real customer inquiry:**

```powershell
python tools\triage\triage.py --message "Hi, do you have Dec 13 open for our HOA in Doral?" --channel instagram_dm --real
```

**From a file** (easier for long messages, avoids shell quoting):

```powershell
python tools\triage\triage.py --file inquiry.txt --channel whatsapp --real
```

**Check the production clock:**

```powershell
python tools\triage\triage.py --status
```

### The approval step

The tool prints both drafts and the validation results, then stops:

```
Nothing has been sent. Type APPROVE to record operator approval,
or anything else to reject.
>
```

Type `APPROVE` exactly. Anything else records a rejection. Approval only marks
the draft as approved — **you still copy it into the customer channel
yourself.** The tool has no send path, by design.

After you send, the `sent_at` field is filled in by hand. That gap is
deliberate: the log should record what a human actually did.

### `--real` vs synthetic

`--real` marks a genuine customer inquiry and writes to the production log.
**Use it only for real inquiries.** Without it, everything goes to the synthetic
log and is excluded from the 15-day count. Do not pass `--real` while testing.

---

## Validation gates

Every draft is checked before you are offered the approval prompt. A `FAIL`
blocks approval outright.

| Check | Blocks on |
|---|---|
| `pricing` | Any dollar figure not in `pricing.json` |
| `bilingual_parity` | EN and ES stating different prices, or an empty draft |
| `missing_information` | Missing date/category/location with no question asked |
| `unsafe_confirmation` | "confirmed", "booked", "deposit received", "reservado", "depósito recibido" — accent-insensitive |
| `insurance_claim` | Any insurance language while the policy is unverified |
| `payment_method` | Venmo, Cash App, Stripe, Square, PayPal, card, wire |

If a draft is blocked, the inquiry is logged with
`outcome: blocked_by_validation` and you handle it manually. **Do not edit the
validators to get past a block.** The block is the product.

### Pricing is locked

`pricing.json` is the single source of truth, mirroring `checkout.html` as
published. To change a price: edit `pricing.json`, bump `price_list_version`,
update `checkout.html` in the same commit, run the tests. The version is
recorded on every log line, so any draft can be traced to the price list that
produced it.

### Insurance stays off until the policy is real

`business/insurance-and-wave1-preflight.md` is the authority. Until it records a
verified active commercial policy, the tool refuses to emit insurance language
in any form. Do not set `policy_verified=True` before that document says so.

---

## Manual fallback

**The business runs without this tool. That is a requirement, not a caveat.**

If Python breaks, the model is unavailable, the subscription lapses, the laptop
dies, or you are on a phone in a parking lot in December — the workflow is
unchanged. The tool saves typing; it is not load-bearing.

### The manual procedure

1. **Read the inquiry** and note: date, event type, location, headcount, gifts
   provided or not, language.
2. **Check the calendar before quoting.** A quote implies availability. Confirm
   the slot is open, including travel time from any earlier event that day, in
   December traffic.
3. **Price from `checkout.html`** — the same figures the tool uses:

   | Service | Price |
   |---|---|
   | Family Visit | $325 first hour, $150 per extra half hour |
   | Event Visit | $450 first hour |
   | HOA / community | $550, two hours, two-hour minimum |
   | School or daycare | $275, one hour, weekday daytime |
   | Corporate | $450 first hour · $600 four hours · $850 full day |
   | Christmas Eve | $500 per 45-minute slot until 8pm |
   | Christmas Eve after 9pm | $375, fifteen minutes |
   | Travel | Free within 25 miles of Doral · $45 between 25 and 50 |

4. **Deposit:** 50% non-refundable locks the date, balance due on arrival.
5. **Payment: Zelle only**, 305-244-0360. Never offer another method.
6. **Reply in the customer's language.** Templates in
   `business/lead-reply-bank.md`.
7. **Never write "confirmed", "booked", or "reserved" before the deposit
   clears.** A date is held, not booked, until money lands.
8. **Never claim insurance** until the policy is verified.
9. **Write the row down** — date, channel, language, what you quoted, what you
   asked for. When the tool comes back, that row goes into the log with
   `fallback_used: true`.

### Recording a fallback period

Log the gap honestly rather than leaving a hole. For each inquiry handled by
hand, append a line with `fallback_used: true`, `model: "manual"`, and
`error_code` naming why (`MODEL_UNAVAILABLE`, `TOOL_UNAVAILABLE`). A reviewer
seeing an honest fallback record trusts the rest of the log more, not less.

---

## Tests

```powershell
python -m pytest tools\triage\test_triage.py -q
```

43 tests: extraction, language detection, schedule risk, pricing coverage, bilingual parity, and negative cases
proving the validators actually block bad drafts. All inquiries in the suite are
synthetic and write nowhere near the production log.

Also run the repo's existing check:

```powershell
python scripts\validate_slot_confirmations.py
```

---

## Files

| File | Purpose |
|---|---|
| `triage.py` | The operator tool |
| `validators.py` | The six validation gates |
| `pricing.json` | Locked price list, versioned |
| `test_triage.py` | 43 tests, all synthetic |
| `log-schema.md` | Production log fields and derived metrics |
| `examples/inquiry-redacted.jsonl` | Redacted five-line sample (synthetic) |
