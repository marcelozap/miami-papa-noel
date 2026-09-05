"""Lane 2: Elf #2, North Pole road-travel logistics.

For a given date, orders bookings by calendar date/time and checks every ordered
pair: is the gap between them enough for the drive (zone matrix) plus the
next visit's setup time plus a safety buffer? Results:

  ok          margin >= TIGHT_MARGIN_MIN
  tight       0 <= margin < TIGHT_MARGIN_MIN
  impossible  margin < 0 (or the visits overlap outright)

An 'impossible' result blocks pending_review -> confirmed in store.py.
Drive times are ESTIMATES from the zone matrix, not live traffic — same as
business/december-slot-board.html. Real-world constraints this encodes:
Christmas Eve slots run 60 min apart with 45-min visits (~15 min budget);
peak evenings run 90 apart with 60-min visits (~30 min budget).
Non-adjacent pairs are checked too: an overlapping provisional visit must
not hide an existing confirmed visit or its required travel time.
Checks refresh the whole active schedule so another day's refresh cannot
erase an overnight conflict. Reports include legs touching the requested date.
"""

from datetime import date as calendar_date, datetime
from itertools import combinations

import store
import zones

BUFFER_MIN = 5        # parking + walking + breathing room
TIGHT_MARGIN_MIN = 5  # margin under this flags 'tight'

ACTOR = "logistics_agent"


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _start_minute(rec):
    # Integer calendar minutes also handle long visits without datetime overflow.
    return calendar_date.fromisoformat(rec["date"]).toordinal() * 1440 + _minutes(rec["start_time"])


def _schedule_error(rec):
    try:
        date = rec.get("date")
        if calendar_date.fromisoformat(date).isoformat() != date:
            return "date must use YYYY-MM-DD"
    except (TypeError, ValueError):
        return "date must be a valid YYYY-MM-DD date"
    try:
        start = rec.get("start_time")
        if datetime.strptime(start, "%H:%M").strftime("%H:%M") != start:
            return "start_time must use HH:MM"
    except (TypeError, ValueError):
        return "start_time must be a valid HH:MM time"
    duration = rec.get("duration_min")
    if type(duration) is not int or duration <= 0:
        return "duration_min must be a positive integer"
    setup = rec.get("setup_min", 0)
    if type(setup) is not int or setup < 0:
        return "setup_min must be a non-negative integer"
    return None


def check_date(records, date):
    """Refresh every scheduled (hold or later, not cancelled) booking.
    Return the requested date's pairwise checks and invalid-input findings.
    These are conservative feasibility constraints, not an optimized route."""
    scheduled = [
        r for r in records
        if r["status"] in ("hold", "pending_review", "confirmed")
    ]
    invalid = {r["id"]: error for r in scheduled if (error := _schedule_error(r))}
    day = [r for r in scheduled if r["id"] not in invalid]
    day.sort(key=_start_minute)

    legs = []
    worst = {r["id"]: "ok" for r in day}
    rank = {"ok": 0, "tight": 1, "impossible": 2}

    for a, b in combinations(day, 2):
        end_a = _start_minute(a) + a["duration_min"]
        gap = _start_minute(b) - end_a
        drive = zones.drive_min(a["zone"], b["zone"])
        need = drive + int(b.get("setup_min") or 0) + BUFFER_MIN
        margin = gap - need
        if gap < 0:
            result = "impossible"  # outright overlap
        elif margin < 0:
            result = "impossible"
        elif margin < TIGHT_MARGIN_MIN:
            result = "tight"
        else:
            result = "ok"
        legs.append({
            "from": a["id"], "to": b["id"],
            "from_zone": a["zone"], "to_zone": b["zone"],
            "gap_min": gap, "drive_min": drive, "need_min": need,
            "margin_min": margin, "result": result,
        })
        # A bad leg is blamed on the booking that is NOT yet confirmed
        # (the incoming one), so an already-confirmed visit is never blocked
        # by a later request. If both sides are in the same state class,
        # the later visit carries it.
        if a["status"] == "confirmed" and b["status"] != "confirmed":
            blamed = [b["id"]]
        elif b["status"] == "confirmed" and a["status"] != "confirmed":
            blamed = [a["id"]]
        elif a["status"] == "confirmed" and b["status"] == "confirmed":
            blamed = [b["id"]]  # regression between two confirmed: flag later
        else:
            blamed = [b["id"]]
        for rid in blamed:
            if rank[result] > rank[worst[rid]]:
                worst[rid] = result

    checked_at = store.now_iso()
    for r in day:
        leg = next(
            (l for l in legs if r["id"] in (l["from"], l["to"])
             and l["result"] == worst[r["id"]]), None)
        r["logistics"] = {
            "result": worst[r["id"]],
            "gap_min": leg["gap_min"] if leg else None,
            "drive_min": leg["drive_min"] if leg else None,
            "checked_at": checked_at,
            "estimates": zones.using_estimates(),
        }
    # Unknown dates, lengths or setup cannot safely be bounded to one day.
    # Keep valid confirmations locked; repair active bad facts before new approval.
    if invalid:
        legs.extend({
            "kind": "invalid_schedule", "reservation": rid,
            "result": "impossible", "reason": reason,
        } for rid, reason in invalid.items())
        for r in scheduled:
            if r["id"] in invalid or r["status"] != "confirmed":
                r["logistics"] = {
                    "result": "impossible", "gap_min": None, "drive_min": None,
                    "checked_at": checked_at, "estimates": zones.using_estimates(),
                    "reason": invalid.get(r["id"], "repair invalid scheduling facts in the active schedule before approval"),
                }
    target_ids = {r["id"] for r in scheduled if r.get("date") == date}
    return [leg for leg in legs if leg.get("kind") == "invalid_schedule"
            or leg.get("from") in target_ids or leg.get("to") in target_ids]


def check_reservation(records, res_id):
    """Run the day check for one reservation's date; return its result."""
    rec = store.find(records, res_id)
    if not rec.get("date"):
        raise store.TransitionError("reservation has no date to check")
    check_date(records, rec["date"])
    return rec["logistics"]
