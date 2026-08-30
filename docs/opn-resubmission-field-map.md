# OPN Resubmission Field Map

This is the operator's map for the OpenAI Partner Network Technical Capability
Assessment marked **Resubmission Requested**. It points each form section to the
evidence and repository record that belong there. It is a preparation guide,
not a substitute for the facts in the external evidence folder.

## 1. Production AI/ML Delivery

Use **Add deployment** for the Miami Papa Noel deployment only if it was a real
production workflow. Use the exact operating-business name shown by the
records. Describe the ownership accurately: Marcelo Zapata operated the
workflow; do not describe Miami Papa Noel as an unrelated external customer
unless a separate-entity agreement or counterparty statement supports that.

Enter only values supported by records for usage frequency, users, and volume.
Do not increase the production-project count merely because a design or mockup
exists.

## 2. Describe a recent AI use case

This is the primary resubmission field. Describe the end-to-end workflow as one
bounded use case:

1. **Deployment:** Miami Papa Noel seasonal operations.
2. **Status and dates:** the actual period in which the workflow was used in
   real operations; call it seasonal or between seasons when that is accurate.
3. **Operational owner:** Marcelo Zapata.
4. **Live functionality:** marketing and content creation, lead and message
   handling, bilingual drafting, call preparation, scheduling and logistics,
   payment-receipt tracking, and follow-up, limited to the functions that the
   records support.
5. **Production model:** the exact model name or names that actually ran. Do
   not guess from a tool brand or from a later configuration.
6. **How it worked:** inquiry and content task intake flowed through role-based
   steps; the operator reviewed customer-facing work before sending or acting.
7. **Outcome:** one defensible number or concrete result from the records.
8. **Evidence:** identify which dated messages, screenshots, receipts, or
   counterparty statement support each claim.

The phone call is one channel in this workflow, not the whole use case. Free or
pro-bono work can still be real production work; the price is not the test.

## 3. Delivery Methodology

Keep the existing founder-led methodology if it is accurate: workflow mapping,
role specification, implementation, testing, documentation, training, and
client or operator enablement. Add the Santa workflow as a concrete example,
not as a claim that every role was autonomous.

## 4. Governance and Responsible AI

Identify the real operator and explain the controls that were actually used:
human review before customer-facing actions, privacy protection, locked
pricing, Zelle-only payment language, no unsupported insurance claims, and
manual fallback when an agent or tool was unavailable. Point to the release and
failure-handling documentation.

## 5. Supporting Evidence

Upload only evidence that is permitted and redacted:

- dated receipts or booking records for real business activity
- dated message or content history showing AI-assisted work
- screenshots of the workflow in use
- a dated statement from the Santa company or counterparty

Receipts establish real operations; they do not by themselves prove that AI
processed the work. Keep those claims in separate evidence rows. Never upload
customer names, phone numbers, emails, addresses, Zelle memos, account
identifiers, or children's faces.

## 6. Before submitting

1. Run `python scripts\validate_opn_submission.py --preflight`.
2. Add and hash each redacted external artifact with
   `scripts\evidence_index.py`.
3. Replace submission fields only from dated records and the exact model log.
4. Wait until the production record shows at least 15 days of operation.
5. Run `python scripts\validate_opn_submission.py --final`.
6. Build the final ZIP only after final validation passes, then verify its
   manifest and hashes.

Until those steps pass, submit the current status honestly rather than
converting a design into a production claim.
