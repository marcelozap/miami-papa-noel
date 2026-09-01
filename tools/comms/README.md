# Comms Adapter Layer - Phase 3 Skeleton

The calls/texts provider adapter layer. In this version it is a **dry-run
event logger and a deliberately inert provider skeleton** - nothing more.

**What it does:** records that a call or text came in on the public number.
The operator runs a `simulate-inbound-*` command; the tool validates the
opaque lead reference, **redacts** the free-text summary (phone numbers,
emails, and street addresses are stripped before anything touches disk), and
appends one line to an append-only JSONL event log outside the repository.

**What it never does:** send, post, publish, call, or submit anything
anywhere. There is no network code in `adapter.py`. It never records a call,
never stores a phone number, email, or address, and never accepts a phone
number as an identifier. Every outbound artifact anywhere in this system is a
DRAFT a human sends manually.

---

## Setup

Nothing to install. Python 3.10+ and the standard library.

```powershell
cd "C:\Users\Green Machine\miami-papa-noel"
python tools\comms\adapter.py status
```

### Environment variables

| Variable | Effect |
|---|---|
| `MPN_COMMS_DIR` | State directory. Default `%LOCALAPPDATA%\MiamiPapaNoel\comms` |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `MPN_COMMS_LIVE` | Gate the TwilioAdapter skeleton - see below. Setting them enables **nothing** in this version. |

State file: `events.jsonl` - append-only, one JSON object per line, **outside
the repository, never committed**.

---

## Commands

**Log an inbound text (dry run):**

```powershell
python tools\comms\adapter.py simulate-inbound-sms --from-ref L-014 --summary "asked about Dec 13 pricing"
```

**Log an inbound call (dry run):**

```powershell
python tools\comms\adapter.py simulate-inbound-call --from-ref L-014 --summary "asked about Christmas Eve" --duration-seconds 120 --consent none
```

**Status / audit:**

```powershell
python tools\comms\adapter.py status
python tools\comms\adapter.py audit
```

### `--from-ref` is an opaque reference

`L-014`-style lead references only: letter first, then letters, digits,
dashes or underscores. A phone number is refused outright. The event log
identifies people by reference, never by contact data.

### `--summary` is redacted before storage

Anything matching a phone number, an email address, or a street address is
replaced with `[REDACTED-PHONE]` / `[REDACTED-EMAIL]` / `[REDACTED-ADDRESS]`
before the line is written. The phone pattern extends the contact-detection
regex from `tools/triage/triage.py` with optional `+1` and parentheses.
Redaction is deliberately greedy: over-redacting a harmless phrase is
accepted, under-redacting a customer's contact data is not. If you need the
contact details, they belong in the operator's private records - not in this
log.

---

## Event schema

Each line of `events.jsonl`:

| Field | Meaning |
|---|---|
| `ts` | Local timestamp, ISO seconds |
| `kind` | `sms_in` or `call_in` |
| `from_ref` | Opaque lead reference (`L-014`), never a phone number |
| `redacted_summary` | The summary after redaction |
| `duration_seconds` | Calls only |
| `consent` | `none` or `obtained` (recording consent; informational) |
| `recording` | Always the literal string `NOT RECORDED` |

## Recording policy - enforced, not promised

Recording metadata may only ever be something other than `NOT RECORDED` if
consent is `obtained` **and** a live, tested provider is configured. In this
version a live provider is never configured, so the field is **always**
`NOT RECORDED`, and the enforcement is layered:

1. `--recording-requested` with `--consent none` is refused loudly.
2. `--recording-requested` with `--consent obtained` is **still refused**,
   because consent alone is not enough without a live, tested provider.
3. `append_event` refuses to write any event whose `recording` field is not
   exactly `NOT RECORDED`, so nothing else can reach disk even by mistake.

Do not edit the enforcement to get past a refusal. The refusal is the product.

## The TwilioAdapter skeleton

`TwilioAdapter` exists so the call sites exist. It is wired to nothing:

- Without `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, **and**
  `MPN_COMMS_LIVE=1` all set, every method raises `ProviderNotConfigured`.
- Even with all three set, every method raises `NotImplementedError`: live
  wiring requires a tested provider connection, which this version does not
  have. It never invents credentials and never makes a network call.

The default and only working adapter is `NullAdapter` (dry run).

---

## Manual fallback

The business runs without this tool. The public number **786-975-9557 is
answered by a human**; there is no automated calling and no recording either
way. If Python breaks, write the call or text down on paper (date, lead ref,
what was asked) and append the lines by hand when the tool is back.

---

## Tests

```powershell
python -m pytest tools\comms\test_comms.py -q
```

19 tests: redaction of phones, emails, and addresses; the layered recording
refusals; the TwilioAdapter gates; from-ref validation; JSONL validity; and
proof that raw phone digits from a summary never reach the log. All data in
the suite is synthetic and the state dir is always a temp directory.

## Files

| File | Purpose |
|---|---|
| `adapter.py` | NullAdapter (dry run), TwilioAdapter skeleton, redaction, event log, CLI |
| `test_comms.py` | 19 tests, all synthetic |
