"""Tests for the inquiry triage tool.

All inquiries here are SYNTHETIC. Running this suite must never write to the
production log and must never count toward the 15-day production requirement.

    python -m pytest tools/triage/test_triage.py -q
"""
from __future__ import annotations

import datetime as dt
import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import triage  # noqa: E402
import validators  # noqa: E402

PRICING = triage.load_pricing()
NOW = dt.datetime(2026, 9, 1, 10, 0, 0)


@pytest.fixture(autouse=True)
def isolated_model_environment(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MPN_MODEL", raising=False)
    # Keep every log AND the shared paid-call quota inside the test sandbox -
    # a model-path test must never touch the operator's real directories.
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path / "test-logs"))
    monkeypatch.setenv("MPN_API_QUOTA_DIR", str(tmp_path / "test-quota"))
    monkeypatch.delenv("MPN_API_DAILY_CALL_CAP", raising=False)
    monkeypatch.delenv("MPN_API_MAX_OUTPUT_TOKENS", raising=False)

    def no_network(*args, **kwargs):
        pytest.fail("Tests must replace the API with a synthetic response")

    monkeypatch.setattr(triage.urllib.request, "urlopen", no_network)


def build(text, channel="instagram_dm"):
    return triage.build_record(text, channel, real=False, pricing=PRICING, now=NOW)


# ------------------------------------------------------------- extraction ---

def test_detects_spanish():
    rec = build("Hola, quisiera saber el precio para una fiesta en diciembre.")
    assert rec["language"] == "es"


def test_north_pole_identity_keeps_real_service_terms():
    rec = build("Family visit in Doral on December 10, 2026")
    assert "Mrs. Claus Office" in rec["draft_en"] and "North Pole" in rec["draft_en"]
    assert "Sra. Claus" in rec["draft_es"] and "Polo Norte" in rec["draft_es"]
    assert rec["prompt_version"] == "triage-v1.1.0"
    for draft in (rec["draft_en"], rec["draft_es"]):
        assert "$325" in draft and "Doral" in draft and "50%" in draft
    prompt = triage._model_instructions(PRICING)
    assert "Mrs. Claus" in prompt and "North Pole" in prompt
    assert "operator must review and send manually" in prompt


def test_detects_english():
    rec = build("Hi, how much for a Santa visit for our office party in December?")
    assert rec["language"] == "en"


def test_extracts_date_english_month_first():
    assert build("Do you have Dec 13 open?")["requested_date"] == "2026-12-13"


def test_extracts_date_spanish_day_first():
    assert build("Necesito Papa Noel el 20 de diciembre")["requested_date"] == "2026-12-20"


def test_extracts_iso_date():
    assert build("Our event is 2026-12-19")["requested_date"] == "2026-12-19"


def test_category_school_beats_generic_event():
    assert build("Our preschool wants a visit")["category"] == "school_daycare"


def test_category_christmas_eve():
    assert build("Anything for Christmas Eve?")["category"] == "christmas_eve"


def test_category_jingle():
    assert build("Do you have the Jingle entry visit on Dec 8?")["category"] == "jingle"


def test_category_photographer():
    assert build("We need a photographer mini-session block in Doral")["category"] == "photographer"


def test_category_hoa():
    assert build("Our HOA clubhouse event in Doral")["category"] == "hoa_community"


def test_extracts_location():
    assert build("party at my house in Kendall")["location"] == "Kendall"


def test_contact_status_phone():
    assert build("call me at 305-555-0142")["contact_status"] == "phone_only"


def test_missing_fields_reported():
    rec = build("how much for santa?")
    assert "date" in rec["missing_fields"]
    assert "location" in rec["missing_fields"]


# ----------------------------------------------------------- schedule risk --

def test_high_risk_date_flagged():
    rec = build("Can you do Dec 24?")
    assert rec["schedule_risk"] == "high"


def test_low_risk_offseason():
    rec = build("Anything on July 18 for a summer event in Doral?")
    assert rec["requested_date"] == "2026-07-18"
    assert rec["schedule_risk"] == "low"


def test_bare_month_is_not_treated_as_a_date():
    """A month with no day is not a date. Risk must stay unknown, never guessed."""
    rec = build("Anything in July for a summer event in Doral?")
    assert rec["requested_date"] is None
    assert rec["schedule_risk"] == "unknown"


def test_risk_unknown_without_date():
    assert build("how much for santa?")["schedule_risk"] == "unknown"


# ------------------------------------------------------------- safety gates --

def test_draft_never_confirms_booking():
    for text in ("Dec 13 HOA in Doral", "Hola, 20 de diciembre en Kendall", "christmas eve please"):
        rec = build(text)
        findings = [f for f in rec["validation"] if f["check"] == "unsafe_confirmation"]
        assert all(f["level"] == "PASS" for f in findings), rec["draft_en"]


def test_draft_never_mentions_insurance():
    rec = build("Our school needs a COI, do you have insurance?")
    findings = [f for f in rec["validation"] if f["check"] == "insurance_claim"]
    assert all(f["level"] == "PASS" for f in findings)
    assert "insur" not in rec["draft_en"].lower()


