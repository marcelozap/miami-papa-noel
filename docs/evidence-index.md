# Evidence Index

Every claim in this package traced to a source. Audited 2026-08-29 by direct
inspection of the repository, its git history, and the runnable tool.

**Status legend:** `VERIFIED` = confirmed in a file or a passing test ·
`ATTESTED` = operator's record, evidence in assembly · `[TO FILL]` = resolves
with production use · `N/A` = does not exist

---

## The deployment (2026 season)

| Claim | Source | Date | Status |
|---|---|---|---|
| Triage tool exists and runs | `tools/triage/triage.py`, `--demo` executed end to end | 2026-08-29 | VERIFIED |
| Detects English and Spanish | `test_detects_spanish`, `test_detects_english` | 2026-08-29 | VERIFIED |
| Extracts dates in EN, ES, and ISO formats | `test_extracts_date_*` (3 tests) | 2026-08-29 | VERIFIED |
| Does not guess a date from a bare month | `test_bare_month_is_not_treated_as_a_date` | 2026-08-29 | VERIFIED |
| Extracts category, location, contact status | `test_category_*`, `test_extracts_location`, `test_contact_status_phone` | 2026-08-29 | VERIFIED |
| Flags schedule risk on first-to-fill dates | `test_high_risk_date_flagged` | 2026-08-29 | VERIFIED |
| Drafts in both languages with matching terms | `validate_bilingual_parity`, `test_validator_catches_price_mismatch_between_languages` | 2026-08-29 | VERIFIED |
| Quotes only locked prices | `test_validator_rejects_unlocked_price`, `pricing.json` v`2026-08-28.1` | 2026-08-29 | VERIFIED |
| Never confirms a booking | `test_draft_never_confirms_booking`, `test_validator_catches_confirmation_language_*` | 2026-08-29 | VERIFIED |
| Never claims a deposit was received | accent-insensitive block on "deposit received" / "depósito recibido" | 2026-08-29 | VERIFIED |
| Never promises insurance while unverified | `test_draft_never_mentions_insurance` | 2026-08-29 | VERIFIED |
| Zelle only | `test_draft_is_zelle_only` | 2026-08-29 | VERIFIED |
| No send path to a customer exists | `triage.py` has no customer-channel integration; approval only marks a record. The only network call is to the OpenAI API in opt-in AI mode | 2026-08-29 | VERIFIED |
| Model output is re-validated before an operator sees it | `model_triage()` runs all six gates on model drafts and falls back on any FAIL | 2026-08-29 | VERIFIED |
| Inquiry text sent to the API in AI mode only | `call_openai_triage()` with `store: false`; deterministic mode makes no network call | 2026-08-29 | VERIFIED |
| Records never pre-approved | `test_new_record_is_never_pre_approved` | 2026-08-29 | VERIFIED |
| Log excludes message and draft bodies | `test_log_line_excludes_draft_bodies` | 2026-08-29 | VERIFIED |
| Synthetic and production logs separate | `test_synthetic_and_production_logs_are_separate_files` | 2026-08-29 | VERIFIED |
| Full test suite passes | `python -m pytest tools/triage/test_triage.py -q` → **45 passed** | 2026-08-30 | VERIFIED |
| Existing repo validator still passes | `python scripts/validate_slot_confirmations.py` → "Slot validation passed." | 2026-08-29 | VERIFIED |
| Production launch date | first `--real` log line | — | `[TO FILL]` |
| Model actually run in production | `model` field on the log | — | `[TO FILL]` |
| Measured outcome | derived from the log | — | `[TO FILL]` |

## Business and website

