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

    def test_different_dates_with_known_travel_do_not_conflict(self):
        day = [
            visit(ref="L-001", date="2026-12-13", start="17:00"),
            visit(ref="L-002", date="2026-12-14", start="17:10",
                  travel_min_from_prev=30),
        ]
        # A full overnight gap accommodates the operator's known travel time.
        verdict, _ = MOD.validate_day(day)
        self.assertEqual(verdict, MOD.OK)

    def test_overnight_overlap_is_blocked_in_either_input_order(self):
        for first_date, second_date in (("2026-12-24", "2026-12-25"),
                                        ("2026-12-31", "2027-01-01")):
            for reverse in (False, True):
                with self.subTest(date=first_date, reverse=reverse):
                    visits = [visit(ref="EARLY", date=first_date, start="23:30",
                                    duration_min=60),
                              visit(ref="LATE", date=second_date, start="00:15",
                                    setup_min=0, travel_min_from_prev=10)]
                    verdict, findings = MOD.validate_day(visits[::-1] if reverse else visits)
                    self.assertEqual(verdict, MOD.BLOCKED)
                    self.assertTrue(any("overlaps" in f.detail for f in findings))

    def test_overnight_travel_and_setup_are_required(self):
        for start, setup in (("00:05", 0), ("00:15", 10)):
            with self.subTest(start=start, setup=setup):
                verdict, findings = MOD.validate_day([
                    visit(ref="EARLY", start="23:00", duration_min=60),
                    visit(ref="LATE", date="2026-12-25", start=start,
                          travel_min_from_prev=10, setup_min=setup),
                ])
                self.assertEqual(verdict, MOD.BLOCKED)
                self.assertTrue(any("insufficient buffer" in f.detail for f in findings))

    def test_overnight_exact_travel_and_setup_boundary_is_ok(self):
        verdict, _ = MOD.validate_day([
            visit(ref="EARLY", start="23:00", duration_min=60),
            visit(ref="LATE", date="2026-12-25", start="00:20",
                  travel_min_from_prev=10, setup_min=10),
        ])
        self.assertEqual(verdict, MOD.OK)

    def test_unknown_cross_date_travel_requires_review(self):
        verdict, findings = MOD.validate_day([
            visit(ref="EARLY", start="23:00", duration_min=60),
            visit(ref="LATE", date="2026-12-25", start="01:00",
                  travel_min_from_prev=None),
        ])
        self.assertEqual(verdict, MOD.NEEDS_ROUTE_REVIEW)
        self.assertTrue(any("not recorded" in f.detail for f in findings))

    def test_invalid_facts_block_without_route_arithmetic_errors(self):
        for field, value in (("date", "invalid"), ("setup_min", "15"),
                             ("setup_min", None), ("setup_min", True),
                             ("duration_min", True), ("travel_min_from_prev", True)):
            with self.subTest(field=field, value=value):
                late = visit(ref="LATE", date="2026-12-25", start="01:00")
                late[field] = value
                verdict, _ = MOD.validate_day([
                    visit(ref="EARLY", start="23:00", duration_min=60),
                    late,
                ])
                self.assertEqual(verdict, MOD.BLOCKED)

    def test_large_valid_numeric_buffer_blocks_without_overflow(self):
        verdict, _ = MOD.validate_day([
            visit(ref="EARLY", start="23:00", duration_min=60),
            visit(ref="LATE", date="2026-12-25", start="01:00", setup_min=10**20),
        ])
        self.assertEqual(verdict, MOD.BLOCKED)


if __name__ == "__main__":
    unittest.main()
