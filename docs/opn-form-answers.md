# OPN Resubmission - Finished Form Copy

Final text for the Technical Capability Assessment resubmission. Companion to
`docs/opn-resubmission-field-map.md` (which explains where each piece goes).
Facts here are the operator's record per
`docs/operator-attestation-2025-season.md`; the evidence uploads that
corroborate them are assembled per `docs/evidence-intake.md`.

---

## Use case (primary field)

> **Miami Papa Noel — themed agent workflow for a seasonal bilingual service
> business**
>
> Miami Papa Noel provides Santa visits across Miami: hospitals, Miami-Dade
> County sites, Publix locations, fire and police departments, and local
> families. The performers are experienced but not technical and had no system
> for intake, communications, scheduling, or follow-up.
>
> I proposed the system, built it, and operated it as sole technical and
> operational owner. The client performs the service; the workflow and its
> daily operation are mine.
>
> **Architecture.** Rather than a single assistant, I built a set of themed
> agent workflows mapped to business functions — Santa, Mrs. Claus, and the
> elves — each owning one lane of the operation. The theming was deliberate:
> it held every customer-facing message in a consistent voice appropriate to
> the service, and it let non-technical performers understand and trust the
> system because it was described in terms they already knew.
>
> **Pipeline:** marketing and content generation -> lead intake -> bilingual
> (EN/ES) client communications -> lead summarisation into pre-visit briefs ->
> scheduling and logistics -> payment and receipt tracking -> post-visit
> follow-up.
>
> **Where AI did the work:** managing client communications, generating
> marketing content, summarising incoming leads into pre-visit briefs, and
> drafting follow-ups — in English and Spanish. Miami is a bilingual market,
> and institutional bookings and family bookings need different registers in
> both languages; that drafting and adaptation load is what the system removed.
> I reviewed every customer-facing message before it sent. Scheduling,
> logistics and payment tracking were operated by me, with the agent workflows
> supporting intake and communications around them.
>
> **Outcome:** 14 visits across a 40-day operating season, spanning hospitals,
> county sites, retail, emergency services and private families. The
> operational load moved off the performers entirely — Santa shows up and
> performs, and nothing else lands on him. The client is running it again for
> the 2026 season, with the workflow being extended to formalised booking
> intake and a verified business listing.

## Deployment entry

> **Miami Papa Noel**
> Seasonal production deployment — currently between seasons, ramping for the
> 2026 season.
> Live **15 November 2025 - 24 December 2025 (40 days)**.
> Frequency: per-booking across the active season; 14 visits delivered.
> Operational owner: **Marcelo Zapata — built and operated.**

## Form-entry guards

Read these before typing anything into the form:

- **Duration and volume are different numbers. Never let them swap.**
  Duration = **40 days** (Nov 15 - Dec 24, 2025, inclusive). Volume =
  **14 visits**. Writing 14 in a duration field fails a bar the deployment
  clears by nearly 3x.
- **Status wording:** "2025 production deployment completed; 2026 seasonal
  reactivation in progress." Do not write "currently active" — it is not
  operating today, and between-seasons is the accurate state.
- **Production model:** enter only the exact model name the records show ran
  in 2025. If the records do not name one, leave the field blank rather than
  guess — it is the field a technical reviewer checks hardest.
- **Confirm 14 is exact** against the records before submitting. A precise
  number you can evidence beats "around 14."
- **Do not pad the volume.** The review tests whether the workflow was real,
  in production, and ran 15+ days. 40 days and 14 visits clear all three;
  padding is the only way to lose.
- **Best single upload:** one dated message thread spanning several days,
  ideally coordinating an institutional booking — it proves duration and
  production use in one artifact. Redact patient names, children's faces,
  room numbers, department contacts, and phone numbers; keep the dates and
  the volume visible.
- **Mark every pipeline step AI-driven, AI-assisted, or manual before
  claiming it.** The copy above claims AI only for communications, content,
  lead summarisation, and follow-up drafting; scheduling, logistics, and
  receipt tracking are described as the operational surround. Describing a
  manual step as AI is the fastest way to sink an otherwise-strong
  application.
- **2026 improvements** (Google Business profile, formalised booking intake)
  belong in the forward-looking line only. Last season's entry describes last
  season.

## Pre-submission checklist

- [ ] 14-visit count confirmed exact against records
- [ ] Redacted message thread selected and indexed via `scripts\evidence_index.py`
- [ ] Model field filled from records, or left blank
- [ ] `python scripts\validate_opn_submission.py --preflight` passes
- [ ] Status wording matches this document everywhere it appears
