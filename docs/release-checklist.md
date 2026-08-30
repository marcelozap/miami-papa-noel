# Release Checklist

Run before any change to the triage tool, the price list, or customer-facing
copy reaches real inquiries. Approver: Marcelo Zapata.

---

## Every release

- [ ] `python -m pytest tools\triage\test_triage.py -q` — all tests pass
- [ ] `python scripts\validate_slot_confirmations.py` — passes
- [ ] `python scripts\validate_opn_submission.py --preflight` — package and safety checks pass
- [ ] Before any OPN submission: `python scripts\validate_opn_submission.py --final` must PASS - never submit around a FAIL
- [ ] `python tools\triage\triage.py --demo` — four synthetic inquiries render, all gates PASS
- [ ] `git status --short` reviewed — no `.jsonl`, `.env`, `.pem`, or `.key` staged
- [ ] `git diff --cached` reviewed — no customer name, phone, email, or street address
- [ ] No production log file staged (`*.jsonl` is git-ignored except the redacted example)
- [ ] External evidence index, when present, passes the validator and remains outside Git
- [ ] `scripts\evidence_index.py` used for each redacted artifact; no manual hash entry

## Price changes

- [ ] `tools/triage/pricing.json` updated
- [ ] `price_list_version` bumped
- [ ] `checkout.html` updated in the **same commit** — the tool mirrors the published page
- [ ] `business/offer-and-pricing.md` reconciled
- [ ] `tools/triage/README.md` manual fallback table updated
- [ ] Tests re-run; `--demo` output shows the new figures
- [ ] `allowed_amounts` contains every figure that can appear in a draft

## Prompt or model changes

- [ ] `PROMPT_VERSION` bumped in `triage.py`
- [ ] `MPN_MODEL` set to an **exact** model id — never a guess, never a family name
- [ ] Last 20 real inquiries re-run through the new version, drafts diffed and reviewed
- [ ] Deterministic fallback still works with `MPN_MODEL` unset
- [ ] Model id appears correctly in a fresh log line before shipping

## Copy and safety review

- [ ] No draft output can contain "confirmed", "booked", "reserved", "deposit received", or the Spanish equivalents
- [ ] No insurance language unless `business/insurance-and-wave1-preflight.md` records a **verified active policy**
- [ ] Zelle is the only payment method mentioned anywhere customer-facing
- [ ] English and Spanish state identical prices, deposits, and durations
- [ ] Every quoted figure appears in `pricing.json`

## Website changes

- [ ] Page opened locally and checked
- [ ] Prices match `pricing.json`
- [ ] Zelle-only; no Cash App, Venmo, Square, Stripe, or card language
- [ ] No insurance claim unless the policy is verified
- [ ] Canonical URL and language toggles intact

## Rollback

- [ ] Previous commit identified before merging
- [ ] Manual fallback in `tools/triage/README.md` is current — it is the real rollback

If a release goes wrong mid-season, stop using the tool and work manually. The
business does not depend on it, and that is the point.

---

## Sign-off

| Field | Value |
|---|---|
| Release date | |
| Change summary | |
| Tests passing | ☐ |
| Price list version | |
| Prompt version | |
| Model id | |
| Approved by | |
