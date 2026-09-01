"""Tests for the Mrs. Claus Office intake agent. Synthetic data only.

    python -m pytest tools/mrs_claus_office/test_intake.py -q
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

SCRIPT = Path(__file__).with_name("intake.py")
SPEC = importlib.util.spec_from_file_location("mc_intake", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

FULL = {
    "channel": "text", "lang": "auto", "name": "Test Family",
    "phone": "3055550100", "date": "2026-12-13", "time": "6pm",
    "city": "Doral", "address_or_neighborhood": "Doral Isles",
    "event_type": "family party at home", "guest_details": "20 guests, 8 kids",
    "notes": "", "chair": "yes", "air_conditioning": "yes",
    "gift_adult": "yes", "parking": "yes",
}


def build(**over):
    args = dict(FULL)
    args.update(over)
    return MOD.build_record(args)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._env = mock.patch.dict("os.environ", {
            "MPN_INTAKE_DIR": self._tmp.name,
            "MPN_SLOTS_DIR": str(Path(self._tmp.name) / "slots"),
        })
        self._env.start()

    def tearDown(self):
        self._env.stop()
        self._tmp.cleanup()

    # ------------------------------------------------------ price drift ----

    def test_drafts_quote_only_locked_prices(self):
        rec = build()
        pricing = MOD.triage.load_pricing()
        allowed = set(pricing["allowed_amounts"])
        for draft in (rec["draft_en"], rec["draft_es"]):
            for amount in re.findall(r"\$\s?(\d{1,4})\b", draft):
                self.assertIn(int(amount), allowed, draft)
        self.assertFalse(MOD.blocking(rec), rec["validation"])

    def test_price_drift_is_caught_by_gates(self):
        pricing = MOD.triage.load_pricing()
        findings = MOD.validators.validate_pricing(
            "The visit is $999.", "La visita es $999.", pricing)
        self.assertTrue(any(f.level == "FAIL" for f in findings))

    # --------------------------------------------------- missing fields ----

    def test_missing_fields_are_listed_and_asked(self):
        rec = build(name="", date="", chair="unknown")
        self.assertIn("name", rec["missing_fields"])
        self.assertIn("date", rec["missing_fields"])
        self.assertIn("req_chair", rec["missing_fields"])
        self.assertIn("your name", rec["draft_en"])
        self.assertIn("su nombre", rec["draft_es"])
        self.assertIn("silla", rec["draft_es"])

    def test_complete_intake_asks_for_nothing(self):
        rec = build()
        self.assertEqual(rec["missing_fields"], [])
        self.assertNotIn("Could you share", rec["draft_en"])

    # ------------------------------------------------- unsafe language -----

    def test_drafts_never_confirm_or_promise_availability(self):
        rec = build()
        for draft in (rec["draft_en"], rec["draft_es"]):
            low = draft.lower()
            for banned in ("confirmed", "confirmada", "booked", "reservada",
                           "deposit received", "deposito recibido",
                           "the date is yours", "la fecha es suya"):
                self.assertNotIn(banned, low)
        self.assertIn("cannot promise a date", rec["draft_en"])
        self.assertIn("no puedo prometer una fecha", rec["draft_es"])
        gate = [f for f in rec["validation"]
                if f["check"] == "unsafe_confirmation"]
        self.assertTrue(all(f["level"] == "PASS" for f in gate))

    def test_no_discount_language_ever(self):
        rec = build(notes="any discount for veterans?")
        for draft in (rec["draft_en"], rec["draft_es"]):
            self.assertNotIn("discount", draft.lower())
            self.assertNotIn("descuento", draft.lower())
        self.assertIn("discount_request", rec["escalations"])

    # ----------------------------------------------------------- parity ----

    def test_english_spanish_parity(self):
        rec = build()
        findings = MOD.validators.validate_bilingual_parity(
            rec["draft_en"], rec["draft_es"])
        self.assertTrue(all(f.level != "FAIL" for f in findings),
                        [f.detail for f in findings])

    def test_spanish_notes_set_primary_language(self):
        rec = build(notes="Hola, quisiera una visita de Papa Noel para mi hija")
        self.assertEqual(rec["language"], "es")

    # ------------------------------------------------------- escalation ----

    def test_payment_question_escalates(self):
        rec = build(notes="I paid the deposit yesterday, did you get my zelle?")
        self.assertIn("payment_question", rec["escalations"])
        self.assertEqual(rec["outcome"], "escalate_to_operator")

    def test_complaint_escalates(self):
        rec = build(notes="I am very unhappy with how this was handled")
        self.assertIn("complaint", rec["escalations"])

    def test_final_availability_escalates(self):
        rec = build(notes="Are you available on the 13th? Can you guarantee it?")
        self.assertIn("availability_final", rec["escalations"])

    def test_unclear_request_escalates(self):
        rec = build(date="", event_type="", notes="hi")
        self.assertIn("unclear_request", rec["escalations"])

    def test_clean_intake_does_not_escalate(self):
        rec = build()
        self.assertEqual(rec["outcome"], "draft_ready_for_operator")

    # --------------------------------------------------- double booking ----

    def test_fully_booked_date_flags_internal_review(self):
        slots_dir = Path(self._tmp.name) / "slots"
        slots_dir.mkdir(parents=True, exist_ok=True)
        catalog = MOD.slots_mod.load_catalog()
        day = [sid for sid, s in catalog.items()
               if s.get("date") == "2026-12-24"]
        self.assertTrue(day, "catalog has no Dec 24 slots to test with")
        state = {sid: {"state": "BOOKED"} for sid in day}
        (slots_dir / "slot-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        rec = build(date="2026-12-24")
        self.assertEqual(rec["booking_pressure"], "all_booked")
        self.assertIn("date_fully_booked_review", rec["escalations"])
        # And the customer is never told the date is gone - the operator is.
        self.assertNotIn("fully booked", rec["draft_en"].lower())
        self.assertNotIn("not available", rec["draft_en"].lower())

    def test_open_date_reports_open(self):
        rec = build(date="2026-12-24")
        self.assertEqual(rec["booking_pressure"], "open")
        self.assertNotIn("date_fully_booked_review", rec["escalations"])

    # ------------------------------------------------------------ store ----

    def test_log_written_outside_repo(self):
        rec = build()
        path = MOD.write_log(rec)
        self.assertTrue(str(path).startswith(self._tmp.name))
        line = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(line["intake_id"], rec["intake_id"])

    def test_requirements_recorded(self):
        rec = build(parking="no")
        self.assertEqual(rec["parking"], "no")
        self.assertNotIn("req_parking", rec["missing_fields"])


    # ------------------------------------------- audit regressions ---------

    def test_cash_and_other_payment_methods_escalate(self):
        for note in ("Can I pay in cash when you arrive?",
                     "Do you take venmo instead of zelle?",
                     "puedo pagar en efectivo?"):
            rec = build(notes=note)
            self.assertIn("payment_question", rec["escalations"], note)

    def test_casual_availability_phrasing_escalates(self):
        for note in ("Is Dec 13 open?", "Is the 24th still open?",
                     "el 13 esta libre?"):
            rec = build(notes=note)
            self.assertIn("availability_final", rec["escalations"], note)

    def test_family_party_at_home_is_priced_as_family_visit(self):
        rec = build(event_type="family party at home")
        self.assertEqual(rec["event_type_key"], "family_visit")
        self.assertIn("$325", rec["draft_en"])
        self.assertNotIn("$450", rec["draft_en"])


if __name__ == "__main__":
    unittest.main()
