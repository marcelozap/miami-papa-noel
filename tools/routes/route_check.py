#!/usr/bin/env python3
"""Local route and logistics validator for a day of Santa visits.

Checks each visit's date, start time, duration, setup buffer, travel minutes,
and address/neighborhood, and blocks overlapping or physically impossible
schedules. Three verdicts, worst-wins per day:

    OK                  every check passed with operator-supplied numbers
    NEEDS_ROUTE_REVIEW  travel time missing/unverified - NEVER auto-approved
    BLOCKED             overlap, insufficient buffer, or missing hard facts

This tool NEVER invents map distances or traffic data. Travel minutes come
from the operator (their maps app, their judgment); when absent, the day
cannot be OK - it needs route review by a human. Setup buffer defaults to
15 minutes and can be set per visit.

The day file is written by the operator and may contain addresses, so it
belongs OUTSIDE the repository with the other operational state. Only
synthetic fixtures appear in tests.

    python tools/routes/route_check.py check --file day.json
    python tools/routes/route_check.py template > day.json

Day file shape (JSON list):
    [{"ref": "L-014", "date": "2026-12-24", "start": "17:00",
      "duration_min": 45, "travel_min_from_prev": 25, "setup_min": 15,
      "address_or_neighborhood": "Doral Isles clubhouse"}, ...]

Standard library only. Read-only: no state, no network, nothing sent.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

OK = "OK"
NEEDS_ROUTE_REVIEW = "NEEDS_ROUTE_REVIEW"
BLOCKED = "BLOCKED"

SETUP_MIN_DEFAULT = 15
MAX_VISIT_MIN = 240


class Finding:
    def __init__(self, level: str, ref: str, detail: str):
        self.level = level
        self.ref = ref
        self.detail = detail

    def as_dict(self) -> dict:
        return {"level": self.level, "ref": self.ref, "detail": self.detail}


def _parse_time(value: str):
    for fmt in ("%H:%M", "%I:%M%p", "%I%p"):
        try:
            return dt.datetime.strptime(str(value).strip().lower(), fmt).time()
        except ValueError:
            continue
    return None


def validate_visit(visit: dict) -> list:
    """Per-visit hard facts. Missing facts BLOCK - a schedule cannot be
    approved around an unknown address or an unparseable time."""
    findings = []
    ref = str(visit.get("ref") or "?")

    try:
        dt.date.fromisoformat(str(visit.get("date")))
    except (TypeError, ValueError):
        findings.append(Finding(BLOCKED, ref,
                                "date %r is not a valid ISO date"
                                % visit.get("date")))
    if _parse_time(visit.get("start", "")) is None:
        findings.append(Finding(BLOCKED, ref,
                                "start time %r is not a recognizable time"
                                % visit.get("start")))
    duration = visit.get("duration_min")
    if not isinstance(duration, int) or not 0 < duration <= MAX_VISIT_MIN:
        findings.append(Finding(BLOCKED, ref,
                                "duration_min must be 1-%d minutes, got %r"
                                % (MAX_VISIT_MIN, duration)))
    if not str(visit.get("address_or_neighborhood") or "").strip():
        findings.append(Finding(BLOCKED, ref,
                                "address_or_neighborhood is missing - a visit "
                                "cannot be routed to nowhere"))
    setup = visit.get("setup_min", SETUP_MIN_DEFAULT)
    if not isinstance(setup, int) or setup < 0:
        findings.append(Finding(BLOCKED, ref,
                                "setup_min must be a non-negative integer, "
                                "got %r" % setup))
    return findings


def validate_day(visits: list) -> tuple:
    """Returns (verdict, findings). Worst finding wins the day.

    Rule between consecutive visits on the same date, in start order:
        end(prev) + travel(next) + setup(next) <= start(next)
    Travel minutes are the operator's own number. None/absent means the route
    is unverified: the day becomes NEEDS_ROUTE_REVIEW, never OK.
    """
    findings = []
    for visit in visits:
        findings.extend(validate_visit(visit))

    parseable = [v for v in visits
                 if _parse_time(v.get("start", "")) is not None
                 and isinstance(v.get("duration_min"), int)]
    by_date = {}
    for v in parseable:
        by_date.setdefault(str(v.get("date")), []).append(v)

    for date, day in by_date.items():
        day.sort(key=lambda v: _parse_time(v["start"]))
        for prev, cur in zip(day, day[1:]):
            ref = str(cur.get("ref") or "?")
            start_prev = _parse_time(prev["start"])
            start_cur = _parse_time(cur["start"])
            end_prev = (dt.datetime.combine(dt.date.min, start_prev)
                        + dt.timedelta(minutes=prev["duration_min"]))
            start_cur_dt = dt.datetime.combine(dt.date.min, start_cur)

            if start_cur_dt < end_prev:
                findings.append(Finding(
                    BLOCKED, ref,
                    "%s: overlaps previous visit %s (previous ends %s, this "
                    "starts %s) - physically impossible"
                    % (date, prev.get("ref"), end_prev.time().strftime("%H:%M"),
                       start_cur.strftime("%H:%M"))))
                continue

            travel = cur.get("travel_min_from_prev")
            setup = cur.get("setup_min", SETUP_MIN_DEFAULT)
            if travel is None:
                findings.append(Finding(
                    NEEDS_ROUTE_REVIEW, ref,
                    "%s: travel time from %s is not recorded - the operator "
                    "must check the route themselves; this is never "
                    "auto-approved" % (date, prev.get("ref"))))
                continue
            if not isinstance(travel, int) or travel < 0:
                findings.append(Finding(
                    BLOCKED, ref,
                    "travel_min_from_prev must be a non-negative integer, "
                    "got %r" % travel))
                continue

            earliest = end_prev + dt.timedelta(minutes=travel + setup)
            if start_cur_dt < earliest:
                findings.append(Finding(
                    BLOCKED, ref,
                    "%s: insufficient buffer after %s - previous ends %s, "
                    "%d min travel + %d min setup means earliest start is "
                    "%s, but this starts %s"
                    % (date, prev.get("ref"),
                       end_prev.time().strftime("%H:%M"), travel, setup,
                       earliest.time().strftime("%H:%M"),
                       start_cur.strftime("%H:%M"))))

    if any(f.level == BLOCKED for f in findings):
        return BLOCKED, findings
    if any(f.level == NEEDS_ROUTE_REVIEW for f in findings):
        return NEEDS_ROUTE_REVIEW, findings
    return OK, findings


TEMPLATE = [{
    "ref": "L-001", "date": "2026-12-24", "start": "17:00",
    "duration_min": 45, "travel_min_from_prev": None, "setup_min": 15,
    "address_or_neighborhood": "",
}]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check", help="validate a day file")
    p.add_argument("--file", required=True)
    sub.add_parser("template", help="print a blank day file")
    args = ap.parse_args(argv)

    if args.cmd == "template":
        print(json.dumps(TEMPLATE, indent=2))
        return 0

    try:
        visits = json.loads(Path(args.file).read_text(encoding="utf-8"))
        if not isinstance(visits, list):
            raise ValueError("day file must be a JSON list of visits")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("BLOCKED: cannot read day file - %s" % exc)
        return 2

    verdict, findings = validate_day(visits)
    print("ROUTE CHECK - %d visit(s)" % len(visits))
    for f in findings:
        print("  %-19s %-8s %s" % (f.level, f.ref, f.detail))
    print("DAY VERDICT: %s" % verdict)
    if verdict == NEEDS_ROUTE_REVIEW:
        print("A human must verify the missing travel times before this "
              "schedule is workable. Nothing is approved automatically.")
    return 0 if verdict == OK else (1 if verdict == NEEDS_ROUTE_REVIEW else 2)


if __name__ == "__main__":
    raise SystemExit(main())
