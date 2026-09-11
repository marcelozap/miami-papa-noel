# Website Chat Admission

Server-side component only. Not connected to a public endpoint yet. Makes
no network requests, generates no replies, and grants no permission to spend.
Claude owns the website and endpoint integration; Codex owns this module.

## Integration contract

Import from `tools.web_chat_guard.guard` with the repository root on the Python
module path. Construct `AdmissionGuard(absolute_private_database_path,
stable_server_secret_bytes)` once at startup. Secret must be at least 32
bytes, generated securely and stored only server-side. All workers must use
the same private database and secret; differing secrets fail closed.

For each public request:

1. Enforce HTTPS, same-origin policy, validated transport/proxy identity,
   request timeout and body-length limits before reading or parsing input.
   Read at most `MAX_BODY_BYTES + 1` bytes; reject oversize requests.
2. Call `parse_request(raw_bytes)`. Accept exactly JSON `message` (nonblank,
   at most 1000 characters) and `consent: true`. Catch `InvalidRequest` and
   return a generic bilingual 400. Do not accept client history, roles,
   model names, price policy, budget overrides, or system instructions.
3. Call `guard.reserve(verified_client_ip, message)` once before processing.
   Never trust a browser-supplied address or arbitrary forwarding header.
4. Only `None` admits the request. `CHAT_DUPLICATE` means no repeat processing
   or paid retry. Rate/capacity refusals return a short static message with
   the business phone option; accounting errors must not fail open.
5. Use approved templates first. Any optional model path must STILL pass
   the existing call cap and estimated-cost guard. Paid generation stays
   disabled until explicitly enabled by the owner. No background retries.
6. Return only allowlisted visitor-visible fields, not the internal triage
   record, operator metadata, raw errors, secrets, or another visitor's reply.
   Render text safely, not as model-provided HTML. Keep consent and inquiry
   storage in the existing private operator queue, not this admission store.

Reservations persist before downstream work and are not refunded on errors.
Duplicate fingerprints are caller-specific; never return someone else's
cached conversation. If history is introduced, keep it bounded and owned by
the server behind an authenticated session, not submitted as trusted roles.

## Limits and privacy

Six admitted turns per caller per rolling 300 seconds; 200 globally per
rolling 86400 seconds. Equivalent normalized messages from the same caller
are suppressed for that day. SQLite immediate transactions serialize workers.
State contains timestamps and keyed hashes, no raw messages or IP addresses;
these hashes are still pseudonymous operational data, not anonymous data.
Old rows are purged on subsequent traffic; idle databases retain them until
next access. Storage contains at most 200 admitted rows under normal use.

These are application admission limits, NOT dollar guarantees or DDoS
protection. Shared networks share a caller limit; changing IP can evade the
per-caller limit but not the global one. Infrastructure traffic may still
cost money. Add host-level controls before launch. Do not delete the database
to clear limits. Secret rotation requires a planned guard-state migration;
it intentionally refuses an unexplained identity change. Protect the private
directory from other local writers. Accounting corruption, lock timeout, or
clock rollback refuses admission.

Test offline: `python -B -m pytest tools/web_chat_guard/test_guard.py -q`.
No synthetic result is production Day 1 evidence.
