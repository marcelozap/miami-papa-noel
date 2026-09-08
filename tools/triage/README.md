# Inquiry Triage - Setup and Manual Fallback

AI-assisted bilingual inquiry triage with mandatory human approval.

**What it does:** the operator pastes a real customer inquiry. The tool detects
English or Spanish, extracts the date, service category, location and contact
status, flags schedule risk, and drafts a short reply in both languages using
only the locked price list and configured payment terms. Until a real Stripe
Payment Link is configured, drafts offer Zelle only.

**What it never does:** send anything, confirm a booking, say a deposit was
received, promise insurance, or quote a price that is not in `pricing.json`.

---

## Setup

Nothing to install. Python 3.10+ and the standard library.

```powershell
cd "C:\XIV\santa"
python tools\triage\triage.py --demo
```

That runs four synthetic inquiries end to end. **Synthetic runs never count
toward the 15-day production requirement** and are written to a separate log.

### Optional: model-assisted mode

The tool is fully functional offline. Model assistance is opt-in:

```powershell
$secret = Read-Host 'Replacement OpenAI key' -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
Remove-Variable secret
$env:MPN_MODEL = 'gpt-5.6-luna'
python -B C:\XIV\santa\tools\triage\triage.py --check-model
```

Use a replacement for any key exposed in chat. This sets the key only in the
current terminal's environment without putting its value in shell history.
The selected Luna model succeeded on a separate haiku request; that is not yet
verification of this workflow or free ongoing access.

`--check-model` makes one synthetic Spanish home-visit request through the
same Responses API, structured schema and six validation gates used for
inquiries. It prints EN/ES drafts for review and **writes no local inquiry log,
approval or send record**. Exit 0 means the model path, expected extraction
and gates passed for this sample; exit 1 means not verified, including any
offline fallback. Incompatible modes such as `--real` are rejected with exit 2
before a request. This check may consume API credit. It never starts Day 1,
certifies a production launch or establishes OPN eligibility. Review both
languages, even after a pass. It does not automatically retry.

No install required — the call goes over `urllib` from the standard library to
the OpenAI Responses API, with a strict JSON schema and `store: false`.

Rules:

- **The key lives in a private runtime environment, never in the repository.**
  This CLI reads environment variables; it does not automatically load `.env`.
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

Put a genuine incoming inquiry in a private text file outside Git, then run
with its actual source channel. Do not use a canned example with `--real`.

```powershell
$inquiryFile = Join-Path $env:LOCALAPPDATA 'MiamiPapaNoel\intake\inquiry.txt'
python tools\triage\triage.py --file $inquiryFile --channel email --reviewer 'Marcelo Zapata' --real
```

The file must already exist and contain real business work. It is not created
by this command. For synthetic testing use `--check-model` or `--demo` instead.

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

After you copy the draft into the customer channel and actually send it, type
`SENT` exactly at the second prompt. The record then becomes
`approved_and_sent` with the timestamp captured by the tool. Anything else
leaves it as `approved_awaiting_send`; it never assumes that approval means a
message was sent.

### `--real` vs synthetic

`--real` marks a genuine customer inquiry and writes to the production log.
**Use it only for real inquiries.** Without it, everything goes to the synthetic
log and is excluded from the 15-day count. Do not pass `--real` while testing.
The flag alone does not establish Day 1: `--status` uses the first valid
model-backed, gated, reviewed-and-sent record, not a fallback or pending draft.
It reports a 15-full-day evidence review target, never OPN qualification.

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
| `payment_method` | Unapproved methods or a promised payment link before a real Stripe link is configured |

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

45 tests: extraction, language detection, schedule risk, pricing coverage, bilingual parity, and negative cases
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
| `test_triage.py` | 45 tests, all synthetic |
| `log-schema.md` | Production log fields and derived metrics |
| `examples/inquiry-redacted.jsonl` | Redacted five-line sample (synthetic) |

## Spending controls (v2: shared, atomic, off by default)

Paid generation is **disabled by default, even with a key configured**.
It runs only when the owner explicitly sets `MPN_API_DAILY_CALL_CAP` to a
positive number - the zero-spend opt-in the owner asked for.

When enabled, the daily allowance is enforced by atomic slot-file
reservations (`O_CREAT|O_EXCL`) in one shared quota directory
(`%LOCALAPPDATA%\MiamiPapaNoelpi-quota`, override `MPN_API_QUOTA_DIR`):

- **Shared across everything**: concurrent processes AND both paid adapters
  (triage/web queue and the reservations content adapter) draw from a
  single count. Two racing processes cannot exceed the cap together.
- **Reserved before the request**: a timeout or crash after reservation may
  still have billed, so the slot stays spent and is never auto-retried.
- **Fail closed**: an unreadable, corrupted, or unwritable quota store
  REFUSES paid generation (`BUDGET_ACCOUNTING_UNAVAILABLE`) - it never
  resets the allowance. Over-cap refusals are `BUDGET_CAP_REACHED`;
  disabled mode is `PAID_CALLS_DISABLED`. All fall back to offline drafts.
- **Restart-persistent**: slot files survive restarts; the day's spent
  allowance cannot be recovered by relaunching.
- **Input and output bounds**: inquiries over 6000 characters are never
  sent (`MODEL_INPUT_TOO_LARGE`), and every request carries
  `max_output_tokens` (`MPN_API_MAX_OUTPUT_TOKENS`, default 900). The cap
  value itself is ceilinged at 500/day.

**What this is NOT: a dollar guarantee.** It bounds request count and
per-call size. Token prices, other applications on the same account, and
provider-side billing behavior are outside its reach. Dashboard budget
alerts are not a verified hard cutoff - do not rely on them as one.
The usage ledger (`api-usage.jsonl`, token counts only) is informational
and never the counter.
