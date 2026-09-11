# Mrs. Claus Office: Inquiry Review

This is a **local, operator-assisted inquiry workflow**, not the public
website deployment or an automatic phone/text agent. It uses the existing
triage engine. Booking availability and deposit verification remain in the
existing reservation system; this queue never changes them.

## Start Locally

Use Python 3.10+ and a PowerShell window. No third-party runtime packages
are needed to run the service. Tests use pytest and Node.js 18+ for the
client-session regression harness; no npm packages are required.

```powershell
Set-Location 'C:\XIV\santa'
$secret = Read-Host 'Private operator token (32+ random ASCII characters)' -AsSecureString
$env:MPN_OPERATOR_TOKEN = [System.Net.NetworkCredential]::new('', $secret).Password
$env:MPN_INQUIRY_DIR = Join-Path $env:LOCALAPPDATA 'MiamiPapaNoel\web-inquiry-demo'
python tools\web_inquiry\server.py --offline
```

Open <http://127.0.0.1:8226/> for the form and
<http://127.0.0.1:8226/operator> for private review. Enter your operator name
and token on the review screen. The token stays in browser memory, not
browser storage or cookies. Reloading or signing out removes access from
that page. Never use the synthetic token in the test suite for operation.

Set `MPN_CHAT_SECRET` (64 hex characters, at least 32 random bytes) to enable
the public chat widget at `/`; leave it unset to run the form only, exactly
as before. Generate one locally with
`python -c "import secrets;print(secrets.token_hex(32))"` and never commit
it. The secret must stay the same across restarts and worker processes -
tools/web_chat_guard fails closed on a changed or missing secret rather than
silently resetting anyone's rate limit.

```powershell
$env:MPN_CHAT_SECRET = (python -c "import secrets;print(secrets.token_hex(32))")
```

Use `--port 8227` if another program already occupies 8226. The service
refuses a second process using the same data directory. Stop with Ctrl+C.
The computer and server process must stay running for this local version;
a Codex/Claude development loop is **not** a hosting service.

Default mode accepts **synthetic requests only** and cannot mark one as
real customer activity. `--offline` additionally prevents any API call,
even if API credentials are present in the launching shell.

## Operate an Inquiry

1. Submit name, phone/email, inquiry, and consent. A successful receipt
   means the request was durably saved, not booked. Submitting does not
   call OpenAI or send anything to the customer.
2. Sign in at `/operator`, refresh the queue, and select a request. Older
   requests are available in additional pages of 100.
3. Select **Generate draft**. Only this authenticated action can call the
   model. Both English and Spanish drafts appear; the detected language
   appears first. The actual model or offline fallback is shown.
4. Review both drafts, all validation results, prices, and missing details.
   Reject an unsuitable draft. Regenerate a reviewable draft after changes
   to pricing/prompt policy; approval rechecks the current six gates and
   version identifiers. Approval, rejection and manual-send recording must
   match the exact saved snapshot displayed in that tab. A stale tab gets a
   conflict and must refresh/review; it cannot approve an unseen regenerated
   draft. No in-browser free-text edits bypass the gates.
5. Choose the reply language and approve. Approval does not send anything.
   Copy the approved reply and send it yourself through the agreed customer
   channel. Only afterward select **Record manual send** and confirm.
   This is an operator attestation, not provider proof of delivery.
6. Export evidence from the toolbar when needed. Review remains required
   for an offline fallback; it never counts as successful model use.

The queue does not send email alerts or poll automatically. An operator
must check it while accepting inquiries. There are no customer-facing
AI responses until the operator actually sends an approved reply.

## Chat with Mrs. Claus

When `MPN_CHAT_SECRET` is set, `/` shows a chat thread instead of the plain
form. This talks to `tools.web_chat.service.ChatService` (template-first
replies, sensitive-topic keywords routed to a human, optional model path
left off by default - set `MPN_CHAT_ALLOW_MODEL=1` only after owner
approval, and even then the existing triage call cap and estimated-cost
guard still apply) through `tools.web_chat_guard.guard.AdmissionGuard`
(server-side rate limit, duplicate suppression, and daily capacity, keyed
by a hashed caller identity - no raw IP or message text is stored).

Each visitor's browser session keeps its own short-lived running context
in the server process only (never in browser storage, matching the
existing no-persistent-storage rule for this file): later messages build
on earlier ones so Mrs. Claus does not re-ask for a date the visitor
already gave. A page reload starts a new context; the bounded per-session
turn count and character limit are separate from, and in addition to, the
guard's own six-turns-per-five-minutes and 200-per-day caps.

`App.chat_reply()` also enforces its own per-visitor daily ceiling
(`CHAT_DAILY_TURNS_PER_CALLER`, default 3), independent of and stricter
than the guard's 200-turns/day *global* pool - the guard limits the site's
total, this limits one caller's share of it, so a single visitor (or a
script) cannot exhaust the whole day's allowance before anyone else gets a
turn. Identity is a salted hash of the verified IP (same trust boundary as
`client_ip()`/the operator-desk rate limiter), never stored raw, tracked
in-memory only and reset at the next UTC day. Reaching it shows a distinct
"you've reached today's limit" message (not the guard's "check back
tomorrow" one, since it resets for that visitor at midnight UTC just like
the shared pool, but the wording should read as personal, not sitewide) and
points at the send-to-team form and the phone number - never a dead end.