def test_draft_uses_only_official_payment_rails():
    rec = build("Can I pay with Venmo or Cash App for a Doral party Dec 13?")
    assert "Zelle" in rec["draft_en"]
    # Until the operator creates a real Stripe Payment Link, Zelle is the
    # only rail a draft may mention - never a promise of a link that does
    # not exist, and never a processor name.
    for banned in ("venmo", "cash app", "stripe", "paypal", "square",
                   "payment link", "enlace de pago"):
        assert banned not in rec["draft_en"].lower()
        assert banned not in rec["draft_es"].lower()


def test_all_validations_pass_on_normal_inquiry():
    rec = build("Hi, HOA clubhouse event in Doral on Dec 13, around 60 kids. 305-555-0142")
    assert not [f for f in rec["validation"] if f["level"] == "FAIL"], rec["validation"]


# --------------------------------------- validators reject bad drafts ------

def test_validator_rejects_unlocked_price():
    findings = validators.validate_pricing("The visit is $999.", "La visita es $999.", PRICING)
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_accepts_locked_price():
    findings = validators.validate_pricing("The visit is $325.", "La visita es $325.", PRICING)
    assert all(f.level == validators.PASS for f in findings)


def test_validator_catches_price_mismatch_between_languages():
    findings = validators.validate_bilingual_parity("It is $325.", "Son $450.")
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_catches_empty_second_language():
    findings = validators.validate_bilingual_parity("It is $325.", "   ")
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_matches_hyphenated_minutes_across_languages():
    findings = validators.validate_bilingual_parity(
        "Christmas Eve is $500 per 45-minute slot.",
        "Nochebuena: $500 por bloque de 45 minutos.",
    )
    assert all(f.level == validators.PASS for f in findings)


def test_validator_catches_confirmation_language_english():
    findings = validators.validate_no_unsafe_confirmation(
        "Your date is confirmed!", "Gracias.", PRICING)
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_catches_confirmation_language_spanish_with_accents():
    findings = validators.validate_no_unsafe_confirmation(
        "Thanks.", "Su depósito recibido, fecha reservada.", PRICING)
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_catches_spanish_gender_and_number_agreement():
    """confirmado / confirmada / confirmados must all be caught, not just one form."""
    for phrase in ("Su fecha está confirmada.", "Fecha confirmado.",
                   "Los dos eventos están confirmados.", "La fecha queda reservada.",
                   "Su lugar está asegurado."):
        findings = validators.validate_no_unsafe_confirmation("Thanks.", phrase, PRICING)
        assert any(f.level == validators.FAIL for f in findings), phrase


def test_deposit_wording_is_not_falsely_flagged():
    """'asegura la fecha' describes what a deposit does - it must not trip the gate."""
    es = PRICING["deposit"]["text_es"]
    findings = validators.validate_no_unsafe_confirmation("Thanks.", es, PRICING)
    assert all(f.level == validators.PASS for f in findings), es


def test_validator_catches_insurance_claim():
    findings = validators.validate_no_insurance_claim(
        "We are fully insured.", "Gracias.", PRICING, policy_verified=False)
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_allows_insurance_when_policy_verified():
    findings = validators.validate_no_insurance_claim(
        "We are fully insured.", "Estamos asegurados.", PRICING, policy_verified=True)
    assert all(f.level == validators.PASS for f in findings)


def test_validator_catches_non_zelle_payment():
    findings = validators.validate_payment_method("Pay by Venmo.", "Pague por Zelle.")
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_flags_missing_info_without_a_question():
    findings = validators.validate_missing_information({}, "Here is our pricing.")
    assert any(f.level == validators.FAIL for f in findings)


def test_validator_downgrades_missing_info_when_asked():
    findings = validators.validate_missing_information({}, "What date did you have in mind?")
    assert any(f.level == validators.WARN for f in findings)


# ------------------------------------------------------------------ record --

def test_record_has_every_log_schema_field():
    required = ["inquiry_id", "received_at", "channel", "language", "requested_date",
                "category", "missing_fields", "model", "prompt_version", "reviewer",
                "approved_at", "sent_at", "fallback_used", "outcome", "error_code"]
    rec = build("Dec 13 Doral HOA")
    for field in required:
        assert field in rec, field


def test_new_record_is_never_pre_approved():
    rec = build("Dec 13 Doral HOA")
    assert rec["reviewer"] is None
    assert rec["approved_at"] is None
    assert rec["sent_at"] is None
    assert rec["outcome"] == "pending_review"


def test_approval_waits_for_explicit_send_marker():
    rec = build("Dec 13 Doral HOA")
    triage.apply_approval(rec, "operator", NOW)
    assert rec["reviewer"] == "operator"
    assert rec["approved_at"] == "2026-09-01T10:00:00"
    assert rec["sent_at"] is None
    assert rec["outcome"] == "approved_awaiting_send"


