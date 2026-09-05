# Miami Papa Noel Coordination Rules

This repository is the Miami Papa Noel seasonal operations lane. Read `C:\XIV\START_HERE.md`, this file, and `docs/santa-agent-workboard.md` before every turn.

## Shared coordination

- Relocation completed 2026-09-04: the repository lives at `C:\XIV\santa` and the shared workboard is `C:\XIV\santa\docs\santa-agent-workboard.md`. The old `C:\Users\Green Machine\miami-papa-noel` directory is empty except for a `MOVED.md` pointer; do not recreate files there.
- Follow `C:\XIV\START_HERE.md` for the checked move. Checkpoint active workers first; carry the existing Git history, edits, private local data, and workboard together. Do not create a second independent workboard or overwrite another worker's files.
- At the start of every turn, read the workboard, run `git status --short --branch`, and inspect recent commits.
- Claim one work item before editing. Do not edit a file already claimed by another worker.
- Record the files changed, tests run, blockers, and next status in the workboard after each meaningful step.
- Use statuses `PLANNED`, `IN_PROGRESS`, `READY_FOR_REVIEW`, `VERIFIED`, `COMMITTED`, and `BLOCKED`.
- A worker marked `READY_FOR_REVIEW` must not change its implementation until the coordinator has reviewed the diff and tests.
- Never use a destructive Git command. Preserve unrelated user changes and the in-progress `tools/slots/` work.

## Operating boundaries

- Public phone/text/WhatsApp: `786-975-9557`.
- Approved deposit rails: Zelle to `305-244-0360` and Stripe-hosted Payment Links only.
- Official booking email: `santa@miamipapanoel.com`.
- A booking is sold only at `BOOKED` after a human verifies the 50% deposit in Zelle or Stripe.
- Stripe bank details, login credentials, and secret keys stay inside Stripe or deployment secrets. Only a public `buy.stripe.com` Payment Link may enter this repository.
- Never invent prices, customers, affiliations, testimonials, model usage, or payment confirmation.
- Use synthetic fixtures only. Never commit customer data, call recordings, transcripts, payment records, API keys, or `.env` files.
- Do not send messages, record calls, post content, change DNS, charge money, or alter external accounts from a coding task.
- Do not touch the separate GateKPT or MaloSound repositories, or unrelated XIV projects. The Santa repo may maintain a local MaloSound adapter boundary, but must not invent an endpoint or claim that the external integration is live without evidence.

## Verification contract

After every implementation step, run the narrow tests first, then the full suite. Review the diff for privacy, pricing, bilingual parity, payment-rail accuracy, and accidental public claims. Do not declare completion until the workboard acceptance checklist is green.
