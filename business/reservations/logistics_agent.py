"""Lane 2 — Logistics agent.

For a given date, orders bookings by start time and checks every consecutive
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
"""

import store
import zones

BUFFER_MIN = 5        # parking + walking + breathing room
TIGHT_MARGIN_MIN = 5  # margin under this flags 'tight'

ACTOR = "logistics_agent"


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def check_date(records, date):
    """Check every scheduled (hold or later, not cancelled) booking on a
    date. Writes each record's `logistics` field and returns the legs."""
    day = [
        r for r in records
        if r.get("date") == date
        and r["status"] in ("hold", "pending_review", "confirmed")
        and r.get("start_time")
    ]
    day.sort(key=lambda r: _minutes(r["start_time"]))

    legs = []
    worst = {r["id"]: "ok" for r in day}
    rank = {"ok": 0, "tight": 1, "impossible": 2}

    for a, b in zip(day, day[1:]):
        end_a = _minutes(a["start_time"]) + int(a.get("duration_min") or 60)
        gap = _minutes(b["start_time"]) - end_a
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
    return legs


def check_reservation(records, res_id):
    """Run the day check for one reservation's date; return its result."""
    rec = store.find(records, res_id)
    if not rec.get("date"):
        raise store.TransitionError("reservation has no date to check")
    check_date(records, rec["date"])
    return rec["logistics"]
