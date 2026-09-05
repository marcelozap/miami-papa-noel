# Persistent Inquiry Host

Deployment handoff, **not an installed or publicly verified service**. This
keeps the existing static website where it is and puts the Mrs. Claus form
and private operator queue on one persistent Linux host. No container,
Claude session, Codex loop, or running desktop is required once that host is
installed and verified. Hosting and OpenAI API availability are separate.

## Before Installing

- Obtain the owner's hosting account, budget, hostname and deployment approval.
  Nothing in this kit authorizes a purchase, DNS change or public launch.
- Use a supported Linux distribution with systemd, nginx, Python 3.10+,
  private persistent storage and an OS administrator. One app process and
  one SQLite queue per host; no autoscaling or ephemeral serverless disk.
- Put the reviewed application release at `/opt/miami-papa-noel`, owned by
  root and read-only to the service user. Include the triage module, locked
  pricing and referenced image assets. Do not deploy private state or secrets.
- Create a non-login system user/group named `mpn-inquiry`. Reserve
  `/var/lib/miami-papa-noel` for that user, mode 0700, on persistent storage.
  Do not reuse an existing unrelated directory or migrate demo records into live.
- Keep the Python listener on loopback. Firewall the host so only approved
  administration and HTTPS/HTTP ports are reachable, never port 8226.
- Select an approved HTTPS hostname and provision its valid certificate.
  `inquiry.example.invalid` is a placeholder, not a proposed live endpoint.

## Configure and Verify Demo First

1. Copy `inquiry.env.example` to `/etc/miami-papa-noel/inquiry.env` as root,
   mode 0600, in a private directory. Set the exact external HTTPS origin
   and a newly generated random operator token of at least 32 ASCII characters.
   Keep API credentials empty for the initial test. Do not paste secrets into
   chat, command arguments, public files, Git, screenshots or shared logs.
2. Copy the `.service` and `.timer` files to `/etc/systemd/system/`. Review
   the paths and inspect any existing files before replacing them. The main
   service deliberately starts with `--offline` and separate `inquiry-demo`
   storage. The private environment file is read by systemd before it drops
   to the service user; do not make it world-readable for the application.
3. Review `nginx.conf.example`, replace every placeholder hostname/certificate
   path, and install it in nginx's `http` context. Resolve any existing
   virtual-host conflicts. This configuration assumes a **direct connection
   to nginx**, not a CDN/load balancer in front of it. It replaces
   `X-MPN-Client-IP` with the socket's remote IP. The app only accepts that
   identity from its configured `127.0.0.1` proxy. Never use incoming XFF
   values or disable the app's limits. Re-review a multi-proxy topology.
4. Validate on the actual host before starting anything:

   ```sh
   sudo systemd-analyze verify /etc/systemd/system/mpn-inquiry*.service /etc/systemd/system/mpn-inquiry*.timer
   sudo nginx -t
   ```

5. After approval and validation, load/start the configured units and proxy:

   ```sh
   sudo systemctl daemon-reload
   sudo systemctl enable --now mpn-inquiry.service
   sudo systemctl reload nginx
   sudo systemctl start mpn-inquiry-health.service
   sudo systemctl start mpn-inquiry-backup.service
   ```

6. Verify `/health` publicly and use the private operator page to submit,
   generate, review and reject **synthetic** EN/ES inquiries. Try invalid
   consent, stale approval, wrong token, logout during refresh and both rate
   limits. No customer message is sent by this queue. Restart the service
   and confirm the same requests survive and interrupted drafts are marked
   failed rather than sent. Verify HTTPS from a phone on a different network.
7. Complete the restore drill below, then enable the two timers:

   ```sh
   sudo systemctl enable --now mpn-inquiry-health.timer mpn-inquiry-backup.timer
   sudo systemctl list-timers mpn-inquiry-health.timer mpn-inquiry-backup.timer
   ```

These templates have Python/static-contract tests locally. Linux systemd,
nginx/TLS, firewall, reboot persistence and actual hosted browser checks
must pass on the selected host; local tests do not certify those steps.
See the workboard for dated verification and remaining platform test gaps.

## Health and Alerts

`/health` reports process liveness only. Authenticated `/api/readiness`
checks free disk headroom and a rolled-back 64 KiB SQLite allocation, then
returns queue counts and the count of
current draft errors, never messages, contacts, tokens or draft bodies.
Its scope is explicitly `local_storage_only`. It does not test OpenAI,
Stripe, phone routing, message delivery or backup freshness. The 16 MiB free
space floor is a minimum health guard, not capacity planning or a guarantee
that a later write succeeds. Disk-space trend alerts are still required.

