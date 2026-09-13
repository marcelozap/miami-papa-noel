# Your Santa Project

Project folder: C:\XIV\santa
GitHub: https://github.com/marcelozap/miami-papa-noel

The files are yours to keep and edit without a Claude or Codex subscription.
The runtime uses Python and your hosting, not either coding chat session.
OpenAI API billing is separate and optional; it remains disabled here.

## Open the offline workshop

In PowerShell:

```powershell
cd C:\XIV\santa
python -B tools\offline_workshop.py
```

Open http://127.0.0.1:8240 . Python 3.10+ is required; no package installation
is needed for this launcher. If the port is occupied, add `--port 8241` and
use the printed URL. The terminal prints a temporary operator token for
/operator. Use only synthetic practice inquiries. Ctrl+C stops the server
and clears this workshop session. It does not touch real booking/evidence
files. With the computer or launcher off, this local workshop is unavailable.

This is a practice copy of the chat, NOT a publicly available production
assistant. The two review findings from September 9 (the daily limit
resetting on restart; a session usable by a different visitor) were fixed in
commit 9c84196 and re-verified. What still blocks a public chat is not those
two defects but hosting and evidence: an approved always-on server with
permanent storage (the SQLite backend is not a drop-in Vercel function), a
verified HTTPS address, browser and privacy checks, and honest operating
evidence. See docs/chat-release-status.md.

## Use with your standalone website editor

Open this project folder, not the rally-coach project. The file
santa-editor-project.json is a plain project description for your app to
read or adapt; it is NOT an implemented connection to an unknown editor.

- Main website: index.html, book.html, other root HTML pages and assets/.
- Chat interface: tools/web_inquiry/index.html, app.css, app.js.
- Operator queue/backend: tools/web_inquiry/server.py.
- Price/term source: tools/triage/pricing.json. Change through reviewed policy,
  not by independently rewriting prices in page copy.
- Release status: docs/chat-release-status.md.
- Coordination: docs/santa-agent-workboard.md and docs/agent-sync/.

Keep secrets, logs, databases and actual customer information outside the
project and the editor's sync/upload directory. Do not let a visual editor
change cost guards, payment verification or evidence logic automatically.

## What works and what does not

The existing public site was verified at https://miamipapanoel.com/ .
Your dad can continue answering 786-975-9557 himself. Those calls are not
connected to this AI software. Local bilingual template chat and lead intake
work. The new public chat is not deployed and no public page links to it;
the chat interface under tools\web_inquiry still contains a placeholder
URL and must not be published as ready.

Before launch: choose approved hosting with durable state (the current
SQLite backend is not deployable unchanged as a Vercel function), verify the
endpoint, remove the placeholder URL from the chat interface, then publish
after review. Do not spend on hosting or AI merely to meet an application
date. No production Day 1 has been established here.

## Update the website (the only publishing path)

Vercel builds the live site from the GitHub branch `main`. A commit that
reaches `main` on GitHub triggers a deployment attempt, including edits made
in the github.com web editor, so never edit files on github.com directly.
Local edits publish nothing until they are pushed.

On this PC the local `main` branch can be behind GitHub, and the branch that
was checked out at handoff (santa-ops-hardening-2026-09-04) has no upstream,
so a plain `git push` can fail. Start every change the same way, in
PowerShell:

```powershell
cd C:\XIV\santa
git status --short
```

If that prints any file, someone left unfinished work. Do not delete it:
stop and get help, or review and commit only known-safe source changes on
the current branch. Never stage credentials, customer data or unknown files.
When it
prints nothing:

```powershell
git fetch origin
git checkout main
git pull --ff-only origin main
git log --oneline -1
```

The last line must match the newest commit shown at
https://github.com/marcelozap/miami-papa-noel/commits/main .

Edit index.html, book.html or another root page. For a new photo:

- Save it under assets\ with a name made only of letters, digits, hyphens or
  underscores and the lowercase extension .jpg, .png or .svg. No spaces,
  parentheses, .jpeg or .JPG: the build refuses those with "Private or
  unsafe path in public manifest".
- Remove location data first. Phone photos carry GPS coordinates, and the
  checks below fail on purpose if any published photo still has them. In
  Windows: right-click the file, Properties, Details, "Remove Properties and
  Personal Information".
- Add its path, for example "assets/family-2026.jpg", to
  deploy\public-files.json. Files not listed there are never published.
- The homepage gallery is pinned by scripts\test_public_release.py (the
  GALLERY_PHOTOS list names the gallery photos in order). If you change
  gallery photos, update that list in the same commit or the check fails.

