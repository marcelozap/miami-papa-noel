"""Template-first chat service for the website endpoint; no HTTP server here."""
import datetime as dt
import re

from tools.triage import triage
from tools.web_chat_guard.guard import parse_request


class ChatService:
    def __init__(self, admission, *, allow_model=False, builder=None):
        if type(allow_model) is not bool:
            raise ValueError("Explicit boolean model setting required")
        self.admission = admission
        self.allow_model = allow_model
        self.builder = builder or triage.build_record

    def respond(self, body, verified_ip):
        """Return a small public object, never an operator/evidence record.

        Caller supplies raw bounded JSON and a transport-verified address.
        No reply delivery, booking, inquiry save or evidence attestation occurs.
        """
        message = parse_request(body)
        language = triage.detect_language(message)
        refused = self.admission.reserve(verified_ip, message)
        if refused:
            return self._public(language, self._contact(language), "template", refused)
        if re.search(r"\b(refund\w*|cancel\w*|complain\w*|discount\w*|available|availability|"
                     r"confirm\w*|paid|payment|deposit\w*|reembols\w*|queja\w*|"
                     r"descuento\w*|disponib\w*|pago\w*|pague)\b", triage.fold(message)):
            return self._public(language, self._contact(language), "template", "human_required")
        pricing = triage.load_pricing()
        now = dt.datetime.now(dt.timezone.utc)
        extracted = triage.extract(message, now.year)
        missing = triage.missing_fields(extracted)
        risk = triage.schedule_risk(extracted, pricing)
        drafts = triage.draft_replies(extracted, missing, risk, pricing)
        # Recognizable service inquiries need no model. Unknown messages can
        # reach the model only via an explicit server setting AND its own caps.
        if not extracted.get("category") and self.allow_model:
            try:
                record = self.builder(message, "web_form", real=False,
                                      pricing=pricing, now=now)
                checks = triage.validators.run_all(
                    record, record["draft_en"], record["draft_es"], pricing,
                    policy_verified=False)
                if (not record.get("fallback_used", True)
                        and not record.get("error_code")
                        and isinstance(record.get("model"), str)
                        and record["model"] not in ("", triage.OFFLINE_MODEL)
                        and set(f.check for f in checks) == set(triage.VALIDATION_CHECKS)
                        and not triage.validators.blocking(checks)
                        and record.get("language") == language
                        and all(isinstance(record.get(k), str) and 0 < len(record[k]) <= 4000
                                for k in ("draft_en", "draft_es"))):
                    return self._public(language, record["draft_" + language], "ai", "reply")
            except Exception:
                # Never return provider exceptions or automatically retry.
                pass
        text = drafts[1 if language == "es" else 0]
        return self._public(language, text, "template", "reply")

    @staticmethod
    def _contact(language):
        if language == "es":
            return "Por favor llame a Santa al 786-975-9557 para continuar. Esta no es una reserva confirmada."
        return "Please call Santa at 786-975-9557 to continue. This is not a confirmed booking."

    @staticmethod
    def _public(language, text, source, status):
        return {"language": language, "message": text, "source": source,
                "status": status, "booking_confirmed": False}


def submit_inquiry(app, *, name, contact, message, request_key, consent):
    """Use the existing queue; never fabricate a name, contact or send record.

    Endpoint must authenticate its conversation and run intake throttling.
    App.submit owns validation, idempotency, private storage and receipt IDs.
    """
    receipt = app.submit({"name": name, "contact": contact, "message": message,
                          "request_key": request_key, "consent": consent})
    return {"request_id": receipt["request_id"], "status": "received",
            "booking_confirmed": False}
