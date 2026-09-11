# Chat HTTP integration adapter

Opt-in extension of the existing inquiry server. Tested on loopback only;
not the configured production entrypoint and not deployed.

Construct existing `tools.web_inquiry.server.App`, shared
`tools.web_chat_guard.guard.AdmissionGuard`, and
`tools.web_chat.service.ChatService(guard)` (model disabled by default).
Then construct `ChatServer(("127.0.0.1", port), app, chat)` imported from
`tools.web_chat_http.adapter`, and serve it using the existing lifecycle.
Always close the server and App on shutdown. Repository root must be on
the Python module search path. Existing server.py remains untouched.

The new POST /api/chat accepts exactly message and consent=true JSON.
It reuses the configured Host and trusted-proxy checks, requires a single
same-origin Origin header, rejects transfer encoding and duplicate/invalid
length headers, and caps body length at 4096 bytes. Read timeout is ten
seconds; connection closes after each chat response. Error details stay
private. Existing inquiry/operator routes and page assets are inherited.

HTTP status mapping: 200 reply/human handoff; 400 invalid request; 403
origin/host rejection; 409 duplicate; 413 oversized body; 415 wrong media
type; 429 traffic quota; 503 accounting/service failure. Do not automatically
retry any chat request. Render response message as text, not HTML. The
inherited rate-limit response header is a generic wait hint, not a guarantee
that global daily capacity is restored after five minutes.

Website integration still belongs to Claude: add the chat UI, consent,
bounded conversation state, inquiry collection and receipt handling.
The inherited root page remains the original form, not a chat experience.
Any model enabling requires explicit owner approval and both existing cost
guards; no API settings are changed here. Public operation also needs
HTTPS proxy, host-level connection limits, persistence, deployment approval,
privacy controls and accurate automatic-chat telemetry. This standard-library
threaded server alone is not a DDoS protection layer. Never expose its
operator routes without the existing authentication.

Offline integration: `python -B -m pytest tools/web_chat_http/test_http.py -q`.
Tests use ephemeral localhost ports, synthetic records and no model calls.
