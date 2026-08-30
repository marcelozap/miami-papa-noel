# OpenAI Partner Network Validation

This repository contains a local validator for the written Partner Network
requirements. It does not submit anything to OpenAI and cannot predict or
guarantee a review decision.

## Before evidence arrives

Run from the repository root:

```powershell
python scripts\validate_opn_submission.py --preflight
```

Preflight must pass the package structure, tests, Git privacy check, public
surface safety scan, locked pricing check, and slot validator. It reports the
production log and evidence index as warnings while they do not
exist yet; public-surface defects fail preflight too, because a live page
defect is not pending evidence.

## Final packet

Run this only after the evidence is real and the submission fields are filled:

```powershell
python scripts\validate_opn_submission.py --final
```

Final mode fails closed unless all of these are true:

- `docs/OPN-SUBMISSION.md` and the deployment record have no unresolved
  `[TO FILL]` fields.
- The external production JSONL contains valid, privacy-minimal real records.
- At least one real inquiry was processed by a non-fallback model, approved by
  the operator, and sent manually.
- The earliest real record is at least 15 calendar days old.
- The external evidence index contains redacted artifacts with matching
  SHA-256 hashes, including a receipt or counterparty statement.
- Public customer surfaces remain Zelle-only, policy-safe, and aligned with
  `tools/triage/pricing.json`.

The safety scan also checks ready-to-send subjects and blockquoted message
lines in `business/wave1-batch-01.md`, including its phone scripts.

The validator reads production data only from outside Git:

```text
%LOCALAPPDATA%\MiamiPapaNoel\triage\production-log.jsonl
%LOCALAPPDATA%\MiamiPapaNoel\evidence\evidence-index.jsonl
```

Use `MPN_LOG_DIR` or `MPN_EVIDENCE_DIR` when those folders must be elsewhere.
The validator never creates, edits, uploads, or redacts evidence.

After placing a redacted artifact in the external folder, index it without
hand-editing JSONL:

```powershell
python scripts\evidence_index.py --file receipts\redacted-receipt-01.pdf `
  --ref E-01 --type receipt --date 2025-12-24 `
  --notes "dated seasonal customer operation" --redacted
```

The command refuses missing files, duplicate references, path escapes, future
dates, and contact data in notes. Run preflight afterward.

To create a shareable draft packet from the allowlisted repository files:

```powershell
python scripts\build_opn_packet.py --preflight
```

The ZIP is written outside the repository and contains no customer evidence.
Use `--final` only after the final validator passes; it refuses to create a
final packet around any blocker.

After copying or emailing a packet, verify the ZIP and its manifest with:

```powershell
python scripts\build_opn_packet.py --verify `
  "$env:LOCALAPPDATA\MiamiPapaNoel\packets\opn-submission-packet.zip"
```

Verification checks every manifest hash and rejects extra archive members.

## Evidence index

The index is JSONL metadata only: one object per line. Each artifact must be
redacted before it is placed in the external evidence folder. Paths are
relative to that folder and the validator hashes the referenced file without
importing its contents.

Required artifact fields:

| Field | Rule |
|---|---|
| `ref` | Unique local reference such as `E-01` |
| `type` | `receipt`, `booking_record`, `message_thread`, `screenshot`, `statement`, `calendar`, or `zelle_history` |
| `date` | Actual ISO date, never an estimate |
| `redacted` | Must be `true` |
| `sha256` | SHA-256 of the external file |
| `artifact` | Relative file path inside the evidence folder |
| `notes` | Short, non-personal description of what it proves |

Example line with deliberately fake metadata:

```json
{"ref": "E-01",
 "type": "receipt",
 "date": "YYYY-MM-DD",
 "artifact": "receipts/redacted-receipt-01.pdf",
 "sha256": "64-hex-character-digest-goes-here",
 "redacted": true,
 "notes": "dated seasonal customer operation"}
```

Do not commit the index or its artifacts. Keep customer names, phone
numbers, emails, addresses, faces, Zelle memos, and account identifiers out of
both the index and the repository.

## Claim-integrity checks

Both modes also verify the repository's own claims:

- no model name in `docs/OPN-SUBMISSION.md` or the deployment record that
  never appears in the production log
- no launch or first-inquiry date that contradicts the earliest log record
- test-count claims in the docs match what the suites actually pass
- no tracked `.env`, `.pem`, `.key`, or `.jsonl` file in Git (the redacted
  example is the one exception)

Scaffold the empty external evidence folders and index header (no data is
ever created) with:

```powershell
python scripts\validate_opn_submission.py --init-evidence
```

## Result interpretation

`PREFLIGHT PASS - evidence still required` means the software and safety
controls are ready for real evidence collection. It is not a Partner Network
qualification.

`PASS` in final mode means the local packet satisfies the encoded checklist.
OpenAI still makes the partnership decision.
