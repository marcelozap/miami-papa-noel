# 15-Day Evidence Checklist

The production clock starts when the tool processes the **first real customer
inquiry** and not one moment earlier. Synthetic runs, demos, and tests never
count. **Never backdate.**

---

## Before day 1

- [ ] Tests pass: `python -m pytest tools\triage\test_triage.py -q`
- [ ] Demo runs clean: `python tools\triage\triage.py --demo`
- [ ] Log directory confirmed: `python tools\triage\triage.py --status`
- [ ] Decide the model path and record it once it runs:
  - deterministic (`offline-rules-v1`), or
  - AI mode with `MPN_MODEL` set to an exact model id
- [ ] `MPN_REVIEWER` set, or `--reviewer` passed each run
- [ ] Confirm `.gitignore` excludes `*.jsonl`, `.env`, `*.pem`, `*.key`
- [ ] Read the manual fallback in `tools/triage/README.md` — you will need it at some point

## Day 1

- [ ] First **real** inquiry processed with `--real`
- [ ] Record the exact `received_at` here → `[TO FILL]`
- [ ] Qualification date = that date + 15 days → `[TO FILL]`
- [ ] Confirm the line landed in `production-log.jsonl`, not the synthetic log

## Every day, days 1-15

- [ ] Every real inquiry goes through the tool with `--real`
- [ ] Approve or reject each draft explicitly — no silent skips
- [ ] Fill `sent_at` by hand after sending
- [ ] Any inquiry handled manually gets a line with `fallback_used: true`, `model: "manual"`, and an `error_code`
- [ ] `--status` checked; day count advancing

**A gap day is not fatal.** Handle it honestly: log the manual rows with the
reason. An unbroken log with recorded fallbacks is more credible than a
suspiciously perfect one.

## Weekly

- [ ] Log backed up outside the repository (it is not in Git by design)
- [ ] Skim for anything that should not be there — no names, phones, addresses, message bodies
- [ ] Review validation blocks: is a gate firing too often, or wrongly?
- [ ] Review rejections: is the drafting getting worse or better?

## On qualification day

- [ ] `--status` reports **QUALIFIED**
- [ ] Compute and record:
  - [ ] Inquiries handled (total, and by language)
  - [ ] Days in production
  - [ ] Median first-response time (`sent_at − received_at`)
  - [ ] Share of drafts approved without edit
  - [ ] Rejection rate
  - [ ] Validation blocks, by gate
  - [ ] Fallback rate
  - [ ] Bookings created from handled inquiries
  - [ ] Double-bookings that occurred (target: zero)
- [ ] Produce a **redacted** export of the log for the submission
- [ ] Verify the export carries no customer-identifying data
- [ ] Update `docs/production-deployment-record.md`: launch date, model, outcomes
- [ ] Update `docs/OPN-SUBMISSION.md`: replace every `[TO FILL]`
- [ ] Update `docs/gap-report.md`: mark requirement 11 met
- [ ] Update `docs/evidence-index.md`: flip the three `[TO FILL]` rows to VERIFIED

## Redacted export

```powershell
$logDir = if ($env:MPN_LOG_DIR) { $env:MPN_LOG_DIR } else { Join-Path $env:LOCALAPPDATA 'MiamiPapaNoel\triage' }
$src = Join-Path $logDir 'production-log.jsonl'
$outDir = Join-Path $env:LOCALAPPDATA 'MiamiPapaNoel\packets'
$out = Join-Path $outDir 'production-log-redacted.jsonl'
New-Item -ItemType Directory -Force $outDir | Out-Null
$rows = Get-Content -LiteralPath $src | Where-Object { $_.Trim() } | ForEach-Object {
    $row = $_ | ConvertFrom-Json
    $row.PSObject.Properties.Remove('location')
    $row | ConvertTo-Json -Compress -Depth 10
}
$rows | Set-Content -LiteralPath $out -Encoding utf8
Write-Output ("wrote {0} rows to {1}" -f @($rows).Count, $out)
```

The log already excludes message bodies, draft bodies, names, phone numbers,
emails, and street addresses. This step drops the coarse area field as well.
The output stays outside the repository. **Read it before sending it anywhere.**

## What must never happen

- Passing `--real` on a test inquiry
- Editing `received_at`, `approved_at`, or `model` by hand
- Backdating the launch date
- Counting synthetic or demo rows
- Committing the production log
- Writing a model name into a document before that model has run

One fabricated row costs more than fifteen honest days.
