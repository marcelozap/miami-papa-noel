# Continue Here - Laptop Handoff

Written 2026-08-30 on the desktop. Read this top to bottom before doing
anything else on the laptop.

---

## THE SIMPLE VERSION - only four things are actually left

All the writing, tools, and tests are DONE. What remains is four real-world
actions. Everything below this box is just detail supporting these four:

1. **Walter signs the letter.** Print it, he signs and dates it, photograph it.
2. **Find one receipt or booking record** from Nov-Dec 2025 (a Zelle entry,
   a calendar screenshot - anything dated). Cover names/numbers with a finger
   or crop; leave the date visible.
3. **Find one screenshot of the AI drafting** from that season - any saved
   chat where it wrote a customer message, a caption, or a lead summary.
4. **Check your old chat account settings/history for which model/plan you
   had.** Found it: use it. Not there: the form copy already says "not
   retained" for you - that answer is written and it is fine.

Then open `docs/opn-form-answers.md`, copy the answers into the form, done.
That file was written so you never have to compose a sentence under pressure.

## 0. Get the work onto the laptop

**On the desktop, before you leave it** (the repo is 4 commits ahead of
GitHub after the handoff commit):

```powershell
cd "C:\Users\Green Machine\miami-papa-noel"
git push
```

**On the laptop:**

```powershell
git clone https://github.com/marcelozap/miami-papa-noel
cd miami-papa-noel
python -m pytest tools\triage\test_triage.py scripts\test_validate_opn_submission.py scripts\test_evidence_index.py scripts\test_build_opn_packet.py -q
python scripts\validate_opn_submission.py --preflight
```

Expected: **68 passed** and **PREFLIGHT PASS with 9 warnings**. If you get
different numbers, you are not at the same commit - check `git log -1`.

### Two things that do NOT travel through git - decide which machine owns them