Then, in the same PowerShell window:

```powershell
$env:MPN_API_DAILY_CALL_CAP='0'; $env:MPN_CHAT_ALLOW_MODEL='0'; $env:OPENAI_API_KEY=''
node scripts\build_public_site.cjs --check
python -B -m pytest scripts\test_public_release.py -q
git add <only the files you changed>
git commit -m "describe the change"
git push origin main
```

Both checks must end without an error line. `--check` prints the list of
files that will be published (53 on 2026-09-11); nothing under business/,
docs/, tools/ or lead-tracker.csv may appear in it. For text that mentions
prices, deposits, payment or insurance, also run
`python -B scripts\ops_check.py` (one to two minutes): it refuses prices that
differ from tools\triage\pricing.json and unverified insurance claims.

If GitHub answers "rejected" or "non-fast-forward", this push did not publish:
run `git pull --ff-only origin main` and push again. If that pull also
fails, stop; do not search for a workaround.

Never run `git push --force`, never push from a branch other than an
up-to-date `main`, and never delete vercel.json, deploy\public-files.json,
.vercelignore or scripts\build_public_site.cjs to make a deploy pass. They
are the only thing keeping private files off the public site.

## Confirm the site updated

1. Open https://github.com/marcelozap/miami-papa-noel/commits/main . Your
   commit must be at the top. A yellow dot next to it means Vercel is still
   checking; a green check alone does not prove a production deployment.
   Open the Vercel deployment details and confirm the intended commit is
   Ready for Production and assigned to miamipapanoel.com. For a failed
   deployment, open Details and read the last lines of the
   log. Typical causes: a path in deploy\public-files.json that does not
   exist, a placeholder URL ending in .invalid, or something that looks like
   an API key. Fix the cause and push again; never remove the build command.
   The same status is visible in the Vercel dashboard under the project's
   Deployments.
2. Open https://miamipapanoel.com/ in a private browser window and check
   your change. The old site stays up until a new build succeeds, so a
   refused build looks like "nothing changed", not like an outage.
3. Check that private files are still hidden. All of these must show a 404
   page: https://miamipapanoel.com/business/season-dashboard/ ,
   https://miamipapanoel.com/lead-tracker.csv ,
   https://miamipapanoel.com/tools/triage/pricing.json and
   https://miamipapanoel.com/assets/santa-pet-visit.jpg . If any of them
   loads, revert the last commit right away (next section).

## Roll back a bad change

Roll back with a reviewed new commit, never by re-promoting an older deployment in
the Vercel dashboard: every deployment built before the gallery release of
2026-09-11 (commit b2ffa09) still contains six GPS-tagged photo originals
that were removed from the public site in that release, and a promote does
not re-run any check.

```powershell
cd C:\XIV\santa
git status --short
git checkout main
git pull --ff-only origin main
git log --oneline -5
git revert <bad commit id> --no-edit
node scripts\build_public_site.cjs --check
python -B -m pytest scripts\test_public_release.py -q
git push origin main
```

`git status --short` must print nothing before you start. Use the offline
environment from the update instructions. Stop if either check fails; a
revert must not restore private paths or GPS originals. Then run the
"Confirm the site updated" steps again.

## Keep the booking form and phone working

The request form on https://miamipapanoel.com/book is a plain web form. It
posts to formsubmit.co (a free relay with no account; the address is in the
`action=` of the form in book.html), which emails each request to
bookings@miamipapanoel.com, your Google Workspace mailbox (see
business\email-form-finish.md). No server of ours sits in between. Phone,
text and WhatsApp links are separate and do not depend on it.

Three things only you can do:

1. Before each season, and after any change to book.html, submit one
   obviously fake request (name TEST, your own phone, no customer data) from
   the live /book page and confirm it arrives in bookings@. If FormSubmit shows
   an activation notice instead of the thank-you page, open bookings@, click
   the activation link FormSubmit emailed, and submit the test again. Keep
   the date of the successful test in a private note outside this folder.
2. Keep the Google Workspace subscription for bookings@ paid and the mailbox
   not full. If it closes, form requests may be lost with no error on our
   side, and every email link on the site stops working.
3. To deliver the form to a different address (staying on FormSubmit),
   change it in TWO places: the `action=` in book.html and the same address
   asserted in scripts\test_public_release.py. Run the checks in "Update the
   website", push, then repeat step 1: a new address needs its own
   activation.

## Accounts you must keep

This file is in the repository. Never write logins, passwords, renewal dates
or account numbers here; keep those in a private note outside the project.

