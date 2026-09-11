# Mrs. Claus Release Verification

## Current repair addendum - September 10, 2026

No deployment or production start in this repair pass. Public index.html and
book.html no longer advertise the undeployed chat or link to its placeholder.
Existing services, request, phone and WhatsApp paths are retained. Chat source
remains in tools/web_inquiry for later hosting work, not in the public artifact.

The new scripts/build_public_site.cjs uses deploy/public-files.json as an
explicit allowlist. vercel.json selects that build and dist as its output;
.vercelignore adds source-upload exclusions. Business/operator files, trackers,
docs and backend source are not copied to dist. These controls affect future
deployments only after the configuration is released. They neither prove nor
remove historical exposure through GitHub or earlier deployment URLs.

Claude's durable caller-limit/session-ownership changes and legacy-backup
compatibility are in the working tree; old blockers below are historical.
The active chat blockers are an approved persistent backend host, verified
HTTPS/entrypoint configuration, public browser/privacy checks, and truthful
model/template operating evidence. Paid model use remains disabled.

Read business/season-dashboard/README.md for no-subscription operation,
release/recovery commands and the dashboard's outstanding browser-verification
limit. No pricing source, phone, bank account, production log or budget ledger
was changed. The OPN final evidence requirements remain unmet.

## Historical September 9 verification

Checked September 9, 2026. RELEASE HELD, not deployed and not Day 1.

## Verified repository and hosting

- Repository: https://github.com/marcelozap/miami-papa-noel
- Local branch: santa-ops-hardening-2026-09-04; HEAD c14b896.
- Remote checkpoint codex/santa-checkpoint-2026-09-04: c14b896.
- Remote main: 882433d. No branch changed during this verification.
- Existing public site: https://www.miamipapanoel.com (Vercel response header).
  This URL is the existing website, NOT a newly deployed chat.
- GitHub commit status for c14b896 reports a successful Vercel deployment:
  https://vercel.com/marcelos-projects-5a09363b/miami-papa-noel/Fashpfwc6jhatRoMXTAaVpw8hEvz
  Therefore pushes must be treated as deployment-triggering, including
  checkpoint previews. Project production-branch settings not inspected.
- No local Vercel project linkage, CLI or GitHub Actions directory found.
- Existing backend template expects a Linux service, nginx, HTTPS, and
  durable local state. It starts tools/web_inquiry/server.py --offline.
- At that September 9 check, its hostname and proposed marketing-page Chat
  links used inquiry.example.invalid. The current repair removes those page
  links; the backend template still needs an approved real hostname.

Vercel's local SQLite storage limitation is documented at
https://vercel.com/kb/guide/is-sqlite-supported-in-vercel . This code needs
persistent shared SQLite; it is not a drop-in Vercel function deployment.
Do not substitute ephemeral disk or reset guards on cold starts.

## Actual entrypoint verification

Ran the actual server.py entrypoint, not just the separate HTTP adapter,
on localhost port 8237 with --offline, API key absent, chat model disabled,
call cap zero, synthetic-only token/secret and a temporary private directory.

Browser QA verified:
- The entrypoint serves the new chat screen and DEMO label.
- Spanish family-visit inquiry receives the locked $325 template reply.
- Chat-to-team form collects name/contact and requires explicit consent.
- Submitting synthetic-release@example.test yields an inquiry receipt with
  an explicit not-a-booking-confirmation disclaimer.
- Operator sign-in shows the same synthetic lead in status New, without
  approval, send or booking. Operator then signed out.
- Desktop 1440x1000 and mobile 375x812 screenshots checked. Santa photo
  loaded; document widths stayed within viewport. Mobile operator queue fits.
- Browser viewport restored afterward. No production evidence exported.
- Fresh full offline check: 775 passed, 6 skipped, 52 subtests; all 25 suites
  and seven ops steps PASS. Local QA listener stopped afterward.

## Release blockers

1. Claude 016 still needs the two fixes in Codex mailbox 014: durable
   personal/day accounting and session ownership isolation. Existing tests
   passing does not waive these independently reproduced failures.
2. An approved backend host/account with durable storage is not configured.
   The static Vercel site alone is insufficient for this server as written.
3. Replace placeholder Chat URLs only after the real backend HTTPS endpoint
   is verified. Do not guess an endpoint or change DNS without approval.
4. Keep model/template provenance truthful. The current local browser reply
   was a template, not proof of OpenAI use. No automatic chat interaction
   may be recorded as a human-reviewed-and-sent event.

## Costs and safe rollout

No purchases or paid API calls during verification. Existing Vercel plan
and billing amounts are unverified. Backend recurring cost remains unknown
until the owner identifies an account/host. Do not promise zero hosting cost.

Once the fixes and host are verified: run fresh tests and privacy checks,
review the complete diff, commit the explicit release paths, push the
checkpoint (expect a preview build), deploy backend in template-only mode,
verify HTTPS and synthetic intake, then update website Chat links and verify
the actual public journey. Do not enable AI, move main, or expose a broken
preview as a successful production release just to satisfy a date.

## Rollback

No new deployment exists to roll back. For the eventual rollout, record the
previous production deployment identifier before promotion. Re-promote that
known deployment for static-site rollback; restore the prior service code
release and restart the service for backend rollback. Preserve private queue,
admission and cost ledgers; never clear state to resolve a deploy problem.
Take and verify a private backup before any schema-changing release. If chat
must be removed, route visitors to the real phone/inquiry workflow rather
than a dead chat URL. No rollback action was executed during this check.
