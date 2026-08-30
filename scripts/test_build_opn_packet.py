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


if __name__ == "__main__":
    unittest.main()
