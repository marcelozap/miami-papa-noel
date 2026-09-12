# Release Checklist

Run before any change to the triage tool, the price list, or customer-facing
copy reaches real inquiries. Approver: Marcelo Zapata.

---

## Every release

Run checks with paid generation explicitly disabled in the check shell:

```powershell
$env:MPN_API_DAILY_CALL_CAP = '0'
$env:OPENAI_API_KEY = ''
$env:MPN_API_COST_POLICY = ''
$env:MPN_MODEL = ''
python -B scripts\ops_check.py
```

This changes only that shell's environment. All registered suites must pass.
Any demo below must use that same offline shell. Never treat a release
checklist as authorization for paid replays, customer sends, or deployment.
**Stale as of 2026-09-11:** the September 8 release described in
docs/release-handoff.md shipped. Publication now goes through an up-to-date
`main` as described in START-SANTA.md, "Update the website". Do not push to
codex/santa-checkpoint-2026-09-04. If github.com still shows PR #1 open, it
is stale; closing it without merging loses nothing, because `main` already
contains newer work.

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
- [ ] Synthetic regression cases run first with mocked APIs. Any later replay of real inquiries requires privacy review and explicit spending authorization; do not duplicate sends or production evidence.
- [ ] Deterministic fallback still works with `MPN_MODEL` unset
- [ ] If the release enables or changes a live model, a separately authorized bounded model test verifies its identity and gates. Synthetic checks never start production evidence.

## Copy and safety review

- [ ] No draft output can contain "confirmed", "booked", "reserved", "deposit received", or the Spanish equivalents
- [ ] No insurance language unless `business/insurance-and-wave1-preflight.md` records a **verified active policy**
- [ ] `business/wave1-batch-01.md` passes the outreach-surface scan before sending
- [ ] Official rails only anywhere customer-facing: Zelle to 305-244-0360; the business's own buy.stripe.com Payment Link once the operator creates it (adopted 2026-08-30, not yet live). All other methods prohibited
- [ ] English and Spanish state identical prices, deposits, and durations
- [ ] Every quoted figure appears in `pricing.json`

## Website changes

- [ ] Page opened locally and checked
- [ ] Prices match `pricing.json`
- [ ] Official rails only: Zelle to 305-244-0360; the business's own buy.stripe.com Payment Link once the operator creates it (adopted 2026-08-30, not yet live). All other methods prohibited
- [ ] No insurance claim unless the policy is verified
- [ ] Canonical URL and language toggles intact

## Rollback

Disable paid generation first. Do not reset or check out over unfinished work.
Keep private logs, accounting, and backups outside version control and preserve
them during rollback. An older code revision may lack the current spending
guard, so never re-enable paid calls merely because that revision starts.

- [ ] Previous commit identified before merging
- [ ] Manual fallback in `tools/triage/README.md` is current — it is the real rollback

If a release goes wrong mid-season, stop using the tool and work manually. The
business does not depend on it, and that is the point.

---

## Sign-off

**Historical (2026-09-08):** Owner decision received: approve launch preparation and publication to
codex/santa-checkpoint-2026-09-04, including its update to PR #1. The decision
initially referred to 22 paths; the owner subsequently confirmed all 24 paths
in the current inventory for commit and push, including PR #1. Keep paid generation disabled
until the API 429 root cause is resolved and spending is separately approved.
No production customer sends or deployment actions are authorized. A passing
offline check or draft evidence packet does not establish production Day 1.

| Field | Value |
|---|---|
| Release date | |
| Change summary | |
| Tests passing | ☐ |
| Price list version | |
| Prompt version | |
| Model id | |
| Approved by | |
