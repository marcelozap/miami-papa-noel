# Sample inquiry run — 2026-09-04 (synthetic, offline)

One inquiry through the complete triage process, end to end, plus the four built-in demo inquiries. Purpose: a concrete basis for deciding what to change and what is finished for this version. No customer data. Nothing was sent. The production log was not touched (`--status` reports NOT STARTED before and after).

## What ran

| Item | Result |
|---|---|
| Runtime | `C:\XIV\santa`, system Python 3.10, `OPENAI_API_KEY` and `MPN_MODEL` empty (deterministic mode by design of this check) |
| Tests | `python -m pytest tools/triage/test_triage.py -q` → 45 passed |
| Demo | `python tools/triage/triage.py --demo` → 4 synthetic inquiries, all six gates PASS or WARN, logged to the synthetic log only |
| One inquiry through approval | Spanish WhatsApp message: family party, 20 Dec, Doral, 12 people, 5 children. Extracted: `es`, `2026-12-20`, `Doral`, schedule risk high (first-to-fill date). Draft produced in EN and ES. Gates: 6/6 PASS. Approval prompt → `APPROVE` recorded with reviewer `synthetic-check`; second prompt answered "no" → outcome `approved_awaiting_send`, `sent_at` null. Record `MPN-20260904-0F8F5F`, `real_customer: false`, `model: offline-rules-v1`, `fallback_used: true`, `price_list_version 2026-08-28.1`. |
| Where it is saved | `%LOCALAPPDATA%\MiamiPapaNoel\triage\synthetic-log.jsonl` (9 rows after this run). Production log untouched. Console captures in the session scratchpad. |

The process works: message in, language and fields out, bilingual draft, six gates, human approval, honest send status, saved record. That part is finished for this version.

## Problems observed (specific, in priority order)

1. **A family party is priced as an Event Visit.** The message said "fiesta familiar" (family party) and was categorized `event_visit` at $450 instead of `family_visit` at $325. Cause: `tools/triage/triage.py` `CATEGORY_RULES` are matched in order and the first hit wins; the `event_visit` rule ("party", "fiesta", "evento", ...) sits above the `family_visit` rule ("home", "family", "familia", "casa", "cumpleaños", ...). Any home birthday described as a "party" or "fiesta" will be quoted $125 too high. This is a customer-facing pricing error, and the `pricing` gate cannot catch it because $450 is a locked amount. Fix options: score all rules and prefer `family_visit` when a home or family word is present, or ask the customer when both match instead of quoting.

2. **Drafts promise a payment link that does not exist.** Every draft says "Deposits are by Zelle or our secure online payment link" (ES: "por nuestro enlace de pago seguro"). Source: `tools/triage/pricing.json` deposit text, method "Zelle or Stripe payment link". The workboard lists the public Stripe link as an external dependency that has not been created, and the README still describes "Zelle-only terms". The `payment_method` gate reports `PASS  Zelle only` because it only blocks named competitors, so the mismatch passes silently. Until the link exists, the sentence should be Zelle only, and the gate's PASS label should not say "Zelle only" when the text says otherwise.

3. **Spanish drafts have no accents.** "depositos", "dias", "asi", "telefono", "Papa Noel" in customer-facing copy. Cause: the ES strings in `pricing.json` and the draft templates are written without accents. The validators are already accent-insensitive, so adding accents breaks nothing.

4. **Headcount and gifts are not captured or asked.** The message gave 12 people and 5 children; the record has no headcount field and the draft does not ask about headcount or whether gifts are provided, although the manual procedure lists both as step-one facts. The two missing-information questions asked were phone/email only.

5. **Timestamps carry no timezone.** `received_at`, `approved_at`, `sent_at` are local time via `now.isoformat(timespec="seconds")` with no offset. For a dated evidence log this should be explicit (America/New_York with offset, or UTC).

6. **Prices are quoted before any availability check when date or location is missing.** Demo inquiries with no date still received a full price quote; the gate only WARNs. The draft's "I will check availability and come back to you" softens it, but the manual procedure says a quote implies availability. Consider withholding the price until a date is known, or making the WARN a FAIL for the no-date case.

7. **The AI-assisted path was not exercised.** With no `MPN_MODEL` and no key, every row is `fallback_used: true`, `model: offline-rules-v1`. That is correct behavior, and it means the model-backed draft, the schema validation, and the fallback-on-bad-output path still need one observed run from the operator's configured terminal before "AI-assisted" is a verified claim. `docs/production-launch.md` already says this.

## What is finished for this version

Language detection, date/category/location extraction for well-formed messages, bilingual drafting from the locked list, the six gates with real blocking behavior (45 tests), the two-step approve/sent prompts that never assume a send, separate synthetic and production logs, and the production clock.

## What to change before the first real inquiry

Items 1 and 2 above. They are the two that would put a wrong statement in front of a customer. Item 3 is cheap and worth doing at the same time. Items 4 to 7 are for the next version.

Run by the XIV session (local_1c36dd26) on 2026-09-04, 20:00 New York, in synthetic mode. Nothing in this repository was modified by the run itself; this document is the only file added.