Chatting never creates an operator-visible inquiry by itself - that stays
consent-gated. The visitor sends the conversation to the team with a small
"Ready to send this to our team?" form (name, phone/email, the same consent
checkbox as before) that posts the visible transcript through the existing
`/api/inquiry` endpoint, unchanged. This is the replacement for the old
copy-and-paste-into-email flow: the transcript is filled in automatically
instead of retyped, but a human still explicitly chooses to send it, and an
operator still drafts, reviews and manually sends any reply, exactly as
before. Nothing here confirms a booking, availability, or a price outside
`tools/triage/pricing.json`.

`tools/web_chat_http/` is a separate, independently delivered adapter that
also exposes a bounded `POST /api/chat` on top of the same `App` and
`ChatService`/`AdmissionGuard` pair, as its own `ChatServer` class with its
own entrypoint. It is not used by `server.py`'s own chat route above; see
that module's README before running both, to avoid maintaining two chat
entrypoints for the same feature.

## Storage and Privacy

`MPN_INQUIRY_DIR` contains:

- `inquiries.sqlite3`: customer messages/contact, draft versions currently
  under review, approval/send state, and timestamped audit events.
- `server.lock`: prevents two local processes from owning the same queue.
- `evidence/synthetic-log.jsonl` and `evidence/production-log.jsonl`:
  replaceable metadata snapshots generated only when records exist.

The data directory must be **outside the repository**. The code rejects
paths within `C:\XIV\santa`. Do not copy private state into another public
repository or synchronize it to a shared folder. This application does
not encrypt SQLite; use a private OS account, appropriate folder
permissions, disk encryption, and private backups. Retention/deletion is
an operator responsibility. There is no automatic deletion policy.

The form discloses that inquiry/contact text is sent to OpenAI when the
operator uses AI drafting. Offline drafting has no network egress.
The existing adapter uses `store: false`; this is not a promise that the
API provider has no retention of any kind. Do not enter patient details,
children's identifying information, card numbers, or bank credentials.

The HTTP access log is suppressed. Browser responses are non-cacheable;
tokens are sent only in the Authorization header. Exact Host and Origin
checks, fixed asset routes, no CORS, a restrictive content policy, payload
limits, contact/consent validation, duplicate keys/body checks, and
in-memory rate limits guard the local workflow. Inquiry text is rendered
as text, never HTML. These controls do not turn the stdlib development
server into an Internet-hardened service.

Malformed or excessively nested request JSON returns a generic bilingual
400 response before any inquiry is stored or model call is attempted. Raw
input and parser tracebacks are not included in that response or access log.

Sign-out aborts outstanding operator requests, clears the displayed queue,
and invalidates their session. Late responses cannot redisplay private data
or overwrite a later login/refresh. Sign-out does not undo an action the
server already completed before it received the disconnect.

Use `maintenance.py backup --database PATH --backup-dir PRIVATE_DIRECTORY`
for an online SQLite backup and `maintenance.py restore-check --backup PATH
--restore-dir NEW_DIRECTORY` for an isolated restore drill. The target's
parent must exist outside Git; the restore directory must not exist. Both
commands validate integrity, schema and data without starting the app or
replaying events. Keep backups encrypted/private and configure retention,
off-host copies and disk alerts. Export alone is not a backup. See
`deploy/inquiry/README.md` for the deployment and recovery procedure.

## Evidence Is Not a Launch Claim

Default demo operation cannot attest real activity. For genuine customer
operation after the deployment steps below, use a separate private data
directory and explicitly start with `--live` (and omit `--offline` only
when intentionally enabling configured model calls). The operator must
then separately select the genuine-inquiry checkbox when approving each
real request. The flag by itself does not create production evidence.

Each export contains one current record per inquiry ID, separated by
the `real_customer` flag. Draft bodies/contact values are omitted from
these exports. Operator names and operational metadata remain private.
Queue events preserve transitions; exported JSONL is a **snapshot**, not
an immutable event ledger. Draft regeneration replaces the current draft;
the queue is not an archive of every historical draft body.

`received_at` in the exported triage record is the time drafting actually
ran, not an earlier inferred launch date. Intake receipt time is stored
separately in SQLite. Approval and manual-send timestamps are generated
at their respective actions, in UTC. An approved offline response remains
offline evidence. A synthetic model fixture remains synthetic evidence.

Do not append these snapshots to the CLI's JSONL: that validator expects
unique IDs. To inspect only this workflow's exported records, pass its
external evidence directory explicitly:

```powershell
python scripts\validate_opn_submission.py --preflight --log-dir "$env:MPN_INQUIRY_DIR\evidence"
```