def test_explicit_send_marker_records_completed_outcome():
    rec = build("Dec 13 Doral HOA")
    sent_at = NOW + dt.timedelta(minutes=3)
    triage.apply_approval(rec, "operator", NOW, sent_at)
    assert rec["sent_at"] == "2026-09-01T10:03:00"
    assert rec["outcome"] == "approved_and_sent"


def test_synthetic_record_is_marked_not_real():
    assert build("Dec 13 Doral HOA")["real_customer"] is False


def test_offline_mode_is_recorded_as_fallback(monkeypatch):
    monkeypatch.delenv("MPN_MODEL", raising=False)
    rec = build("Dec 13 Doral HOA")
    assert rec["fallback_used"] is True
    assert rec["model"] == triage.OFFLINE_MODEL


def test_log_line_excludes_draft_bodies(tmp_path, monkeypatch):
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path))
    rec = build("Dec 13 Doral HOA")
    path = triage.write_log(rec)
    line = json.loads(path.read_text(encoding="utf-8").strip())
    assert "draft_en" not in line
    assert "draft_es" not in line
    assert line["inquiry_id"] == rec["inquiry_id"]


def test_synthetic_and_production_logs_are_separate_files(tmp_path, monkeypatch):
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path))
    assert triage.log_path(real=True).name == "production-log.jsonl"
    assert triage.log_path(real=False).name == "synthetic-log.jsonl"
    assert triage.log_path(real=True) != triage.log_path(real=False)


# ------------------------------------------------------------ model path -----

def test_successful_openai_response_is_used_and_recorded(monkeypatch):
    model_result = {
        "language": "en",
        "requested_date": "2026-12-13",
        "category": "hoa_community",
        "location": "Doral clubhouse",
        "contact_status": "phone_only",
        "draft_en": (
            "Thank you for reaching out about Papa Noel. HOA / community event is "
            "$550, two hours, two-hour minimum. Travel is free within 25 miles of "
            "Doral, and $45 between 25 and 50 miles. A 50% non-refundable deposit "
            "locks the date. The balance is due on arrival. Payment is by Zelle only. "
            "I will check availability and come back to you with the exact time."
        ),
        "draft_es": (
            "Gracias por escribir sobre Papa Noel. Evento comunitario / HOA: $550, "
            "dos horas, minimo de dos horas. El viaje es gratis dentro de 25 millas "
            "de Doral, y $45 entre 25 y 50 millas. Un deposito no reembolsable del "
            "50% asegura la fecha. El saldo se paga al llegar. El pago es unicamente "
            "por Zelle. Reviso la disponibilidad y le confirmo la hora exacta."
        ),
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"output_text": json.dumps(model_result)}).encode("utf-8")

    def fake_urlopen(request, timeout):
        assert timeout == triage.MODEL_TIMEOUT_SECONDS
        assert "test-key" not in request.data.decode("utf-8")
        return FakeResponse()

    monkeypatch.setenv("MPN_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # Explicit opt-in: paid generation is disabled by default.
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "5")
    monkeypatch.setattr(triage.urllib.request, "urlopen", fake_urlopen)

    rec = build("Our HOA event is Dec 13 in Doral. Call me at 305-555-0142.")

    assert rec["model"] == "test-model"
    assert rec["fallback_used"] is False
    assert rec["error_code"] is None
    assert rec["category"] == "hoa_community"
    assert rec["location"] == "Doral"
    assert rec["draft_en"] == model_result["draft_en"]


