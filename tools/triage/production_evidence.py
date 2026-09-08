"""Read-only evidence rules shared by operator status and submission checks."""
from __future__ import annotations

import datetime as dt

QUALIFYING_DAYS = 15
VALIDATION_CHECKS = frozenset({
    "pricing", "bilingual_parity", "missing_information",
    "unsafe_confirmation", "insurance_claim", "payment_method",
})


def log_timestamp(value: str) -> dt.datetime:
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("expected an ISO timestamp")
    try:
        # Legacy CLI timestamps were local without an offset. New writes include it.
        return dt.datetime.fromisoformat(value).astimezone(dt.timezone.utc)
    except (ValueError, OverflowError, OSError):
        raise ValueError("invalid ISO timestamp") from None


def reviewed_model_send_at(record: dict, now: dt.datetime) -> dt.datetime | None:
    """Return the evidenced send time, not a certification of genuine use."""
    if record.get("real_customer") is not True or record.get("fallback_used") is not False:
        return None
    model = record.get("model")
    reviewer = record.get("reviewer")
    if (not isinstance(model, str) or not model.strip()
            or model.strip().lower() in {"offline-rules-v1", "manual"}
            or not isinstance(reviewer, str) or not reviewer.strip()
            or record.get("outcome") != "approved_and_sent"
            or "error_code" not in record
            or record.get("error_code") is not None):
        return None
    findings = record.get("validation")
    if (not isinstance(findings, list) or not findings
            or any(not isinstance(f, dict) or f.get("level") not in ("PASS", "WARN")
                   or not isinstance(f.get("check"), str) for f in findings)
            or not VALIDATION_CHECKS <= {f["check"] for f in findings}):
        return None
    try:
        received, approved, sent = (log_timestamp(record.get(key))
                                    for key in ("received_at", "approved_at", "sent_at"))
        if received <= approved <= sent <= now.astimezone(dt.timezone.utc):
            return sent
    except (ValueError, TypeError, OverflowError, OSError):
        pass
    return None
