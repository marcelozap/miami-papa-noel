# Claude: Santa Launch Preflight

## Task Delivered: Coordinator Wrap-Up

September 5, 2026: Claude delivered the handoff. Codex independently verified
it and closed the remaining direct-demo origin/proxy mismatch, with focused
regressions, then registered the suite in ops_check. The user authorized
Codex to commit the reviewed work locally. Do not rebuild this task or edit
its folder during the final verification/commit window. The original brief
below is historical context; read the latest workboard checkpoint first.
Remaining public-host/API/Stripe/phone inputs are recorded in the launch
checklist. Do not loop on unchanged missing account access or credentials.

Work in `C:\XIV\santa`. Read `C:\XIV\START_HERE.md`, `CLAUDE.md`, `loop.md`,
`docs/santa-agent-workboard.md`, `docs/tonight-launch-checklist.md`,
`docs/north-pole-agent-team.md`, `deploy/inquiry/README.md` and
`tools/web_inquiry/README.md` first. Inspect Git status and recent commits.
Preserve all unfinished work. Do not restart from an old project folder.

## Coordinator Update After Your Verification

Your 22-case local HTTP verification and final ops result are recorded in
the shared workboard. The trusted-proxy, storage-readiness, backup/restore
and deployment-template work is now reviewed and locally verified; it is
not deployed. Do not rebuild it. The task below was reserved for you and
has now been delivered, as noted above.

Include the location of your consolidated synthetic probe script/results
and, if retained, the earlier failing test IDs and sanitized tracebacks in
your handoff. Passing reruns alone do not establish concurrent edits as the
cause. Checkpoint before a coordinator full-battery run; do not edit files
during that agreed verification window. Never include tokens or private
customer records in verification artifacts.

## Your Bounded Task

Implement a read-only, stdlib Python launch-preflight CLI, focused tests and
README in the reserved **new** directory `tools/launch_preflight/` only.
The reservation is PLANNED on the shared workboard. Codex is reviewing the
inquiry service, backups, hosting templates and North Pole branding; do not
edit those files or `scripts/ops_check.py`. Return progress and final results
in `tools/launch_preflight/handoff.md` so Codex can integrate without a
workboard write race. If another worker has claimed this folder, stop editing
and report the collision rather than switching to their files.

Deliver a command that tells Marcelo what is actually missing for the
operator-assisted bilingual inquiry launch, without exposing secrets or
creating production evidence:

1. Reuse/read the existing configuration contracts. Report presence only for
   `OPENAI_API_KEY` and `MPN_OPERATOR_TOKEN`; never their contents, prefixes,
   hashes or lengths. Check required token validity privately. A configured
   key/model is CONFIGURED, never VERIFIED or proof the earlier HTTP 429 ended.
2. Validate an explicitly selected HTTPS origin, reject placeholder domains,
   and check the exact trusted-proxy setting for the documented single-host
   topology. Keep local demo readiness separate from public-host readiness.
3. Check an explicitly selected existing private data directory outside Git,
   source database existence, path/link safety and supported platform/runtime.
   Use the maintenance tool's read-only validation API if appropriate. Do not
   start App, acquire its lease, create files in the queue, migrate records,
   write a production log or assume that an ephemeral mount is persistent.
4. Check static deployment prerequisites where locally observable. Host TLS,
   reboot persistence, alert delivery, off-host restore and successful model
   access must remain NOT VERIFIED until supported by actual checks. Do not
   infer them from a file existing. Clearly separate configuration, locally
   verified checks and owner/host verification still needed.
5. Report Stripe verification/public Payment Link and phone/provider wiring
   as separate unfinished features, not blockers to an assisted inquiry reply.
   No public Payment Link exists yet; 786-975-9557 is T-Mobile, with no proven
   automated calls or SMS. Do not substitute fake providers or URLs.
6. Default to no network, no model call and no side effects. Provide concise
   human output and JSON, deterministic exit codes, redacted errors and
   tests for missing config, placeholder origin, unsafe path, bad/missing
   database and secret-free output. Tests use synthetic temporary state only.

Do not duplicate existing release tests or change the OPN qualification
validator. Before designing flags, inspect the existing host/maintenance CLI
so your preflight fits their interfaces. Record limitations, not fake green
checks. Keep the implementation small and focused.

## North Pole Identity

All agents belong to Miami Papa Noel's North Pole Workshop. The actual
display names are Mrs. Claus, Santa Claus and Elf #1 onward. Mrs. Claus owns
communications, with a warm female EN/ES voice when a voice provider is
connected. Santa Claus owns content. Elf #1 handles bookings, Elf #2 real
travel planning, Elf #3 outreach and Elf #4 monitoring. Job descriptions
are secondary labels, not alternative character names. Marcelo remains the
human operator. Retain stable actor IDs and existing approval/payment gates.
No persona implies that a provider connection or customer deployment is live.

## Boundaries and Completion

No commits, staging, resets, pushes, public deployment, DNS/account changes,
purchases, customer charges/messages, number transfers, recordings, social
posting, real-state writes or invented customer/model/launch evidence. Do not
ask for credentials in chat. Do not re-argue the 2025 history or promise OPN
acceptance. The current build is local and the actual launch is still pending.

Run your focused tests, review negative cases and stop at READY_FOR_REVIEW.
Return exact changed files, test command/results, outstanding owner actions
and the test suite path that Codex must register in ops_check. Do not call
the whole Santa project complete. Do not touch any other folder without a
new coordinated claim. The loop is inspect, implement, test, review, fix,
test again, then hand off; do not loop on unchanged missing credentials.
