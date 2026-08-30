#!/usr/bin/env python3
"""Focused tests for the local OpenAI Partner Network submission validator."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
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
            self.write_log(log, [self.base_row(received_at=f"{old_date}T10:00:00-04:00")])
            cfg = self.config(root, True, log, evidence)
            findings, earliest, models, approved, model_backed = MODULE.check_production_log(cfg)
            findings += MODULE.check_duration(cfg, earliest, approved, model_backed)
            self.assertFalse(self.failures(findings))

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
        import shutil
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


if __name__ == "__main__":
    unittest.main()
