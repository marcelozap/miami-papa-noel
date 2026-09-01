"""Tests for elf outreach. Synthetic data only.

    python -m pytest tools/elves/test_elves.py -q
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

SCRIPT = Path(__file__).with_name("outreach.py")
SPEC = importlib.util.spec_from_file_location("mpn_elves", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class ElfOutreachTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._env = mock.patch.dict("os.environ",
                                    {"MPN_ELVES_DIR": self._tmp.name})
        self._env.start()
        self.store = {}

    def tearDown(self):
        self._env.stop()
        self._tmp.cleanup()

    def add(self, org="Example Elementary School", category="school",
            city="Doral", contact="frontdesk@example-school.org"):
        return MOD.add_prospect(self.store, org, category, city, contact,
                                notes="synthetic", operator="op")

    # ------------------------------------------------------- add guards ----

    def test_prospect_without_public_contact_path_refused(self):
        with self.assertRaises(MOD.OutreachError):
            MOD.add_prospect(self.store, "Example HOA", "hoa", "Kendall", "")
        with self.assertRaises(MOD.OutreachError):
            MOD.add_prospect(self.store, "Example HOA", "hoa", "Kendall", "  ")
        self.assertEqual(self.store, {})

    def test_personal_gmail_refused_public_addresses_accepted(self):
        with self.assertRaises(MOD.OutreachError):
            self.add(contact="jane.doe@gmail.com")
        with self.assertRaises(MOD.OutreachError):
            self.add(contact="John.Smith@yahoo.com")
        # Public org prefixes and org domains are fine.
        p1 = self.add(contact="info@example-school.org")
        p2 = self.add(org="Example Bakery", category="business",
                      contact="office@examplebakery.com")
        p3 = self.add(org="Example HOA", category="hoa",
                      contact="https://example-hoa.org/contact")
        self.assertEqual([p1["state"], p2["state"], p3["state"]],
                         [MOD.RESEARCHED] * 3)

    def test_job_board_org_names_refused(self):
        for bad in ("Miami Job Board Weekly", "Indeed Listings",
                    "LinkedIn Jobs Feed", "Craigslist Gigs"):
            with self.assertRaises(MOD.OutreachError):
                self.add(org=bad, category="business",
                         contact="info@example.org")
        self.assertEqual(self.store, {})

    def test_category_outside_the_five_refused(self):
        for bad in ("church", "residential", "family", ""):
            with self.assertRaises(MOD.OutreachError):
                self.add(category=bad)
        p = self.add(category="community_event")
        self.assertEqual(p["category"], "community_event")

    # --------------------------------------------------- do-not-contact ----

    def test_do_not_contact_is_sticky(self):
        p = self.add()
        MOD.suppress(self.store, p["ref"], "op", "asked us not to contact")
        self.assertEqual(self.store[p["ref"]]["state"], MOD.DO_NOT_CONTACT)
        with self.assertRaises(MOD.OutreachError):
            MOD.draft(self.store, p["ref"])
        with self.assertRaises(MOD.OutreachError):
            MOD.approve(self.store, p["ref"], "op")
        with self.assertRaises(MOD.OutreachError):
            MOD.record_sent(self.store, p["ref"], "op", "email")
        self.assertEqual(self.store[p["ref"]]["state"], MOD.DO_NOT_CONTACT)

    def test_suppress_works_from_drafted_too(self):
        p = self.add()
        MOD.draft(self.store, p["ref"])
        MOD.suppress(self.store, p["ref"], "op", "org dissolved")
        self.assertEqual(self.store[p["ref"]]["state"], MOD.DO_NOT_CONTACT)
        with self.assertRaises(MOD.OutreachError):
            MOD.approve(self.store, p["ref"], "op")

    # ------------------------------------------------------- rate guard ----

    def test_drafted_cap_at_15_enforced(self):
        refs = []
        for i in range(16):
            p = self.add(org="Example Org %02d" % i,
                         contact="info@example%02d.org" % i)
            refs.append(p["ref"])
        for ref in refs[:15]:
            MOD.draft(self.store, ref)
        self.assertEqual(MOD.drafted_count(self.store), 15)
        with self.assertRaises(MOD.OutreachError):
            MOD.draft(self.store, refs[15])
        self.assertEqual(self.store[refs[15]]["state"], MOD.RESEARCHED)
        # Sending one out frees a slot: the cap forces send-and-record flow.
        MOD.approve(self.store, refs[0], "op")
        MOD.record_sent(self.store, refs[0], "op", "contact form")
        text = MOD.draft(self.store, refs[15])
        self.assertIn("[EN]", text)

    # ------------------------------------------------------------ draft ----

    def test_draft_is_bilingual_with_phone_email_no_affiliation(self):
        p = self.add()
        text = MOD.draft(self.store, p["ref"])
        self.assertIn("[EN]", text)
        self.assertIn("[ES]", text)
        self.assertEqual(text.count(MOD.PUBLIC_PHONE), 2)   # EN and ES
        self.assertEqual(text.count(MOD.OFFICIAL_EMAIL), 2)
        self.assertIn("coordinates holiday events", text)
        self.assertIn("coordina los eventos", text)
        lowered = text.lower()
        for term in MOD.FORBIDDEN_CUSTOM_TERMS:
            self.assertNotIn(term, lowered)
        self.assertIn("DRAFT", text)
        # ASCII only, for the Windows console.
        text.encode("ascii")

    def test_draft_is_deterministic_per_category(self):
        for category in MOD.CATEGORIES:
            prospect = {
                "ref": "P-900", "org_name": "Example Org",
                "category": category, "city": "Hialeah",
                "public_contact_path": "info@example.org",
            }
            a = MOD.build_draft(prospect, "We loved your tree lighting.")
            b = MOD.build_draft(prospect, "We loved your tree lighting.")
            self.assertEqual(a, b)
            self.assertIn(MOD.PUBLIC_PHONE, a)
            self.assertIn(MOD.OFFICIAL_EMAIL, a)

    def test_forbidden_custom_lines_refused(self):
        for bad in ("We are affiliated with the city",
                    "As an OFFICIAL PARTNER of the county",
                    "Endorsed by the school district",
                    "Reaching out on behalf of the HOA board",
                    "We are fully insured",
                    "Certificate of insurance available"):
            p = self.add(org="Example Org for %s" % bad[:12],
                         contact="info@example.org")
            with self.assertRaises(MOD.OutreachError):
                MOD.draft(self.store, p["ref"], custom_line=bad)
            self.assertEqual(self.store[p["ref"]]["state"], MOD.RESEARCHED)

    def test_draft_requires_researched_state(self):
        p = self.add()
        MOD.draft(self.store, p["ref"])
        with self.assertRaises(MOD.OutreachError):
            MOD.draft(self.store, p["ref"])  # no double-drafting

    # ---------------------------------------------------------- approve ----

    def test_approve_requires_operator_and_drafted_state(self):
        p = self.add()
        with self.assertRaises(MOD.OutreachError):
            MOD.approve(self.store, p["ref"], "op")  # not DRAFTED yet
        MOD.draft(self.store, p["ref"])
        with self.assertRaises(MOD.OutreachError):
            MOD.approve(self.store, p["ref"], "  ")
        MOD.approve(self.store, p["ref"], "op")
        self.assertEqual(self.store[p["ref"]]["state"], MOD.APPROVED)

    def test_record_sent_requires_operator_and_sent_via(self):
        p = self.add()
        MOD.draft(self.store, p["ref"])
        MOD.approve(self.store, p["ref"], "op")
        with self.assertRaises(MOD.OutreachError):
            MOD.record_sent(self.store, p["ref"], " ", "email")
        with self.assertRaises(MOD.OutreachError):
            MOD.record_sent(self.store, p["ref"], "op", "")
        MOD.record_sent(self.store, p["ref"], "op", "contact form")
        self.assertEqual(self.store[p["ref"]]["state"], MOD.SENT_BY_HUMAN)

    # -------------------------------------------------------- full path ----

    def test_full_legal_path_to_sent_by_human(self):
        p = self.add()
        ref = p["ref"]
        self.assertEqual(ref, "P-001")
        MOD.draft(self.store, ref)
        MOD.approve(self.store, ref, "op")
        MOD.record_sent(self.store, ref, "op",
                        "email from santa@miamipapanoel.com")
        self.assertEqual(self.store[ref]["state"], MOD.SENT_BY_HUMAN)
        lines = [json.loads(l) for l in
                 MOD.log_path().read_text(encoding="utf-8").splitlines()]
        self.assertEqual([l["action"] for l in lines],
                         ["add", "draft", "approve", "record-sent"])
        self.assertTrue(all(l["operator"] for l in lines))

    def test_cannot_skip_states(self):
        p = self.add()
        with self.assertRaises(MOD.OutreachError):
            MOD.record_sent(self.store, p["ref"], "op", "email")
        MOD.draft(self.store, p["ref"])
        with self.assertRaises(MOD.OutreachError):
            MOD.record_sent(self.store, p["ref"], "op", "email")

    # ---------------------------------------------------------- no send ----

    def test_tool_has_no_network_or_send_capability(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for module in ("smtplib", "urllib", "http.client", "requests",
                       "socket", "webbrowser", "subprocess"):
            self.assertNotIn("import %s" % module, source)


if __name__ == "__main__":
    unittest.main()
