# Release, Monitoring, and Failure Handling

Scope: the bilingual inquiry triage deployment and the workflow around it.

---

## 1. How changes are tested

| Change | Check | State |
|---|---|---|
| Triage logic, extraction, drafting | `python -m pytest tools\triage\test_triage.py -q` — **43 tests, all passing** | **LIVE** |
| Validation gates | Negative tests assert each gate actually blocks: unlocked price, EN/ES mismatch, confirmation language (EN and accented ES), insurance claim, non-Zelle method, missing info without a question | **LIVE** |
| Log integrity | Tests assert drafts and message bodies never reach the log, records are never pre-approved, synthetic and production logs are separate files | **LIVE** |
| Slot confirmations | `python scripts\validate_slot_confirmations.py` — passing | **LIVE** |
| Price changes | Edit `pricing.json`, bump `price_list_version`, update `checkout.html` in the same commit, re-run tests | **LIVE-MANUAL** |
| Website pages | Opened locally before commit | **LIVE-MANUAL** |
| Prompt changes (AI mode) | Re-run the last real inquiries through the new version and diff the drafts before shipping | **PLANNED** |

**All test inquiries are synthetic** and write to a separate log. They never
count toward the 15-day requirement.

## 2. Who approves releases

**Marcelo Zapata — sole operator and sole committer in the repository history.** One
person proposes, tests, and approves. That is accurate for a business this size
and is stated rather than dressed up as a review board.

The checklist that governs a release is `docs/release-checklist.md`. Model
version is pinned explicitly; a model change is a deliberate release, never
automatic.

## 3. Pricing and bilingual parity checks

**Pricing.** `tools/triage/pricing.json` is the locked source of truth,
mirroring `checkout.html` as published. Gate G4 fails any draft containing a
figure outside `allowed_amounts`. The version stamp on every log line means any
draft can be traced to the exact price list that produced it.

`business/offer-and-pricing.md` is reconciled with `checkout.html` and the
locked list, including the Jingle, peak, school, HOA, photographer, late
Christmas Eve, and travel figures. The local submission validator checks every
customer-surface dollar figure against `pricing.json`.

**Bilingual parity.** The bilingual parity gate extracts money and duration tokens from both
drafts and compares them. Differing prices are a `FAIL`; differing durations a
`WARN`. An empty draft in either language is a `FAIL`. The rule: **the two
languages must carry identical commercial terms.** A Spanish quote stating a
different deposit than its English twin is a defect, not a translation choice.

## 4. Double-booking and capacity gates

| Gate | Rule | State |
|---|---|---|
| **G1** | No overlap with an existing booking once travel and setup are included. December traffic assumptions, not map times | `LIVE-MANUAL`, informed by the tool's risk flag |
| **G3** | Daily capacity limits; Christmas Eve sold in 45-minute slots, never two in one window | `LIVE-MANUAL` |
| Risk flag | Requested date scored against first-to-fill dates (Dec 12, 13, 19, 20, 24) and December weekend weighting | **`LIVE-AUTOMATED`** |
| Slot board | `business/december-slot-board.html` + `scripts/validate_slot_confirmations.py` | **LIVE** |

**Ordering rule:** capacity is checked before a price is quoted. A quote implies
availability, so availability is established first. The tool surfaces risk; the
operator reads the slot board and decides. **The tool never books.**

## 5. Missing payment handling

**Zelle only** — 305-244-0360. No processor, no card handling, no online payment
acceptance, no stored instrument. The system never moves money.

| Situation | Handling |
|---|---|
| No deposit received | Stays a hold. **Never confirmed.** G2 blocks it |
| Deposit claimed but not seen | Ask for the transfer confirmation. Do not confirm until it clears |
| Partial deposit | Stays a hold; resolved by message before confirming |
| Balance unpaid before event | Due on arrival per published terms; Christmas Eve balances collected before Dec 24 |
| Deposit received but slot gone | Refund immediately and in full, offer the nearest slot |

The tool is structurally incapable of saying a deposit was received — the unsafe-confirmation gate
blocks that phrasing in English and Spanish, accent-insensitively.

## 6. Incomplete customer information

Required before a quote: date, service category, location. Contact method is
tracked separately as a soft field.

