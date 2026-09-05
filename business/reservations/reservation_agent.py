"""Lane 1 — Reservation agent.

Collects the booking data (date, time, address, package, guest details,
deposit status) and moves a record as far as the data allows:

  inquiry -> hold             once date/time/zone/package are in
  hold -> pending_review      once address + guests are in AND the operator
                              has verified the deposit

It can never verify a deposit and can never confirm — store.py refuses both
for this actor. On out-of-scope input it stops and escalates to the
operator (records the escalation in the event log) rather than guessing.
"""

import store

ACTOR = "reservation_agent"

FIELDS = (
    "client_name", "phone", "email", "language", "package", "date",
    "start_time", "duration_min", "address", "zone", "guest_count",
    "kids_names_and_gifts", "parking_notes", "setup_min", "lead_id", "notes",
)

BOOKING_FIELDS = (
    "package", "date", "start_time", "duration_min", "address", "zone",
    "guest_count", "setup_min",
)


def create(records, **fields):
    rec = store.new_reservation(**fields)
    records.append(rec)
    store.append_event(ACTOR, rec["id"], None, "inquiry", "created")
    advance(records, rec["id"])
    return rec


def update(records, res_id, **fields):
    rec = store.find(records, res_id)
    unknown = [k for k in fields if k not in FIELDS]
    if unknown:
        escalate(rec, "out-of-scope fields %s — stopping, operator decides" % unknown)
        raise store.TransitionError("out-of-scope input escalated: %s" % unknown)
    changed_booking = [
        k for k in BOOKING_FIELDS
        if k in fields and fields[k] is not None and fields[k] != rec.get(k)
    ]
    if rec["status"] in ("confirmed", "completed", "cancelled") and changed_booking:
        raise store.TransitionError(
            "booking details are locked; the operator must review cancellation "
            "and rebooking before changing %s" % ", ".join(changed_booking)
        )
    rec.update({k: v for k, v in fields.items() if v is not None})
    if "package" in fields and fields["package"]:
        from rates import validate_package
        rec["price_quoted"] = validate_package(fields["package"])["price"]
    store.append_event(ACTOR, res_id, rec["status"], rec["status"],
                       "updated %s" % ", ".join(sorted(fields)))
    advance(records, res_id)
    return rec


def advance(records, res_id):
    """Move the record forward as far as its data allows. Silently stops at
    the first gate that fails — completing the data later advances it."""
    rec = store.find(records, res_id)
    for target in ("hold", "pending_review"):
        if target in store.ALLOWED[rec["status"]]:
            try:
                store.transition(records, res_id, target, ACTOR, "data complete")
            except store.TransitionError:
                break
    return rec


def escalate(rec, reason):
    store.append_event(ACTOR, rec["id"], rec["status"], rec["status"],
                       "ESCALATION: " + reason)
