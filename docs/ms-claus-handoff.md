# Ms. Claus seasonal operations handoff

Updated 2026-09-01 for the Miami Papa Noel seasonal workflow.

## Current operating rules

- Public calls, texts, and WhatsApp use `786-975-9557`.
- Customer deposits remain Zelle-only to `305-244-0360`.
- A booking request is not a booking confirmation. The operator verifies availability, the 50% deposit, and the required site conditions before confirming.
- The request path asks for a sturdy armless chair, air conditioning, a designated adult for gifts and the photo queue, and parking within 100 feet.
- No customer data was added by this work. Do not put names, phone numbers, addresses, payment memos, screenshots, or message bodies in git.

## Ms. Claus command

Run from the repository root:

```powershell
python tools\ms_claus\ms_claus.py --strict
```

The command is local and read-only. It scans deployed root HTML pages and reports:

- stale public contact numbers, while allowing the old number in Zelle instructions;
- unapproved payment methods;
- insurance wording that needs verification;
- booking requirements missing from checkout;
- one human-approved next change.

Machine-readable output is available with `--json`.

## Verification

```powershell
python -m pytest tools\ms_claus\test_ms_claus.py tools\triage\test_triage.py scripts\test_validate_opn_submission.py scripts\test_evidence_index.py scripts\test_build_opn_packet.py -q
python scripts\validate_slot_confirmations.py
python scripts\validate_opn_submission.py --preflight
```

Last verified result: **72 tests passed**, slot validation passed, and OpenAI preflight returned **0 blocking findings** with the existing evidence and production-clock warnings.

## Git safety

The worktree already contains unrelated website and deployment edits. Do not run `git add .`.

Before committing, inspect:

```powershell
git status --short
git diff --check
git diff -- tools\ms_claus business\ms-claus-structure-agent.md docs\ms-claus-handoff.md
```

The new Ms. Claus files are safe documentation/code with synthetic tests only. Review the website phone and booking-form hunks separately before staging them. Keep `lead-tracker.csv`, production logs, and evidence artifacts out of commits.

## Deliberate boundaries

Ms. Claus does not send customer messages, record calls, confirm bank deposits, edit the website, publish social posts, or post to job boards. Those actions require an explicit operator step and, where applicable, a separate approved provider integration.