| Service | What it does | If it lapses |
|---|---|---|
| GitHub, github.com/marcelozap/miami-papa-noel | Source of truth; a push to `main` publishes the site | No way to change the site. Make the repository Private (decision 1) |
| Vercel, team marcelos-projects-5a09363b, project miami-papa-noel | Builds and serves miamipapanoel.com from `main` | Site goes down. Keep the account email one you read |
| Domain miamipapanoel.com | Sends web traffic to Vercel and mail to Google | Site and email stop. The registrar is not recorded in this project: find it in your email receipts and note it privately |
| Google Workspace, bookings@miamipapanoel.com | Receives /book requests and all customer email | Form requests and customer mail lost |
| FormSubmit (formsubmit.co) | Relays the /book form to bookings@ | No account; activation is tied to the bookings@ inbox (step 1 above) |
| Zelle 305-244-0360 | The only live deposit rail | No way to take deposits |
| Phone 786-975-9557 | Public phone, text and WhatsApp | Customers cannot reach you |
| Stripe | Optional second rail; no public Payment Link configured (decision 4) | Nothing changes |
| OpenAI API | Optional paid drafting, OFF (decision 2) | Templates keep working |

Recurring costs: the domain renewal, Google Workspace and the phone line.
GitHub and Vercel need working sign-ins. No coding subscription is involved.

## Back up and restore

GitHub holds the pushed project, but is not a substitute for an independent
backup: account loss or repository deletion can remove access. Keep a
verified bundle on a separate device as well.
To recover the current project into a NEW folder (never on top of
C:\XIV\santa):

```powershell
git clone https://github.com/marcelozap/miami-papa-noel.git C:\XIV\santa-recovered
```

To also keep a copy of the full history off this disk, from C:\XIV\santa:

```powershell
git bundle create "C:\XIV\backups\santa-history-$(Get-Date -Format yyyyMMdd).bundle" --all
```

and copy that .bundle to an external drive. GitHub and the bundle hold
committed work only, so commit before you rely on them.

STALE SNAPSHOT: C:\XIV\backups\santa-handoff-20260909-132040 stops at commit
c14b896, the commit immediately before the public-file allowlist was
introduced. Its tree has no deploy\public-files.json, no
scripts\build_public_site.cjs, no .vercelignore and a vercel.json without a
build command. It is fine for reading history, but never push a tree
restored from it: Vercel would publish the whole repository (business/,
docs/, tools/, lead-tracker.csv) and the six GPS-tagged photo originals that
are excluded from the public site. After ANY restore, before pushing,
confirm both: vercel.json contains "buildCommand":
"node scripts/build_public_site.cjs" and "outputDirectory": "dist"; and
`node scripts\build_public_site.cjs --check` prints a file list with nothing
under business/, docs/, tools/ or lead-tracker.csv. If either check fails,
the restored tree is too old; use the GitHub clone instead.

Customer and operating data must never enter Git. The default location is
outside the project, %LOCALAPPDATA%\MiamiPapaNoel (open
it with `explorer "$env:LOCALAPPDATA\MiamiPapaNoel"`). Environment overrides,
packaged-app execution and explicit data-directory options can change the
actual location; inventory those locations before backing up. The tools create
subfolders as you use them: triage\ (inquiry logs; once production-log.jsonl
exists it is the only proof of real operation and cannot be recreated),
api-quota\ (the paid-call counter and spend record; never delete it or copy
an older backup over it), intake\, slots\ (bookings), comms\, content\,
elves\, web-inquiries\ (the inquiry queue and chat-limit databases, only if
you run the local queue), evidence\ and packets\. Never copy this folder
into C:\XIV\santa, into GitHub or into any editor sync folder.

At the end of every day you used a Santa tool, close every Santa tool window
first (some files are live databases), then copy the whole folder to a drive
that is not this computer's disk; replace E:\SantaPrivate with yours:

```powershell
$stamp = Get-Date -Format yyyyMMdd-HHmm
New-Item -ItemType Directory -Force "E:\SantaPrivate" | Out-Null
Copy-Item "$env:LOCALAPPDATA\MiamiPapaNoel" "E:\SantaPrivate\MiamiPapaNoel-$stamp" -Recurse
```

To restore: keep paid calls disabled and stop all Santa services, not just
their windows. Restore first into a separate private recovery folder and
verify the files. Preserve the current live folder. Never replace current
api-quota counters, chat limits or newer evidence with an older backup.
If the latest accounting state is lost, leave paid calls disabled until it
has been reconciled; do not reset a budget by restoring. Get help before
promoting recovered data. GitHub and the bundle do NOT contain this data.

