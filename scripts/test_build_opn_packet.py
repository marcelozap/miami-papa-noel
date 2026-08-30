#!/usr/bin/env python3
"""Tests for the safe OPN packet builder."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_opn_packet.py")
SPEC = importlib.util.spec_from_file_location("build_opn_packet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PacketBuilderTests(unittest.TestCase):
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
                self.assertIn("docs/OPN-SUBMISSION.md", names)
                self.assertIn("scripts/test_build_opn_packet.py", names)
                self.assertNotIn("lead-tracker.csv", names)
                self.assertNotIn("production-log.jsonl", names)
                manifest = json.loads(archive.read("PACKET-MANIFEST.json"))
                self.assertFalse(manifest["customer_evidence_included"])
                self.assertEqual(manifest["mode"], "preflight")
                self.assertEqual(len(manifest["files"]), len(MODULE.PACKET_FILES))

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


if __name__ == "__main__":
    unittest.main()
