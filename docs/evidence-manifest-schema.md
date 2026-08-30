# External Evidence Index

The evidence index is stored outside the repository at:

```text
%LOCALAPPDATA%\MiamiPapaNoel\evidence\evidence-index.jsonl
```

(Override the folder with `MPN_EVIDENCE_DIR`.) It is a redacted index, not a
customer database. The corresponding files stay in the same external folder.
Scaffold the empty folders and index header with:

```powershell
python scripts\validate_opn_submission.py --init-evidence
```

After placing a redacted file in the external folder, index it with:

```powershell
python scripts\evidence_index.py --file receipts\redacted-receipt-01.pdf `
  --ref E-01 --type receipt --date 2025-12-24 `
  --notes "dated seasonal customer operation" --redacted
```

## Format

One JSON object per line (JSONL). Lines starting with `#` are comments.
Required keys for every entry:

| Key | Rule |
|---|---|
| `ref` | Unique local reference such as `E-01` |
| `type` | `receipt`, `booking_record`, `message_thread`, `screenshot`, `statement`, `calendar`, or `zelle_history` |
| `date` | Actual ISO date from the source artifact, never an estimate |
| `artifact` | Relative file path inside the evidence folder (no absolute paths, no `..`) |
| `sha256` | SHA-256 of the REDACTED file, 64 hex characters |
| `redacted` | Must be `true` - never index unredacted material |
| `notes` | Short, non-personal description of what it establishes |

Example line with deliberately fake metadata:

```json
{"ref": "E-01", "type": "receipt", "date": "2025-12-24", "artifact": "receipts/redacted-receipt-01.pdf", "sha256": "<64-hex-digest>", "redacted": true, "notes": "dated seasonal customer operation"}
```

## Enforcement

`python scripts\validate_opn_submission.py --preflight` (and `--final`) verifies
each entry: schema keys present, type in the allowed list, ISO date, unique
ref, 64-hex digest, path stays inside the evidence folder, and the referenced
file's hash matches the recorded one. A final packet requires at least one
`receipt` or `statement` entry.

Entries containing private-data fields (`name`, `phone`, `email`, `address`,
`memo`, ...) or values that look like phone numbers, email addresses, or
street addresses are rejected. Before indexing, remove customer names, phone
numbers, emails, street addresses, Zelle memos, account identifiers, and faces
of children. Leave event dates, service type, amount, and a non-sensitive
identifier legible - a receipt with a blurred date is not evidence.

Never commit the index or its artifacts. `.gitignore` excludes `*.jsonl`, and
the validator's git-privacy check fails if any log, key, or env file is ever
tracked.
