"""Tests for the canonical slot state machine. Synthetic data only.

    python -m pytest tools/slots/test_slots.py -q
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

SCRIPT = Path(__file__).with_name("slots.py")
SPEC = importlib.util.spec_from_file_location("mpn_slots", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

CATALOG = {
    "S-DEC13-1800": {"slot_id": "S-DEC13-1800", "date": "2026-12-13", "window": "6:00-6:45pm"},
    "S-DEC24-1700": {"slot_id": "S-DEC24-1700", "date": "2026-12-24", "window": "5:00-5:45pm"},
}


class SlotMachineTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._env = mock.patch.dict("os.environ",
                                    {"MPN_SLOTS_DIR": self._tmp.name})
        self._env.start()
        self.state = {}

    def tearDown(self):
        self._env.stop()
        self._tmp.cleanup()

    # ------------------------------------------------------- happy path ----

    def book(self, slot="S-DEC13-1800"):
        MOD.hold(self.state, slot, "L-001", "operator")
        MOD.deposit_sent(self.state, slot, "operator")
        MOD.verify_zelle(self.state, slot, "operator", "275", "MEMO-7")

    def test_full_legal_path_reaches_booked(self):
        self.book()
        self.assertEqual(MOD.current_state(self.state, "S-DEC13-1800"), MOD.BOOKED)

    def test_slot_is_sold_only_at_booked(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        avail = [r["slot_id"] for r in MOD.availability(CATALOG, self.state)]
        self.assertIn("S-DEC13-1800", avail)  # DEPOSIT_SENT is still public
        MOD.verify_zelle(self.state, "S-DEC13-1800", "op", "275", "M-1")
        avail = [r["slot_id"] for r in MOD.availability(CATALOG, self.state)]
        self.assertNotIn("S-DEC13-1800", avail)  # removed ONLY at BOOKED
        self.assertIn("S-DEC24-1700", avail)

    # -------------------------------------------------- illegal moves ------

    def test_cannot_book_from_open(self):
        with self.assertRaises(MOD.TransitionError):
            MOD.verify_zelle(self.state, "S-DEC13-1800", "op", "275", "M-1")

    def test_cannot_book_from_held_without_deposit_sent(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.verify_zelle(self.state, "S-DEC13-1800", "op", "275", "M-1")

    def test_cannot_double_hold(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.hold(self.state, "S-DEC13-1800", "L-002", "op")

    def test_cannot_hold_a_deposit_sent_slot(self):
        """Phase 2 closure: a public hold request on a DEPOSIT_SENT slot is
        refused - the pending deposit is protected until verified/released."""
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.hold(self.state, "S-DEC13-1800", "L-002", "op")

    def test_cannot_hold_a_booked_slot(self):
        self.book()
        with self.assertRaises(MOD.TransitionError):
            MOD.hold(self.state, "S-DEC13-1800", "L-002", "op")

    def test_verify_requires_operator_amount_and_memo(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.verify_zelle(self.state, "S-DEC13-1800", " ", "275", "M-1")
        with self.assertRaises(MOD.TransitionError):
            MOD.verify_zelle(self.state, "S-DEC13-1800", "op", "lots", "M-1")
        with self.assertRaises(MOD.TransitionError):
            MOD.verify_zelle(self.state, "S-DEC13-1800", "op", "275", "")

    def test_hold_requires_reference(self):
        with self.assertRaises(MOD.TransitionError):
            MOD.hold(self.state, "S-DEC13-1800", "  ", "op")

    # ------------------------------------------------------ confirmation ---

    def test_confirmation_refused_before_booked(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.confirmation_draft(CATALOG, self.state, "S-DEC13-1800")

    def test_confirmation_contains_requirements_and_verified_line(self):
        self.book()
        text = MOD.confirmation_draft(CATALOG, self.state, "S-DEC13-1800")
        for en, es in MOD.REQUIREMENTS:
            self.assertIn(en, text)
            self.assertIn(es, text)
        self.assertIn("verified by our team", text)
        self.assertIn("verificado", text)
        self.assertIn(MOD.ZELLE_DESTINATION, text)
        self.assertIn(MOD.PUBLIC_PHONE, text)
        self.assertIn("DRAFT - operator sends manually", text)

    def test_confirmation_never_claims_cleared_without_verification(self):
        # The only path to the word "verified" is verify_zelle itself;
        # a DEPOSIT_SENT slot cannot produce any confirmation text at all.
        MOD.hold(self.state, "S-DEC24-1700", "L-002", "op")
        MOD.deposit_sent(self.state, "S-DEC24-1700", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.confirmation_draft(CATALOG, self.state, "S-DEC24-1700")

    # ------------------------------------------------- release / cancel ----

    def test_expired_hold_is_released_but_deposit_sent_is_not(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op", hours=48)
        self.state["S-DEC13-1800"]["held_until"] = (
            dt.datetime.now() - dt.timedelta(hours=1)).isoformat(timespec="seconds")
        MOD.hold(self.state, "S-DEC24-1700", "L-002", "op")
        MOD.deposit_sent(self.state, "S-DEC24-1700", "op")
        released = MOD.expire_holds(self.state)
        self.assertEqual(released, ["S-DEC13-1800"])
        self.assertEqual(MOD.current_state(self.state, "S-DEC24-1700"),
                         MOD.DEPOSIT_SENT)

    def test_cancel_requires_documented_retainer_outcome(self):
        self.book()
        with self.assertRaises(MOD.TransitionError):
            MOD.cancel(self.state, "S-DEC13-1800", "op", "REFUND", "changed mind")
        MOD.cancel(self.state, "S-DEC13-1800", "op", "FORFEIT", "changed mind")
        self.assertEqual(MOD.current_state(self.state, "S-DEC13-1800"), MOD.OPEN)

    def test_release_clears_customer_reference(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.release(self.state, "S-DEC13-1800", "op", "no reply")
        self.assertNotIn("ref", self.state["S-DEC13-1800"])

    # ------------------------------------------------------------ ledger ---

    def test_every_transition_writes_a_ledger_line(self):
        self.book()
        lines = [json.loads(l) for l in
                 MOD.ledger_path().read_text(encoding="utf-8").splitlines()]
        self.assertEqual([l["action"] for l in lines],
                         ["hold", "deposit-sent", "verify-zelle"])
        self.assertTrue(all(l["operator"] for l in lines))

    def test_ledger_never_contains_memo_text_field(self):
        self.book()
        raw = MOD.ledger_path().read_text(encoding="utf-8")
        self.assertNotIn("memo_text", raw)

    # ------------------------------------------------------------ legacy ---

    def test_legacy_states_normalize(self):
        self.assertEqual(MOD.normalize_state("HOLD_48HR"), MOD.HELD)
        self.assertEqual(MOD.normalize_state("DEPOSIT_PAID"), MOD.DEPOSIT_SENT)
        self.assertEqual(MOD.normalize_state("CONFIRMED"), MOD.BOOKED)
        with self.assertRaises(ValueError):
            MOD.normalize_state("SOLD")

    def test_export_is_labelled_local_mode(self):
        self.book()
        out = Path(self._tmp.name) / "snap.json"
        snap = MOD.export_availability(CATALOG, self.state, out)
        self.assertIn("LOCAL SNAPSHOT", snap["mode"])
        written = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(len(written["available_slots"]), 1)

    # ------------------------------------------------------ tracker guard --

    def test_tracker_privacy_flags_bookings_and_private_customers(self):
        tracker = Path(self._tmp.name) / "lead-tracker.csv"
        tracker.write_text(
            "Business Name,Contact Name,Phone,Email,Type,state\n"
            "Example Daycare,,,,Daycare,\n"
            "Sunshine Preschool,,3055550001,,School,\n"
            "Maria Gonzalez,,3055550000,,Family,\n"
            "Rivera Household,,3055550002,,Family,BOOKED\n",
            encoding="utf-8")
        warnings = MOD.check_tracker_privacy(tracker)
        self.assertEqual(len(warnings), 2)
        joined = " ".join(warnings)
        self.assertIn("Maria", joined)          # private customer w/ contact
        self.assertIn("Rivera", joined)         # locked booking state
        self.assertNotIn("Sunshine", joined)    # public business prospect OK


    # ------------------------------------------- audit regressions ---------

    def test_hand_edited_booked_state_cannot_produce_confirmation(self):
        """A CONFIRMED/BOOKED label written directly into slot-state.json has
        no operator verification record and must never yield a confirmation."""
        self.state["S-DEC13-1800"] = {"state": "CONFIRMED"}
        self.assertEqual(MOD.current_state(self.state, "S-DEC13-1800"), MOD.BOOKED)
        with self.assertRaises(MOD.TransitionError):
            MOD.confirmation_draft(CATALOG, self.state, "S-DEC13-1800")

    def test_zero_dollar_deposit_refused(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        for bad in ("0", "$0", "0.00"):
            with self.assertRaises(MOD.TransitionError):
                MOD.verify_zelle(self.state, "S-DEC13-1800", "op", bad, "M-1")

    def test_customer_name_or_phone_refused_as_reference(self):
        for bad in ("Maria Gonzalez 305-555-0123", "call 3055550123",
                    "Maria Gonzalez", "3055550123"):
            with self.assertRaises(MOD.TransitionError):
                MOD.hold(self.state, "S-DEC13-1800", bad, "op")
        MOD.hold(self.state, "S-DEC13-1800", "L-014", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.verify_zelle(self.state, "S-DEC13-1800", "op", "250",
                             "memo said Maria Gonzalez dec 24")

    def test_stripe_deposit_books_and_confirmation_names_the_card_rail(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        MOD.verify_deposit(self.state, "S-DEC13-1800", "op", "225",
                           "pi-7Q2K", "stripe")
        self.assertEqual(MOD.current_state(self.state, "S-DEC13-1800"),
                         MOD.BOOKED)
        text = MOD.confirmation_draft(CATALOG, self.state, "S-DEC13-1800")
        self.assertIn("card deposit (via our secure payment link)", text)
        self.assertIn("deposito con tarjeta", text)
        self.assertNotIn("Zelle deposit was", text)
        # Balance terms stay exactly as documented.
        self.assertIn(MOD.ZELLE_DESTINATION, text)

    def test_unknown_deposit_method_refused(self):
        MOD.hold(self.state, "S-DEC13-1800", "L-001", "op")
        MOD.deposit_sent(self.state, "S-DEC13-1800", "op")
        with self.assertRaises(MOD.TransitionError):
            MOD.verify_deposit(self.state, "S-DEC13-1800", "op", "225",
                               "X-1", "venmo")

    def test_zelle_shorthand_still_books_with_method_recorded(self):
        self.book()
        entry = self.state["S-DEC13-1800"]
        self.assertEqual(entry["verified"]["method"], "zelle")
        text = MOD.confirmation_draft(CATALOG, self.state, "S-DEC13-1800")
        self.assertIn("Zelle deposit", text)

    def test_real_catalog_start_end_times_render_in_window(self):
        catalog = {"X": {"slot_id": "X", "date": "2026-12-12",
                         "start_time": "16:00", "end_time": "17:00"}}
        self.assertEqual(MOD.slot_window(catalog["X"]), "16:00-17:00")


if __name__ == "__main__":
    unittest.main()
