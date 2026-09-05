# Santa Launch Checklist

Checked September 5, 2026, Miami time. This is a launch handoff, not a
declaration that the deployment is live or that OPN has accepted it.

## First Working Customer AI Workflow

Marcelo receives a genuine business inquiry, generates an English/Spanish
draft, reviews it, and sends the approved reply through the existing
customer channel. Stripe and an automated phone agent are not prerequisites
for this human-operated inquiry workflow.

| Item | Current evidence | Remaining action |
| --- | --- | --- |
| Bilingual inquiry and review software | Local form, private queue, six gates, snapshot-bound approval/send tracking and logout privacy fixes independently reviewed; full local checks pass | Verify the hosted synthetic workflow after hosting controls are ready |
| Launch-readiness checker | Claude's handoff reviewed; R1/R2 origin/proxy mismatches corrected with regressions. Suite registered and full local release check passes | Run in the actual configured runtime; exit 0 does not verify host deployment or model access |
| Working model connection | Last operator-supplied API result was HTTP 429 with offline fallback; this Codex process has no API key | Check API billing/limits in the owning project, configure the key privately in the runtime, and verify one synthetic request uses the selected model successfully |
| Operational owner | Marcelo Zapata operates the workflow; performers deliver the Santa visit | Choose when/how the inbox will be checked and retain actual review/send records |
| Local assisted operation | Existing email/phone inbox plus the triage CLI can be operated without a public backend | Follow production-launch.md in the configured operator terminal when a genuine inquiry arrives |
| 24/7 website intake | Public site is static; new queue has not been connected to it | Select and authorize a persistent HTTPS host, deployment, and website routing after synthetic end-to-end verification |
| First production evidence | No new model-backed customer use was established by this build | Keep the actual inquiry, model result, reviewer, timestamps and real outcome privately; derive dates from actual operation |

## Hosting Shape

Existing configuration check, September 4, 2026 (Miami): README.md and
vercel.json describe a static Vercel website. No local Vercel project link
is present, so the actual account, current plan and available credit remain
unverified. Do not sign up for another service or upgrade an existing plan
from this checklist; no new spending is assumed authorized.

The current SQLite-backed inquiry process cannot simply be uploaded as a
Vercel Function: function storage does not provide the shared persistent
filesystem this design requires. Reusing Vercel for the backend would need
a storage/runtime redesign and fresh verification. Keep the existing site
unchanged while selecting the backend. See
[Vercel's SQLite guidance](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel).
Check the existing plan as well: Vercel describes Hobby as personal,
non-commercial use; do not assume it covers this business or that an upgrade
has already been paid for. See [Hobby limits](https://vercel.com/docs/plans/hobby).

The existing public website stays at miamipapanoel.com. Its inquiry link
will lead to the hosted Mrs. Claus form. One backend process stores the
queue on a private persistent disk; an HTTPS proxy protects it. Marcelo
uses the authenticated operator page to generate/review replies. Model
calls happen only on operator action, not for every form submission.

The host needs process restart, backups with a tested restore, health/error
monitoring and server-side secrets. Do not put the current SQLite queue on
an ephemeral serverless filesystem. Keep the current local preview private
until those controls are verified. A phone cannot directly reach this
computer's 127.0.0.1 address; that address is not a public deployment.

The shared-proxy submission bottleneck is fixed locally: a configured exact
proxy peer supplies one overwritten client address, with separate client and
global limits. Forged forwarding headers are ignored in default mode. The
deployment kit at deploy/inquiry/README.md provides offline-first systemd,
nginx HTTPS, authenticated storage checks and daily private backup templates.
It is not installed or a claim of 24/7 operation. The selected Linux host
still needs configuration validation, HTTPS/phone browser QA, restart/restore
verification, disk/off-host monitoring and a tested owner alert destination.

An always-on hosted runtime would operate independently of Codex or Claude
coding subscriptions. Hosting and API availability still need their own
account/billing configuration. No new service has been purchased here.

## Other Requested Features

| Feature | What remains |
| --- | --- |
| Stripe deposits | Owner completes the correct legal-business verification in Stripe and creates a real public Payment Link. Wire the real link, reconcile public terms, and test the 50% human-verification path. Never send bank details or secret keys in chat. |
| Automatic availability updates | Current export is a manually deployed local snapshot. A persistent booking source, authenticated update path and deployment integration must be connected and tested before claiming live removal. |
| Automatic confirmations | Current software produces approved drafts; it does not deliver customer messages. Connect a delivery provider and test retries/idempotency after owner authorization. |
| Mrs. Claus calls/texts | The 786-975-9557 T-Mobile line is not yet connected to an automated voice/SMS provider. Provider setup, number strategy, inbound routing, disclosures and testing remain. No recording is enabled. |
| Santa content and scheduled posting | Draft/approval tools exist. Real media/provider integration, social credentials and approved schedules remain; no live publishing is claimed. |
| Elves outreach | Draft-only workflow exists; approved recipients/channels and sending integration remain. No bulk outreach is enabled. |

## Owner Inputs Needed Next

1. Privately resolve the API billing/limit issue and configure the intended
   model in the terminal or host that will actually run the workflow.
2. Sign in to the existing Vercel account so the Santa project and plan can
   be inspected; no authenticated account was accessible in the app at the
   latest check. Decide and authorize the backend deployment arrangement
   before public routing. Do not create an account or spend from this list.
3. When Stripe verification is ready, provide only the public Payment Link.
4. Choose the phone provider/number arrangement before any transfer or setup.

## Release and Evidence

Overnight booking/travel checks are now fixed and independently reviewed:
overlaps, insufficient drive/setup/safety time, reverse booking order and
year rollover are covered. Date refreshes retain conflicts. The operator
runbook's route commands have also been repaired and parsed successfully.
See the workboard for exact test results and independent review findings.
The inquiry concurrency/privacy fixes have now also passed independent
review and the full local check. This does not approve public deployment.
The latest North Pole branding needs a fresh visual browser check; no new
preview process was started during commit wrap-up. Hosting templates remain
uninstalled and must be validated on the selected host.

Fresh CLI status remains NOT STARTED. The local port 8226 preview is stopped,
not hosted, and its prior synthetic data must not be reused as production.

Run `python scripts/ops_check.py` after final edits and independently review
pending changes. Tests and scheduled health checks do not create customer
activity. Keep all private queue data, receipts and logs outside Git.

The OPN email requests an active customer AI workflow, launch/status,
owner, functionality, concrete outcome, specific model, architecture,
release testing/approval, monitoring/failure handling, and at least 15 days
of production operation. It does not specify that Santa must telephone
OpenAI or purchase Stripe. Use the existing submission fields and label the
current operating status accurately. OPN makes the acceptance decision.

See production-launch.md for the operator steps and tools/web_inquiry/README.md
for private storage, setup, fallback and deployment prerequisites. Record
implementation verification in santa-agent-workboard.md, not repeated test
counts throughout the submission packet.
