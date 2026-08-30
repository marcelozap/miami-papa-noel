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
> county sites, retail, emergency services and private families — up from a
> previous seasonal maximum of approximately 5 visits, per the owner's written
> confirmation. The operational load moved off the performers entirely —
> Santa shows up and performs, and nothing else lands on him. The client is running it again for
> the 2026 season, with the workflow being extended to formalised booking
> intake and a verified business listing.

## Deployment entry

> **Miami Papa Noel**
> Seasonal production deployment. 2025 seasonal production completed; the
> 2026 seasonal workflow is reactivated and being improved.
> Live **15 November 2025 - 24 December 2025 (40 days)**.
> Frequency: per-booking across the active season; 14 visits delivered.
> Operational owner: **Marcelo Zapata — built and operated.**

## Form-entry guards

Read these before typing anything into the form:

- **Duration and volume are different numbers. Never let them swap.**
  Duration = **40 days** (Nov 15 - Dec 24, 2025, inclusive). Volume =
  **14 visits**. Writing 14 in a duration field fails a bar the deployment
  clears by nearly 3x.
- **Status wording:** "2025 seasonal production completed; 2026 seasonal
  workflow reactivated and being improved." Do not write "currently active",
  and never describe it as a year-round service - it is seasonal, and
  between-seasons is the accurate state on any day outside the season.
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

## Technical explanation fields

Finished copy for the form's technical questions. Each answer separates what
operated in the 2025 season from what the 2026 reactivation adds, because a
reviewer will ask - and the honest split reads stronger, not weaker.

### Operational owner

> Marcelo Zapata - built and operated. I proposed the system, implemented it,
> and ran it day to day as sole technical and operational owner. The
> performers deliver the service; every message, schedule, and payment record
> passed through me.

### Live AI functionality

> Bilingual (EN/ES) customer communications, marketing and content
> generation, summarisation of incoming leads into pre-visit briefs, and
> follow-up drafting - operated through themed role workflows (Santa,
> Mrs. Claus, the elves), each owning one lane of the operation. Every
> customer-facing output was reviewed by me before sending. Scheduling,
> logistics, and payment tracking were the manual operational surround, not
> AI functions, and are not claimed as such.

### Concrete outcome

> 14 visits delivered across a 40-day operating season (15 November -
> 24 December 2025), spanning hospitals, Miami-Dade County sites, Publix
> locations, fire and police departments, and private families — up from a
> previous seasonal maximum of approximately 5 visits, per the owner's written
> confirmation of 2026-08-30. The operational load moved off the
> non-technical performers entirely. The client is running the workflow again
> for the 2026 season.

### Production model or models

Search the old account history FIRST. Then use exactly one of these two
variants - never a guess:

**Variant A - the 2025 model is verified in the records:**

> The 2025 season ran on **[EXACT MODEL/TIER FROM THE ACCOUNT HISTORY]**.
> For the 2026 reactivation the model is pinned explicitly: every logged
> inquiry records the exact model id that produced its draft, and a
> deterministic rules engine (`offline-rules-v1`) is the no-model fallback -
> always logged as a fallback, never presented as a model.

**Variant B - the 2025 records do not name a model:**

> The 2025 season ran on a commercial assistant; the account records do not
> preserve the specific model version, and we state that plainly rather than
> guess. The 2026 reactivation removes the ambiguity: the production model is
> **[EXACT MODEL ID FROM THE 2026 PRODUCTION LOG]**, recorded verbatim on
> every logged inquiry, with a deterministic rules engine
> (`offline-rules-v1`) as the no-model fallback - always logged as a
> fallback, never presented as a model.

Either way, close with the policy line:

> Our documentation policy is that no model name appears anywhere before it
> has appeared in the production log.

### How the important parts work together

> An inquiry enters from a customer channel and flows through one pipeline:
> language detection (EN/ES) and structured extraction (date, service
> category, location, what is still missing) -> schedule and capacity risk
> flagging against the season's first-to-fill dates -> reply drafting in
> both languages from a locked, versioned price list -> six validation gates
> (locked pricing, EN/ES commercial parity, missing-information handling, no
> booking- or deposit-confirmation language, no insurance claims while the
> policy is unverified, Zelle-only payment terms) -> mandatory human
> approval. The tool has no send path: the operator copies the approved
> draft into the channel, and a structured log line ties every draft to the
> model id, prompt version, and price-list version that produced it. In 2025
> the same pipeline was operated through the themed role workflows with the
> operator as the integration point; the 2026 reactivation codifies it as
> runnable, tested software.

