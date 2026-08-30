"""Tests for the inquiry triage tool.

All inquiries here are SYNTHETIC. Running this suite must never write to the
production log and must never count toward the 15-day production requirement.

    python -m pytest tools/triage/test_triage.py -q
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import triage  # noqa: E402
import validators  # noqa: E402

PRICING = triage.load_pricing()
NOW = dt.datetime(2026, 9, 1, 10, 0, 0)


def build(text, channel="instagram_dm"):
    return triage.build_record(text, channel, real=False, pricing=PRICING, now=NOW)


# ------------------------------------------------------------- extraction ---

def test_detects_spanish():
    rec = build("Hola, quisiera saber el precio para una fiesta en diciembre.")
    assert rec["language"] == "es"


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


def test_draft_is_zelle_only():
    rec = build("Can I pay with Venmo or Cash App for a Doral party Dec 13?")
    assert "Zelle" in rec["draft_en"]
    for banned in ("venmo", "cash app", "stripe", "paypal", "square"):
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
    monkeypatch.setattr(triage.urllib.request, "urlopen", fake_urlopen)

    rec = build("Our HOA event is Dec 13 in Doral. Call me at 305-555-0142.")

    assert rec["model"] == "test-model"
    assert rec["fallback_used"] is False
    assert rec["error_code"] is None
    assert rec["category"] == "hoa_community"
    assert rec["location"] == "Doral"
    assert rec["draft_en"] == model_result["draft_en"]


def test_model_failure_falls_back_to_rules(monkeypatch):
    def fake_urlopen(*args, **kwargs):
        raise urllib.error.URLError("offline")

    monkeypatch.setenv("MPN_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(triage.urllib.request, "urlopen", fake_urlopen)

    rec = build("Our HOA event is Dec 13 in Doral. Call me at 305-555-0142.")

    assert rec["model"] == triage.OFFLINE_MODEL
    assert rec["fallback_used"] is True
    assert rec["error_code"] == "MODEL_UNAVAILABLE"
