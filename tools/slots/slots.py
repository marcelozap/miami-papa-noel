#!/usr/bin/env python3
"""Canonical slot state machine and operator CLI for Miami Papa Noel.

    OPEN -> HELD -> DEPOSIT_SENT -> BOOKED

A slot is sold only at BOOKED. BOOKED is reachable only through the operator's
manual Zelle verification (`verify-zelle`) - the system never decides on its
own that money arrived. Confirmation text can be produced only for a BOOKED
slot. Public availability excludes only BOOKED slots.

Slot *catalog* (ids, dates, times, rates) lives in the repository at
schedules/peak_slots_2026.json. Slot *state* and customer references live
OUTSIDE the repository, because they are customer-adjacent:

    %MPN_SLOTS_DIR%  or  %LOCALAPPDATA%\\MiamiPapaNoel\\slots\\
        slot-state.json     current state per slot
        slot-ledger.jsonl   append-only audit trail (one line per transition)

Legacy state names from earlier tooling are accepted as aliases and
normalized: HOLD_48HR -> HELD, DEPOSIT_PAID -> DEPOSIT_SENT,
CONFIRMED -> BOOKED.

LOCAL MODE, stated plainly: the public site is static and cannot share live
state across devices. This tool does not pretend otherwise. `export-availability`
writes a dated snapshot for a manual deploy; until deployed, the site shows the
last exported snapshot, and the operator remains the source of truth.

Cancellation / retainer policy (preserved exactly as documented in
business/booking-sop.md and checkout.html): the 50% Zelle deposit is a
non-refundable retainer that locks the date after it clears; the balance is
due on arrival. Cancellation releases the slot; the retainer is recorded as
FORFEIT, or TRANSFERRED when the operator moves it to a new date.

Standard library only. Synthetic data only in the repository.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "schedules" / "peak_slots_2026.json"

OPEN = "OPEN"
HELD = "HELD"
DEPOSIT_SENT = "DEPOSIT_SENT"
BOOKED = "BOOKED"

CANONICAL_STATES = [OPEN, HELD, DEPOSIT_SENT, BOOKED]

LEGACY_ALIASES = {
    "HOLD_48HR": HELD,
    "DEPOSIT_PAID": DEPOSIT_SENT,
    "CONFIRMED": BOOKED,
}

# The only legal transitions. Anything else is rejected, loudly.
TRANSITIONS = {
    (OPEN, HELD): "hold",
    (HELD, DEPOSIT_SENT): "deposit-sent",
    (DEPOSIT_SENT, BOOKED): "verify-zelle",
    (HELD, OPEN): "release",
    (DEPOSIT_SENT, OPEN): "release",
    (BOOKED, OPEN): "cancel",
}

HOLD_HOURS_DEFAULT = 48

RETAINER_OUTCOMES = {"FORFEIT", "TRANSFERRED"}

ZELLE_DESTINATION = "305-244-0360"
PUBLIC_PHONE = "786-975-9557"
OFFICIAL_EMAIL = "santa@miamipapanoel.com"

# Booking requirements, exact bilingual phrasing shared with the Ms. Claus
# review checklist (tools/ms_claus/ms_claus.py). Keep in sync.
REQUIREMENTS = [
    ("a sturdy chair for Santa", "una silla firme para Santa"),
    ("air conditioning at the visit area", "aire acondicionado en el area de la visita"),
    ("a designated adult for gifts and photos", "un adulto encargado de regalos y fotos"),
    ("parking within 100 feet", "estacionamiento a menos de 100 pies"),
]


def state_dir() -> Path:
    override = os.environ.get("MPN_SLOTS_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "slots"


def state_path() -> Path:
    return state_dir() / "slot-state.json"


def ledger_path() -> Path:
    return state_dir() / "slot-ledger.jsonl"


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def normalize_state(value: str) -> str:
    value = (value or "").strip().upper()
    value = LEGACY_ALIASES.get(value, value)
    if value not in CANONICAL_STATES:
        raise ValueError("unknown slot state %r" % value)
    return value


# ------------------------------------------------------------------ catalog --

def load_catalog() -> dict:
    with open(CATALOG_PATH, encoding="utf-8") as fh:
        payload = json.load(fh)
    slots = {}
    for slot in payload.get("slots", []):
        slot_id = slot.get("slot_id")
        if not slot_id:
            raise ValueError("catalog contains a slot without slot_id")
        if slot_id in slots:
            raise ValueError("catalog contains duplicate slot_id %s" % slot_id)
        slots[slot_id] = slot
    return slots


# -------------------------------------------------------------------- store --

def load_state() -> dict:
    path = state_path()
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    normalized = {}
    for slot_id, entry in data.items():
        entry = dict(entry)
        entry["state"] = normalize_state(entry.get("state", OPEN))
        normalized[slot_id] = entry
    return normalized


def save_state(state: dict) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=1, ensure_ascii=False),
                    encoding="utf-8")


def append_ledger(slot_id: str, action: str, from_state: str, to_state: str,
                  operator: str, detail: str) -> None:
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": now_iso(),
        "slot_id": slot_id,
        "action": action,
        "from": from_state,
        "to": to_state,
        "operator": operator,
        "detail": detail,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def slot_entry(state: dict, slot_id: str) -> dict:
    return state.get(slot_id, {"state": OPEN})


def current_state(state: dict, slot_id: str) -> str:
    return normalize_state(slot_entry(state, slot_id).get("state", OPEN))


# -------------------------------------------------------------- transitions --

class TransitionError(Exception):
    pass


def transition(state: dict, slot_id: str, to_state: str, operator: str,
               detail: str = "", extra: dict | None = None) -> dict:
    frm = current_state(state, slot_id)
    action = TRANSITIONS.get((frm, to_state))
    if action is None:
        raise TransitionError(
            "illegal transition %s -> %s for slot %s (a slot is sold only at "
            "BOOKED, and BOOKED is reached only via verify-zelle)"
            % (frm, to_state, slot_id))
    entry = dict(slot_entry(state, slot_id))
    entry["state"] = to_state
    entry["updated_at"] = now_iso()
    if extra:
        entry.update(extra)
    if to_state == OPEN:
        # Releasing or cancelling clears the customer reference.
        for key in ("ref", "held_until", "deposit_marked_at", "verified"):
            entry.pop(key, None)
    state[slot_id] = entry
    append_ledger(slot_id, action, frm, to_state, operator, detail)
    return entry


OPAQUE_REF_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,23}$")


def require_opaque_ref(value: str, what: str) -> str:
    """Refs must be opaque tokens (L-014, MEMO-7) - never a name, phone, or
    memo text. Enforced, not advisory: no spaces, letter-first, max 24 chars,
    and no long digit runs."""
    value = (value or "").strip()
    if not OPAQUE_REF_RE.fullmatch(value) or re.search(r"\d{7,}", value):
        raise TransitionError(
            "%s must be an opaque reference like L-014 - never a customer "
            "name, phone number, or memo text (got %r)" % (what, value))
    return value


def hold(state: dict, slot_id: str, ref: str, operator: str,
         hours: int = HOLD_HOURS_DEFAULT) -> dict:
    ref = require_opaque_ref(ref, "hold --ref")
    held_until = (dt.datetime.now() + dt.timedelta(hours=hours)
                  ).isoformat(timespec="seconds")
    return transition(state, slot_id, HELD, operator,
                      "hold for %s until %s" % (ref, held_until),
                      {"ref": ref, "held_until": held_until})


def deposit_sent(state: dict, slot_id: str, operator: str) -> dict:
    return transition(state, slot_id, DEPOSIT_SENT, operator,
                      "customer reports Zelle deposit sent - NOT verified",
                      {"deposit_marked_at": now_iso()})


def verify_zelle(state: dict, slot_id: str, operator: str, amount: str,
                 memo_ref: str) -> dict:
    """The one and only path to BOOKED: a human checked the Zelle account."""
    if not operator.strip():
        raise TransitionError("verify-zelle requires --operator (a human name)")
    amt = amount.strip().lstrip("$")
    if not re.fullmatch(r"\d{1,4}(\.\d{2})?", amt) or float(amt) <= 0:
        raise TransitionError("verify-zelle requires --amount as a positive "
                              "dollar figure - a zero-dollar deposit cannot "
                              "book a slot")
    memo_ref = require_opaque_ref(memo_ref, "verify-zelle --memo-ref")
    return transition(
        state, slot_id, BOOKED, operator,
        "operator verified Zelle deposit %s memo-ref %s" % (amount, memo_ref),
        {"verified": {"by": operator, "at": now_iso(),
                      "amount": amount, "memo_ref": memo_ref}})


def release(state: dict, slot_id: str, operator: str, reason: str) -> dict:
    return transition(state, slot_id, OPEN, operator, "released: %s" % reason)


def cancel(state: dict, slot_id: str, operator: str, retainer: str,
           reason: str) -> dict:
    retainer = retainer.strip().upper()
    if retainer not in RETAINER_OUTCOMES:
        raise TransitionError(
            "cancel requires --retainer FORFEIT or TRANSFERRED - the 50%% "
            "deposit is a non-refundable retainer per the documented policy")
    return transition(state, slot_id, OPEN, operator,
                      "cancelled (%s): retainer %s" % (reason, retainer))


def expire_holds(state: dict, operator: str = "system") -> list:
    """Release HELD slots whose hold window has passed. Never touches
    DEPOSIT_SENT or BOOKED."""
    released = []
    now = dt.datetime.now()
    for slot_id, entry in list(state.items()):
        if normalize_state(entry.get("state", OPEN)) != HELD:
            continue
        held_until = entry.get("held_until")
        if not held_until:
            continue
        try:
            if dt.datetime.fromisoformat(held_until) < now:
                release(state, slot_id, operator, "hold expired")
                released.append(slot_id)
        except ValueError:
            continue
    return released


# ------------------------------------------------------------- availability --

def slot_window(slot: dict) -> str:
    """The human-readable time window, tolerant of both catalog schemas."""
    if slot.get("window"):
        return str(slot["window"])
    if slot.get("time"):
        return str(slot["time"])
    start, end = slot.get("start_time"), slot.get("end_time")
    if start and end:
        return "%s-%s" % (start, end)
    return str(start or end or "")


def availability(catalog: dict, state: dict) -> list:
    """Public availability. A slot leaves public availability ONLY at BOOKED."""
    out = []
    for slot_id, slot in sorted(catalog.items()):
        st = current_state(state, slot_id)
        if st != BOOKED:
            out.append({
                "slot_id": slot_id,
                "date": slot.get("date"),
                "window": slot_window(slot),
            })
    return out


def export_availability(catalog: dict, state: dict, out_path: Path) -> dict:
    snapshot = {
        "generated_at": now_iso(),
        "mode": "LOCAL SNAPSHOT - the static site does not share live state; "
                "this file must be deployed manually and is stale the moment "
                "a new booking lands",
        "available_slots": availability(catalog, state),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=1, ensure_ascii=False),
                        encoding="utf-8")
    return snapshot


# ------------------------------------------------------------- confirmation --

def confirmation_draft(catalog: dict, state: dict, slot_id: str) -> str:
    """Bilingual confirmation DRAFT. Only exists for a BOOKED slot. The
    operator still sends it by hand - there is no send path."""
    st = current_state(state, slot_id)
    if st != BOOKED:
        raise TransitionError(
            "confirmation refused: slot %s is %s, not BOOKED. A confirmation "
            "exists only after the operator verified the Zelle deposit."
            % (slot_id, st))
    entry = slot_entry(state, slot_id)
    verified = entry.get("verified", {})
    if not (verified.get("by") and verified.get("at")):
        raise TransitionError(
            "confirmation refused: slot %s is labeled BOOKED but carries no "
            "operator verification record. Only verify-zelle may book a slot; "
            "a hand-edited state file cannot produce a confirmation." % slot_id)
    slot = catalog.get(slot_id, {})
    req_en = "; ".join(en for en, _ in REQUIREMENTS)
    req_es = "; ".join(es for _, es in REQUIREMENTS)
    return (
        "== DRAFT - operator sends manually ==\n"
        "[EN] Your date is confirmed. Your Zelle deposit was verified by our "
        "team on %s. Date: %s, window: %s. The balance is due on arrival "
        "(Zelle %s). Please have ready: %s. Questions: %s / %s.\n"
        "[ES] Su fecha esta confirmada. Su deposito por Zelle fue verificado "
        "por nuestro equipo el %s. Fecha: %s, horario: %s. El saldo se paga "
        "al llegar (Zelle %s). Por favor tenga listo: %s. Preguntas: %s / %s."
        % (verified.get("at", ""), slot.get("date", ""),
           slot_window(slot), ZELLE_DESTINATION,
           req_en, PUBLIC_PHONE, OFFICIAL_EMAIL,
           verified.get("at", ""), slot.get("date", ""),
           slot_window(slot), ZELLE_DESTINATION,
           req_es, PUBLIC_PHONE, OFFICIAL_EMAIL))


# ---------------------------------------------------------- tracker privacy --

EXAMPLE_MARKERS = ("example", "synthetic", "test", "demo", "sample")


LOCKING_TRACKER_STATES = {"HELD", "DEPOSIT_SENT", "BOOKED",
                          "HOLD_48HR", "DEPOSIT_PAID", "CONFIRMED"}
PRIVATE_CUSTOMER_TYPES = ("family", "private", "residencial privado")


def check_tracker_privacy(tracker_path: Path) -> list:
    """Warn when the TRACKED lead-tracker.csv looks like it holds real
    CUSTOMERS. Public business prospects (schools, HOAs, shops) researched
    through public contact paths are legitimate committed data; what must
    never be committed is a private customer or a real booking: a row in a
    locking slot state, or a family/private row with contact data."""
    import csv
    warnings = []
    if not tracker_path.is_file():
        return warnings
    with open(tracker_path, newline="", encoding="utf-8-sig") as fh:
        for lineno, row in enumerate(csv.DictReader(fh), 2):
            name = (row.get("Business Name") or row.get("Contact Name") or "")
            if not name.strip():
                continue
            if any(m in name.lower() for m in EXAMPLE_MARKERS):
                continue
            state = (row.get("state") or "").strip().upper()
            row_type = (row.get("Type") or "").lower()
            contact = ((row.get("Phone") or "") + (row.get("Email") or "")).strip()
            if state in LOCKING_TRACKER_STATES:
                warnings.append(
                    "lead-tracker.csv line %d (%r) is in booking state %s - a "
                    "real booking means a real customer, which must never be "
                    "committed; keep the operational tracker outside Git"
                    % (lineno, name, state))
            elif contact and any(t in row_type for t in PRIVATE_CUSTOMER_TYPES):
                warnings.append(
                    "lead-tracker.csv line %d (%r) looks like a private "
                    "customer with contact data - must never be committed"
                    % (lineno, name))
    return warnings


# ---------------------------------------------------------------------- CLI --

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("hold", help="OPEN -> HELD (48h default)")
    p.add_argument("--slot", required=True)
    p.add_argument("--ref", required=True,
                   help="lead reference (L-014), never a full customer name")
    p.add_argument("--operator", required=True)
    p.add_argument("--hours", type=int, default=HOLD_HOURS_DEFAULT)

    p = sub.add_parser("deposit-sent", help="HELD -> DEPOSIT_SENT (unverified)")
    p.add_argument("--slot", required=True)
    p.add_argument("--operator", required=True)

    p = sub.add_parser("verify-zelle",
                       help="DEPOSIT_SENT -> BOOKED after a HUMAN checked Zelle")
    p.add_argument("--slot", required=True)
    p.add_argument("--operator", required=True)
    p.add_argument("--amount", required=True)
    p.add_argument("--memo-ref", required=True)

    p = sub.add_parser("release", help="HELD/DEPOSIT_SENT -> OPEN")
    p.add_argument("--slot", required=True)
    p.add_argument("--operator", required=True)
    p.add_argument("--reason", default="operator release")

    p = sub.add_parser("cancel", help="BOOKED -> OPEN; retainer FORFEIT/TRANSFERRED")
    p.add_argument("--slot", required=True)
    p.add_argument("--operator", required=True)
    p.add_argument("--retainer", required=True)
    p.add_argument("--reason", default="customer cancellation")

    p = sub.add_parser("confirmation", help="print bilingual draft (BOOKED only)")
    p.add_argument("--slot", required=True)

    sub.add_parser("availability", help="list publicly available slots")

    p = sub.add_parser("export-availability", help="write local-mode snapshot")
    p.add_argument("--out", default=None)

    sub.add_parser("expire-holds", help="release HELD slots past their window")
    sub.add_parser("status", help="state of every slot")
    sub.add_parser("audit", help="print the ledger")
    sub.add_parser("check-tracker-privacy",
                   help="warn if the committed tracker holds real-looking data")

    args = ap.parse_args(argv)
    catalog = load_catalog()
    state = load_state()

    try:
        if args.cmd == "hold":
            if args.slot not in catalog:
                raise TransitionError("unknown slot %s" % args.slot)
            entry = hold(state, args.slot, args.ref, args.operator, args.hours)
            save_state(state)
            print("HELD %s for %s until %s" % (args.slot, args.ref,
                                               entry["held_until"]))
        elif args.cmd == "deposit-sent":
            deposit_sent(state, args.slot, args.operator)
            save_state(state)
            print("DEPOSIT_SENT %s - awaiting operator Zelle verification. "
                  "The slot is NOT sold." % args.slot)
        elif args.cmd == "verify-zelle":
            verify_zelle(state, args.slot, args.operator, args.amount,
                         args.memo_ref)
            save_state(state)
            print("BOOKED %s - Zelle deposit verified by %s. Generate the "
                  "confirmation with: slots.py confirmation --slot %s"
                  % (args.slot, args.operator, args.slot))
        elif args.cmd == "release":
            release(state, args.slot, args.operator, args.reason)
            save_state(state)
            print("OPEN %s (released)" % args.slot)
        elif args.cmd == "cancel":
            cancel(state, args.slot, args.operator, args.retainer, args.reason)
            save_state(state)
            print("OPEN %s (cancelled; retainer %s per documented policy)"
                  % (args.slot, args.retainer.upper()))
        elif args.cmd == "confirmation":
            print(confirmation_draft(catalog, state, args.slot))
        elif args.cmd == "availability":
            for row in availability(catalog, state):
                print("%-14s %s %s" % (row["slot_id"], row["date"],
                                       row["window"]))
        elif args.cmd == "export-availability":
            out = Path(args.out) if args.out else state_dir() / "availability-snapshot.json"
            snap = export_availability(catalog, state, out)
            print("wrote %d available slot(s) to %s (LOCAL SNAPSHOT - deploy "
                  "manually)" % (len(snap["available_slots"]), out))
        elif args.cmd == "expire-holds":
            released = expire_holds(state)
            save_state(state)
            print("released %d expired hold(s): %s"
                  % (len(released), ", ".join(released) or "-"))
        elif args.cmd == "status":
            for slot_id in sorted(catalog):
                print("%-14s %s" % (slot_id, current_state(state, slot_id)))
        elif args.cmd == "audit":
            path = ledger_path()
            if path.is_file():
                sys.stdout.write(path.read_text(encoding="utf-8"))
            else:
                print("(ledger empty)")
        elif args.cmd == "check-tracker-privacy":
            warnings = check_tracker_privacy(REPO_ROOT / "lead-tracker.csv")
            for w in warnings:
                print("WARN " + w)
            print("%d warning(s)" % len(warnings))
            return 1 if warnings else 0
    except TransitionError as exc:
        print("REFUSED: %s" % exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