def test_model_failure_falls_back_to_rules(monkeypatch, capsys):
    def fake_urlopen(*args, **kwargs):
        raise failure

    monkeypatch.setenv("MPN_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # This regression loops through 23 simulated failures - raise the local
    # spending cap so it exercises diagnostics, not the budget refusal.
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "100")
    monkeypatch.setattr(triage.urllib.request, "urlopen", fake_urlopen)

    private = "DO-NOT-PRINT-test-key-or-customer-305-555-0142"

    class ErrorBody(io.BytesIO):
        def read(self, size=-1):
            assert size == 4096
            return super().read(size)

    class UnreadableBody(ErrorBody):
        def read(self, size=-1):
            assert size == 4096
            raise OSError(private)

    cases = [(urllib.error.URLError("offline"), "MODEL_UNAVAILABLE", None, None)]
    for status, code in [
        (401, "invalid_api_key"), (429, "insufficient_quota"),
        (429, "rate_limit_exceeded"), (404, "model_not_found"),
        (429, "credit_balance_exhausted"),
        (429, "organization_spend_limit_exceeded"),
        (429, "project_spend_limit_exceeded"),
        (429, "organization_usage_limit_exceeded"), (429, "slow_down"),
        (403, "insufficient_permissions"), (400, "invalid_json_schema"),
        (400, "unsupported_parameter"), (400, "invalid_value"),
        (401, private), (403, [private]), (500, None),
    ]:
        body = json.dumps({"error": {"code": code, "message": private}}).encode()
        error = urllib.error.HTTPError(private, status, private, {"X-Private": private}, ErrorBody(body))
        category = code if isinstance(code, str) and code != private else "unclassified"
        cases.append((error, "MODEL_HTTP_ERROR", status, category))

    for body in [
        ErrorBody(b"not json"), ErrorBody(b"[]"), ErrorBody(b'{"error": []}'),
        ErrorBody(b'"' + b"x" * 5000 + b'"'), ErrorBody(b"\xff"),
        UnreadableBody(),
    ]:
        error = urllib.error.HTTPError(private, 429, private, {}, body)
        cases.append((error, "MODEL_HTTP_ERROR", 429, "unclassified"))

    for failure, error_code, status, category in cases:
        rec = build("Our HOA event is Dec 13 in Doral. Call me at 305-555-0142.")
        assert rec["model"] == triage.OFFLINE_MODEL
        assert rec["fallback_used"] is True
        assert rec["error_code"] == error_code
        assert rec["approved_at"] is None
        assert rec["sent_at"] is None
        captured = capsys.readouterr()
        assert captured.out == ""
        assert private not in captured.err
        assert "test-key" not in captured.err
        assert "305-555-0142" not in captured.err
        if status is None:
            assert captured.err == ""
        else:
            assert "HTTP %s; category=%s." % (status, category) in captured.err
            expected_hint = {
                "credit_balance_exhausted": "API prepaid credit is exhausted",
                "organization_spend_limit_exceeded": "organization spending limit",
                "project_spend_limit_exceeded": "project spending limit",
                "organization_usage_limit_exceeded": "OpenAI-assigned organization usage limit",
                "slow_down": "honor Retry-After",
            }.get(category)
            if expected_hint:
                assert expected_hint in captured.err
            if status == 429 and category == "unclassified":
                assert "does not distinguish" in captured.err


# ------------------------------------------- category ambiguity (pricing) ---

def test_family_party_is_ambiguous_and_asks_instead_of_quoting():
    # "fiesta familiar" matches event_visit ($450) AND family_visit ($325).
    # Guessing either price is a customer-facing error - the category must
    # come back unclear and the draft must ask, not quote.
    rec = build("Hola, quisiera una fiesta familiar en casa el 20 de diciembre en Doral.")
    assert rec["category"] is None
    assert "service category" in rec["missing_fields"]
    assert "$450" not in rec["draft_en"] and "$325" not in rec["draft_en"]
    assert "$450" not in rec["draft_es"] and "$325" not in rec["draft_es"]


def test_family_only_words_still_price_family_visit():
    rec = build("Santa visit at our home for my daughter's birthday, Dec 20, Doral.")
    assert rec["category"] == "family_visit"


def test_event_only_words_still_price_event_visit():
    rec = build("We want Santa at our restaurant event on Dec 13 in Doral.")
    assert rec["category"] == "event_visit"


# --------------------------- model output must obey the same protections ---

def _fake_model(monkeypatch, model_result):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"output_text": json.dumps(model_result)}).encode("utf-8")

    monkeypatch.setenv("MPN_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # Explicit opt-in: paid generation is disabled by default.
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "5")
    monkeypatch.setattr(triage.urllib.request, "urlopen",
                        lambda request, timeout: FakeResponse())


def test_model_may_not_resolve_ambiguous_family_party(monkeypatch):
    # Codex probe 2026-09-05: the model prices the ambiguous "fiesta familiar"
    # as a $450 event. The deterministic ambiguity rule must override it and
    # fall back to a draft that asks instead of quoting.
    _fake_model(monkeypatch, {
        "language": "es", "requested_date": "2026-12-20",
        "category": "event_visit", "location": "Doral",
        "contact_status": "phone_only",
        "draft_en": "Event visit is $450. Deposits are by Zelle.",
        "draft_es": "Evento: $450. Los depositos son por Zelle.",
    })
    rec = build("Hola, quisiera una fiesta familiar en casa el 20 de diciembre en Doral. 305-555-0142")
    assert rec["fallback_used"] is True
    assert rec["error_code"] == "MODEL_CATEGORY_AMBIGUOUS"
    assert rec["category"] is None
    assert "$450" not in rec["draft_en"] and "$450" not in rec["draft_es"]


def test_model_draft_promising_unconfigured_payment_link_is_rejected(monkeypatch):
    # Codex probe 2026-09-05: a model draft promising "our secure online
    # payment link" while pricing.json has no Stripe URL must FAIL the
    # payment gate and fall back to the deterministic Zelle-only draft.
    _fake_model(monkeypatch, {
        "language": "en", "requested_date": "2026-12-13",
        "category": "hoa_community", "location": "Doral",
        "contact_status": "phone_only",
        "draft_en": ("HOA / community event is $550, two hours, two-hour minimum. "
                     "Deposits are by Zelle or our secure online payment link."),
        "draft_es": ("Evento comunitario / HOA: $550, dos horas, minimo de dos horas. "
                     "Los depositos son por Zelle o por nuestro enlace de pago seguro."),
    })
    rec = build("Our HOA event is Dec 13 in Doral. Call me at 305-555-0142.")
    assert rec["fallback_used"] is True
    assert rec["error_code"] == "MODEL_OUTPUT_VALIDATION_FAIL"
    assert "payment link" not in rec["draft_en"].lower()
    assert "enlace de pago" not in rec["draft_es"].lower()


