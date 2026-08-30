#!/usr/bin/env python3
"""Tests for the external evidence index helper."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("evidence_index.py")
SPEC = importlib.util.spec_from_file_location("evidence_index", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EvidenceIndexTests(unittest.TestCase):
    def test_indexes_redacted_file_with_matching_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "receipts" / "receipt.pdf"
            artifact.parent.mkdir()
            artifact.write_bytes(b"redacted receipt")
            index, entry = MODULE.index_artifact(
                root, "receipts/receipt.pdf", "E-01", "receipt",
                "2025-12-24", "dated seasonal customer operation", True,
            )
            self.assertEqual(index.name, MODULE.INDEX_NAME)
            self.assertEqual(entry["sha256"], hashlib.sha256(artifact.read_bytes()).hexdigest())
            self.assertTrue(entry["redacted"])
            self.assertEqual(json.loads(index.read_text(encoding="utf-8"))["ref"], "E-01")

    def test_requires_redaction_and_rejects_duplicate_ref(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "receipt.pdf"
            artifact.write_bytes(b"redacted")
            with self.assertRaisesRegex(ValueError, "redacted"):
                MODULE.index_artifact(root, "receipt.pdf", "E-01", "receipt",
                                      "2025-12-24", "dated operation", False)
            MODULE.index_artifact(root, "receipt.pdf", "E-01", "receipt",
                                  "2025-12-24", "dated operation", True)
            (root / "other.pdf").write_bytes(b"another redacted file")
            with self.assertRaisesRegex(ValueError, "ref already exists"):
                MODULE.index_artifact(root, "other.pdf", "E-01", "statement",
                                      "2025-12-25", "another operation", True)
            with self.assertRaisesRegex(ValueError, "already indexed"):
                MODULE.index_artifact(root, "receipt.pdf", "E-02", "statement",
                                      "2025-12-25", "another operation", True)

    def test_rejects_private_notes_and_path_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "receipt.pdf").write_bytes(b"redacted")
            with self.assertRaisesRegex(ValueError, "email"):
                MODULE.index_artifact(root, "receipt.pdf", "E-01", "receipt",
                                      "2025-12-24", "contact someone@example.com", True)
            with self.assertRaisesRegex(ValueError, "relative path"):
                MODULE.index_artifact(root, "../receipt.pdf", "E-01", "receipt",
                                      "2025-12-24", "dated operation", True)


if __name__ == "__main__":
    unittest.main()