`healthcheck.py` connects only to loopback, passes the private token in a
header and never follows redirects. Exit 0 means the local storage check
passed; 1 means unavailable/invalid; 2 means failed/blocked drafts or current
model errors need operator attention. The five-minute timer records these
results in the journal. It **does not send an alert** by itself.

Before public intake, configure and test an owner-approved alert destination
for failed health/backup units, low disk space and an off-host HTTPS check.
Monitor backup age too: a dead host cannot report its own failure. Keep
monitoring messages limited to status/counts. The operator must still check
the queue for new inquiries; this release sends no new-inquiry notifications.

The proxy suppresses normal access logs, limits request bodies/connections,
and keeps forwarding identities explicit. Critical nginx diagnostics can
still contain request metadata: restrict log permissions/retention. Host
agents, provider logs and other existing nginx hosts need their own privacy
review. Do not enable body, Authorization, or full inquiry request logging.

## Backup and Restore Drill

The backup job uses SQLite's online backup API, not a copy of the live file.
It validates integrity/schema and creates a unique private
`backups/backup-<random>/inquiries.sqlite3`. It checks that row counts, data
digests and schema match the source snapshot. It never replaces a prior
backup. A backup may briefly delay a writer when using rollback journaling.

Read the generated path from the private backup service journal. Run the
following as the service user, replacing the sample backup path with that
actual file and the restore target with a **new, never-used directory**:

```sh
sudo -u mpn-inquiry /usr/bin/python3 /opt/miami-papa-noel/tools/web_inquiry/maintenance.py restore-check --backup /var/lib/miami-papa-noel/backups/backup-ACTUAL/inquiries.sqlite3 --restore-dir /var/lib/miami-papa-noel/restore-drill-UNIQUE
```

The target's parent must already exist. Existing targets, repository paths,
symlinks/reparse paths and non-private destination directories are refused.
The check opens the restored database and compares actual data, without
starting the app, replaying events or touching the live queue. Output has
paths/counts/status only. Restored data is still private customer data, not
an artifact to commit. Use synthetic data for the prelaunch drill.

The CLI has a cooperative deadline (30 seconds by default, maximum 300);
the service has a 120-second supervisor limit for OS/storage stalls. A
forced kill can leave partial artifacts. Treat a failed run as unusable
until inspected and successfully rechecked; do not bulk-delete unknown files.

Backups here are unencrypted local files. Before launch, enable private disk
encryption, an approved encrypted off-host copy and a retention/storage budget.
No automated pruning or external upload is included. Alert on disk space and
backup age. Repeat the restore drill after upgrades and on an agreed schedule.
For an actual recovery, stop intake/service, preserve damaged state, verify
the restored copy, and deliberately point the service at it. Never overwrite
the active database while the server is running.

## Enable Real Operation Deliberately

First resolve API billing/limits, set the intended model and key privately,
and remove `--offline` in a reviewed systemd override **without adding
`--live`**. Restart and verify a synthetic model-backed draft succeeds and
shows the actual selected model. Test failure/fallback separately. A 429
or an offline draft is not a successful model call.

Only after owner authorization, consent review and hosted verification:

1. Stop the service. Change `MPN_INQUIRY_DIR` to a new private live directory
   such as `/var/lib/miami-papa-noel/inquiry-live`. Leave demo state intact.
2. In the reviewed override, clear the existing `ExecStart` before replacing
   it with `/usr/bin/python3 /opt/miami-papa-noel/tools/web_inquiry/server.py --live`.
   Reload systemd and restart. Check health, backups and restore against the
   new location; the backup job reads the same private data-path setting.
3. Only then change the public website's inquiry route to the verified HTTPS
   form. Existing phone/email remain fallback channels. Keep review/send
   manual and preserve real operator actions and customer outcomes privately.

The flags and timers do not create production use or start a qualification
clock. Stripe, automatic availability, voice/SMS, automatic sends, content
publishing and outreach are separate integrations, not enabled by this kit.

## Reference Behavior

The proxy header design follows nginx's
[proxy_set_header documentation](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header).
Process environment and restart controls follow the
[systemd execution](https://manpages.ubuntu.com/manpages/noble/man5/systemd.exec.5.html)
and [service documentation](https://manpages.ubuntu.com/manpages/noble/man5/systemd.service.5.html).
The maintenance tool uses Python's
[SQLite online backup API](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup).
