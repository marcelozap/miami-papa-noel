# Miami Papa Noel Coordination Rules

This repository is the Miami Papa Noel seasonal operations lane. Read this file and `docs/santa-agent-workboard.md` before every turn.

## Shared coordination

- The common coordination file is `C:\Users\Green Machine\miami-papa-noel\docs\santa-agent-workboard.md`.
- At the start of every turn, read the workboard, run `git status --short --branch`, and inspect recent commits.
- Claim one work item before editing. Do not edit a file already claimed by another worker.
- Record the files changed, tests run, blockers, and next status in the workboard after each meaningful step.
- Use statuses `PLANNED`, `IN_PROGRESS`, `READY_FOR_REVIEW`, `VERIFIED`, `COMMITTED`, and `BLOCKED`.
- A worker marked `READY_FOR_REVIEW` must not change its implementation until the coordinator has reviewed the diff and tests.
- Never use a destructive Git command. Preserve unrelated user changes and the in-progress `tools/slots/` work.

## Operating boundaries

- Public phone/text/WhatsApp: `786-975-9557`.
- Zelle deposit destination only: `305-244-0360`.
- Official booking email: `santa@miamipapanoel.com`.
- A booking is sold only at `BOOKED` after a human verifies the 50% Zelle deposit.
- Never invent prices, customers, affiliations, testimonials, model usage, or payment confirmation.
- Use synthetic fixtures only. Never commit customer data, call recordings, transcripts, payment records, API keys, or `.env` files.
- Do not send messages, record calls, post content, change DNS, charge money, or alter external accounts from a coding task.
- Do not touch GateKPT, MaloSound, or unrelated XIV projects.

## Verification contract

After every implementation step, run the narrow tests first, then the full suite. Review the diff for privacy, pricing, bilingual parity, and accidental public claims. Do not declare completion until the workboard acceptance checklist is green.
