#!/usr/bin/env python3
"""Miami Papa Noel - calls/texts provider adapter layer (Phase 3 skeleton).

What this tool does: it is the ONLY place the operator records that a call or
text came in on the public number. The default adapter is a dry-run
NullAdapter: `simulate-inbound-sms` and `simulate-inbound-call` append one
line each to an append-only event log, after REDACTING the free-text summary
(phone numbers, email addresses, and street addresses are stripped before
anything touches disk). Callers are identified only by an opaque lead
reference like L-014 - never by a phone number.

What this tool does NOT do, by design:

- It never sends, posts, publishes, calls, or submits anything anywhere.
  There is no network code in this file. Every outbound artifact anywhere in
  this system is a DRAFT that a human sends manually.
- It never records a call. The `recording` field of every event is the
  literal string "NOT RECORDED". Recording metadata could only ever be
  something else if consent == "obtained" AND a live, tested provider were
  configured - and in this version no live provider is ever configured, so
  the field is ALWAYS "NOT RECORDED" and the tool refuses any attempt to
  request otherwise.
- It never stores a customer phone number, email, or address. The summary is
  redacted before it is written; the from-ref is validated to make sure it
  is not secretly a phone number.
- The TwilioAdapter here is a SKELETON. Without TWILIO_ACCOUNT_SID,
  TWILIO_AUTH_TOKEN, and MPN_COMMS_LIVE=1 in the environment, every method
  raises ProviderNotConfigured. Even with all three set, every method raises
  NotImplementedError: live wiring requires a tested provider connection,
  which this version does not have. It never invents credentials and never
  makes a network call.

Event log (append-only JSONL, OUTSIDE the repository):

    %MPN_COMMS_DIR%  or  %LOCALAPPDATA%\\MiamiPapaNoel\\comms\\
        events.jsonl    one line per event:
                        ts, kind (sms_in|call_in), from_ref,
                        redacted_summary, duration_seconds (calls only),
                        consent, recording ("NOT RECORDED")

    python tools/comms/adapter.py status
    python tools/comms/adapter.py simulate-inbound-sms --from-ref L-014 --summary "asked about Dec 13"
    python tools/comms/adapter.py simulate-inbound-call --from-ref L-014 --summary "asked about pricing" --duration-seconds 120 --consent none

Redaction note: the phone pattern extends the contact-detection regex used in
tools/triage/triage.py (\\b\\d{3}[-. ]?\\d{3}[-. ]?\\d{4}\\b) with optional
"+1" and parentheses. Redaction is deliberately greedy - over-redacting a
harmless phrase is accepted; under-redacting a customer's contact data is not.

Standard library only. Python 3.10. Synthetic data only in tests and examples.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

PUBLIC_PHONE = "786-975-9557"          # answered by a human, always
ZELLE_DESTINATION = "305-244-0360"     # Zelle ONLY - no other method exists
OFFICIAL_EMAIL = "santa@miamipapanoel.com"

NOT_RECORDED = "NOT RECORDED"
NOT_TRANSCRIBED = "NOT TRANSCRIBED"

KIND_SMS_IN = "sms_in"
KIND_CALL_IN = "call_in"

CONSENT_VALUES = ("none", "obtained")

# ------------------------------------------------------------------ storage --

def state_dir() -> Path:
    """Runtime state lives OUTSIDE the repository. Never committed."""
    override = os.environ.get("MPN_COMMS_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "comms"


def events_path() -> Path:
    return state_dir() / "events.jsonl"


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------- redaction --

# Phone: any run of 7-15 digits with arbitrary separator noise between them
# (spaces, dots, dashes, parens, and unicode spaces like NBSP   that
# web/WhatsApp copy-paste produces). Deliberately greedy: over-redaction is
# accepted, under-redaction is not.
PHONE_RE = re.compile(
    r"(?:\+?\d[\s.\-()   ]*){6,14}\d")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Street address: house number + optional directional + up to three name
# words + street-type suffix ("8901 NW 33rd Ave", "742 Evergreen Terrace"),
# plus Spanish number-first ordering ("1234 Calle Ocho", "avenida ..."),
# plus directional blocks with apt/unit tails ("8901 NW 33rd apt 4").
ADDRESS_RE = re.compile(
    r"\d{1,6}\s+"
    r"(?:"
    r"(?:[A-Za-z0-9']+\s+){0,3}?"
    r"(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|"
    r"Court|Ct|Place|Pl|Terrace|Ter|Trail|Trl|Way|Circle|Cir|Highway|Hwy)"
    r"\.?(?=[\s,.;:]|$)"
    r"|(?:Calle|Avenida|Carrera)\s+\w+"
    r"|(?:NW|NE|SW|SE)\s+\w+(?:\s+(?:apt|unit|#)\s*\w+)?"
    r")",
    re.IGNORECASE)

# An opaque lead reference: starts with a letter, short, no way to be a
# phone number by construction.
REF_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}")


def redact(text: str) -> str:
    """Strip emails, street addresses, and phone numbers, in that order.

    Addresses go before phones so a house number is consumed as part of the
    address token, never left behind as loose digits.
    """
    out = EMAIL_RE.sub("[REDACTED-EMAIL]", text or "")
    out = ADDRESS_RE.sub("[REDACTED-ADDRESS]", out)
    out = PHONE_RE.sub("[REDACTED-PHONE]", out)
    return out


# --------------------------------------------------------------- exceptions --

class CommsError(Exception):
    """Refusal: the operation violates a comms rule. Nothing was written."""


class ProviderNotConfigured(CommsError):
    """No live provider is configured. In this version, there never is one."""


class RecordingRefused(CommsError):
    """Recording metadata may only ever be NOT RECORDED in this version."""


# --------------------------------------------------------------- validation --

def validate_from_ref(ref: str) -> str:
    """A from-ref is an opaque reference like L-014, NEVER a phone number."""
    ref = (ref or "").strip()
    if not re.fullmatch(REF_RE, ref):
        raise CommsError(
            "from-ref %r refused: use an opaque lead reference like L-014 "
            "(letter first, letters/digits/dash only) - never a phone number "
            "or free text" % ref)
    if PHONE_RE.search(ref):
        raise CommsError("from-ref %r refused: it looks like a phone number" % ref)
    return ref


def validate_consent(consent: str) -> str:
    consent = (consent or "").strip().lower()
    if consent not in CONSENT_VALUES:
        raise CommsError("consent must be one of %s, got %r"
                         % ("/".join(CONSENT_VALUES), consent))
    return consent


def recording_metadata(consent: str, recording_requested: bool,
                       live_provider_configured: bool = False) -> str:
    """The ONLY producer of the `recording` field.

    Recording metadata may only ever be something other than NOT RECORDED if
    consent == "obtained" AND a live, tested provider is configured. In this
    version a live provider is never configured, so the answer is always
    NOT RECORDED - and an explicit request to record is refused loudly rather
    than silently downgraded.
    """
    if recording_requested:
        if consent != "obtained":
            raise RecordingRefused(
                "recording refused: consent is %r, not 'obtained'. No call is "
                "ever recorded without consent." % consent)
        if not live_provider_configured:
            raise RecordingRefused(
                "recording refused: consent alone is not enough - a live, "
                "tested provider connection is required, and this version "
                "never has one. The recording field stays %r." % NOT_RECORDED)
    return NOT_RECORDED


# ------------------------------------------------------------------- events --

def transcript_metadata(consent: str, transcript_requested: bool) -> str:
    """The ONLY producer of the `transcript` field. Mirrors the recording
    invariant: a transcript could only ever exist with obtained consent AND a
    live, tested provider - this version never has one, so the field is
    ALWAYS NOT TRANSCRIBED and an explicit request is refused loudly."""
    if transcript_requested:
        if consent != "obtained":
            raise RecordingRefused(
                "transcript refused: consent is %r, not 'obtained'. No call "
                "audio is processed without consent." % consent)
        raise RecordingRefused(
            "transcript refused: consent alone is not enough - transcription "
            "requires a live, tested provider connection, which this version "
            "never has. The transcript field stays %r." % NOT_TRANSCRIBED)
    return NOT_TRANSCRIBED


def append_event(event: dict) -> Path:
    """Append one event line. Enforces the recording invariant at the door:
    nothing with recording != NOT RECORDED ever reaches disk."""
    if event.get("recording") != NOT_RECORDED:
        raise RecordingRefused(
            "event refused: recording metadata may only ever be %r in this "
            "version, got %r" % (NOT_RECORDED, event.get("recording")))
    if event.get("kind") == "call_in" and             event.get("transcript") != NOT_TRANSCRIBED:
        raise RecordingRefused(
            "event refused: transcript metadata may only ever be %r in this "
            "version, got %r" % (NOT_TRANSCRIBED, event.get("transcript")))
    path = events_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


# ----------------------------------------------------------------- adapters --

class TwilioAdapter:
    """SKELETON. Present so the call sites exist; wired to nothing.

    Every method raises ProviderNotConfigured unless BOTH
    TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are set AND MPN_COMMS_LIVE=1.
    Even then, every method raises NotImplementedError: live wiring requires
    a tested provider connection, which this version does not have. This
    class never invents credentials and never makes a network call.
    """

    @staticmethod
    def configured() -> bool:
        return bool(os.environ.get("TWILIO_ACCOUNT_SID")
                    and os.environ.get("TWILIO_AUTH_TOKEN")
                    and os.environ.get("MPN_COMMS_LIVE") == "1")

    def _gate(self, method: str) -> None:
        if not self.configured():
            raise ProviderNotConfigured(
                "%s refused: no live provider is configured. Set "
                "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and MPN_COMMS_LIVE=1 "
                "- and even then this version will refuse (see below). The "
                "public number %s is answered by a human." % (method, PUBLIC_PHONE))
        raise NotImplementedError(
            "%s: live wiring requires a tested provider connection. This "
            "version makes no network calls and invents no credentials; use "
            "the NullAdapter dry-run commands instead." % method)

    def send_sms(self, to_ref: str, body: str) -> None:
        self._gate("send_sms")

    def place_call(self, to_ref: str) -> None:
        self._gate("place_call")

    def fetch_inbound_sms(self) -> None:
        self._gate("fetch_inbound_sms")

    def fetch_inbound_calls(self) -> None:
        self._gate("fetch_inbound_calls")

    def start_recording(self, call_ref: str, consent: str) -> None:
        self._gate("start_recording")


class NullAdapter:
    """Default adapter: dry-run. Logs redacted events; touches nothing else."""

    def simulate_inbound_sms(self, from_ref: str, summary: str) -> dict:
        event = {
            "ts": now_iso(),
            "kind": KIND_SMS_IN,
            "from_ref": validate_from_ref(from_ref),
            "redacted_summary": redact(summary),
            "consent": "none",
            "recording": recording_metadata("none", recording_requested=False),
        }
        append_event(event)
        return event

    def simulate_inbound_call(self, from_ref: str, summary: str,
                              duration_seconds: int, consent: str,
                              recording_requested: bool = False,
                              transcript_requested: bool = False) -> dict:
        consent = validate_consent(consent)
        if duration_seconds < 0:
            raise CommsError("duration-seconds must be >= 0, got %d"
                             % duration_seconds)
        event = {
            "ts": now_iso(),
            "kind": KIND_CALL_IN,
            "from_ref": validate_from_ref(from_ref),
            "redacted_summary": redact(summary),
            "duration_seconds": int(duration_seconds),
            "consent": consent,
            "recording": recording_metadata(consent, recording_requested),
            "transcript": transcript_metadata(consent, transcript_requested),
        }
        append_event(event)
        return event


# ---------------------------------------------------------------------- CLI --

def cmd_status() -> int:
    path = events_path()
    count = 0
    if path.is_file():
        with open(path, encoding="utf-8") as fh:
            count = sum(1 for line in fh if line.strip())
    print("provider       : NOT CONFIGURED (dry-run NullAdapter; no network code)")
    print("public number  : %s is answered by a human" % PUBLIC_PHONE)
    print("automation     : no automated calling, no automated texting - "
          "every outbound message is a draft a human sends manually")
    print("recording      : no recording - the recording field is always %r "
          "in this version" % NOT_RECORDED)
    print("events log     : %s (%d event line(s))" % (path, count))
    return 0


def cmd_audit() -> int:
    path = events_path()
    if path.is_file():
        sys.stdout.write(path.read_text(encoding="utf-8"))
    else:
        print("(no events)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("simulate-inbound-sms",
                       help="dry-run: log a redacted inbound-text event")
    p.add_argument("--from-ref", required=True,
                   help="opaque lead reference like L-014, NEVER a phone number")
    p.add_argument("--summary", required=True,
                   help="free text; phones/emails/addresses are redacted before storage")

    p = sub.add_parser("simulate-inbound-call",
                       help="dry-run: log a redacted inbound-call event")
    p.add_argument("--from-ref", required=True,
                   help="opaque lead reference like L-014, NEVER a phone number")
    p.add_argument("--summary", required=True,
                   help="free text; phones/emails/addresses are redacted before storage")
    p.add_argument("--duration-seconds", required=True, type=int)
    p.add_argument("--consent", required=True, choices=list(CONSENT_VALUES),
                   help="whether the caller gave recording consent (informational; "
                        "nothing is recorded in this version either way)")
    p.add_argument("--transcript-requested", action="store_true",
                   help="always refused: transcription needs consent AND a "
                        "live tested provider, which this version never has")
    p.add_argument("--recording-requested", action="store_true",
                   help="request recording metadata - ALWAYS refused in this "
                        "version; the flag exists so the refusal is exercised, "
                        "not assumed")

    sub.add_parser("status", help="provider and policy status")
    sub.add_parser("audit", help="print the raw event log")

    args = ap.parse_args(argv)

    try:
        if args.cmd == "simulate-inbound-sms":
            event = NullAdapter().simulate_inbound_sms(args.from_ref, args.summary)
            print("LOGGED %s from %s -> %s" % (event["kind"], event["from_ref"],
                                               events_path()))
            print("DRY RUN - nothing was sent, called, posted, or recorded.")
        elif args.cmd == "simulate-inbound-call":
            event = NullAdapter().simulate_inbound_call(
                args.from_ref, args.summary, args.duration_seconds,
                args.consent, recording_requested=args.recording_requested,
                transcript_requested=args.transcript_requested)
            print("LOGGED %s from %s (%ds, consent %s, recording %s) -> %s"
                  % (event["kind"], event["from_ref"], event["duration_seconds"],
                     event["consent"], event["recording"], events_path()))
            print("DRY RUN - nothing was sent, called, posted, or recorded.")
        elif args.cmd == "status":
            return cmd_status()
        elif args.cmd == "audit":
            return cmd_audit()
    except CommsError as exc:
        print("REFUSED: %s" % exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
