# Launch Preflight

Read-only CLI that tells the operator what is **actually missing** for the
operator-assisted bilingual inquiry launch. It never fixes anything, never
starts the service, and never certifies a launch.

## Run

```powershell
# Local demo readiness (loopback service):
python tools\launch_preflight\preflight.py --mode demo --data-dir "$env:LOCALAPPDATA\MiamiPapaNoel\web-inquiry-demo"

# Public-host prerequisites (checkable-from-here portion only):
python tools\launch_preflight\preflight.py --mode public `
    --data-dir "$env:LOCALAPPDATA\MiamiPapaNoel\web-inquiry-demo" `
    --origin https://THE-APPROVED-HOSTNAME
```

Add `--json` for machine-readable output. Exit codes: `0` no blocking
findings for the selected mode, `1` blocking finding(s), `2` usage error.

The direct loopback demo requires `MPN_TRUSTED_PROXY_IP` to be unset or
empty: a browser does not supply the trusted proxy's required header.
`MPN_PUBLIC_ORIGIN` should be unset for the server default, or a canonical
HTTP origin on `127.0.0.1`/`localhost` matching the chosen server port and
browser URL. A public-host environment is not a direct-demo configuration.
The checker validates configuration, not whether the server is listening.

## What it checks

- **Configuration**: `MPN_OPERATOR_TOKEN` (presence + documented policy,
  value never shown in any form), `OPENAI_API_KEY` (presence only — a
  present key is CONFIGURED, never VERIFIED, and does not end the reported
  HTTP 429), `MPN_MODEL`, the exact `--origin` (HTTPS, bare origin, no
  placeholder hostnames), `MPN_TRUSTED_PROXY_IP` (must be `127.0.0.1` for
  the documented single-host nginx topology), and the presence of the
  `deploy/inquiry` templates.
- **Locally verified**: Python runtime, data-directory safety (outside the
  repository, no link/junction indirection, never created by this tool),
  and a read-only queue-database validation through the maintenance tool's
  `check` API — no lease, no writes, no migration.
- **Owner/host verification still needed** (always reported, never
  inferrable from files existing): host TLS, reboot persistence, alert
  delivery, off-host restore drill, storage persistence, and one successful
  synthetic model-backed draft.
- **Separate unfinished features** (reported, never blockers): the Stripe
  public Payment Link (none exists yet) and phone/provider wiring
  (786-975-9557 is T-Mobile, manual voice/text only).

## What it will never do

No network. No model calls. No file or directory creation. No secrets in
output. No production evidence, launch dates, or qualification claims —
`--mode public` exiting `0` means the locally checkable prerequisites
pass, nothing more.

SQLite caveat: reading a WAL-journal queue may maintain its standard
`-wal`/`-shm` sidecars beside the database. No queue row is changed; this
is the same read-only limitation documented by the maintenance tool.

## Verify

```powershell
python -m pytest tools\launch_preflight\test_launch_preflight.py -q
```

Tests use synthetic temporary state, strip all `MPN_*`/`OPENAI_*` variables,
block the network at the socket level, and assert canary secrets never
appear in any output.