def test_payment_gate_flags_link_only_when_unconfigured():
    en = "Deposits are by Zelle or our secure online payment link."
    es = "Los depositos son por Zelle o por nuestro enlace de pago seguro."
    unconfigured = validators.validate_payment_method(en, es, PRICING)
    assert any(f.level == validators.FAIL for f in unconfigured)
    # Synthetic URL for the test only - the real link is pasted by the
    # operator into pricing.json from the Stripe dashboard.
    configured = dict(PRICING, payment=dict(PRICING["payment"],
                                            stripe_payment_link="https://buy.stripe.com/test_SYNTHETIC"))
    findings = validators.validate_payment_method(en, es, configured)
    assert all(f.level == validators.PASS for f in findings)


# --------------------------------------------------- synthetic model check ---

@pytest.fixture
def model_check(monkeypatch, tmp_path):
    baseline = build(triage.MODEL_CHECK_INQUIRY, channel="web_form")
    state = {
        "result": {key: baseline[key] for key in (
            "language", "requested_date", "category", "location",
            "contact_status", "draft_en", "draft_es")},
        "calls": [], "failure": None,
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({
                "model": "gpt-5.6-luna", "status": "completed",
                "output": [{"type": "message", "content": [
                    {"type": "output_text", "text": json.dumps(state["result"])}]}],
            }).encode("utf-8")

    def fake_urlopen(request, timeout):
        payload = json.loads(request.data)
        state["calls"].append(payload)
        assert request.full_url == "https://api.openai.com/v1/responses"
        assert request.method == "POST"
        assert timeout == triage.MODEL_TIMEOUT_SECONDS
        assert payload["model"] == "gpt-5.6-luna"
        assert payload["store"] is False
        assert payload["text"]["format"]["strict"] is True
        assert payload["text"]["format"]["schema"] == triage.MODEL_SCHEMA
        assert payload["input"][1]["content"][0]["text"] == triage.MODEL_CHECK_INQUIRY
        assert "PRIVATE-KEY-CANARY" not in request.data.decode("utf-8")
        if state["failure"]:
            raise state["failure"]
        return FakeResponse()

    def no_side_effect(*args, **kwargs):
        pytest.fail("Model checks must not log, prompt, approve or send")

    original_build = triage.build_record

    def synthetic_only(*args, **kwargs):
        assert kwargs["real"] is False
        return original_build(*args, **kwargs)

    monkeypatch.setenv("OPENAI_API_KEY", "PRIVATE-KEY-CANARY")
    monkeypatch.setenv("MPN_MODEL", "gpt-5.6-luna")
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path / "must-not-exist"))
    # Paid generation is off by default; the model check is an owner-approved
    # paid action, so the fixture opts in with a small explicit allowance.
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "5")
    monkeypatch.setattr(triage.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(triage, "build_record", synthetic_only)
    monkeypatch.setattr(triage, "write_log", no_side_effect)
    monkeypatch.setattr(triage, "apply_approval", no_side_effect)
    monkeypatch.setattr("builtins.input", no_side_effect)
    yield state
    leftovers = sorted(p.relative_to(tmp_path).as_posix()
                       for p in tmp_path.rglob("*") if p.is_file()
                       and not p.relative_to(tmp_path).as_posix().startswith("test-quota/"))
    # Quota slot files (sandboxed under test-quota/) and the usage ledger are
    # the ONLY permitted writes: every API attempt is metered against the
    # shared spending cap, --check-model included. No inquiry log, approval,
    # or send may ever appear here.
    assert leftovers in ([], ["must-not-exist/api-usage.jsonl"]), leftovers


def test_check_model_uses_real_adapter_schema_and_gates_without_logging(model_check, capsys):
    assert triage.main(["--check-model"]) == 0
    assert len(model_check["calls"]) == 1
    output = capsys.readouterr()
    assert "MODEL CHECK PASSED" in output.out
    assert "gpt-5.6-luna" in output.out
    assert "DRAFT (EN)" in output.out and "DRAFT (ES)" in output.out
    assert "not customer use or Day 1 evidence" in output.out
    assert "PRIVATE-KEY-CANARY" not in output.out + output.err


@pytest.mark.parametrize("missing", ["OPENAI_API_KEY", "MPN_MODEL"])
@pytest.mark.parametrize("value", [None, "", "  "])
def test_check_model_requires_both_settings_before_network(model_check, monkeypatch, capsys,
                                                          missing, value):
    if value is None:
        monkeypatch.delenv(missing)
    else:
        monkeypatch.setenv(missing, value)
    assert triage.main(["--check-model"]) == 1
    assert model_check["calls"] == []
    assert "NOT VERIFIED" in capsys.readouterr().out


@pytest.mark.parametrize("flags", [
    ["--real"], ["--demo"], ["--status"],
    ["--message", "synthetic"], ["--file", "missing.txt"],
])
def test_check_model_rejects_conflicting_modes_before_network(model_check, flags):
    with pytest.raises(SystemExit) as result:
        triage.main(["--check-model", *flags])
    assert result.value.code == 2
    assert model_check["calls"] == []


def test_check_model_http_failure_is_not_false_success(model_check, capsys):
    body = json.dumps({"error": {"code": "credit_balance_exhausted",
                                  "message": "PRIVATE-KEY-CANARY"}}).encode()
    model_check["failure"] = urllib.error.HTTPError(
        "https://api.openai.com/v1/responses", 429, "PRIVATE-KEY-CANARY", {}, io.BytesIO(body))
    assert triage.main(["--check-model", "--no-prompt"]) == 1
    assert len(model_check["calls"]) == 1
    output = capsys.readouterr()
    assert "NOT VERIFIED" in output.out
    assert "MODEL CHECK PASSED" not in output.out
    assert "credit_balance_exhausted" in output.err
    assert "PRIVATE-KEY-CANARY" not in output.out + output.err


@pytest.mark.parametrize("field,value", [
    ("draft_es", ""), ("draft_en", "Your booking is confirmed."),
    ("language", "en"), ("requested_date", "2026-12-11"),
    ("category", "school_daycare"),
])
def test_check_model_rejects_bad_drafts_or_wrong_synthetic_facts(model_check, capsys, field, value):
    model_check["result"][field] = value
    assert triage.main(["--check-model"]) == 1
    assert len(model_check["calls"]) == 1
    assert "MODEL CHECK PASSED" not in capsys.readouterr().out


def test_check_model_does_not_pass_when_a_gate_disappears(model_check, monkeypatch, capsys):
    original_run = triage.validators.run_all
    monkeypatch.setattr(triage.validators, "run_all",
                        lambda *args, **kwargs: original_run(*args, **kwargs)[:-1])
    assert triage.main(["--check-model"]) == 1
    assert len(model_check["calls"]) == 1
    assert "MODEL CHECK PASSED" not in capsys.readouterr().out


# ------------------------------------------------------- production evidence ---

def operated_record(**overrides):
    record = build(triage.MODEL_CHECK_INQUIRY)
    record.update(
        received_at="2026-09-01T09:00:00-04:00", approved_at="2026-09-01T09:02:00-04:00",
        sent_at="2026-09-01T09:03:00-04:00", real_customer=True, model="gpt-test-model",
        fallback_used=False, error_code=None, reviewer="Synthetic operator",
        outcome="approved_and_sent",
    )
    record.update(overrides)
    return record


def write_status_fixture(tmp_path, monkeypatch, records):
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path))
    path = tmp_path / "production-log.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in records), encoding="utf-8")
    return path


