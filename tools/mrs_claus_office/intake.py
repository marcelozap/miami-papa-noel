#!/usr/bin/env python3
"""Mrs. Claus Office - bilingual intake for website, text, and call inquiries.

Collects the booking facts (name, phone, date, time, city, address or
neighborhood, event type, guest details, notes) plus the four visit
requirements (chair, air conditioning, gift adult, parking), and produces a
bilingual reply DRAFT from the locked price list.

What this workflow NEVER does, by construction and by test:
- promise or confirm availability ("I will check the calendar" is the ceiling)
- confirm a booking or say a deposit cleared (operator-only, via tools/slots)
- verify payment, discuss refunds, or offer discounts
- claim any affiliation
- send anything (drafts only; the operator sends by hand)

Payment questions, discount requests, complaints, exceptions, unclear
inquiries, and final availability all ESCALATE to the human operator with a
reason code.

Deterministic by default: no model, no API key, no network. Intake records are
customer data and live OUTSIDE the repository:

    %MPN_INTAKE_DIR%  or  %LOCALAPPDATA%\\MiamiPapaNoel\\intake\\intake-log.jsonl

Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import unicodedata
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "triage"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "slots"))

import triage      # noqa: E402  (language detection, date parsing, pricing)
import validators  # noqa: E402  (the six draft gates)
import slots as slots_mod  # noqa: E402  (double-booking awareness)

CHANNELS = ("website", "text", "call")

FIELD_LABELS = {
    "name": ("your name", "su nombre"),
    "phone": ("a phone number", "un numero de telefono"),
    "date": ("the event date", "la fecha del evento"),
    "time": ("the start time", "la hora de inicio"),
    "city": ("the city", "la ciudad"),
    "address_or_neighborhood": ("the address or neighborhood",
                                "la direccion o el vecindario"),
    "event_type": ("the type of event", "el tipo de evento"),
    "guest_details": ("about how many guests and children",
                      "cuantos invitados y ninos aproximadamente"),
}

REQUIREMENT_LABELS = {
    "chair": ("a sturdy chair for Santa", "una silla firme para Santa"),
    "air_conditioning": ("air conditioning at the visit area",
                         "aire acondicionado en el area de la visita"),
    "gift_adult": ("a designated adult for gifts and photos",
                   "un adulto encargado de regalos y fotos"),
    "parking": ("parking within 100 feet", "estacionamiento a menos de 100 pies"),
}

# ------------------------------------------------------------- escalation ---

ESCALATION_TRIGGERS = {
    "payment_question": (
        "refund", "reembolso", "did you get my", "recibieron mi", "i paid",
        "ya pague", "zelle status", "deposit status", "estado del deposito",
        "receipt", "recibo", "pay in cash", "pagar en efectivo", "efectivo",
        "cash when", "venmo", "cash app", "paypal", "credit card", "tarjeta",
        "instead of zelle", "en vez de zelle", "payment plan", "en pagos",
    ),
    "discount_request": (
        "discount", "descuento", "cheaper", "mas barato", "price match",
        "deal", "coupon", "cupon", "% off",
    ),
    "complaint": (
        "complaint", "queja", "unhappy", "molesto", "molesta", "disappointed",
        "decepcionad", "terrible", "never again",
    ),
    "availability_final": (
        "are you available", "esta disponible", "estan disponibles",
        "confirm the date", "confirmar la fecha", "is the date free",
        "la fecha esta libre", "can you guarantee", "puede garantizar",
        "is dec", "is december", "still open", "sigue abierto", "esta libre",
        " open?", " libre?", "do you have the", "tienen el",
    ),
}


def fold(text: str) -> str:
    d = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(c for c in d if not unicodedata.combining(c))


def escalation_reasons(record: dict) -> list:
    text = fold(" ".join(str(record.get(k) or "") for k in
                         ("notes", "guest_details", "event_type")))
    reasons = []
    for reason, terms in ESCALATION_TRIGGERS.items():
        if any(fold(t) in text for t in terms):
            reasons.append(reason)
    if not record.get("event_type") and not record.get("date"):
        reasons.append("unclear_request")
    if record.get("exception"):
        reasons.append("operator_exception")
    return reasons


# ---------------------------------------------------------- double booking --

def date_booking_pressure(date_iso: str) -> str:
    """Internal flag only - never spoken to the customer.
    Returns 'no_catalog', 'open', or 'all_booked' for the requested date."""
    if not date_iso:
        return "no_catalog"
    try:
        catalog = slots_mod.load_catalog()
        state = slots_mod.load_state()
    except (OSError, ValueError, json.JSONDecodeError):
        return "no_catalog"
    day_slots = [sid for sid, s in catalog.items() if s.get("date") == date_iso]
    if not day_slots:
        return "no_catalog"
    open_left = [sid for sid in day_slots
                 if slots_mod.current_state(state, sid) != slots_mod.BOOKED]
    return "open" if open_left else "all_booked"


# ---------------------------------------------------------------- drafting --

def missing_fields(record: dict) -> list:
    missing = [k for k in FIELD_LABELS if not str(record.get(k) or "").strip()]
    missing += ["req_" + k for k, v in REQUIREMENT_LABELS.items()
                if str(record.get(k) or "unknown").lower() not in ("yes", "si", "no")]
    return missing


def _package_line(pricing: dict, category: str | None) -> tuple:
    pkg = pricing["packages"].get(category or "")
    if not pkg:
        return ("I will send exact pricing once I know the type of event.",
                "Le envio el precio exacto cuando sepa el tipo de evento.")
    return ("%s is $%d, %s." % (pkg["label_en"], pkg["base"], pkg["unit_en"]),
            "%s: $%d, %s." % (pkg["label_es"], pkg["base"], pkg["unit_es"]))


def build_drafts(record: dict, pricing: dict, missing: list) -> tuple:
    price_en, price_es = _package_line(pricing, record.get("event_type_key"))
    dep, pay = pricing["deposit"], pricing["payment"]

    ask_en_parts, ask_es_parts = [], []
    for field in missing:
        if field.startswith("req_"):
            en, es = REQUIREMENT_LABELS[field[4:]]
            ask_en_parts.append("can you confirm %s" % en)
            ask_es_parts.append("puede confirmar %s" % es)
        else:
            en, es = FIELD_LABELS[field]
            ask_en_parts.append(en)
            ask_es_parts.append(es)
    ask_en = (" Could you share: %s?" % "; ".join(ask_en_parts)) if ask_en_parts else ""
    ask_es = (" Nos puede compartir: %s?" % "; ".join(ask_es_parts)) if ask_es_parts else ""

    draft_en = (
        "Thank you for writing to Miami Papa Noel! " + price_en + " "
        + dep["text_en"] + " " + pay["text_en"]
        + " I will check the calendar and come back to you with what is "
        "possible - I cannot promise a date until our coordinator confirms it."
        + ask_en)
    draft_es = (
        "Gracias por escribir a Miami Papa Noel! " + price_es + " "
        + dep["text_es"] + " " + pay["text_es"]
        + " Reviso el calendario y le respondo con lo que es posible - no "
        "puedo prometer una fecha hasta que nuestra coordinadora la confirme."
        + ask_es)
    return draft_en, draft_es


# ------------------------------------------------------------------ record --

def build_record(args_dict: dict, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now()
    pricing = triage.load_pricing()

    notes = args_dict.get("notes") or ""
    lang = args_dict.get("lang") or "auto"
    if lang == "auto":
        lang = triage.detect_language(notes) if notes.strip() else "en"

    raw_date = args_dict.get("date") or ""
    date_iso = None
    if raw_date.strip():
        try:
            date_iso = dt.date.fromisoformat(raw_date.strip()).isoformat()
        except ValueError:
            date_iso = triage.extract_date(raw_date, now.year)

    category = triage.extract_category(args_dict.get("event_type") or "")
    # A family event AT A HOME is a Family Visit even when the word "party"
    # appears. The shared triage rules return None for that ambiguity (on a
    # raw customer message the tool must ask, never guess a price); here the
    # operator typed the event_type deliberately, so home/family wording
    # resolves it to the family rate.
    if category in ("event_visit", None):
        et = fold(args_dict.get("event_type") or "")
        if any(w in et for w in ("home", "house", "casa", "family", "familia",
                                 "birthday", "cumplean")):
            category = "family_visit"

    record = {
        "intake_id": "MC-%s-%s" % (now.strftime("%Y%m%d"),
                                   uuid.uuid4().hex[:6].upper()),
        "received_at": now.isoformat(timespec="seconds"),
        "channel": args_dict.get("channel") or "website",
        "language": lang,
        "name": args_dict.get("name") or "",
        "phone": args_dict.get("phone") or "",
        "email": args_dict.get("email") or "",
        "date": date_iso,
        "time": args_dict.get("time") or "",
        "city": args_dict.get("city") or "",
        "address_or_neighborhood": args_dict.get("address_or_neighborhood") or "",
        "event_type": args_dict.get("event_type") or "",
        "event_type_key": category,
        "guest_details": args_dict.get("guest_details") or "",
        "notes": notes,
        "chair": args_dict.get("chair") or "unknown",
        "air_conditioning": args_dict.get("air_conditioning") or "unknown",
        "gift_adult": args_dict.get("gift_adult") or "unknown",
        "parking": args_dict.get("parking") or "unknown",
        "exception": bool(args_dict.get("exception")),
    }

    record["missing_fields"] = missing_fields(record)
    record["escalations"] = escalation_reasons(record)
    record["booking_pressure"] = date_booking_pressure(date_iso or "")
    if record["booking_pressure"] == "all_booked":
        record["escalations"].append("date_fully_booked_review")

    draft_en, draft_es = build_drafts(record, pricing, record["missing_fields"])
    extracted = {"requested_date": record["date"],
                 "category": record["event_type_key"] or record["event_type"],
                 "location": record["city"] or record["address_or_neighborhood"]}
    findings = validators.run_all(extracted, draft_en, draft_es, pricing,
                                  policy_verified=False)
    record["validation"] = [f.as_dict() for f in findings]
    record["draft_en"] = draft_en
    record["draft_es"] = draft_es
    record["outcome"] = ("escalate_to_operator" if record["escalations"]
                         else "draft_ready_for_operator")
    record["price_list_version"] = pricing["price_list_version"]
    return record


def blocking(record: dict) -> list:
    return [f for f in record["validation"] if f["level"] == "FAIL"]


# ----------------------------------------------------------------- storage --

def intake_dir() -> Path:
    override = os.environ.get("MPN_INTAKE_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "intake"


def write_log(record: dict) -> Path:
    path = intake_dir() / "intake-log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


# --------------------------------------------------------------------- CLI --

def render(record: dict) -> str:
    lines = ["=" * 66,
             "MRS. CLAUS OFFICE  %s  %s  (%s)" % (
                 record["intake_id"], record["received_at"], record["channel"]),
             "=" * 66,
             "language : %s" % record["language"],
             "date     : %s" % (record["date"] or "-- not stated --"),
             "event    : %s" % (record["event_type"] or "-- unclear --"),
             "missing  : %s" % (", ".join(record["missing_fields"]) or "nothing"),
             "outcome  : %s" % record["outcome"]]
    if record["escalations"]:
        lines.append("ESCALATE : %s -> hand to the human operator"
                     % ", ".join(sorted(set(record["escalations"]))))
    lines += ["", "-- DRAFT (%s primary) ---" % record["language"].upper(),
              record["draft_es"] if record["language"] == "es" else record["draft_en"],
              "", "-- DRAFT (other language) ---",
              record["draft_en"] if record["language"] == "es" else record["draft_es"],
              "", "-- VALIDATION ---"]
    lines += ["  %-5s %-20s %s" % (f["level"], f["check"], f["detail"])
              for f in record["validation"]]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--channel", choices=CHANNELS, default="website")
    ap.add_argument("--lang", choices=("auto", "en", "es"), default="auto")
    for field in ("name", "phone", "email", "date", "time", "city",
                  "address-or-neighborhood", "event-type", "guest-details",
                  "notes"):
        ap.add_argument("--" + field, default="")
    for req in ("chair", "air-conditioning", "gift-adult", "parking"):
        ap.add_argument("--" + req, choices=("yes", "no", "si", "unknown"),
                        default="unknown")
    ap.add_argument("--exception", action="store_true",
                    help="operator marked this as an exception case")
    args = ap.parse_args(argv)

    record = build_record({k.replace("-", "_"): v
                           for k, v in vars(args).items()})
    print(render(record))
    if blocking(record):
        print("\nBLOCKED by validation - handle manually. Nothing was sent.")
        record["outcome"] = "blocked_by_validation"
        write_log(record)
        return 2
    path = write_log(record)
    print("\nlogged: %s" % path)
    print("Nothing was sent. The operator reviews the draft and sends it "
          "manually from 786-975-9557 or santa@miamipapanoel.com.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
