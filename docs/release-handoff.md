# Pending Santa Release

> **Historical.** This plan was executed on 2026-09-08 (see the workboard).
> Do not re-run its push steps; current publishing is in START-SANTA.md,
> "Update the website".

Prepared by Codex, 2026-09-08. This is a publication plan, not authorization
to stage, commit, push, merge, deploy, or enable paid generation.

## Pre-release publication snapshot

- Local HEAD: 448e46c, branch santa-ops-hardening-2026-09-04.
- Remote santa-ops-hardening-2026-09-04: 448e46c.
- Remote codex/santa-checkpoint-2026-09-04: 448e46c.
- Remote main: 882433d; it does not contain the working branches' full code.
- Verified using git ls-remote during this task, not an old workboard claim.
- Index was empty. New spending/backup/readiness work remains uncommitted.
- No .github/workflows directory exists in this checkout. Do not assume a
  GitHub push runs these local tests or deploys the backend automatically.
- Public hosting/deployment behavior was not changed or verified here.
- GitHub API verified PR #1 is OPEN from codex/santa-checkpoint-2026-09-04
  into main: https://github.com/marcelozap/miami-papa-noel/pull/1.
  Pushing that checkpoint branch updates the existing PR, not only a branch.
  Recheck PR state and obtain approval for that effect before publishing.

## Explicit proposed file set

Inspect these paths individually after both workers freeze their handoffs.
Do not use git add -A or include private runtime files.

Runtime and regression tests:

```text
business/reservations/openai_adapter.py
business/reservations/tests/test_openai_adapter.py
scripts/ops_check.py
tools/triage/triage.py
tools/triage/test_triage.py
tools/triage/spend_guard.py
tools/triage/test_spend_guard.py
tools/triage/evidence_backup.py
tools/triage/test_evidence_backup.py
```

Guides and coordination:

```text
CLAUDE.md
loop.md
docs/15-day-evidence-checklist.md
docs/day-one-operator-card.md
docs/santa-agent-workboard.md
docs/OPN-VALIDATION.md
docs/HANDOFF-CONTINUE.md
docs/production-readiness.md
docs/release-checklist.md
docs/release-handoff.md
docs/agent-sync/README.md
docs/agent-sync/claude-to-codex.md
docs/agent-sync/codex-to-claude.md
tools/triage/README.md
tools/triage/log-schema.md
```

The new spend_guard.py is a required import for BOTH adapters. Publishing
only adapter edits breaks startup. Include evidence_backup.py with its tests
and suite registration. production_evidence.py is already tracked in HEAD;
preserve it. A private pricing policy is NOT a release artifact.

## Release conditions

September 8 reconciliation: Claude independently verified the three guard
fixes; Codex independently verified the two backup fixes. The explicit file
set above covers all 24 current modified/untracked paths. Claude's final
readiness wording corrections were independently reviewed and accepted.
No files were staged. Review completion is not publication authorization.

Owner explicitly confirmed all 24 listed paths after the count correction,
including commit and push to codex/santa-checkpoint-2026-09-04 and PR #1's
update. This authorizes code publication only, not merge or activation. Paid calls
remain disabled pending resolution of the API 429 cause AND separate spending
authorization. No customer sends or deployment actions are authorized.

1. Preserve the completed peer reviews: guard, backup, readiness wording,
   and release inventory. Re-review any later changes before publication.
2. Reinspect Git status and the exact final diff for unexpected files or
   changes since this inventory. Review examples for synthetic data only.
3. Run ops_check in the offline shell described in release-checklist.md:
   MPN_API_DAILY_CALL_CAP=0; OPENAI_API_KEY, MPN_API_COST_POLICY and MPN_MODEL
   unset in that shell only. Existing independently
   verified checkpoint: 702 passed, 6 skipped, 52 subtests, 22 suites, seven
   ops steps PASS. That result does not cover later unreviewed edits.
4. Obtain explicit owner authorization before committing/publishing.
5. Stage explicit approved paths, inspect staged diff, commit, and push
   only the agreed branch. If it is codex/santa-checkpoint-2026-09-04,
   authorization must include updating PR #1. Do not force-push or merge
   main implicitly.
6. Verify remote commit and files after an authorized push. Report code
   publication separately from deployment and actual business operation.

## Operator safety and rollback

Until a separate budget/test authorization, keep paid generation disabled.
Git publication must not ship a key, cost-policy file, quota database,
customer message, production log, bank detail, or real backup.

To fall back operationally, set MPN_API_DAILY_CALL_CAP=0 in the relevant
operator process and use the existing templates/manual inbox. Preserve
accounting records and evidence; deleting them is not rollback.
Before a code rollback, preserve unfinished edits and identify the intended
revision. Older revisions may omit the cost guard, so keep paid calls off.
Do not use destructive reset/checkout commands as an automatic remedy.

This release does not connect the T-Mobile number, activate Stripe, enable
24/7 hosting, create a customer record, or establish production Day 1.