| Claim | Source | Date | Status |
|---|---|---|---|
| Business performs real events | `assets/extra/IMG_20221224_*.jpg` | 2022-12-24 | VERIFIED |
| Repeat seasonal operation | `assets/extra/20231210_*.jpg`, `20231214_*.jpg` | 2023-12-10, 2023-12-14 | VERIFIED |
| Public website | 28 tracked HTML pages incl. `index`, `book`, `checkout`, `christmas-eve`, `hoa-apartments`, `schools-daycares`, `service-areas`, `partners`, `reviews`, `after-visit` | 2026-08-28 | VERIFIED |
| Domain | `miamipapanoel.com` (canonical tags in `checkout.html`) | 2026-08-28 | VERIFIED in source; live uptime `[TO FILL]` |
| Published price list | `checkout.html` — $195 / $325 / $450 / $425 / $500 / $375 / $550 / $275 / $600 / $850, travel $45 | 2026-08-28 | VERIFIED |
| Deposit terms | `checkout.html` — 50% non-refundable, balance on arrival | 2026-08-28 | VERIFIED |
| Zelle-only payment | `checkout.html` — "Zelle to 305-244-0360" | 2026-08-28 | VERIFIED |
| Sustained development | 77 commits, single committer | 2026-06-10 → 2026-08-29 | VERIFIED |
| Booking procedure formalized | `business/booking-sop.md` | 2026-06-10 | VERIFIED |
| Bilingual reply library | `business/lead-reply-bank.md` | 2026-06-15 | VERIFIED |
| Role architecture: Scout, Dispatcher, Concierge, Bookkeeper | `business/AGENT-ROLES.md` | 2026-08-26 | VERIFIED |
| Seasonal ops workflow documented | `business/seasonal-ops-workflow.md` | 2026-08-28 | VERIFIED |
| Slot board and confirmation validator | `business/december-slot-board.html`, `scripts/validate_slot_confirmations.py` | 2026-08-28 | VERIFIED |

## Prior season (2025)

| Claim | Source | Status |
|---|---|---|
| Role-based workflow operated during the 2025 Christmas season, supporting real inquiries, bilingual drafting, booking coordination, outreach, payment tracking, logistics and follow-up | `docs/operator-attestation-2025-season.md` | **ATTESTED** — operator's record, dated 2026-08-29 |
| Season window, channels, volume, model used, concrete outcome | attestation evidence table, fields 1-10 | `[TO FILL]` — artifacts sit in message history, calendar, and payment records outside this repository, which began 2026-06-10 |

## Pre-implementation safety audit

Findings from the required checks. Two are resolved in this working tree; one remains open.

| Check | Result |
|---|---|
| Private customer data in repo | **CLEAN** — `lead-tracker.csv` and `miami-prospect-expansion.csv` hold placeholder/prospect rows; no customer names, phones, emails, or addresses committed |
| API keys, `.env`, certificates, `.pem` | **CLEAN** — none tracked, none in the working tree. `.gitignore` now excludes `.env`, `.env.*`, `*.pem`, `*.key`, `*.jsonl` |
| Production logs excluded from Git | **RESOLVED** — logs default to `%LOCALAPPDATA%`, and `*.jsonl` is git-ignored except the redacted example |
| **Unverified insurance claims** | **RESOLVED in this working tree** — `checkout.html` and `business/content-engine.html` use policy-neutral wording. `business/insurance-and-wave1-preflight.md` remains the authority before any insurance or COI language is restored |
| **Non-Zelle payment methods** | **RESOLVED** — `business/account-setup-checklist.md` now lists Zelle only and prohibits Cash App, Venmo, Square, Stripe, card, and wire instructions |
| **Pricing inconsistency** | **RESOLVED** — `business/offer-and-pricing.md`, `checkout.html`, and `tools/triage/pricing.json` contain the same locked rate card, including $195, $425, $275, $550, $600, $850, and $45 travel |
| Automation overclaims | **CLEAN in this package** — no phone, WhatsApp, payment, or autonomous-agent automation is claimed anywhere. `business/AGENT-ROLES.md` describes operating roles performed by a human, and is not presented as running software |

## Privacy status

No redaction was required for this package. The committed example log is
synthetic. The tool never stores inquiry text or draft bodies, records only a
coarse area rather than a street address, and records whether a phone or email
was supplied rather than its value.