### How releases are tested and approved

> Automated suites cover extraction, bilingual parity, and adversarial
> negative cases that prove each safety gate blocks rather than warns. A
> repository-wide validator additionally checks every public page against
> the locked price list, forbidden payment methods, unverified insurance
> language, and documentation drift (test counts, model names, and launch
> dates that no longer match reality). Releases are approved by the
> operational owner against a written checklist; a price change ships in the
> same commit as the public page it mirrors. A fail-closed submission
> validator (--preflight / --final) gates any external claim: final mode
> exits non-zero until every requirement is backed by real, dated evidence.
> In 2025, testing was operator review of every output; the 2026
> reactivation formalised it into the suites above.

### Production monitoring

> Every inquiry appends one structured JSONL record, stored outside the
> repository: timestamps, channel, language, extraction results, schedule
> risk, model id, prompt and price-list versions, reviewer, approval and
> send times, outcome, and fallback/error codes. Message bodies and customer
> contact data are never logged - location is a coarse area, and the log
> records whether a phone or email was supplied, never the value. Every
> reported metric (inquiries handled, median first-response time, approval
> rate, fallback rate, language split) derives from this log, so nothing can
> drift from what actually happened. In 2025 monitoring was manual
> operator tracking; the 2026 reactivation makes it structured and
> machine-checkable from the first real inquiry.

### Failure handling

> Three layers. First, if the model is unavailable, times out, returns
> unparseable output, or produces a draft that fails any validation gate,
> the system falls back automatically to the deterministic path and records
> the reason as an error code - the unsafe draft never reaches the operator.
> Second, if the tool itself is unavailable, a documented manual procedure
> carries the full price table, deposit terms, Zelle details, and the rules
> about what may never be written to a customer; manually handled inquiries
> are logged as fallbacks with the cause, so outages appear in the record
> instead of hiding in it. Third, at the draft level, any gate failure
> blocks approval entirely - a bad price, a confirmation phrase, an
> insurance claim, or a non-Zelle payment method cannot be approved. The
> business earns its year in about six weeks and cannot pause mid-season, so
> nothing is permitted to become load-bearing beyond what the operator can
> do by hand within the hour.

## Minimum strong packet

Five items. With these, the submission stands; without any one of them, it
has a hole a reviewer will find:

1. **Owner confirmation email** - IN HAND: finalized 2026-08-30 by Walter
   Zapata, who operates Miami Papa Noel. Confirms the dates (Nov 15 - Dec 24,
   2025), Marcelo Zapata (XIV) as designer and operator, the functions, human
   review before sends, 14 visits versus a prior seasonal maximum of ~5, the
   2026 renewal, and that this served real operations, not a demonstration.
   Sent from the Santa company's official email account (the strongest form
   a counterparty statement can take). Remaining: save the sent copy as PDF
   with its headers intact so the date and sender are provable, and index it
   via `scripts\evidence_index.py` as type `statement`. No phone call to
   OpenAI is needed.
2. **Redacted receipts** (or calendar/booking records) - proving the business
   operated: real customers, real dates, supporting the 14 visits and the
   40-day period.
3. **One dated AI-workflow artifact** - a redacted screenshot or export of
   AI-assisted drafts, lead summaries, marketing content, or follow-up
   messages. **Receipts prove the business operated; only this proves the AI
   component did.** Keep the two claims on separate evidence rows.
4. **The technical explanation** - the fields above, with the model variant
   resolved from records.
5. **Validator and test output from the exact commit being submitted** -
   rerun `python -m pytest` and `--preflight` at that commit and report the
   number the run actually prints. Never reuse a count from an earlier
   conversation or an earlier commit (63 at one commit is not 63 at the
   next).

## Pre-submission checklist

- [ ] 14-visit count confirmed exact against records
- [ ] Redacted message thread selected and indexed via `scripts\evidence_index.py`
- [ ] Model field filled from records, or left blank
- [ ] `python scripts\validate_opn_submission.py --preflight` passes
- [ ] Status wording matches this document everywhere it appears
- [ ] One dated AI-workflow artifact selected, redacted, and indexed
- [ ] Owner confirmation email dated and indexed
- [ ] Tests and --preflight rerun at the submitted commit; reported counts taken from that run only
