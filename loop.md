# Santa Build Loop

This is the local Claude Code loop for Miami Papa Noel. The reservation record is
the source of truth; content and outreach are downstream of confirmed bookings.

Every loop iteration must follow this order:

1. Read `C:\XIV\START_HERE.md`. The Santa repository relocated to `C:\XIV\santa` on 2026-09-04 (verified: Git history, workboard, and full test suite present). Read `CLAUDE.md` and `docs/santa-agent-workboard.md` from `C:\XIV\santa`. Never start a second workboard elsewhere.
2. Inspect `git status --short --branch`, recent commits, and any current claims.
3. If another worker owns a file, do not touch it. Choose the highest-priority unclaimed item and record the claim on the shared workboard.
4. Implement one coherent slice of work. Do not stop at a plan or a progress note.
5. Run focused tests, then the full relevant test suite.
6. Review the diff, public surfaces, privacy, pricing, payment rails, route feasibility, and English/Spanish parity.
7. Update the workboard with the exact files, tests, result, and status.
8. Mark work `READY_FOR_REVIEW` before a coordinator reviews it. Only the coordinator may mark it `VERIFIED` or `COMMITTED`.

The build is complete only when every acceptance item in the workboard is `VERIFIED` and the final test command passes. If an external provider or credential is needed, implement a local dry-run adapter, document the one manual setup step, and continue with all locally achievable work. Stripe bank details and secret keys are never accepted in chat or committed files; only a real public Stripe Payment Link may be wired into public pages. MaloSound work in this repo is an adapter boundary or draft-only content lane unless a real endpoint and tested credential are supplied outside the repository.

Priority order for the next unclaimed slice:

1. Close reservation and route blockers that could cause double-booking or an impossible drive.
2. Finish safe Stripe Payment Link wiring only when a real public link exists; never add a fake link.
3. Keep Mrs. Claus replies bilingual, informational, and unable to confirm payment or availability.
4. Generate MaloSound-backed content drafts from confirmed reservations only; human approval remains required before posting.
5. Re-run the OPN preflight and update the evidence checklist without inventing a model, receipt, date, or outcome.

Never send customer messages, record calls, publish social content, change DNS, charge money, or claim live integration without explicit operator approval and a real tested connection. Do not push Git unless the operator explicitly authorizes it.
