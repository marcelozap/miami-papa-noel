"""Reservation store and state machine — the single shared source of truth.

Every lane (reservation agent, logistics agent, operator, content agent)
reads and writes reservations through this module. The state machine is
enforced HERE, in code — not by convention:

  inquiry -> hold -> pending_review -> confirmed -> completed
  (cancelled reachable from any non-terminal state)

Hard gates:
  * -> hold           requires date, start_time, zone, package
  * -> pending_review requires full address, guest_count, deposit VERIFIED
  * -> confirmed      requires actor == OPERATOR, a passing (non-impossible)
                      logistics check, and records operator_approval
  * deposits are only ever marked verified by the OPERATOR
  * no agent code path can produce status == confirmed

Storage: data/reservations.json (current state) + data/events.jsonl
(append-only event log: every transition, who did it, when, why).
"""

import json
import os
import uuid
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
RES_PATH = os.path.join(DATA_DIR, "reservations.json")
EVENTS_PATH = os.path.join(DATA_DIR, "events.jsonl")

OPERATOR = "operator"  # the only actor allowed to verify deposits or confirm

STATUSES = ("inquiry", "hold", "pending_review", "confirmed", "completed", "cancelled")

ALLOWED = {
    "inquiry": {"hold", "cancelled"},
    "hold": {"pending_review", "cancelled"},
    "pending_review": {"confirmed", "hold", "cancelled"},
    "confirmed": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}

DEPOSIT_STATUSES = ("unpaid", "claimed", "verified")


class TransitionError(Exception):
    """A state change violated the reservation contract."""


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- storage

def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def load(path=None):
    path = path or RES_PATH
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(records, path=None):
    _ensure_dirs()
    path = path or RES_PATH
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def append_event(actor, res_id, from_status, to_status, reason="", path=None):
    _ensure_dirs()
    path = path or EVENTS_PATH
    row = {
        "at": now_iso(),
        "actor": actor,
        "reservation": res_id,
        "from": from_status,
        "to": to_status,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def find(records, res_id):
    for r in records:
        if r["id"] == res_id:
            return r
    raise KeyError("no reservation with id %s" % res_id)


# ---------------------------------------------------------------- records

def new_reservation(**fields):
    """Create a new record in status 'inquiry'. Package is validated
    against the locked rate card if provided."""
    from rates import validate_package  # local import: no cycles

    rec = {
        "id": uuid.uuid4().hex[:10],
        "created_at": now_iso(),
        "lead_id": fields.get("lead_id"),
        "client_name": fields.get("client_name", ""),
        "phone": fields.get("phone", ""),
        "email": fields.get("email"),
        "language": fields.get("language", "en"),
        "package": fields.get("package"),
        "price_quoted": None,
        "date": fields.get("date"),
        "start_time": fields.get("start_time"),
        "duration_min": fields.get("duration_min", 60),
        "address": fields.get("address"),
        "zone": fields.get("zone"),
        "guest_count": fields.get("guest_count"),
        "kids_names_and_gifts": fields.get("kids_names_and_gifts"),
        "parking_notes": fields.get("parking_notes"),
        "setup_min": fields.get("setup_min", 0),
        "deposit": {
            "method": "zelle",
            "amount": fields.get("deposit_amount"),
            "status": "unpaid",
            "memo": None,
        },
        "status": "inquiry",
        "logistics": None,
        "operator_approval": None,
        "notes": fields.get("notes", ""),
    }
    if rec["package"]:
        rec["price_quoted"] = validate_package(rec["package"])["price"]
    return rec


# ------------------------------------------------------------- the gates

def _require(cond, msg):
    if not cond:
        raise TransitionError(msg)


def _gate_hold(rec):
    for field in ("date", "start_time", "zone", "package"):
        _require(rec.get(field), "hold requires %s" % field)
    from rates import validate_package
    validate_package(rec["package"])
    from zones import validate_zone
    validate_zone(rec["zone"])


def _gate_pending_review(rec):
    _gate_hold(rec)
    _require(rec.get("address"), "pending_review requires the full address")
    _require(rec.get("guest_count"), "pending_review requires guest details")
    _require(
        rec["deposit"]["status"] == "verified",
        "pending_review requires a VERIFIED deposit (operator runs verify-deposit "
        "after checking the Zelle payment; current: %s)" % rec["deposit"]["status"],
    )


def _gate_confirmed(rec, actor):
    _require(
        actor == OPERATOR,
        "only the operator may confirm a booking — agent '%s' refused" % actor,
    )
    _gate_pending_review(rec)
    lg = rec.get("logistics")
    _require(lg is not None, "confirmed requires a logistics check on file")
    _require(
        lg.get("result") in ("ok", "tight"),
        "confirmed blocked: logistics result is '%s'" % lg.get("result"),
    )


def verify_deposit(records, res_id, actor, amount=None, memo=None):
    """Only the operator records deposit verification, after checking the
    actual Zelle payment (50%, memo = event date + client name)."""
    if actor != OPERATOR:
        raise TransitionError(
            "only the operator may verify a deposit — agent '%s' refused" % actor
        )
    rec = find(records, res_id)
    rec["deposit"]["status"] = "verified"
    if amount is not None:
        rec["deposit"]["amount"] = amount
    if memo is not None:
        rec["deposit"]["memo"] = memo
    append_event(actor, res_id, rec["status"], rec["status"], "deposit verified")
    return rec


def transition(records, res_id, to_status, actor, reason=""):
    """The ONLY way status changes. Enforces the lifecycle and the gates."""
    rec = find(records, res_id)
    frm = rec["status"]
    _require(to_status in STATUSES, "unknown status %s" % to_status)
    _require(
        to_status in ALLOWED[frm],
        "illegal transition %s -> %s" % (frm, to_status),
    )
    if to_status == "hold":
        _gate_hold(rec)
    elif to_status == "pending_review":
        _gate_pending_review(rec)
    elif to_status == "confirmed":
        _gate_confirmed(rec, actor)
        rec["operator_approval"] = {"approved_by": actor, "at": now_iso()}
    rec["status"] = to_status
    append_event(actor, res_id, frm, to_status, reason)
    return rec


def confirmed_only(records):
    """The content lane's ONLY entry point to reservation data."""
    return [r for r in records if r["status"] == "confirmed"]
