"""End-to-end integration test: one synthetic customer crosses every lane.

Proves the six lanes compose into one season workflow with SHARED external
state (a single temp root stands in for %LOCALAPPDATA%\\MiamiPapaNoel):

    inbound text (comms, redacted)
      -> Mrs. Claus intake (bilingual draft, gates, escalation)
      -> slot hold -> deposit-sent -> operator verify-zelle -> BOOKED
      -> confirmation draft (requirements + verification line)
      -> availability shrinks; intake sees the booked date
      -> content draft approved and dry-run scheduled
      -> elf prospect drafted, approved, recorded sent by a human

Synthetic data only. Nothing here sends, posts, records, or charges.

    python -m pytest tools/test_integration_season.py -q
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class SeasonIntegrationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        root = Path(self._tmp.name)
        self._env = mock.patch.dict("os.environ", {
            "MPN_SLOTS_DIR": str(root / "slots"),
            "MPN_INTAKE_DIR": str(root / "intake"),
            "MPN_COMMS_DIR": str(root / "comms"),
            "MPN_CONTENT_DIR": str(root / "content"),
            "MPN_ELVES_DIR": str(root / "elves"),
            "MPN_LOG_DIR": str(root / "triage"),
        }, clear=False)
        self._env.start()
        self.root = root
        self.slots = load("it_slots", HERE / "slots" / "slots.py")
        self.comms = load("it_comms", HERE / "comms" / "adapter.py")
        self.content = load("it_content", HERE / "content" / "queue.py")
        self.elves = load("it_elves", HERE / "elves" / "outreach.py")
        self.intake = load("it_intake", HERE / "mrs_claus_office" / "intake.py")

    def tearDown(self):
        self._env.stop()
        self._tmp.cleanup()

    def test_full_season_walkthrough(self):
        # ---- 1. Inbound text arrives; comms logs it redacted -------------
        events = self.comms.main([
            "simulate-inbound-sms", "--from-ref", "L-014",
            "--summary", "Family asks about Dec 24, call back at 305-555-0142",
        ])
        self.assertEqual(events, 0)
        raw = (self.root / "comms" / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("305-555-0142", raw)
        self.assertIn("L-014", raw)

        # ---- 2. Mrs. Claus intake drafts the bilingual reply -------------
        rec = self.intake.build_record({
            "channel": "text", "lang": "auto", "name": "Test Family",
            "phone": "3055550142", "date": "2026-12-24", "time": "5pm",
            "city": "Doral", "address_or_neighborhood": "Doral Isles",
            "event_type": "christmas eve delivery at home",
            "guest_details": "2 kids", "notes": "",
            "chair": "yes", "air_conditioning": "yes",
            "gift_adult": "yes", "parking": "yes",
        })
        self.assertFalse(self.intake.blocking(rec), rec["validation"])
        self.assertEqual(rec["booking_pressure"], "open")
        self.assertNotIn("confirmed", rec["draft_en"].lower())

        # ---- 3. Operator books a real catalog slot the honest way --------
        catalog = self.slots.load_catalog()
        slot_id = sorted(sid for sid, s in catalog.items()
                         if s.get("date") == "2026-12-24")[0]
        state = self.slots.load_state()
        self.slots.hold(state, slot_id, "L-014", "operator")
        self.slots.deposit_sent(state, slot_id, "operator")
        with self.assertRaises(self.slots.TransitionError):
            # No confirmation exists before the human verifies the Zelle.
            self.slots.confirmation_draft(catalog, state, slot_id)
        self.slots.verify_zelle(state, slot_id, "operator", "250", "MEMO-14")
        self.slots.save_state(state)

        text = self.slots.confirmation_draft(catalog, state, slot_id)
        for en, _es in self.slots.REQUIREMENTS:
            self.assertIn(en, text)
        self.assertIn("verified by our team", text)
        self.assertIn(self.slots.ZELLE_DESTINATION, text)

        # ---- 4. Availability shrinks; the snapshot is honest -------------
        avail = [r["slot_id"] for r in self.slots.availability(catalog, state)]
        self.assertNotIn(slot_id, avail)
        snap = self.slots.export_availability(
            catalog, state, self.root / "slots" / "snap.json")
        self.assertIn("LOCAL SNAPSHOT", snap["mode"])
        self.assertNotIn(slot_id,
                         [r["slot_id"] for r in snap["available_slots"]])

        # ---- 5. A later intake for the same date sees the pressure -------
        day_slots = [sid for sid, s in catalog.items()
                     if s.get("date") == "2026-12-24"]
        for sid in day_slots:
            if self.slots.current_state(state, sid) != self.slots.BOOKED:
                self.slots.hold(state, sid, "L-099", "operator")
                self.slots.deposit_sent(state, sid, "operator")
                self.slots.verify_zelle(state, sid, "operator", "250",
                                        "MEMO-99")
        self.slots.save_state(state)
        rec2 = self.intake.build_record({
            "channel": "website", "lang": "en", "name": "Second Family",
            "phone": "3055550199", "date": "2026-12-24", "time": "7pm",
            "city": "Doral", "address_or_neighborhood": "Doral",
            "event_type": "christmas eve delivery", "guest_details": "3 kids",
            "notes": "", "chair": "yes", "air_conditioning": "yes",
            "gift_adult": "yes", "parking": "yes",
        })
        self.assertEqual(rec2["booking_pressure"], "all_booked")
        self.assertIn("date_fully_booked_review", rec2["escalations"])
        self.assertNotIn("fully booked", rec2["draft_en"].lower())

        # ---- 6. Content and outreach lanes run their approval paths ------
        cstore = self.content.load_store()
        item = self.content.create_draft(
            cstore, "video.mp4", "Christmas Eve gift delivery windows in Miami")
        self.assertIn(self.slots.PUBLIC_PHONE, item["caption_en"])
        self.assertIn(self.slots.PUBLIC_PHONE, item["caption_es"])
        with self.assertRaises(self.content.QueueError
                               if hasattr(self.content, "QueueError")
                               else Exception):
            self.content.create_draft(cstore, "video.mp4",
                                      "our new partner Publix event")

        estore = {}
        self.elves.add_prospect(estore, "Example Preschool", "school",
                                "Doral", "office@example-preschool.org")
        self.elves.draft(estore, "P-001")
        self.elves.approve(estore, "P-001", "operator")
        self.elves.record_sent(estore, "P-001", "operator", "public form")
        self.assertEqual(estore["P-001"]["state"], self.elves.SENT_BY_HUMAN)

        # ---- 7. The whole journey left audit trails, all outside repo ----
        ledger = (self.root / "slots" / "slot-ledger.jsonl"
                  ).read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(ledger), 3)
        for line in ledger:
            entry = json.loads(line)
            self.assertTrue(entry["operator"])
        repo_root = HERE.parent
        for stray in ("slot-state.json", "events.jsonl", "intake-log.jsonl"):
            self.assertFalse((repo_root / stray).exists(),
                             "%s leaked into the repository" % stray)


class ReservationRouteIntegrationTest(unittest.TestCase):
    """Exercise the reservation, payment-review, and route lanes together."""

    def setUp(self):
        path = mock.patch.object(sys, "path", [
            str(HERE.parent / "business" / "reservations"), *sys.path,
        ])
        path.start()
        self.addCleanup(path.stop)
        import store
        import reservation_agent
        import operator_review
        self.store = store
        self.agent = reservation_agent
        self.operator = operator_review
        events = mock.patch.object(store, "append_event")
        self.events = events.start()
        self.addCleanup(events.stop)
        self.records = []

    def booking(self, time, package="standard", duration=60, zone="doral",
                paid=True, date="2026-12-10"):
        rec = self.agent.create(
            self.records, client_name="Synthetic route fixture", phone="305-555-0142",
            package=package, date=date, start_time=time, duration_min=duration,
            zone=zone, address="100 Example Street", guest_count=4,
        )
        if paid:
            self.operator.verify_deposit(
                self.records, rec["id"], amount=rec["price_quoted"] / 2,
                memo="SYNTHETIC-NOT-A-PAYMENT",
            )
            self.agent.advance(self.records, rec["id"])
        return rec

    def assert_route_blocks(self, rec):
        self.events.reset_mock()
        with self.assertRaisesRegex(self.store.TransitionError, "impossible"):
            self.operator.approve(self.records, rec["id"])
        self.assertEqual(rec["status"], "pending_review")
        self.assertIsNone(rec["operator_approval"])
        self.events.assert_not_called()

    def test_intermediate_hold_cannot_hide_long_confirmed_visit(self):
        first = self.booking("15:00", package="hoa", duration=120)
        self.operator.approve(self.records, first["id"])
        self.booking("15:30", package="jingle", duration=45, paid=False)
        incoming = self.booking("16:30")
        self.assert_route_blocks(incoming)
        self.assertEqual(first["status"], "confirmed")

    def test_intermediate_paid_request_cannot_hide_confirmed_visit(self):
        first = self.booking("15:00", package="hoa", duration=120)
        self.operator.approve(self.records, first["id"])
        self.booking("15:30", package="jingle", duration=45)
        self.assert_route_blocks(self.booking("16:30"))

    def test_incoming_long_visit_cannot_hide_later_confirmation(self):
        last = self.booking("17:00")
        self.operator.approve(self.records, last["id"])
        incoming = self.booking("15:00", package="photographer_4hr", duration=240)
        self.booking("16:00", package="jingle", duration=45, paid=False)
        self.assert_route_blocks(incoming)
        self.assertEqual(last["status"], "confirmed")

    def test_intermediate_hold_cannot_hide_impossible_drive(self):
        first = self.booking("15:00", package="hoa", duration=120)
        self.operator.approve(self.records, first["id"])
        self.booking("16:00", package="jingle", duration=45, zone="homestead", paid=False)
        incoming = self.booking("17:30", zone="homestead")
        self.assert_route_blocks(incoming)

    def test_three_feasible_visits_still_confirm(self):
        day = [self.booking(time) for time in ("15:00", "16:30", "18:00")]
        for rec in day:
            self.operator.approve(self.records, rec["id"])
            self.assertEqual(rec["status"], "confirmed")

    def test_cancelled_and_other_date_do_not_block(self):
        cancelled = self.booking("15:00", package="hoa", duration=120, paid=False)
        self.operator.cancel(self.records, cancelled["id"], "synthetic cancellation")
        other_day = self.booking("15:00", package="hoa", duration=120, date="2026-12-11")
        self.operator.approve(self.records, other_day["id"])
        incoming = self.booking("15:30")
        self.operator.approve(self.records, incoming["id"])
        self.assertEqual(incoming["status"], "confirmed")


if __name__ == "__main__":
    unittest.main()