Preflight is not final qualification. A working demo, a heartbeat, an
API key, an enabled `--live` flag, or a manual test is not evidence that a
customer AI deployment has operated for 15 days. This tool does not
declare a launch date, qualification date, or guaranteed OPN acceptance.

## Deployment Prerequisites

The public marketing site does **not** link to this service. An earlier
revision of this file said its primary button pointed at a placeholder
hostname; that was true of an earlier working tree and is no longer true -
as of 2026-09-11 `index.html` and `book.html` contain no chat link and no
chat copy at all (verified: zero occurrences of `inquiry.example.invalid`,
"chat", or "Mrs. Claus" in either). The placeholder hostname survives only
in deployment examples and internal notes, never in a served page.

So there is no dead link to fix - there is a link to *add*, once a real
host exists. `deploy/inquiry/nginx.conf.example` still uses
`inquiry.example.invalid` as its example hostname. Before genuine public
intake:

1. Choose an approved, continuously running host with a private persistent
   volume and backups. Keep one application process per data directory.
   Do not place this SQLite queue on ephemeral serverless storage.
2. Put a production HTTPS reverse proxy in front of the loopback listener.
   Set `MPN_PUBLIC_ORIGIN` to the exact externally visible origin, such as
   a domain the owner actually controls. Preserve that Host header and
   forward requests only through the trusted proxy. Do not expose the
   Python listener directly to the Internet.
3. Configure TLS, connection/body/time limits, provider-level abuse
   controls, and operator-route protection. With no trusted proxy configured,
   the app ignores forwarding headers. For the same-host proxy in the
   deployment kit, set `MPN_TRUSTED_PROXY_IP=127.0.0.1`; that exact peer must
   supply one `X-MPN-Client-IP` header overwritten with its actual socket
   client address. Other peers and missing/invalid/duplicate identities are
   refused. The app normalizes IPv4/IPv6 identities, keeps five public
   submissions per client per five minutes, and a global 100 per five minutes.
   Operator limits are separate. Tests cover spoofing and client rotation;
   validate the real proxy configuration before launch. Do not trust incoming
   visitor headers, arbitrary proxy chains or disable limits. In-memory limits
   reset on process restart. See `deploy/inquiry/nginx.conf.example`.
4. Install a private operator token through the host's secret settings.
   Configure OpenAI credentials/model server-side only when funded and
   authorized. Confirm a synthetic model-backed test succeeds; the last
   reported HTTP 429 is not resolved by this local build. Claude credits
   are separate from hosting and API service availability.
5. Install and verify the supervisor/restart, backup/restore and monitoring
   setup in `deploy/inquiry/README.md` on the approved host. `/health` reports
   process liveness only. Authenticated `/api/readiness` checks storage and
   returns private queue/error counts, not model, payment or channel readiness.
   The health timer writes status to the journal, not a delivered notification;
   configure and test an alert destination, backup-age/off-host monitoring and
   disk-space alerts. An operational owner must still check the queue.
6. Review consent/retention and approved business terms. Verify the entire
   synthetic flow on HTTPS before changing the actual site's inquiry
   route. Public deployment, DNS changes, and enabling actual customer
   operation require owner authorization.
7. Replace the `inquiry.example.invalid` placeholder in
   `deploy/inquiry/nginx.conf.example` with the real, owner-approved
   hostname from step 2. Only then add a link to it from the marketing
   pages - and note that `deploy/public-files.json` is the allowlist that
   decides what the site actually publishes, so a new page or asset must
   be added there deliberately, not just dropped in the repository.

Stripe verification/payment links, mobile voice/SMS integration, and
recording consent are separate unfinished provider tasks. This component
does not depend on Stripe to draft inquiries, but it does not enable
card payments, calls, texts, recordings, or automatic reservations.

## Manual Fallback

- **Form unavailable or no receipt:** no acceptance is claimed. Use the
  published phone/email. Preserve the message for the operator and avoid
  repeated submissions with changed details until its receipt is checked.
- **API unavailable/429:** public requests remain in the queue. Use the
  clearly labeled offline draft after human review, or defer a reply.
  Do not record an offline response as a successful model run.
- **Draft failure:** the inquiry stays saved; refresh and retry after the
  cause is fixed. A restart marks an interrupted draft failed, not sent.
- **Unsafe/stale draft:** reject it or regenerate under current policy;
  do not bypass approval by hand-editing state. Requests never reserve
  slots or verify deposits.
- **Complete service outage:** use the existing approved reply templates
  and manual channels. Record actual operator work through the existing
  procedure, without inventing successful queue/API actions.
- **Evidence export failure:** keep the private database, resolve storage,
  and retry Export. Completed review/send state remains in the database;
  do not pretend an unsuccessful export exists.

## Verify

```powershell
python -m pytest tools\web_inquiry\test_web_inquiry.py -q
python scripts\ops_check.py
```

Tests isolate state in temporary folders and clear API credentials. The
live-attestation and model-success branches use explicit synthetic
fixtures only. Browser QA must likewise use the demo mode and synthetic
contacts, never generate a real customer's activity to satisfy a test.
