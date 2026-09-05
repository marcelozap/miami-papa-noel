# Santa Production Launch

Operate one existing workflow first: bilingual inquiry triage for Miami Papa
Noel, reviewed and sent by Marcelo. The software runs locally on demand when an
inquiry arrives. It does not need a publicly exposed operator board.

Status checked 2026-09-04: repository relocated to `C:\XIV\santa`; the default
triage production log reports NOT STARTED. This document does not start it.

## Start

1. In the operator's terminal, configure `OPENAI_API_KEY` privately and set
   `MPN_MODEL` to an exact model available to that API project. Do not paste a
   key into chat or commit it. Configuration in another terminal is not proof
   it is available to the terminal used for customer work.
2. Run `python scripts/ops_check.py` from `C:\XIV\santa`.
3. Run `python tools/triage/triage.py --demo` in that configured terminal.
   This synthetic check may call the paid API. Check for actual model use and
   passing gates; an offline fallback is not an AI connection test.
4. Put one genuine incoming inquiry in a private local text file outside Git.
   Use the business's existing email, website inbox, or messages as its source.
5. Run the following with the file and channel that actually apply:

```powershell
Set-Location -LiteralPath 'C:\XIV\santa'
$inquiryFile = Join-Path $env:LOCALAPPDATA 'MiamiPapaNoel\intake\inquiry.txt'
python tools\triage\triage.py --file $inquiryFile --channel email --reviewer 'Marcelo Zapata' --real
```

The file must contain a real inquiry and exist before this command runs. Other
supported channels are `instagram_dm`, `whatsapp`, `phone`, `web_form`, and
`referral`. Do not run a canned example with `--real`.

6. Review the draft, price, language, and missing details. Type `APPROVE` only
   when approved. Send the reply through the actual customer channel yourself,
   then type `SENT`. Rejected or unsent drafts remain recorded as such.
7. Inspect the private record: actual model ID, `fallback_used: false`, named
   reviewer, approval/send times, and `approved_and_sent` outcome. Record the
   launch from the first evidenced operational AI use, not a demo or failed call.

Default records live at `%LOCALAPPDATA%\MiamiPapaNoel\triage`, outside Git.
Do not move live customer state into `business/reservations/data/` to launch
this workflow. The operator board's current state storage needs its own review.

## Operate for 15 days

- Use this workflow for actual incoming business work during the operating
  window. Keep the operator available to handle inquiries and review drafts.
- Retain actual model/version, approval, send, error, and fallback records.
  Keep dated, redacted evidence of the customer-facing outcome separately.
- On days without inquiries, record that fact in a private operations note.
  Do not create an inquiry to fill the gap. A health check is operational
  evidence, not an additional customer served.
- Check status with `python tools/triage/triage.py --status`. Its QUALIFIED
  label measures elapsed dates only; it does not prove continuing AI use or
  predict the OPN decision. The code can start its date counter on a fallback
  row, so verify the actual first model-backed use separately.
- Record downtime honestly and retain a second private backup of evidence.
  Track inquiries handled, approvals/sends, edits, and failures. Attribute
  bookings or time savings only when records support them.

If actual operation starts September 4, 2026, the 15-day review target is
September 19 at or after the same start time. Shift the target with the actual
start. Maintain evidence that the workflow continues operating across the
window. A newly configured page left idle is not sufficient evidence of use.

## Prepare resubmission

Update the existing form answers with operational owner, launch/status,
specific model actually used, live functionality, measured outcome, and how
release review, monitoring, and failures are handled. Use the private evidence
index and owner statement already planned for this project.

Run `python scripts/validate_opn_submission.py --final`, resolve findings, and
review the packet before submitting it. This is an internal check; OPN makes
the acceptance decision. Keep the 2025 attested season separate from this
2026 evidence window.