@pytest.mark.parametrize("override", [
    {"fallback_used": True}, {"fallback_used": "false"}, {"fallback_used": None},
    {"model": "offline-rules-v1"}, {"model": "manual"}, {"model": " "},
    {"model": None}, {"model": ["test-model"]},
    {"reviewer": ""}, {"reviewer": False},
    {"outcome": "pending_review"}, {"outcome": "approved_awaiting_send"},
    {"error_code": "MODEL_HTTP_ERROR"}, {"approved_at": None}, {"sent_at": None},
    {"approved_at": "2026-08-31T10:00:00-04:00"},
    {"sent_at": "2026-09-01T09:01:00-04:00"}, {"sent_at": "2026-09-01"},
    {"sent_at": "2026-10-01T09:03:00-04:00"}, {"sent_at": "invalid-private-canary"},
    {"sent_at": "9999-12-31T23:59:59-23:59"}, {"sent_at": "0001-01-01T00:00:00+23:59"},
    {"validation": []}, {"validation": None}, {"validation": ["bad gate"]},
])
def test_status_never_counts_incomplete_or_fallback_evidence(tmp_path, monkeypatch, capsys, override):
    write_status_fixture(tmp_path, monkeypatch, [operated_record(**override)])
    now = dt.datetime(2026, 9, 20, tzinfo=dt.timezone.utc)
    assert triage.cmd_status(PRICING, now) == 0
    output = capsys.readouterr().out
    assert "NOT STARTED" in output
    assert "first AI send" not in output and "invalid-private-canary" not in output


@pytest.mark.parametrize("level", ["FAIL", "UNKNOWN"])
def test_status_rejects_failed_or_unknown_gate_levels(tmp_path, monkeypatch, capsys, level):
    record = operated_record()
    record["validation"][0]["level"] = level
    write_status_fixture(tmp_path, monkeypatch, [record])
    assert triage.cmd_status(PRICING, dt.datetime(2026, 9, 20, tzinfo=dt.timezone.utc)) == 0
    assert "NOT STARTED" in capsys.readouterr().out


