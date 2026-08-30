# Evidence Intake

Where receipts, records, and the counterparty statement go when they arrive, and
how to redact them first.

**Rule that governs everything below: no customer data enters this repository.**
Receipts, screenshots, and message exports live in a local evidence folder
outside Git. What comes into the repo is the *index* — dates, identifiers,
amounts, and what each item establishes.

```
Evidence folder (outside Git):
  %LOCALAPPDATA%\MiamiPapaNoel\evidence\
      receipts\
      messages\
      screenshots\
      statements\
```

`.gitignore` already excludes `*.jsonl`, `.env`, `*.pem`, `*.key`. Do not add an
`evidence/` folder inside the repo — keep it out of the tree entirely.

---

## 1. What to collect

Anything with a date on it. Two or three solid items beat a large pile.

| # | Item | What it establishes | Have it? |
|---|---|---|---|
| 1 | Receipts from the Santa company | Real customer operations, dated, with amounts | ☐ |
| 2 | Booking records | Events actually booked and performed | ☐ |
| 3 | Dated message threads | Real inquiries handled, in which language, how fast | ☐ |
| 4 | Screenshots of the workflow in use | What the operator actually saw and did | ☐ |
| 5 | Written confirmation from the company | Independent corroboration of dates, owner, functions, outcome | ☐ |
| 6 | Calendar entries | Event dates and scheduling discipline | ☐ |
| 7 | Zelle transaction history | Payment terms in force, deposits received | ☐ |

## 2. Redact before anything leaves the machine

Strip, every time:

- Customer names → `[CUSTOMER]` or an initial
- Phone numbers, emails → `[PHONE]`, `[EMAIL]`
- Street addresses → keep the area only (`Doral`, `Kendall`)
- Zelle memo text and account identifiers
- Faces of children, and any school or HOA name that did not consent

**Keep visible:** the date, the amount, the service type, and any identifier you
need to reference the item. The date is the whole point — a redacted receipt
with a legible date is evidence; a clean one with the date blurred is not.

## 3. Index each item here as it arrives

Fill one row per artifact. This table is what goes into the repository; the
files themselves stay out.

| Ref | Type | Date | Identifier | Amount | Establishes | Redacted? | Location |
|---|---|---|---|---|---|---|---|
| E-01 | | | | | | ☐ | |
| E-02 | | | | | | ☐ | |
| E-03 | | | | | | ☐ | |
| E-04 | | | | | | ☐ | |
| E-05 | | | | | | ☐ | |

When rows are filled, copy the finished table into `docs/evidence-index.md`
under a new **Prior season — dated artifacts** heading, and flip the matching
`[TO FILL]` rows in `docs/operator-attestation-2025-season.md`.

---

## 4. Statement to request from the company

Send this and ask them to fill the brackets in their own words. **Do not fill
the brackets for them** — a statement written by the applicant and signed by the
counterparty is worth much less than one they authored.

> During **[DATES]**, Marcelo Zapata's Miami Papa Noel workflow supported our
> real seasonal customer operations. The operational owner was **[NAME]**. The
> live functions included **[FUNCTIONS]**. The workflow used **[MODEL/TOOL]**,
> with human review before customer-facing actions. The concrete result was
> **[OUTCOME]**. We can confirm this through the attached redacted receipts and
> records.

Ask for it on company letterhead or from a company email address, with a name
and role. A dated email is sufficient.

**Guidance to send with it, so the fields come back usable:**

- **[DATES]** — actual start and end, not "last season"
- **[NAME]** — the person who ran it day to day
- **[FUNCTIONS]** — the specific steps, e.g. inquiry intake, bilingual drafting, scheduling coordination, payment receipt tracking, follow-up
- **[MODEL/TOOL]** — only if they genuinely know. **If they do not, leave it blank.** A blank field is fine; a guessed model name is not, and it is the field a technical reviewer will check hardest
- **[OUTCOME]** — one number they can stand behind: events supported, inquiries handled, or bookings completed

## 5. One documentation field this changes

`docs/production-deployment-record.md` currently records the relationship as:

> Miami Papa Noel is the operator's own seasonal business, run under XIV. **It is
> not an external third-party customer**, and is not presented as one.

If the Santa company is a **separate legal entity** that XIV contracts with —
which is what a receipt and a counterparty statement would indicate — that line
should be updated to describe the actual arrangement. If Miami Papa Noel and the
Santa company are the same business under different names, the line stays as is.

Either is a normal arrangement and neither weakens the submission. It just has
to match what the receipts show, because that is the first thing a reviewer will
cross-check.

**Field to resolve:** `[ ]` separate entity, contracted · `[ ]` same business ·
`[ ]` other — describe

## 6. What receipts do and do not establish

Worth being clear before assembling, so the story stays tight:

**They do establish** — real customers, real money, real dates, real seasonal
operations, and a real counterparty who will vouch for the work.

**They do not establish** — that an AI system processed those inquiries. That is
a separate claim needing a separate artifact: the message threads, the
screenshots, or the counterparty naming the tool in **[MODEL/TOOL]**.

Keep the two claims in separate rows of the evidence index. A reviewer who sees
receipts labeled as proof of AI operation stops trusting the rest of the
package; a reviewer who sees receipts labeled "real customer operations, dated"
and message threads labeled "bilingual drafting in use" trusts both.

The 2026 deployment carries the AI claim on its own — a running tool, 43 passing
tests, and a log that starts on the first real inquiry. The receipts carry the
business history. Neither has to do the other's job.

---

## Checklist

- [ ] Evidence folder created outside the repository
- [ ] Receipts collected
- [ ] Booking records collected
- [ ] Dated message threads exported
- [ ] Screenshots captured
- [ ] Every item redacted, dates left legible
- [ ] Statement requested from the company
- [ ] Statement received with a name, role, and date
- [ ] Index table above filled
- [ ] Table copied into `docs/evidence-index.md`
- [ ] `[TO FILL]` rows flipped in `docs/operator-attestation-2025-season.md`
- [ ] Relationship field in `docs/production-deployment-record.md` resolved