Missing any required field produces an explicit question in the draft rather
than a quote against assumptions. If a draft omits required information *and*
fails to ask for it, `missing_information` returns `FAIL` and approval is
refused. A bare month is never treated as a date.

## 7. Model or subscription outage fallback

Handled automatically and logged honestly.

| Layer | Behavior |
|---|---|
| `MPN_MODEL` or key unset | Deterministic mode runs. `fallback_used: true`, `model: offline-rules-v1` |
| API error, timeout, bad JSON, or schema violation | Deterministic fallback. `error_code`: `MODEL_HTTP_ERROR`, `MODEL_UNAVAILABLE`, `MODEL_PARSE_ERROR`, `MODEL_SCHEMA_ERROR` |
| **Model returns a draft that fails a gate** | Deterministic fallback. `error_code: MODEL_OUTPUT_VALIDATION_FAIL`. The unsafe draft never reaches the operator |
| Tool unavailable entirely | Manual procedure in `tools/triage/README.md`, including the full price table, deposit terms, Zelle details, and the forbidden-language rules |
| Extended outage | Each manually handled inquiry gets a log line with `fallback_used: true`, `model: "manual"`, and an `error_code` naming the cause |

**The default path requires no network, no key, and no subscription.** A
reviewer seeing an honest fallback record should trust the rest of the log more,
not less.

## 8. Production monitoring

**Current state: the logging layer is built and tested; no production rows exist
yet** because the clock starts on the first real customer inquiry.

Per inquiry, automatically: `inquiry_id`, `received_at`, `channel`, `language`,
`requested_date`, `category`, `missing_fields`, `model`, `prompt_version`,
`price_list_version`, `reviewer`, `approved_at`, `sent_at`, `fallback_used`,
`outcome`, `error_code`.

Derived without extra tracking: inquiries handled, days in production, median
first-response time, share of drafts approved unedited, rejection rate,
validation blocks, fallback rate, language split, schedule-risk distribution.

    python tools\triage\triage.py --status

reports the first real inquiry, days elapsed, and the earliest qualification
date. **Never backdate the production clock.**

## 9. Audit trail and receipt reconciliation

Every inquiry produces one immutable line. Every payment gets a same-day record
and a one-line confirmation to the customer — the habit that prevents nearly
every payment dispute.

Reconciliation keeps date, type (deposit/balance), amount, method (Zelle),
payer, and the event it belongs to, so any booking can be answered with "paid,
this date, this amount" without relying on memory in mid-December.

## 10. Privacy and customer-data handling

| Rule | State |
|---|---|
| No customer data in Git | **Enforced.** Trackers hold placeholder/prospect rows only; no names, phones, emails, or addresses committed |
| Production logs outside the repository | **Enforced.** Default `%LOCALAPPDATA%`; `.gitignore` excludes `*.jsonl` except the redacted example |
| No secrets in Git | **Enforced.** `.gitignore` covers `.env`, `.env.*`, `*.pem`, `*.key`. None tracked, none in the working tree |
| Message and draft bodies never stored | **Enforced and tested** (`test_log_line_excludes_draft_bodies`) |
| Coarse location only | **Enforced.** Area name, never a street address |
| Contact value never logged | **Enforced.** Only whether a phone or email was supplied |
| Committed examples synthetic or redacted | **Enforced.** `examples/inquiry-redacted.jsonl` is synthetic |
| Photographs of children require written parental permission | `LIVE-MANUAL` |
| Data minimalism | Name, one contact method, event address, date. Nothing more |

## 11. Open safety items

The pre-implementation audit found three items. All three are resolved in the
current working tree; the validator keeps them from regressing:

1. **Insurance language on customer surfaces — RESOLVED in this working tree.**
   `checkout.html` now uses policy-neutral copy, and
   `business/content-engine.html` no longer contains ready-to-send insurance
   claims. `business/insurance-and-wave1-preflight.md` remains the authority
   before any insurance or COI language is restored.
2. **Non-Zelle methods recommended internally — RESOLVED.**
   `business/account-setup-checklist.md` now lists Zelle only and explicitly
   prohibits Cash App, Venmo, Square, Stripe, card, and wire instructions.
3. **Pricing documentation — RESOLVED.** `business/offer-and-pricing.md`,
   `checkout.html`, and `tools/triage/pricing.json` share the locked rate card.
