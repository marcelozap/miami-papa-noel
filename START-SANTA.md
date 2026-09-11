# Your Santa Project

Project folder: C:\XIV\santa
GitHub: https://github.com/marcelozap/miami-papa-noel

The files are yours to keep and edit without a Claude or Codex subscription.
The runtime uses Python and your hosting, not either coding chat session.
OpenAI API billing is separate and optional; it remains disabled here.

## Open the offline workshop

In PowerShell:

```powershell
cd C:\XIV\santa
python -B tools\offline_workshop.py
```

Open http://127.0.0.1:8240 . Python 3.10+ is required; no package installation
is needed for this launcher. If the port is occupied, add `--port 8241` and
use the printed URL. The terminal prints a temporary operator token for
/operator. Use only synthetic practice inquiries. Ctrl+C stops the server
and clears this workshop session. It does not touch real booking/evidence
files. With the computer or launcher off, this local workshop is unavailable.

This is a practice copy of the chat, NOT a publicly available production
assistant. The outstanding restart-limit and session-ownership defects
still block deploying the existing server to real customers.

## Use with your standalone website editor

Open this project folder, not the rally-coach project. The file
santa-editor-project.json is a plain project description for your app to
read or adapt; it is NOT an implemented connection to an unknown editor.

- Main website: index.html, book.html, other root HTML pages and assets/.
- Chat interface: tools/web_inquiry/index.html, app.css, app.js.
- Operator queue/backend: tools/web_inquiry/server.py.
- Price/term source: tools/triage/pricing.json. Change through reviewed policy,
  not by independently rewriting prices in page copy.
- Release status: docs/chat-release-status.md.
- Coordination: docs/santa-agent-workboard.md and docs/agent-sync/.

Keep secrets, logs, databases and actual customer information outside the
project and the editor's sync/upload directory. Do not let a visual editor
change cost guards, payment verification or evidence logic automatically.

## What works and what does not

The existing public site was verified at https://www.miamipapanoel.com .
Your dad can continue answering 786-975-9557 himself. Those calls are not
connected to this AI software. Local bilingual template chat and lead intake
work. The new public chat is not deployed; new Chat links still have a
placeholder URL and must not be published as ready.

Before launch: fix the two open Claude review findings, choose approved
hosting with durable state (the current SQLite backend is not deployable
unchanged as a Vercel function), verify the endpoint, replace placeholder
links, then publish after review. Do not spend on hosting or AI merely to
meet an application date. No production Day 1 has been established here.

## Resume later

A verified local snapshot was created at
C:\XIV\backups\santa-handoff-20260909-132040 . Its RESTORE.md explains recovery.
It includes current source and Git history, but excludes private operational
data and ignored files. It is on the same disk; it is not an off-device backup.

Give the next developer or coding tool this folder and START-SANTA.md.
Read current Git status and both mailboxes before changing files. Preserve
unfinished work. Run `python -B scripts/ops_check.py` with paid API settings
disabled. Pytest is required for tests, not for running the workshop.
Git pushes can trigger Vercel deployments: local edits are not publication.
Do not reset private budget/evidence state or claim synthetic tests as use.

No ongoing coding-agent scheduler is promised by this handoff. Existing
external accounts, hosting and billing remain the owner's responsibility.
