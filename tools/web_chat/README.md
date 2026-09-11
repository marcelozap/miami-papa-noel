# Website reply service

Integration component, not a deployed chatbot. Claude's website endpoint
must connect this service to the customer UI and the existing operator queue.
No HTTP routes, hosting or automatic evidence records are created here.

With repository root on sys.path, import `ChatService` and `submit_inquiry`
from `tools.web_chat.service`. Construct ChatService with the shared
AdmissionGuard from tools/web_chat_guard. Leave allow_model=False until
the owner approves enabling the public model path; browser input cannot
change it. Even when enabled, triage's existing cost and call caps apply.

Call respond(raw_json_bytes, verified_client_ip) after the endpoint's
origin, body-length and timeout checks. See the admission README for the
required request schema and proxy/identity rules. InvalidRequest means 400;
admission refusal status means no model call or retry. Public objects contain
only language, message, source (template or ai), status and booking_confirmed
(always false). Render message with textContent, never innerHTML. Keep the
AI disclosure and contact-consent wording in the customer UI.

Recognized service inquiries always use locked-price bilingual templates.
Unclassified messages may use the model only with explicit server opt-in;
failures/invalid output fall back without retry. Sensitive-topic keyword
matches route to the operator without a model call. This matcher is a
conservative first layer, not a complete semantic safety guarantee. Both
model drafts are independently checked using existing validators before a
visitor-visible reply is projected; internal records never leave this API.

For a lead handoff, the UI must collect an actual name, phone/email, message,
explicit contact consent and a stable request identifier. Pass those fields
to submit_inquiry(existing_app, ...). App.submit validates them and writes
the real private queue, idempotently. The endpoint must apply its existing
intake throttling and authenticated conversation ownership; this wrapper
does not bypass those controls or invent contact data. It never calls
App.draft, approve, sent, or a booking/payment operation.

Still required before public launch: HTTP/UI integration, safe bounded
conversation state, hosting, end-to-end browser checks, and truthful
model/template production telemetry. This single-turn service does not
persist chat history or certify a 15-day evidence start. Do not treat its
model test fixtures as customer use. No account settings, billing policy,
phone/SMS service, Stripe configuration or credentials were changed.

Offline tests: `python -B -m pytest tools/web_chat/test_service.py -q`.
