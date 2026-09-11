#!/usr/bin/env python3
"""Focused tests for the local OpenAI Partner Network submission validator."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_opn_submission.py")
SPEC = importlib.util.spec_from_file_location("validate_opn_submission", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from production_evidence import VALIDATION_CHECKS  # noqa: E402


class ValidatorTests(unittest.TestCase):
    def config(self, root: Path, final: bool, log: Path, evidence: Path):
        return MODULE.Config(
            repo_root=root,
            final=final,
            today=dt.date.today(),
            log_path=log,
            evidence_dir=evidence,
            run_external=False,
        )

    def write_log(self, path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row) + "\n")

    def base_row(self, **overrides):
        row = {
            "inquiry_id": "MPN-20260801-ABC123",
            "received_at": "2026-08-01T10:00:00-04:00",
            "channel": "instagram_dm",
            "language": "en",
            "requested_date": "2026-12-13",
            "category": "hoa_community",
            "missing_fields": [],
            "model": "gpt-test-model",
            "prompt_version": "triage-v1.0.0",
            "reviewer": "operator",
            "approved_at": "2026-08-01T10:02:00-04:00",
            "sent_at": "2026-08-01T10:03:00-04:00",
            "fallback_used": False,
            "outcome": "approved_and_sent",
            "error_code": None,
            "real_customer": True,
            "location": "Doral",
            "contact_status": "phone supplied",
            "validation": [{"check": name, "level": "PASS", "detail": "synthetic"}
                           for name in VALIDATION_CHECKS],
        }
        row.update(overrides)
        return row

    def failures(self, findings):
        return [finding for finding in findings if finding.level == MODULE.FAIL]

    def test_missing_log_is_warning_in_preflight_and_failure_in_final(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "triage" / "production-log.jsonl"
            evidence = root / "evidence"
            preflight = self.config(root, False, log, evidence)
            findings, earliest, models, approved, model_backed = MODULE.check_production_log(preflight)
            self.assertFalse(self.failures(findings))
            self.assertIsNone(earliest)
            self.assertFalse(model_backed)

            final = self.config(root, True, log, evidence)
            findings, *_ = MODULE.check_production_log(final)
            self.assertTrue(self.failures(findings))

    def test_private_log_fields_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            evidence = root / "evidence"
            self.write_log(log, [self.base_row(customer_name="Jane Doe")])
            findings, *_ = MODULE.check_production_log(self.config(root, True, log, evidence))
            self.assertTrue(self.failures(findings))
            self.assertTrue(any(f.area == "log-privacy" for f in findings))

    def test_offline_model_cannot_satisfy_final_model_requirement(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            evidence = root / "evidence"
            row = self.base_row(model="offline-rules-v1", fallback_used=True)
            self.write_log(log, [row])
            cfg = self.config(root, True, log, evidence)
            findings, earliest, models, approved, model_backed = MODULE.check_production_log(cfg)
            findings += MODULE.check_duration(cfg, earliest, approved, model_backed)
            self.assertTrue(any(f.area == "model" for f in findings))

    def test_qualifying_model_record_passes_duration_and_model_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            evidence = root / "evidence"
            old_date = (dt.date.today() - dt.timedelta(days=MODULE.QUALIFYING_DAYS + 1)).isoformat()
            self.write_log(log, [self.base_row(
                received_at=f"{old_date}T10:00:00-04:00",
                approved_at=f"{old_date}T10:02:00-04:00",
                sent_at=f"{old_date}T10:03:00-04:00",
            )])
            cfg = self.config(root, True, log, evidence)
            findings, earliest, models, approved, model_backed = MODULE.check_production_log(cfg)
            findings += MODULE.check_duration(cfg, earliest, approved, model_backed)
            self.assertFalse(self.failures(findings))

    def test_old_fallback_or_unsent_inquiry_cannot_age_a_new_model_reply(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            now = dt.datetime(2026, 9, 5, 15, tzinfo=dt.timezone.utc)
            cfg = MODULE.Config(root, True, log_path=log, now=now, run_external=False)
            old = self.base_row(model="offline-rules-v1", fallback_used=True)
            unsent = self.base_row(inquiry_id="MPN-UNSENT", outcome="pending_review",
                                   reviewer=None, approved_at=None, sent_at=None)
            recent = self.base_row(
                inquiry_id="MPN-RECENT", received_at="2026-09-04T10:00:00-04:00",
                approved_at="2026-09-04T10:02:00-04:00", sent_at="2026-09-04T10:03:00-04:00")
            self.write_log(log, [old, unsent, recent])
            findings, earliest, _, approved, model_backed = MODULE.check_production_log(cfg)
            self.assertFalse(self.failures(findings))
            self.assertEqual(earliest, dt.datetime(2026, 9, 4, 14, 3, tzinfo=dt.timezone.utc))
            duration = MODULE.check_duration(cfg, earliest, approved, model_backed)
            self.assertTrue(any(f.area == "duration" for f in self.failures(duration)))

    def test_duration_uses_full_send_timestamp_and_never_certifies_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sent = dt.datetime(2026, 9, 1, 14, 3, tzinfo=dt.timezone.utc)
            target = sent + dt.timedelta(days=15)
            for seconds, should_fail in [(-1, True), (0, False)]:
                with self.subTest(seconds=seconds):
                    cfg = MODULE.Config(root, True, now=target + dt.timedelta(seconds=seconds))
                    findings = MODULE.check_duration(cfg, sent, 1, True)
                    self.assertEqual(bool(self.failures(findings)), should_fail)
                    text = " ".join(f.detail for f in findings)
                    self.assertNotIn("requirement met", text)
                    if not should_fail:
                        self.assertIn("does not certify continued operation or OPN acceptance", text)

    def test_invalid_or_incomplete_model_records_cannot_supply_the_start(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            cfg = self.config(root, True, log, root / "evidence")
            for override in [
                {"validation": []}, {"validation": [{"check": "pricing", "level": "FAIL"}]},
                {"error_code": "MODEL_HTTP_ERROR"}, {"model": None}, {"reviewer": " "},
                {"sent_at": "2026-07-31T10:03:00-04:00"}, {"real_customer": False},
                {"sent_at": "9999-12-31T23:59:59-23:59"},
                {"sent_at": "0001-01-01T00:00:00+23:59"},
            ]:
                with self.subTest(override=override):
                    self.write_log(log, [self.base_row(**override)])
                    _, earliest, _, approved, model_backed = MODULE.check_production_log(cfg)
                    self.assertIsNone(earliest)
                    self.assertFalse(model_backed)
                    self.assertTrue(self.failures(MODULE.check_duration(cfg, earliest, approved, model_backed)))

    def test_timestamps_with_different_offsets_are_compared_as_instants(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            cfg = self.config(root, True, log, root / "evidence")
            self.write_log(log, [self.base_row(
                received_at="2026-08-01T16:00:00+02:00",
                approved_at="2026-08-01T10:02:00-04:00", sent_at="2026-08-01T14:03:00+00:00")])
            findings, earliest, _, _, backed = MODULE.check_production_log(cfg)
            self.assertFalse(self.failures(findings))
            self.assertTrue(backed)
            self.assertEqual(earliest, dt.datetime(2026, 8, 1, 14, 3, tzinfo=dt.timezone.utc))

    def test_future_send_on_same_date_does_not_start_clock(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            cfg = MODULE.Config(root, True, log_path=log,
                                now=dt.datetime(2026, 9, 5, 14, tzinfo=dt.timezone.utc))
            self.write_log(log, [self.base_row(
                received_at="2026-09-05T13:00:00+00:00",
                approved_at="2026-09-05T13:02:00+00:00", sent_at="2026-09-05T15:00:00+00:00")])
            findings, earliest, _, _, backed = MODULE.check_production_log(cfg)
            self.assertTrue(any("future" in f.detail for f in self.failures(findings)))
            self.assertIsNone(earliest)
            self.assertFalse(backed)

    def test_public_surface_scan_blocks_non_zelle_and_unverified_insurance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tools/triage").mkdir(parents=True)
            (root / "tools/triage/pricing.json").write_text(json.dumps({"allowed_amounts": [325]}), encoding="utf-8")
            (root / "checkout.html").write_text("<p>Pay by Venmo. We are insured.</p>", encoding="utf-8")
            findings = MODULE.check_public_surfaces(self.config(root, True, root / "log", root / "evidence"))
            self.assertTrue(self.failures(findings))

    def test_evidence_index_requires_matching_redacted_artifact_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "receipts" / "receipt-01.txt"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("redacted receipt 2025-12-24 amount 500", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            index = root / "evidence-index.jsonl"
            index.write_text(json.dumps({
                "ref": "E-01",
                "type": "receipt",
                "date": "2025-12-24",
                "artifact": "receipts/receipt-01.txt",
                "sha256": digest,
                "redacted": True,
                "notes": "dated seasonal customer operation",
            }) + "\n", encoding="utf-8")
            cfg = self.config(root, True, root / "log", root)
            findings = MODULE.check_evidence_dir(cfg)
            self.assertFalse(self.failures(findings))

            artifact.write_text("changed", encoding="utf-8")
            findings = MODULE.check_evidence_dir(cfg)
            self.assertTrue(self.failures(findings))

    def test_evidence_index_rejects_contact_data_and_path_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "receipt.txt"
            artifact.write_text("redacted", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            (root / "evidence-index.jsonl").write_text(json.dumps({
                "ref": "E-01",
                "type": "receipt",
                "date": "2025-12-24",
                "artifact": "../receipt.txt",
                "sha256": digest,
                "redacted": True,
                "notes": "contact: someone@example.com",
            }) + "\n", encoding="utf-8")
            findings = MODULE.check_evidence_dir(self.config(root, True, root / "log", root))
            self.assertTrue(self.failures(findings))

    def test_evidence_index_rejects_future_date_and_private_extra_key(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "receipt.txt"
            artifact.write_text("redacted", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            future = (dt.date.today() + dt.timedelta(days=1)).isoformat()
            (root / "evidence-index.jsonl").write_text(json.dumps({
                "ref": "E-01",
                "type": "receipt",
                "date": future,
                "artifact": "receipt.txt",
                "sha256": digest,
                "redacted": True,
                "notes": "dated seasonal customer operation",
                "transaction_id": "private-id",
            }) + "\n", encoding="utf-8")
            details = "; ".join(
                f.detail for f in self.failures(MODULE.check_evidence_dir(
                    self.config(root, True, root / "log", root))))
            self.assertIn("future", details)
            self.assertIn("unsupported key", details)
            self.assertIn("private-data field", details)

    def test_log_rejects_future_timestamp_duplicate_id_and_bad_order(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "production-log.jsonl"
            evidence = root / "evidence"
            today = dt.date.today().isoformat()
            first = self.base_row(
                received_at=f"{today}T10:00:00-04:00",
                approved_at=f"{today}T09:00:00-04:00",
                sent_at=f"{today}T08:00:00-04:00",
            )
            second = self.base_row(
                received_at=f"{(dt.date.today() + dt.timedelta(days=1)).isoformat()}T10:00:00-04:00",
            )
            self.write_log(log, [first, second])
            details = "; ".join(
                f.detail for f in self.failures(MODULE.check_production_log(
                    self.config(root, True, log, evidence))[0]))
            self.assertIn("duplicate inquiry_id", details)
            self.assertIn("approved_at precedes received_at", details)
            self.assertIn("sent_at precedes received_at", details)
            self.assertIn("sent_at precedes approved_at", details)
            self.assertIn("future", details)


    def test_surface_scan_covers_every_root_page(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tools/triage").mkdir(parents=True)
            (root / "tools/triage/pricing.json").write_text(
                json.dumps({"allowed_amounts": [325]}), encoding="utf-8")
            (root / "thank-you.html").write_text(
                "<p>Pay by Venmo. Only $999.</p>", encoding="utf-8")
            cfg = self.config(root, True, root / "log.jsonl", root / "evidence")
            details = "; ".join(
                f.detail for f in self.failures(MODULE.check_public_surfaces(cfg)))
            self.assertIn("thank-you.html", details)
            self.assertIn("Venmo", details)
            self.assertIn("$999", details)

    # --- contextual surface scanning (2026-09-11) -------------------------
    # Six findings were lexical false positives: negative insurance guidance
    # read as an insurance claim, and the prospect name "Bark Square" read as
    # Square payment acceptance. These prove the correction is narrow - real
    # claims still fail, and a disclaimer cannot launder a nearby claim.

    def surface_details(self, root, body, filename="index.html", amounts=(325,)):
        (root / "tools/triage").mkdir(parents=True, exist_ok=True)
        (root / "tools/triage/pricing.json").write_text(
            json.dumps({"allowed_amounts": list(amounts)}), encoding="utf-8")
        (root / filename).write_text(body, encoding="utf-8")
        cfg = self.config(root, True, root / "log.jsonl", root / "evidence")
        return "; ".join(f.detail for f in self.failures(MODULE.check_public_surfaces(cfg)))

    def test_negative_insurance_guidance_is_not_a_production_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            details = self.surface_details(Path(temp),
                "<p><code>business/insurance-and-wave1-preflight.md</code> records the "
                "commercial policy as NOT ACTIVE.</p>\n"
                "<p>Until someone has the policy document in hand, do not say insured, "
                "fully insured, certificate of insurance, COI, additional insured or "
                "liability policy.</p>\n"
                "<div><b>Not verified.</b> Commercial insurance: not active as recorded "
                "2026-08-26. Any claim about being\n"
                "insured, or about providing a certificate, stays out of every message "
                "until that changes.</div>\n")
            self.assertNotIn("insurance language", details)

    def test_prospect_name_alone_is_not_payment_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            details = self.surface_details(Path(temp),
                '<script>var LEADS = [{"org":"Bark Square","city":"Doral",'
                '"email":"info@barksquare.com","group":"Pet Business",'
                '"ask":"Pet Photos with Santa"}];</script>')
            self.assertNotIn("non-Zelle", details)

    def test_actual_insurance_claim_still_blocked_without_verified_policy(self):
        for claim in ("<p>We are fully insured and carry general liability.</p>",
                      "<p>Certificate of insurance available on request.</p>",
                      "<p>Estamos asegurados con poliza de responsabilidad civil.</p>",
                      "<p>We have no problem providing a certificate of insurance.</p>"):
            with tempfile.TemporaryDirectory() as temp:
                details = self.surface_details(Path(temp), claim)
                self.assertIn("insurance language", details, claim)

    def test_actual_square_acceptance_still_blocked(self):
        for claim in ("<p>Pay with Square at checkout.</p>",
                      "<p>We accept Square for deposits.</p>",
                      "<p>Square payments accepted.</p>",
                      "<p>Puede pagar con Square.</p>"):
            with tempfile.TemporaryDirectory() as temp:
                details = self.surface_details(Path(temp), claim)
                self.assertIn("non-Zelle", details, claim)

    def test_disclaimer_cannot_launder_a_claim_in_the_same_block_or_page(self):
        with tempfile.TemporaryDirectory() as temp:
            # Same block, adjacent sentence.
            details = self.surface_details(Path(temp),
                "<div><b>Not verified.</b> Commercial insurance is not active. "
                "We are fully insured.</div>")
            self.assertIn("insurance language", details)
        with tempfile.TemporaryDirectory() as temp:
            # Same page, a later line.
            details = self.surface_details(Path(temp),
                "<p>Do not say insured or offer a certificate of insurance.</p>\n"
                "<p>Filler.</p>\n"
                "<p>We are fully insured.</p>\n")
            self.assertIn("insurance language", details)
        with tempfile.TemporaryDirectory() as temp:
            # A payment disclaimer must not launder an acceptance line either.
            details = self.surface_details(Path(temp),
                "<p>Never say we accept Square.</p>\n<p>Pay with Square here.</p>\n")
            self.assertIn("non-Zelle", details)

    def test_html_blocks_separate_claims_without_sentence_punctuation(self):
        """Reviewer finding: prohibition in one block suppressed a claim in the next."""
        for body in ("<p>Do not say insured</p><p>We are fully insured</p>",
                     "<li>Do not say insured</li><li>We are fully insured</li>",
                     "<td>never claim insurance</td><td>we carry general liability</td>",
                     "<div>Not verified</div><div>Estamos asegurados</div>"):
            with tempfile.TemporaryDirectory() as temp:
                details = self.surface_details(Path(temp), body)
                self.assertIn("insurance language", details, body)

    def test_prohibition_cannot_retract_an_assertion_later_in_the_sentence(self):
        with tempfile.TemporaryDirectory() as temp:
            details = self.surface_details(Path(temp),
                "<p>We are fully insured and never say otherwise.</p>")
            self.assertIn("insurance language", details)

    def test_status_disclaimer_cannot_negate_a_positive_assertion(self):
        for body in (
            '<p>Our coverage is not verified, but we are fully insured.</p>',
            '<p>Not active, yet we provide a certificate of insurance.</p>',
            '<p>No verificado, pero estamos asegurados.</p>',
            '<p>Do not say we are insured, but we are fully insured.</p>',
        ):
            with tempfile.TemporaryDirectory() as temp:
                self.assertIn('insurance language', self.surface_details(Path(temp), body), body)

    def test_direct_prohibition_of_inline_assertion_is_allowed(self):
        for body in ('<p>Do not say <b>we are insured</b>.</p>',
                     '<p>Nunca diga que estamos asegurados.</p>'):
            with tempfile.TemporaryDirectory() as temp:
                self.assertNotIn('insurance language', self.surface_details(Path(temp), body), body)

    def test_blank_source_lines_do_not_hide_payment_instructions(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertIn('non-Zelle', self.surface_details(Path(temp),
                '<p>Pay with\n\n\nSquare</p>'))

    def test_colon_introducer_still_governs_the_list_it_introduces(self):
        # The real dashboard pattern: "Held back for that reason:" + <li> items.
        with tempfile.TemporaryDirectory() as temp:
            details = self.surface_details(Path(temp),
                "<div>Held back for that reason, do not offer:<ul><li>"
                "<b>Certificate Of Insurance / Background Check</b></li></ul></div>")
            self.assertNotIn("insurance language", details)

    def test_payment_instruction_split_across_source_lines_still_blocked(self):
        """Reviewer finding: HTML wraps, so "Pay with" / "Square" straddled lines."""
        for body in ("<p>Pay with\nSquare</p>",
                     "<p>Pay with\n   Square at checkout</p>",
                     "<p>Puede pagar con\nSquare</p>"):
            with tempfile.TemporaryDirectory() as temp:
                details = self.surface_details(Path(temp), body)
                self.assertIn("non-Zelle", details, body)

    def test_prospect_name_survives_the_cross_line_window(self):
        # The widened window must not drag unrelated payment words onto a name.
        with tempfile.TemporaryDirectory() as temp:
            details = self.surface_details(Path(temp),
                "<p>Deposit is 50% by Zelle.</p>\n"
                '<script>var LEADS=[{"org":"Bark Square","city":"Doral"}];</script>\n'
                "<p>Balance due on arrival.</p>")
            self.assertNotIn("non-Zelle", details)

    def test_unambiguous_brands_still_match_without_payment_context(self):
        # Only "Square" gained a context requirement; the rest are unchanged.
        for claim in ("<p>Venmo</p>", "<p>PayPal</p>", "<p>Cash App</p>",
                      "<p>Zinli</p>", "<p>credit card</p>"):
            with tempfile.TemporaryDirectory() as temp:
                details = self.surface_details(Path(temp), claim)
                self.assertIn("non-Zelle", details, claim)

    def test_filename_masking_does_not_hide_prose_claims(self):
        with tempfile.TemporaryDirectory() as temp:
            details = self.surface_details(Path(temp),
                "<p>See notes.md &mdash; we are fully insured. Pay with Venmo.</p>")
            self.assertIn("insurance language", details)
            self.assertIn("Venmo", details)

    def test_retired_booking_email_blocks_even_in_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tools/triage").mkdir(parents=True)
            (root / "tools/triage/pricing.json").write_text(
                json.dumps({"allowed_amounts": [325]}), encoding="utf-8")
            (root / "book.html").write_text(
                "<p>Email bookings@miamipapanoel.com</p>", encoding="utf-8")
            cfg = self.config(root, False, root / "log.jsonl", root / "evidence")
            failures = self.failures(MODULE.check_public_surfaces(cfg))
            self.assertTrue(any("bookings@miamipapanoel.com" in f.detail
                                for f in failures))

    def test_outreach_copy_blocks_unverified_insurance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tools/triage").mkdir(parents=True)
            (root / "tools/triage/pricing.json").write_text(
                json.dumps({"allowed_amounts": [550]}), encoding="utf-8")
            batch = root / "business/wave1-batch-01.md"
            batch.parent.mkdir(parents=True)
            batch.write_text(
                "> **Subject (EN):** One vendor, one W-9\n"
                "> Fully insured, $1M/$2M liability.\n", encoding="utf-8")
            failures = self.failures(MODULE.check_public_surfaces(
                self.config(root, False, root / "log.jsonl", root / "evidence")))
            self.assertTrue(any("wave1-batch-01.md" in f.detail and
                                "insurance language" in f.detail for f in failures))

    def test_strict_placeholders_block_final_but_not_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "docs").mkdir(parents=True)
            (root / "docs/OPN-SUBMISSION.md").write_text(
                "Launch date: [TO FILL]", encoding="utf-8")
            final_cfg = self.config(root, True, root / "log.jsonl", root / "e")
            self.assertTrue(self.failures(MODULE.check_placeholders(final_cfg)))
            pre_cfg = self.config(root, False, root / "log.jsonl", root / "e")
            self.assertFalse(self.failures(MODULE.check_placeholders(pre_cfg)))

    def test_git_privacy_flags_tracked_secret_files(self):
        import subprocess as sp
        if shutil.which("git") is None:
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sp.run(["git", "init", "-q"], cwd=temp, check=True)
            (root / ".env").write_text("SECRET=x", encoding="utf-8")
            allowed = root / "tools/triage/examples"
            allowed.mkdir(parents=True)
            (allowed / "inquiry-redacted.jsonl").write_text("{}", encoding="utf-8")
            sp.run(["git", "add", "-f", ".env",
                    "tools/triage/examples/inquiry-redacted.jsonl"],
                   cwd=temp, check=True)
            cfg = self.config(root, True, root / "log.jsonl", root / "e")
            failures = self.failures(MODULE.check_git_privacy(cfg))
            self.assertTrue(any(".env" in f.detail for f in failures))
            self.assertFalse(any("inquiry-redacted" in f.detail for f in failures))

    def test_complete_final_fixture_passes_in_isolation(self):
        """Exercise every final gate with synthetic data in a temp tree only."""
        source_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            for relative in MODULE.REQUIRED_DOCS + MODULE.REQUIRED_TRIAGE_FILES:
                source = source_root / relative
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            checkout = root / "checkout.html"
            checkout.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_root / "checkout.html", checkout)

            submission = root / "docs/OPN-SUBMISSION.md"
            submission_text = submission.read_text(encoding="utf-8")
            submission_text = submission_text.replace(
                "| **Launch date / status** | `[TO FILL]` — Launch date = the first real inquiry record",
                "| **Launch date / status** | `2026-08-01` — Launch date = the first real inquiry record")
            submission_text = submission_text.replace(
                "`[TO FILL]` — supported real inquiry outcome and counts.",
                "`1 synthetic inquiry handled` — supported real inquiry outcome and counts.")
            submission_text = submission_text.replace(
                "`[TO FILL]` — written verbatim only after a configured model",
                "`gpt-test-model` — written verbatim only after a configured model")
            submission_text = submission_text.replace(
                "| `[TO FILL]` | First valid genuine model-backed, reviewed-and-sent record",
                "| `2026-08-01` | First valid genuine model-backed, reviewed-and-sent record")
            submission_text = submission_text.replace(
                "| `[TO FILL + 15]` | Earliest elapsed-window review,",
                "| `2026-08-16` | Earliest elapsed-window review,")
            submission.write_text(submission_text, encoding="utf-8")

            deployment = root / "docs/production-deployment-record.md"
            deployment_text = deployment.read_text(encoding="utf-8")
            deployment_text = deployment_text.replace(
                "`[TO FILL on first real inquiry]`", "`2026-08-01`")
            deployment_text = deployment_text.replace(
                "`[TO FILL]`", "`gpt-test-model`", 1)
            deployment_text = deployment_text.replace(
                "`[TO FILL]`", "`1 inquiry handled; 3-minute median first response`", 1)
            deployment_text = deployment_text.replace("`[NOT YET MET]`", "`MET`")
            deployment.write_text(deployment_text, encoding="utf-8")

            gap = root / "docs/gap-report.md"
            gap.write_text(gap.read_text(encoding="utf-8").replace(
                "**NOT MET**", "**MET**"), encoding="utf-8")

            log = Path(temp) / "external-log" / "production-log.jsonl"
            self.write_log(log, [self.base_row()])
            evidence = Path(temp) / "external-evidence"
            artifact = evidence / "receipts" / "redacted-receipt.txt"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("synthetic redacted receipt", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            evidence.mkdir(parents=True, exist_ok=True)
            (evidence / "evidence-index.jsonl").write_text(json.dumps({
                "ref": "E-TEST",
                "type": "receipt",
                "date": "2025-12-24",
                "artifact": "receipts/redacted-receipt.txt",
                "sha256": digest,
                "redacted": True,
                "notes": "synthetic dated seasonal customer operation",
            }) + "\n", encoding="utf-8")

            cfg = self.config(root, True, log, evidence)
            findings = MODULE.run_validation(cfg)
            failures = self.failures(findings)
            self.assertEqual([], failures, "\n".join(f.detail for f in failures))


if __name__ == "__main__":
    unittest.main()
