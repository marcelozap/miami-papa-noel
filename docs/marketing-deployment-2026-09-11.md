# Marketing Website Deployment

## Latest: Santa Photo Gallery

Verified 2026-09-11T14:02:12Z at https://miamipapanoel.com/.
Release b2ffa094f5fa89f72d21d0a4114c39140c5d62c5 includes five bilingual
gallery photos, keyboard-accessible viewer, preparation acknowledgement
summary fix, and previously local source-preservation commits.
The backend source is saved on GitHub, not deployed. Paid AI remains off.

Independent offline ops: 824 passed, 7 skipped, 52 subtests; all seven steps
PASS. Public build: 53 allowlisted files. Local HTTP mobile review at 390
outer/375 content pixels has no horizontal overflow and five decoded images.
Live homepage/book/five gallery images return 200 and match Git bytes.
Six private URLs and six GPS-tagged originals return 404 on the production
domain. Old deployment URLs and Git history were not purged.

Deploy without an assistant: run the offline checks, build with
`node scripts/build_public_site.cjs`, review the explicit allowlist, then push
an approved commit to main through the existing Vercel integration.
For rollback, prefer a reviewed forward fix/revert that RETAINS the GPS
exclusions. Promoting older releases could restore the removed originals.
No billing, Stripe, DNS, customer-send or production-evidence changes occurred.

## Latest: Simplified Customer Site

Verified 2026-09-11 through 03:00:29 UTC. Supersedes the earlier release below.

- Public URL: https://miamipapanoel.com/
- Commit: 526f1d1ef20eb205f81b3e42695b910563c69124
- Vercel production: 7F3TP1J48j9hHrpSvgbjQUyRNK6y, Ready
- Hostname: miami-papa-noel-pnju5obyj-marcelos-projects-5a09363b.vercel.app
- Changed files: index.html, book.html, scripts/test_public_release.py only.
- Both main and santa-ops-hardening-2026-09-04 point at this commit.

The owner explicitly requested the push before bed. Claude 026 independently
verified the simplification with no blocking findings. The isolated release
(HEAD plus exactly these three files) passed all seven offline ops checks:
716 passed, 7 skipped, 1 warning, 52 subtests, 23 suites. Warning detail was
not retained by the ops summary. This differs from the 821-pass working-tree
run because unfinished tools were intentionally not included in the commit.
Pushed both branches atomically without force; main triggered production.

Public homepage, booking page and both portraits returned 200 and matched
the commit byte-for-byte. Six private routes returned 404: dashboard HTML,
lead tracker, OPN submission, triage pricing, .env and .git/config. The initial
verification script stopped at a legitimate HTTP 308 clean-URL redirect;
after adding redirect support, all checks passed. No site fix was needed.
Live desktop EN/ES, family-card preselection, collapsed optional fields,
four required preparation checkboxes and no overflow were verified without
submitting. Narrow-screen layout/photo QA remains the earlier local browser
frame checks on the identical bytes, not a fresh physical-phone test.

No account is needed for a customer visit request. The site is simpler, but
this is still NOT a public AI chatbot launch. Paid generation stays disabled;
no provider settings, subscriptions, DNS or billing changed. All unfinished
backend/operator/docs work remains local and uncommitted. No customer data
or messages were generated or sent. This handoff is local, not in the release.

Known pre-existing limitation: alternate SMS/WhatsApp/email/copy messages do
not carry the four preparation acknowledgements. Unlike the POST form, those
links also do not enforce the required checkbox validation. Confirm those
details manually before finalizing a booking; this release does not alter it.

Rollback candidate: prior verified production 4X4jssQTuFnDe8vCMTPVqH73GJHu
at 5133819 retains the public-build boundary. Subject to Vercel retention,
re-promote that deployment and recheck public/private paths, or revert only
526f1d1 in a new reviewed commit. Do not reset this shared dirty worktree.

## Earlier Release Record

Verified 2026-09-11 through 02:32:58 UTC. Marketing site only, not AI launch.

## Published Release

- Website: https://miamipapanoel.com/
- Repository: https://github.com/marcelozap/miami-papa-noel
- Production branch: main, verified in the authenticated Vercel overview.
- Commit: 513381952eac3f5112d2f8ca1080b06c84252dec
- Production deployment: 4X4jssQTuFnDe8vCMTPVqH73GJHu
- Deployment hostname: miami-papa-noel-dfblj9i73-marcelos-projects-5a09363b.vercel.app
- Preview verified first: G2aym7PCb5DTDYuYAzVPJmokCbvG
- Previous production: 2e6unMc5u7UQhw45HCBGn2DxKBtf, source main/882433d.

