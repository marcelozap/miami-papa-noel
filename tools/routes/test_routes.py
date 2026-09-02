"""Tests for the route and logistics validator. Synthetic fixtures only.

    python -m pytest tools/routes/test_routes.py -q
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("route_check.py")
SPEC = importlib.util.spec_from_file_location("mpn_routes", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def visit(**over):
    base = {"ref": "L-001", "date": "2026-12-24", "start": "17:00",
            "duration_min": 45, "travel_min_from_prev": 20, "setup_min": 15,
            "address_or_neighborhood": "Doral Isles clubhouse"}
    base.update(over)
    return base


class RouteValidatorTests(unittest.TestCase):
    # ------------------------------------------------------ valid route ----

    def test_valid_route_is_ok(self):
        day = [
            visit(ref="L-001", start="15:00"),
            visit(ref="L-002", start="17:00", travel_min_from_prev=30),
            visit(ref="L-003", start="19:00", travel_min_from_prev=25),
        ]
        verdict, findings = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.OK, [f.detail for f in findings])

    # ------------------------------------------------- overlapping ---------

    def test_overlapping_visits_are_blocked(self):
        day = [
            visit(ref="L-001", start="17:00", duration_min=60),
            visit(ref="L-002", start="17:30", travel_min_from_prev=10),
        ]
        verdict, findings = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.BLOCKED)
        self.assertTrue(any("overlaps" in f.detail for f in findings))
        self.assertTrue(any("physically impossible" in f.detail
                            for f in findings))

    # -------------------------------------------- insufficient buffer ------

    def test_insufficient_buffer_is_blocked(self):
        # Previous ends 17:45; 30 travel + 15 setup -> earliest 18:30,
        # but the next visit starts 18:00.
        day = [
            visit(ref="L-001", start="17:00", duration_min=45),
            visit(ref="L-002", start="18:00", travel_min_from_prev=30),
        ]
        verdict, findings = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.BLOCKED)
        self.assertTrue(any("insufficient buffer" in f.detail
                            for f in findings))

    def test_setup_buffer_is_honored(self):
        # Exactly at the earliest legal start: 17:45 end + 20 + 15 = 18:20.
        day = [
            visit(ref="L-001", start="17:00", duration_min=45),
            visit(ref="L-002", start="18:20", travel_min_from_prev=20),
        ]
        verdict, _ = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.OK)

    # ---------------------------------------------- missing address --------

    def test_missing_address_is_blocked(self):
        verdict, findings = MOD.validate_day(
            [visit(address_or_neighborhood="  ")])
        self.assertEqual(verdict, MOD.BLOCKED)
        self.assertTrue(any("address" in f.detail for f in findings))

    # ------------------------------------------- missing travel time -------

    def test_missing_travel_time_needs_route_review_never_ok(self):
        day = [
            visit(ref="L-001", start="15:00"),
            visit(ref="L-002", start="18:00", travel_min_from_prev=None),
        ]
        verdict, findings = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.NEEDS_ROUTE_REVIEW)
        self.assertTrue(any("never" in f.detail and "auto-approved" in f.detail
                            for f in findings))

    def test_review_never_upgrades_even_with_huge_gap(self):
        """Six hours of slack does not excuse an unverified route - the tool
        must not invent travel feasibility."""
        day = [
            visit(ref="L-001", start="10:00"),
            visit(ref="L-002", start="18:00", travel_min_from_prev=None),
        ]
        verdict, _ = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.NEEDS_ROUTE_REVIEW)

    def test_blocked_outranks_review(self):
        day = [
            visit(ref="L-001", start="17:00", duration_min=60),
            visit(ref="L-002", start="17:30", travel_min_from_prev=None),
            visit(ref="L-003", start="20:00", travel_min_from_prev=None),
        ]
        verdict, _ = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.BLOCKED)

    # ------------------------------------------------ hard-fact guards -----

    def test_bad_date_time_duration_are_blocked(self):
        for bad in (visit(date="dec 24"), visit(start="sometime"),
                    visit(duration_min=0), visit(duration_min=999),
                    visit(duration_min="45")):
            verdict, _ = MOD.validate_day([bad])
            self.assertEqual(verdict, MOD.BLOCKED, bad)

    def test_negative_travel_is_blocked(self):
        day = [
            visit(ref="L-001", start="15:00"),
            visit(ref="L-002", start="18:00", travel_min_from_prev=-10),
        ]
        verdict, findings = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.BLOCKED)

    def test_different_dates_do_not_conflict(self):
        day = [
            visit(ref="L-001", date="2026-12-13", start="17:00"),
            visit(ref="L-002", date="2026-12-14", start="17:10",
                  travel_min_from_prev=None),
        ]
        # Different dates: no consecutive pair, so no travel needed at all.
        verdict, _ = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.OK)


if __name__ == "__main__":
    unittest.main()
