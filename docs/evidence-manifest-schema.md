# External Evidence Index

The evidence index is stored outside the repository at:

```text
%LOCALAPPDATA%\MiamiPapaNoel\evidence\evidence-index.jsonl
```

It is a redacted JSONL index, not a customer database. The corresponding files
stay in the same external folder. Use relative paths and record the SHA-256
hash of each file so the index proves which artifact was reviewed without
copying the artifact into Git.

The accepted per-line schema is described in `docs/OPN-VALIDATION.md` and
enforced by:

```powershell
python scripts\validate_opn_submission.py --preflight
```

Required fields for each artifact are `ref`, `type`, `date`, `artifact`,
`sha256`, `redacted`, and `notes`. Dates and amounts mentioned in notes must
come from the source artifact; never estimate them. The validator checks that
each referenced file exists, is inside the external evidence folder, is marked
redacted, and matches its recorded hash.

Before indexing, remove customer names, phone numbers, emails, street
addresses, Zelle memos, account identifiers, and faces of children. Leave event
dates, service type, amount, and a non-sensitive identifier legible.