1. **The production log** - `%LOCALAPPDATA%\MiamiPapaNoel\triage\production-log.jsonl`
2. **The evidence folder** - `%LOCALAPPDATA%\MiamiPapaNoel\evidence\`

These are machine-local by design (customer-adjacent data never enters git).
**Pick ONE machine to run real inquiries and store evidence, and stay on it.**
A production log split across two machines is a mess you cannot honestly merge.
If the laptop is now the main machine, start the log there and keep it there.

Also: the separate `PapaNoel_MarketingKit` folder (handbook, marketing kit) is
local-only on the desktop - it is not on GitHub. It is not needed for the OPN
submission. The public website is NOT on that repo either; 17 modified website
files sit uncommitted on the desktop working tree, deliberately untouched.

---

## 1. What this project is right now

**Goal:** OpenAI Partner Network resubmission for the Miami Papa Noel
deployment. All writing is done. What remains is evidence collection and two
lookups.

**The story (all facts confirmed by the owner's written statement,
2026-08-30):** Walter Zapata operates Miami Papa Noel; Marcelo Zapata (XIV)
proposed, built, and operated the AI-assisted workflow - sole technical and
operational owner. 2025 season ran **Nov 15 - Dec 24, 2025 (40 days)**,
delivered **14 visits** (prior seasonal max was ~5) across hospitals,
Miami-Dade sites, Publix, fire/police departments, and families. 2026 is the
**second seasonal operating cycle**. Status wording everywhere: *"2025
seasonal production completed; 2026 seasonal workflow reactivated and being
improved."* Never "currently active", never year-round.

**Where everything lives:**

| What | Where |
|---|---|
| Paste-ready form copy (use case, deployment entry, all technical fields) | `docs/opn-form-answers.md` |
| Which form field gets which text | `docs/opn-resubmission-field-map.md` |
| Evidence collection + redaction procedure | `docs/evidence-intake.md` |
| 2025 season record (5 fields filled, 5 open) | `docs/operator-attestation-2025-season.md` |
| The runnable 2026 triage tool | `tools/triage/` (`--demo` to see it run) |
| Fail-closed validator | `scripts/validate_opn_submission.py --preflight` / `--final` |
| Evidence hashing helper | `scripts/evidence_index.py` |
| Packet builder | `scripts/build_opn_packet.py` |
| Live demo script for a reviewer | `docs/demo-runbook.md` |

---

## 2. The minimum strong packet - scoreboard

| # | Item | Status |
|---|---|---|
| 1 | Owner confirmation email (Walter, dated 2026-08-30) | **Nearly done.** Sent from the business account - but that account displays Marcelo's name. Complete per the provenance note in `docs/opn-form-answers.md`: best = Walter hand-signs a printed copy (photo it) + business account with display name fixed to "Miami Papa Noel" + one disclosure line. Then index the PDF as type `statement` |
| 2 | Redacted receipts / booking / calendar records | **Open.** Prove the business ran: dates + amounts, supporting 14 visits / 40 days |
| 3 | One dated AI-workflow artifact | **Open. This is the only item that proves the AI ran** - a redacted screenshot/export of 2025 AI-assisted drafts, lead summaries, marketing content, or follow-ups, date visible |
| 4 | Technical explanation | **Done** - in `docs/opn-form-answers.md`, incl. paste-ready block. One blank: the model |
| 5 | Test/validator output at the submitted commit | **Rerun on submission day** - report what that run prints, never a remembered number |

**The one technical unknown:** the 2025 model. Search the old account history
FIRST. Then use Variant A (model verified -> name it) or Variant B (not
retained in the 2025 records -> say so plainly + use the exact 2026 model id
once it appears in a real production log). Both variants are fully written in
`docs/opn-form-answers.md`. **Never guess a model name.**

---

## 3. Rules that must survive the machine switch

1. **Duration = 40 days. Volume = 14 visits. Never swap them on the form.**
2. **`--real` only for genuine customer inquiries.** The first one starts the
   2026 production clock and can never be moved. Never backdate.
3. **No model name in any document before it appears in the production log.**
4. **Zelle only** on every customer surface. The validator enforces this.
5. **No customer data, secrets, or `.jsonl` logs in git.** The validator's
   git-privacy check enforces this too.
6. **Redact evidence before it leaves the machine; keep dates legible.**
   Hospital/children material: no patient names, faces, room numbers.
7. **Present nothing as independent of Marcelo when it is not** - the
   performers-are-not-technical story covers every administration fact
   honestly; disclosure beats distance.
8. **Test counts:** 68 = all four suites; 45/15/3/5 individually. Whatever you
   report, rerun at that commit and quote the run.

---

## 4. Suggested order on the laptop

1. `git push` from the desktop, clone on the laptop, verify 68 passed +
   preflight PASS (commands in section 0).
2. Search the 2025 account history for the model -> pick Variant A or B in
   `docs/opn-form-answers.md`.
3. Finish the Walter letter per the provenance note; save the PDF.
4. Collect + redact: receipts (item 2) and one AI-workflow artifact (item 3).
5. `python scripts\validate_opn_submission.py --init-evidence` (if the
   evidence folder does not exist on the laptop yet), then index each file
   with `scripts\evidence_index.py`.
6. Fill the E-01..E-05 rows in `docs/evidence-intake.md`, mirror into
   `docs/evidence-index.md`, flip the matching attestation rows.
7. Copy the form answers from `docs/opn-form-answers.md` into the OPN form,
   observing every form-entry guard listed there.
8. Before submitting: rerun the four suites and `--preflight` at that exact
   commit; use those numbers.

When real 2026 inquiries start: `tools\triage\triage.py --message "..." --real`
- and read `docs/15-day-evidence-checklist.md` first.

---

## 5. Context for whichever assistant continues

Two agents worked this repo in parallel from the desktop (shared git index -
stagger commits if that happens again). Technical fields were owned separately
from business facts/evidence. The technical copy in `docs/opn-form-answers.md`
is finished and validated; do not rewrite it, fill its two bracketed blanks
from records. The business facts (dates, 14 visits, owner) are settled by the
owner's written confirmation and must not be changed. The `--final` validator
mode is expected to FAIL until the 2026 log and external evidence index exist -
that is fail-closed behavior working, not a bug.