def test_status_counts_recorded_model_sends_not_earlier_fallback_or_pending(tmp_path, monkeypatch, capsys):
    fallback = operated_record(inquiry_id="fallback", received_at="2026-08-01T09:00:00-04:00",
                               fallback_used=True, model=triage.OFFLINE_MODEL)
    pending = operated_record(inquiry_id="pending", received_at="2026-08-02T09:00:00-04:00",
                              outcome="pending_review", approved_at=None, sent_at=None)
    real = operated_record(inquiry_id="model")
    path = write_status_fixture(tmp_path, monkeypatch, [fallback, pending, real])
    before, modified = path.read_bytes(), path.stat().st_mtime_ns
    assert triage.cmd_status(PRICING, dt.datetime(2026, 9, 5, tzinfo=dt.timezone.utc)) == 0
    output = capsys.readouterr().out
    assert "3 total, 1 recorded model-backed reviewed/sent" in output
    assert "first AI send  : 2026-09-01T13:03:00+00:00" in output
    assert "review after   : 2026-09-16T13:03:00+00:00" in output
    assert "IN PROGRESS" in output and "QUALIFIED" not in output
    assert path.read_bytes() == before and path.stat().st_mtime_ns == modified
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("seconds,status", [(-1, "IN PROGRESS"), (0, "ELAPSED WINDOW REACHED")])
def test_status_waits_fifteen_full_days_without_certifying_opn(tmp_path, monkeypatch, capsys,
                                                            seconds, status):
    write_status_fixture(tmp_path, monkeypatch, [operated_record()])
    now = dt.datetime(2026, 9, 16, 13, 3, tzinfo=dt.timezone.utc) + dt.timedelta(seconds=seconds)
    assert triage.cmd_status(PRICING, now) == 0
    output = capsys.readouterr().out
    assert status in output and "QUALIFIED" not in output
    assert "does not certify continuous operation or acceptance" in output


@pytest.mark.parametrize("contents", [
    'not JSON PRIVATE-CANARY', '[]', 'null', '"PRIVATE-CANARY"',
    '{"real_customer": false}', '{"real_customer": true}',
])
def test_status_fails_closed_on_contaminated_or_malformed_log(tmp_path, monkeypatch, capsys, contents):
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path))
    (tmp_path / "production-log.jsonl").write_text(contents, encoding="utf-8")
    assert triage.cmd_status(PRICING) == 1
    output = capsys.readouterr().out
    assert "NOT VERIFIED" in output and "PRIVATE-CANARY" not in output
    assert "first AI send" not in output


def test_status_duplicate_ids_cannot_certify_a_clock(tmp_path, monkeypatch, capsys):
    record = operated_record()
    write_status_fixture(tmp_path, monkeypatch, [record, record])
    assert triage.cmd_status(PRICING) == 1
    assert "NOT VERIFIED" in capsys.readouterr().out


def test_status_missing_log_is_read_only(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path / "absent"))
    assert triage.cmd_status(PRICING) == 0
    assert "NOT STARTED" in capsys.readouterr().out
    assert not list(tmp_path.iterdir())

# ------------------------------------------- api budget (spending controls v2) ---

BUDGET_RESULT = {
    "language": "en", "requested_date": "2026-12-13",
    "category": "hoa_community", "location": "Doral clubhouse",
    "contact_status": "phone_only",
    "draft_en": (
        "Thank you for reaching out about Papa Noel. HOA / community event is "
        "$550, two hours, two-hour minimum. A 50% non-refundable deposit "
        "locks the date. Payment is by Zelle only."
    ),
    "draft_es": (
        "Gracias por escribir sobre Papa Noel. Evento comunitario / HOA: $550, "
        "dos horas, minimo de dos horas. Un deposito no reembolsable del 50% "
        "asegura la fecha. El pago es unicamente por Zelle."
    ),
}


