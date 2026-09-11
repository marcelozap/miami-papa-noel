#!/usr/bin/env python3
"""Tests for the safe OPN packet builder."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_opn_packet.py")
SPEC = importlib.util.spec_from_file_location("build_opn_packet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PacketBuilderTests(unittest.TestCase):
    def test_working_tree_provenance_is_explicit(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            packet = MODULE.build_packet(root, Path(temp) / 'packet.zip', 'preflight',
                                         evidence_dir=Path(temp) / 'empty', validate=False)
            manifest = MODULE.verify_packet(packet)
            self.assertEqual(manifest['packet_schema'], 2)
            provenance = manifest['provenance']
            self.assertEqual(provenance['source_kind'], 'working_tree_snapshot')
            self.assertIs(provenance['source_commit_is_exact'], False)
            self.assertIsInstance(provenance['worktree_dirty'], bool)
            self.assertTrue(set(provenance['uncommitted_sources']) <= set(MODULE.PACKET_FILES))

    def test_clean_modified_and_untracked_source_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                subprocess.run(['git', *args], cwd=root, check=True, capture_output=True)
            git('init')
            (root / 'README.md').write_text('synthetic\n')
            git('add', 'README.md')
            git('-c', 'user.name=Synthetic Test', '-c', 'user.email=test@example.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '-m', 'synthetic fixture')
            commit = MODULE.git_commit(root)
            clean = MODULE.working_tree_provenance(root, commit, ['README.md'])
            self.assertFalse(clean['worktree_dirty'])
            self.assertEqual(clean['uncommitted_sources'], [])
            (root / 'README.md').write_text('changed synthetic\n')
            (root / 'note.md').write_text('synthetic only\n')
            dirty = MODULE.working_tree_provenance(root, commit, ['README.md', 'note.md'])
            self.assertTrue(dirty['worktree_dirty'])
            self.assertEqual(dirty['uncommitted_sources'], ['README.md', 'note.md'])

    def test_source_change_during_validation_refuses_packet(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'synthetic.txt'
            source.write_bytes(b'before')
            def validation(*args):
                source.write_bytes(b'after')
                return 'synthetic validation'
            output = Path(temp) / 'packet.zip'
            with patch.object(MODULE, 'source_files', return_value=[('README.md', source)]), \
                    patch.object(MODULE, 'run_validation', side_effect=validation):
                with self.assertRaisesRegex(ValueError, 'sources changed'):
                    MODULE.build_packet(root, output, 'preflight', evidence_dir=Path(temp) / 'empty')
            self.assertFalse(output.exists())

    def test_preflight_packet_contains_only_allowlisted_sources(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "packet.zip"
            evidence = Path(temp) / "empty-evidence"
            packet = MODULE.build_packet(root, output, "preflight",
                                         evidence_dir=evidence, validate=False)
            with zipfile.ZipFile(packet) as archive:
                names = set(archive.namelist())
                self.assertIn("PACKET-MANIFEST.json", names)
                self.assertIn("README.md", names)
                self.assertIn("business/AGENT-ROLES.md", names)
                self.assertIn("business/insurance-and-wave1-preflight.md", names)
                self.assertIn("docs/OPN-SUBMISSION.md", names)
                self.assertIn("docs/opn-resubmission-field-map.md", names)
                self.assertIn("docs/opn-form-answers.md", names)
                self.assertIn("docs/model-check-2026-09-10.md", names)
                self.assertIn("docs/day-one-operator-card.md", names)
                self.assertIn("scripts/test_build_opn_packet.py", names)
                self.assertIn("scripts/build_opn_packet.py", names)
                self.assertNotIn("lead-tracker.csv", names)
                self.assertNotIn("production-log.jsonl", names)
                manifest = json.loads(archive.read("PACKET-MANIFEST.json"))
                self.assertFalse(manifest["customer_evidence_included"])
                self.assertEqual(manifest["mode"], "preflight")
                self.assertEqual(len(manifest["files"]), len(MODULE.PACKET_FILES))

    def test_extracted_packet_can_check_status_without_source_checkout(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            packet = MODULE.build_packet(
                root, folder / "packet.zip", "preflight",
                evidence_dir=folder / "empty-evidence", validate=False)
            MODULE.verify_packet(packet)
            extracted = folder / "extracted"
            with zipfile.ZipFile(packet) as archive:
                archive.extractall(extracted)
            log_dir = folder / "unused-private-log"
            env = {**os.environ, "OPENAI_API_KEY": "", "MPN_MODEL": "",
                   "MPN_API_DAILY_CALL_CAP": "0", "MPN_CHAT_ALLOW_MODEL": "0",
                   "MPN_LOG_DIR": str(log_dir), "PYTHONPATH": ""}
            result = subprocess.run(
                [sys.executable, "-B", str(extracted / "tools/triage/triage.py"),
                 "--status"], cwd=extracted, env=env, capture_output=True,
                text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("NOT STARTED", result.stdout)
            self.assertFalse(log_dir.exists())
            verified = subprocess.run(
                [sys.executable, '-B', str(extracted / 'scripts/build_opn_packet.py'),
                 '--verify', str(packet)], cwd=extracted, env=env,
                capture_output=True, text=True, timeout=15)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertIn('working-tree snapshot', verified.stdout)

    def test_output_inside_repository_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            MODULE.build_packet(root, root / "packet.zip", "preflight", validate=False)

    def test_packet_manifest_and_membership_verify(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            packet = MODULE.build_packet(root, Path(temp) / "packet.zip", "preflight",
                                         evidence_dir=Path(temp) / "empty-evidence",
                                         validate=False)
            manifest = MODULE.verify_packet(packet)
            self.assertEqual(manifest["source_commit"], MODULE.git_commit(root))
            self.assertFalse(manifest["customer_evidence_included"])

    def test_packet_hash_tampering_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            packet = MODULE.build_packet(root, Path(temp) / "packet.zip", "preflight",
                                         evidence_dir=Path(temp) / "empty-evidence",
                                         validate=False)
            tampered = Path(temp) / "tampered.zip"
            with zipfile.ZipFile(packet) as source, zipfile.ZipFile(tampered, "w") as target:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "docs/OPN-SUBMISSION.md":
                        data += b"\n"
                    target.writestr(info, data)
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                MODULE.verify_packet(tampered)

    def test_packet_absolute_manifest_path_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            packet = MODULE.build_packet(root, Path(temp) / "packet.zip", "preflight",
                                         evidence_dir=Path(temp) / "empty-evidence",
                                         validate=False)
            rewritten = Path(temp) / "absolute-path.zip"
            with zipfile.ZipFile(packet) as source, zipfile.ZipFile(rewritten, "w") as target:
                manifest = json.loads(source.read("PACKET-MANIFEST.json"))
                manifest["files"][0]["path"] = "C:/outside.txt"
                for info in source.infolist():
                    data = (json.dumps(manifest, indent=2) + "\n").encode()
                    if info.filename != "PACKET-MANIFEST.json":
                        data = source.read(info.filename)
                    target.writestr(info, data)
            with self.assertRaisesRegex(ValueError, "unsafe file path"):
                MODULE.verify_packet(rewritten)


if __name__ == "__main__":
    unittest.main()
