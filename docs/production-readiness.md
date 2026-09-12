# Production Readiness — Operator-Assisted Inquiry Workflow

Scope: the smallest genuinely usable workflow — a customer message arrives in
an existing inbox, Mrs. Claus drafts English/Spanish, Marcelo reviews and
sends the reply himself. This checklist covers only that. Hosting, phone
automation, Stripe, and social publishing are out of scope and are not
required for it.

Status date: 2026-09-08 (Rollback row updated 2026-09-11). Verified against the current tree.

## The checklist

| Requirement | Status | Where it actually lives |
| --- | --- | --- |
| Named operational owner | **MET** | Marcelo Zapata — sole operator, sole reviewer, sole sender. Recorded in `docs/OPN-SUBMISSION.md` and every `--reviewer` value. |
| Where the app runs | **MET (by design, not a server)** | On Marcelo's Windows PC, on demand. Nothing runs while the PC is off — and nothing needs to: the inboxes (phone, Instagram, email) are hosted by their providers and hold messages until he opens the tool. |
| Private data storage | **MET, with the enforcement scope stated** | Default locations `%LOCALAPPDATA%\MiamiPapaNoel\` — `triage\` (inquiry logs), `api-quota\` (spend accounting), `intake\` (pasted messages). These are **defaults**, not a universal guarantee: the operator can repoint them with `MPN_LOG_DIR` / `MPN_API_QUOTA_DIR`. Repo-containment is *enforced* in the evidence-backup tool and the cost guard; it was NOT enforced in the call-slot writers until Codex's 2026-09-08 fix, which is why "enforced everywhere" should not be claimed loosely. Contents are metadata, not transcripts — but note the log **does** record reviewer names and timestamps (see `log-schema.md`); it is private data, not anonymous data. |
| Offline fallback | **MET** | `offline-rules-v1` deterministic bilingual templates. Always available, no key, no network, $0. Every refusal path falls back to it rather than failing the operator. |
| Error visibility | **MET for this workflow** | Sanitized stderr diagnostics (never raw provider text or credentials); an `error_code` on every record (`tools/triage/log-schema.md`); `python scripts/ops_check.py` for the whole battery. |
| Rollback | **MET** | Git: any published commit reverts with `git revert` pushed to `main` (START-SANTA.md, "Roll back a bad change"); never re-promote a Vercel deployment older than b2ffa09. Operationally, `MPN_API_DAILY_CALL_CAP=0` instantly returns the tool to free offline drafting. |
| Backup / restore | **CAPABILITY TESTED** | The tooling works and is covered by tests: inquiry queue via `tools/web_inquiry/maintenance.py`, evidence log via `tools/triage/evidence_backup.py` (below). No production backup or real customer record was created by these coding tasks. Private production storage has not been audited. This row becomes a real safeguard only once the operator runs it on a day with genuine activity. |

## Backing up the evidence log

`%LOCALAPPDATA%\MiamiPapaNoel\triage\production-log.jsonl` is the *only*
record of genuine model-backed operation — the thing a 15-day window would
consist of. It cannot be honestly recreated if lost, because backdating is
forbidden. Back it up on any day that had real activity:

```powershell
python -B tools\triage\evidence_backup.py backup --dest "<your private backup folder>"
```

The tool reads the log without writing to it, refuses any destination inside
the repository, verifies the copy by SHA-256 and record count, and refuses
outright if the log changes while it is being copied. To prove a backup is
actually restorable, restore it into a brand-new directory — this never
touches the live log:

```powershell
python -B tools\triage\evidence_backup.py restore-check --backup "<backup file>" --restore-dir "<a new folder>"
```

**A backup on the same disk protects against accidental deletion and bad
edits. It does NOT protect against that disk failing.** The tool warns when
the backup shares a drive letter with the log — but a *different* drive
letter is not proof of different hardware either: partitions, virtual disks
and mapped network drives can share one physical disk. Confirm the hardware
yourself, and keep at least one copy on separate hardware or in private
storage the operator already has. Nothing here is automated, and nothing
runs while the PC is off — this is an operator action, on purpose. No
purchase and no new account are required.

Every item on the list is now **built and tested**. That is not the same as
**activated**. No production backup or real customer record was created by
these coding tasks. Private production storage has not been audited.
Capability and activation are tracked separately on purpose — this document
describes what the software can do, not what has been operated.

## Prepared — NOT executed: bounded real-model verification

This run sheet exists so the test can be done correctly when authorized. It
has **not** been run by these coding tasks, which approved no budget,
configured no prices, and created no policy file. Paid calls are OFF by
default in the code itself.

The owner chooses the budget, authorizes the test, and enters credentials
privately. An engineer can research prices and prepare the private policy
proposal; nothing is activated without approval.

1. **Marcelo's explicit daily budget** in cents, and explicit authorization
   for this one test.
2. **A replacement API key**, entered privately by him in his own terminal.
   The key exposed in chat is burned and must never be reused.
3. **Current official prices** for the exact selected model. An agent can
   research these from OpenAI's official pricing page and prepare the policy
   file as a proposal — Marcelo does not have to do that engineering step
   himself. What he must do is approve the resulting numbers. Prices are
   never copied from a test fixture, never estimated, and never carried over
   from an earlier conversation; the policy file records the source URL and
   the date they were verified.
4. **A private cost-policy file** outside the repository, per the Engineer
   Notes in `docs/day-one-operator-card.md` (`daily_cents`, `verified_on`
   within 7 days, exact model id, both rates, official source URL).

Then, in his terminal only:

```powershell
python -B tools\triage\triage.py --check-model
```

Expected: exit 0, `MODEL CHECK PASSED`, the selected model named, six gates
passing, both languages reviewed by eye. A refusal code (`COST_*`,
`PAID_CALLS_DISABLED`, `BUDGET_*`) means **this attempt dispatched no
request**, so this attempt generated no charge — that is a statement about
this attempt only, not about the account, which the provider's billing page
alone can answer. **Do not retry repeatedly.** One test, then stop and read it.

What this test does and does not establish: it verifies the model works
through Santa's real gated path. It is **not** Day 1, not customer activity,
and not evidence of production operation. Only a genuine customer inquiry —
reviewed and actually sent by Marcelo — starts the evidence record, and OPN
alone decides whether that evidence meets its requirements.