The owner authorized publication in this chat. Commit 09a48e0 contains the
nine approved marketing files. Commit 5133819 adds only the missing public
test-suite registration. The ops branch was pushed for preview, then main
was fast-forwarded without force to exactly that reviewed release. Existing
committed ancestors moved with main; no pending feature files were staged.

## What Visitors Get

The bilingual marketing pages, two approved solo Santa portraits, existing
visit-request pages, and ordinary call/text/WhatsApp contact links. The public
phone remains 786-975-9557. No new chatbot, automated phone answering, payment
processing, booking confirmation or payment verification was activated.
Pricing sources were not changed. Insurance remains NOT ACTIVE / NOT VERIFIED.

## Verification

The clean release source tree matches the separately tested snapshot:
713 passed, 7 skipped, 1 warning, 52 subtests, 23 suites, all seven ops-check
steps PASS. The ops summary did not retain the warning's details.

All 58 manifest paths returned HTTP 200 from the public site and matched the
release: 35 binary files byte-exact, 23 text files byte-exact against Git
blobs. Comparing text to Windows checkout bytes initially mismatched CRLF
versus Linux LF; the corrected Git-blob comparison verified all 23.

These public-domain paths returned 404:

- /business/season-dashboard/index.html
- /business/season-dashboard/
- /lead-tracker.csv
- /docs/OPN-SUBMISSION.md
- /tools/triage/pricing.json
- /scripts/ops_check.py
- /.env
- /.git/config
- /deploy/public-files.json

These are sampled exclusion checks, not proof about every possible URL.
The build separately copies only the 58 reviewed manifest files to dist.
Anonymous preview requests had redirected to Vercel login, so their final
200 statuses were not treated as website or exclusion verification.
Authenticated preview navigation confirmed actual 404 pages before release.

Live desktop language switching, hero portrait, and public phone links were
checked in the browser. Both portraits loaded in preview. Mobile 390/360px
EN/ES checks were performed earlier on the identical local public artifact;
no new live-mobile screenshot was taken in this publication pass. No form
submission, customer send, booking, payment, or model request was performed.

## Cost and Operation

Existing Vercel project and Hobby plan were used without changing billing,
DNS, environment variables, analytics, or paid features. No new recurring
service was added and no OpenAI API call was made. This is not a guarantee
about future provider charges, quotas, plan eligibility, or domain renewals.
Hosting/account ownership continues independently of coding subscriptions.
The paid AI path and unfinished backend remain separate work.

## Redeploy Without a Coding Subscription

Use the existing GitHub repository and Vercel account. Changes to main trigger
production deployment; other branches currently build previews. Never push
the entire dirty working tree without reviewing exactly what is staged.

Keep vercel.json's buildCommand as node scripts/build_public_site.cjs and
outputDirectory as dist. Keep deploy/public-files.json as the explicit public
allowlist. Add only approved public assets/pages to it. Keep customer records,
keys, operator tools, mailboxes and private files outside that artifact.

Run the offline release tests with MPN_API_DAILY_CALL_CAP=0 and
MPN_CHAT_ALLOW_MODEL=0, plus an empty OPENAI_API_KEY. Test the actual staged
release in isolation, not just a working tree containing unfinished changes.
Build the public artifact, review a Vercel preview, then publish the tested
commit to main and verify the production domain and excluded paths again.

The operational price source is tools/triage/pricing.json, not this report.
Any future public price changes need consistency checks and owner approval.

## Rollback

Do not blindly promote the previous production deployment: it predates the
explicit public-build boundary. A visual rollback should restore only the
appropriate previously approved marketing content in a new reviewed commit,
while preserving the manifest-only build, output directory, exclusion rules
and tests. Verify asset/link integrity and private-path 404s again. Never
reset the shared working tree or overwrite unfinished work as a rollback.

For future releases, this verified production deployment can be considered
as a rollback candidate, subject to Vercel retention and a fresh safety check.

## Separate Unfinished Work

The pending customer-chat integration, operator dashboard, offline workshop,
OPN packet changes and other working-tree edits remain local and uncommitted.
This publication does not establish model-backed customer operation, start
the 15-day evidence window, or establish OpenAI Partner Network eligibility.
This report and the latest coordination notes are local handoff files and
were not included in the deployed commit.