For the evidence log there is also a checked copy tool. If no production
log exists yet it stops and says so, and the folder copy above is all you
need:

```powershell
python -B tools\triage\evidence_backup.py backup --dest E:\SantaPrivate\evidence
python -B tools\triage\evidence_backup.py restore-check --backup <the file it printed> --restore-dir E:\SantaPrivate\restore-test
```

`--dest` must be a private folder outside this project; `--restore-dir`
must be a new, empty folder, never the live log location.

## Decisions only you can make

1. **The GitHub repository is PUBLIC.** Checked on 2026-09-11: anyone can
   download lead-tracker.csv (prospect contacts), business\season-dashboard
   (business contacts), the OPN submission text and the six GPS-tagged photo
   originals under assets\ straight from github.com, no login needed. The
   website allowlist only protects the website, not the repository. To fix:
   on github.com open the repository, Settings, General, scroll to
   "Danger Zone", "Change repository visibility", choose Private. Check
   Vercel's GitHub access and a deployment afterward; private-repository
   support depends on the account, plan and integration permissions. Making it
   private does not undo the time it was public and does not remove the
   GPS data from Git history. A normal cleanup commit removes it only from
   the new revision. Historical removal requires a separately approved
   history rewrite and cannot recall existing clones or downloads.
2. **Paid AI for the OpenAI partner application.** The application clock
   starts only when a real customer message is answered by a real model and
   reviewed and actually sent by the operator, with truthful records over
   at least 15 days. The local evidence checker is not an eligibility
   guarantee; OpenAI's reviewers decide. That needs you to authorize a key and budget
   (docs\15-day-evidence-checklist.md); until you do, the application stays
   NOT STARTED and nothing in this project spends money.
3. **Where a public chat would run.** The chat backend needs an always-on
   server with permanent storage (docs\chat-release-status.md). Without that
   decision the chat stays a local practice copy, which is fine for the
   season: the website contact links are live, but form-to-inbox delivery
   still needs the explicit receipt test above.
4. **Stripe.** No Stripe Payment Link is configured (tools\triage\pricing.json
   has none), so deposits are Zelle to 305-244-0360 only. If you want card
   deposits, create a Payment Link inside Stripe and have the public
   buy.stripe.com address added to pricing.json; Stripe bank details and
   keys never go in this project.
5. **Old Vercel deployments.** Every earlier deployment keeps its own
   *.vercel.app address and still serves what it was built with:
   deployments from 09a48e0 (2026-09-10) up to but not including b2ffa09
   served the six GPS-tagged originals, and deployments before 09a48e0
   served the whole repository, including lead-tracker.csv, business\,
   docs\ and tools\. Nobody has deleted them, and only your Vercel account
   can: in the Vercel dashboard open the project, Deployments, and delete
   only the identified unsafe historical deployments after confirming they
   are not current Production or a required safe rollback. Record their IDs
   first. Do not bulk-delete based on age alone. Then open one of
   the old addresses (two are written in
   docs\marketing-deployment-2026-09-11.md) in a private window; it must no
   longer load.
6. **Vercel plan.** The site was published on the existing Vercel Hobby plan
   with no billing change. Vercel describes Hobby as personal,
   non-commercial use (https://vercel.com/docs/plans/hobby); this is a
   business site. Confirm the plan under Vercel Settings, Billing, and
   decide whether to upgrade. No upgrade has been paid for or authorized
   here. Continued availability or compliance is not guaranteed. No agent
   monitoring is promised after handoff, so
   make sure the Vercel account email is one you read.
7. **Insurance.** There is no verified commercial liability policy:
   business\insurance-and-wave1-preflight.md records NOT ACTIVE / NOT
   VERIFIED (2026-08-26) with a deadline of 2026-10-26. Decide whether to
   buy it. Until you hold the policy document, never tell a customer, school
   or HOA, in any language or channel, that you are insured or can send a
   certificate; the website and reply drafts are written without that
   claim, and the release check refuses public pages that make it. When the
   policy is real, update that file and keep the proof outside the website.

## Resume later

Give the next developer or coding tool this folder and START-SANTA.md.
Read current Git status and both mailboxes before changing files. Preserve
unfinished work. Run `python -B scripts/ops_check.py` with paid API settings
disabled. Pytest is required for tests, not for running the workshop.
Publishing works only as described in "Update the website" above; local
edits are not publication.
Do not reset private budget/evidence state or claim synthetic tests as use.

No ongoing coding-agent scheduler is promised by this handoff. Existing
external accounts, hosting and billing remain the owner's responsibility.
