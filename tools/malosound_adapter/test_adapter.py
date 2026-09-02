"""Tests for the MaloSound.ai adapter boundary. Synthetic data only.

    python -m pytest tools/malosound_adapter/test_adapter.py -q
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("adapter.py")
SPEC = importlib.util.spec_from_file_location("ms_adapter", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

BOOKED_ENTRY = {
    "state": "BOOKED", "ref": "L-014", "held_until": "2026-12-22T10:00:00",
    "verified": {"by": "Marcelo", "at": "2026-12-20T09:00:00",
                 "method": "zelle", "amount": "250", "memo_ref": "MEMO-14"},
}
CATALOG_SLOT = {
    "slot_id": "EVE-2026-12-24-1700", "date": "2026-12-24",
    "start_time": "17:00", "end_time": "17:45", "category": "christmas_eve",
}


class AdapterBoundaryTests(unittest.TestCase):
    def test_status_is_not_configured(self):
        self.assertEqual(MOD.status(), MOD.STATUS_NOT_CONFIGURED)

    def test_handoff_always_raises(self):
        facts = MOD.content_facts(BOOKED_ENTRY, CATALOG_SLOT)
        with self.assertRaises(MOD.AdapterNotConfigured):
            MOD.handoff(facts)

    def test_no_network_modules_imported(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for banned in ("urllib", "socket", "http.client", "requests",
                       "smtplib", "subprocess"):
            self.assertNotIn("import %s" % banned, source)

    # ---------------------------------------------------------- privacy ----

    def test_facts_contain_no_customer_or_payment_data(self):
        facts = MOD.content_facts(BOOKED_ENTRY, CATALOG_SLOT)
        self.assertEqual(set(facts) & MOD.FORBIDDEN_FACT_KEYS, set())
        blob = " ".join(str(v) for v in facts.values())
        for secret in ("L-014", "MEMO-14", "Marcelo", "250"):
            self.assertNotIn(secret, blob)

    def test_facts_carry_only_coarse_public_shape(self):
        facts = MOD.content_facts(BOOKED_ENTRY, CATALOG_SLOT,
                                  "Christmas Eve", "Nochebuena")
        self.assertEqual(facts["date"], "2026-12-24")
        self.assertEqual(facts["window"], "17:00-17:45")
        self.assertIn("Christmas Eve delivery", facts["venue_kind_en"])
        self.assertIn("Nochebuena", facts["venue_kind_es"])

    def test_non_booked_reservation_refused(self):
        for state in ("OPEN", "HELD", "DEPOSIT_SENT", "", "SOLD"):
            with self.assertRaises(ValueError):
                MOD.content_facts({"state": state}, CATALOG_SLOT)

    def test_legacy_confirmed_accepted_as_booked(self):
        facts = MOD.content_facts({"state": "CONFIRMED"}, CATALOG_SLOT)
        self.assertEqual(facts["date"], "2026-12-24")

    def test_unknown_category_falls_back_to_generic_kind(self):
        facts = MOD.content_facts(BOOKED_ENTRY,
                                  dict(CATALOG_SLOT, category="mystery"))
        self.assertIn("private Santa visit", facts["venue_kind_en"])


if __name__ == "__main__":
    unittest.main()
