# Season Dashboard

An offline page for the family to run the season without any subscription.

## Release status - September 10, 2026 (local date)

PRIVATE OPERATOR TOOL. This repaired version is local and uncommitted, not
deployed. No new public chatbot is deployed. Do not upload this directory,
customer notes or exported CSVs to GitHub or the website.

The marketing-site build now uses an explicit allowlist in
`C:\XIV\santa\deploy\public-files.json` and publishes only `dist/` after
the new Vercel configuration is released. The dashboard, business tracker,
docs, Python tools and credentials are not in that artifact. This is a local
configuration change, not proof that any existing deployment has changed.
Existing Git history and old deployment URLs are separate privacy surfaces;
excluding a future build does not erase earlier copies. `noindex` is not access
control. Verify the published artifact and URLs before promoting a release.

## How to open it

Double-click `index.html`. It opens in any browser. There is no server to start,
no login, no internet needed to read it. On a phone, copy `index.html` to the
phone and open it from Files, or keep the printed pages instead.

## What it is

- Rate card copied from `tools/triage/pricing.json` (the locked price source).
- Deposit and booking rules copied from the published checkout page.
- Fifteen EN/ES reply scripts copied word for word from
  `business/client-message-templates.md` and `business/lead-reply-bank.md`.
- 55 lead cards from `business/wave1-hoa-prospects-2026-08-26.md` (30, each with
  the source recorded in that file) and `lead-tracker.csv` (25, labelled as not
  independently checked).
- A short daily checklist and per-lead status and notes.

## What it is not

- Not a backup. Ticks, statuses and notes live in one browser on one device.
  Use **Export my notes (CSV)** at the end of each working day.
- Not connected to anything. It cannot see the bank, cannot verify a deposit,
  cannot send a message, and does not transmit anything anywhere.
- Not a booking system. An inquiry is not a booking until the deposit clears
  and a human confirms it.

## Regenerating it

The page embeds copies of the sources. There is no checked-in regeneration
command for this dashboard. Editing a source file does not update this HTML.
After an owner-approved price or template change, a developer must update the
embedded copy and verify it against the sources before distributing it.

Built 2026-09-09 from price list version 2026-08-28.1.

## Notes backup and recovery

The repaired export includes a version-2 state snapshot alongside the readable
lead rows. It preserves false ticks, empty fields, quotes, line endings and
formula-like notes. Potential spreadsheet formula prefixes are escaped as
literal text; the dashboard reverses its own escape during a version-2 restore.
Do not remove the metadata row or edit a version-2 export before restoring it.
The metadata and visible rows must agree; otherwise import is refused.

Complete legacy exports from this same lead list remain supported. Truncated,
unknown-ID, duplicate-ID, bad-status, malformed and over-2-MB files are refused
before replacing anything. A valid full export of an empty state can clear
the dashboard only after the same explicit replacement confirmation.

1. Export the notes and verify that the browser actually downloaded the CSV.
2. Keep an additional copy on a different device or your existing private backup.
3. Import an unedited export from this dashboard. Read the replacement warning:
   this replaces all notes, statuses and ticks; it is not a merge.
4. Cancel leaves both current and stored data unchanged. A failed save leaves
   existing state unchanged. Only a completed save reports restored.

If normal editing cannot save, an alert explains that new edits remain only
in the open page. Export before closing. The previous stored copy is retained.
If old browser data cannot be read, startup does not replace it with empty data.
Browser/file storage behavior varies; changing browser or moving the HTML can
change which stored notes it sees. Never rely on local storage as the backup.

## Releasing the marketing site without an AI subscription

Requirements: Git, Node.js, Python with the repository's test dependencies,
and access to the existing GitHub and Vercel accounts. No Claude or Codex
subscription is required. Do not install or buy a new hosting plan for this.

In PowerShell at `C:\XIV\santa`:

```powershell
$env:OPENAI_API_KEY = ''
$env:MPN_MODEL = ''
$env:MPN_API_DAILY_CALL_CAP = '0'
$env:MPN_CHAT_ALLOW_MODEL = '0'
$env:MPN_API_COST_POLICY = ''
python -B scripts\ops_check.py
node scripts\build_public_site.cjs --check
node scripts\build_public_site.cjs
```

The last command creates `C:\XIV\santa\dist`; it does not upload it. The build
refuses placeholder URLs, unsafe manifest paths and unexpected existing output
files. If it refuses stale output, inspect that directory first; do not bypass
the check or copy the repository root as a substitute.

After the owner approves the exact release diff, commit only reviewed files.
In the existing Vercel project's Git settings, verify the connected repository,
production branch and root directory before pushing. The committed `vercel.json`
selects `node scripts/build_public_site.cjs` and output directory `dist`.
Inspect the resulting deployment before promotion: services/request/phone
buttons must work, and `/business/season-dashboard/index.html`,
`/lead-tracker.csv`, `/docs/`, `/tools/` and `/.env` must not expose files.
Record the deployed commit, deployment URL and actual verification date.

Rollback must use a reviewed artifact with the same private-file exclusions.
Do not blindly restore an older root-directory deployment that might expose
operator files. Never delete local notes, queue databases, payment records or
spending ledgers as part of website rollback.

Vercel configuration reference:
https://vercel.com/docs/project-configuration/vercel-json#outputdirectory

## Rate card and unfinished items

- Locked rate source: `C:\XIV\santa\tools\triage\pricing.json`.
  Do not edit it without owner approval. No prices were changed in this repair.
- Insurance remains NOT ACTIVE / NOT VERIFIED. No insurance/certificate claim
  is authorized by this dashboard, a passed test or a deployed website.
- The new public chatbot remains undeployed. Dad's existing phone calls remain
  ordinary calls; nothing here answers, records or charges for calls.
- The lead tracker still has the documented column-alignment issue. This page
  is not a fresh verification of any organization or contact information.
- The browser tool could not open file:// due its security policy. Actual
  file-opening, browser-console/network checks and 360px layout for the repaired
  dashboard still need human verification. JavaScript tests use synthetic data
  in an isolated Node harness; they do not prove browser rendering.
- No automated cross-device synchronization, cloud backup, payment verification,
  booking confirmation or 15-day production evidence is created here.
- The public release, Vercel account settings/costs and historical exposure
  remain unverified until an authorized deployment review is completed.

## Files here

- `index.html` — the dashboard.
- `cowork-to-codex.md` — outgoing status reports (Cowork writes this only).
- `codex-to-cowork.md` — incoming replies (Codex writes this only).
- `test-dashboard.cjs` and `test_dashboard.py` - offline synthetic regression checks.
