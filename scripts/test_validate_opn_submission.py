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
                "`[TO FILL]` — recorded automatically as the first `--real` log line.",
                "`2026-08-01` — recorded automatically as the first `--real` log line.")
            submission_text = submission_text.replace(
                "`[TO FILL]` — derives from the log:",
                "`1 inquiry handled; median first-response time 3 minutes` — derives from the log:")
            submission_text = submission_text.replace(
                "`[TO FILL]` — written verbatim only after a configured model",
                "`gpt-test-model` — written verbatim only after a configured model")
            submission_text = submission_text.replace(
                "| `[TO FILL]` | First real customer inquiry",
                "| `2026-08-01` | First real customer inquiry")
            submission_text = submission_text.replace(
                "| `[TO FILL + 15]` | 15 days continuous operation reached",
                "| `2026-08-16` | 15 days continuous operation reached")
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