def _budget_fake_model(monkeypatch, cap=None):
    """Configured model env plus a counting fake transport."""
    calls = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"output_text": json.dumps(BUDGET_RESULT),
                               "usage": {"input_tokens": 12, "output_tokens": 99}}).encode()

    def fake_urlopen(request, timeout):
        calls.append(json.loads(request.data.decode("utf-8")))
        return FakeResponse()

    monkeypatch.setenv("MPN_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    if cap is not None:
        monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", str(cap))
    monkeypatch.setattr(triage.urllib.request, "urlopen", fake_urlopen)
    return calls


def _slot_files():
    return sorted(triage.api_quota_dir().glob("*-slot-*.json"))


def test_default_is_zero_spend_even_with_a_key(monkeypatch):
    calls = _budget_fake_model(monkeypatch)  # cap deliberately NOT set
    rec = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert rec["fallback_used"] is True
    assert rec["error_code"] == "PAID_CALLS_DISABLED"
    assert calls == [] and _slot_files() == []


@pytest.mark.parametrize("raw", ["0", "banana", "-3"])
def test_zero_or_unreadable_cap_disables_paid_calls(monkeypatch, raw):
    calls = _budget_fake_model(monkeypatch, cap=raw)
    rec = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert rec["error_code"] == "PAID_CALLS_DISABLED"
    assert calls == []


def test_cap_reached_falls_back_and_sends_nothing_more(monkeypatch):
    calls = _budget_fake_model(monkeypatch, cap=2)
    first = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    second = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    third = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert first["fallback_used"] is False and second["fallback_used"] is False
    assert third["fallback_used"] is True
    assert third["error_code"] == "BUDGET_CAP_REACHED"
    assert len(calls) == 2 and len(_slot_files()) == 2


def test_restart_persistence_slots_survive(monkeypatch):
    calls = _budget_fake_model(monkeypatch, cap=1)
    build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    # A process restart keeps nothing in memory; only the slot files remain.
    rec = build("Second try after restart. Dec 13 Doral. 305-555-0142")
    assert rec["error_code"] == "BUDGET_CAP_REACHED"
    assert len(calls) == 1 and len(_slot_files()) == 1


def test_concurrent_reservations_never_exceed_cap(monkeypatch, tmp_path):
    import concurrent.futures
    monkeypatch.setenv("MPN_API_QUOTA_DIR", str(tmp_path / "race-quota"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(lambda _: triage.reserve_paid_call(3, "triage"),
                                 range(24)))
    granted = [slot for ok, slot in outcomes if ok]
    assert len(granted) == 3 and len(set(granted)) == 3
    assert all(why == "BUDGET_CAP_REACHED" for ok, why in outcomes if not ok)


def test_mixed_adapters_share_one_allowance(monkeypatch):
    # The content adapter mirrors the same slot-file scheme; pre-claimed
    # slots from EITHER adapter reduce this one's allowance.
    calls = _budget_fake_model(monkeypatch, cap=2)
    ok, _ = triage.reserve_paid_call(2, "content")  # simulates the other stack
    assert ok
    first = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    second = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert first["fallback_used"] is False
    assert second["error_code"] == "BUDGET_CAP_REACHED"
    assert len(calls) == 1


def test_accounting_failure_refuses_spending(monkeypatch, tmp_path):
    blocked = tmp_path / "quota-as-file"
    blocked.write_text("not a directory", encoding="utf-8")
    monkeypatch.setenv("MPN_API_QUOTA_DIR", str(blocked))
    calls = _budget_fake_model(monkeypatch, cap=5)
    rec = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert rec["error_code"] == "BUDGET_ACCOUNTING_UNAVAILABLE"
    assert rec["fallback_used"] is True and calls == []


def test_failed_slot_write_refuses_spending(monkeypatch):
    calls = _budget_fake_model(monkeypatch, cap=5)
    def denied(*args, **kwargs):
        raise PermissionError("synthetic denial")
    monkeypatch.setattr(triage.os, "open", denied)
    rec = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert rec["error_code"] == "BUDGET_ACCOUNTING_UNAVAILABLE"
    assert calls == []


def test_timeout_consumes_the_slot_and_never_retries(monkeypatch):
    monkeypatch.setenv("MPN_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "1")
    attempts = []

    def timing_out(request, timeout):
        attempts.append(1)
        raise TimeoutError("synthetic timeout")

    monkeypatch.setattr(triage.urllib.request, "urlopen", timing_out)
    first = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    second = build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert first["error_code"] == "MODEL_UNAVAILABLE"
    assert second["error_code"] == "BUDGET_CAP_REACHED"
    assert len(attempts) == 1  # a possibly-billed timeout is never retried


def test_oversized_input_is_never_sent(monkeypatch):
    calls = _budget_fake_model(monkeypatch, cap=5)
    rec = build("Dec 13 Doral 305-555-0142 " + "x" * (triage.API_MAX_INPUT_CHARS + 1))
    assert rec["error_code"] == "MODEL_INPUT_TOO_LARGE"
    assert calls == [] and _slot_files() == []


def test_max_output_tokens_bound_is_sent(monkeypatch):
    calls = _budget_fake_model(monkeypatch, cap=5)
    build("Our HOA event is Dec 13 in Doral. 305-555-0142")
    assert calls[0]["max_output_tokens"] == triage.API_MAX_OUTPUT_TOKENS_DEFAULT
    monkeypatch.setenv("MPN_API_MAX_OUTPUT_TOKENS", "500")
    build("Second HOA event Dec 14 in Doral. 305-555-0142")
    assert calls[1]["max_output_tokens"] == 500


def test_quota_and_ledger_contain_no_secret_and_no_inquiry_text(monkeypatch):
    _budget_fake_model(monkeypatch, cap=5)
    build("Our HOA event is Dec 13 in Doral. Call 305-555-0142")
    stored = "".join(p.read_text(encoding="utf-8") for p in _slot_files())
    stored += triage.api_ledger_path().read_text(encoding="utf-8")
    assert "test-key" not in stored
    assert "Doral" not in stored and "305-555-0142" not in stored
