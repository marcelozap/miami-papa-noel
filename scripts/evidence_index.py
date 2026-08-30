#!/usr/bin/env python3
"""Index one redacted external evidence file without copying it into Git.

Example (PowerShell):
    python scripts\evidence_index.py --file receipts\receipt-01.pdf `
        --ref E-01 --type receipt --date 2025-12-24 `
        --notes "dated seasonal customer operation" --redacted

The evidence folder defaults to %LOCALAPPDATA%\MiamiPapaNoel\evidence and can
be overridden with MPN_EVIDENCE_DIR or --evidence-dir. The command is local,
stdlib-only, and never reads the artifact into the repository or sends it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path

INDEX_NAME = "evidence-index.jsonl"
EVIDENCE_TYPES = {
    "receipt", "booking_record", "message_thread", "screenshot",
    "statement", "calendar", "zelle_history",
}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-])\d{3}[\s.-]\d{4}\b")


def default_evidence_dir() -> Path:
    override = os.environ.get("MPN_EVIDENCE_DIR")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "evidence"


def safe_artifact_path(root: Path, value: str) -> tuple[Path, str]:
    relative = Path(value)
    if relative.is_absolute() or not value.strip() or ".." in relative.parts:
        raise ValueError("--file must be a non-empty relative path inside the evidence folder")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("--file escapes the evidence folder") from exc
    return candidate, relative.as_posix()


def existing_entries(index: Path) -> list[dict]:
    if not index.exists():
        return []
    entries = []
    for number, line in enumerate(index.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"existing index line {number} is not valid JSON: {exc.msg}") from exc
        if not isinstance(entry, dict):
            raise ValueError(f"existing index line {number} is not an object")
        entries.append(entry)
    return entries


def index_artifact(evidence_dir: Path, artifact: str, ref: str, artifact_type: str,
                   date: str, notes: str, redacted: bool) -> tuple[Path, dict]:
    if not redacted:
        raise ValueError("--redacted is required; redact the artifact before indexing it")
    if not ref.strip():
        raise ValueError("--ref must be non-empty")
    if artifact_type not in EVIDENCE_TYPES:
        raise ValueError("--type must be one of: " + ", ".join(sorted(EVIDENCE_TYPES)))
    try:
        artifact_date = dt.date.fromisoformat(date)
    except ValueError as exc:
        raise ValueError("--date must be an ISO date YYYY-MM-DD") from exc
    if artifact_date > dt.date.today():
        raise ValueError("--date cannot be in the future")
    if not notes.strip():
        raise ValueError("--notes must describe what the redacted artifact establishes")
    if EMAIL_RE.search(notes) or PHONE_RE.search(notes):
        raise ValueError("--notes may not contain email or phone data")

    evidence_dir.mkdir(parents=True, exist_ok=True)
    path, relative = safe_artifact_path(evidence_dir, artifact)
    if not path.is_file():
        raise ValueError(f"artifact file does not exist: {relative}")
    index = evidence_dir / INDEX_NAME
    entries = existing_entries(index)
    if any(str(entry.get("ref")) == ref for entry in entries):
        raise ValueError(f"ref already exists: {ref}")
    if any(str(entry.get("artifact")) == relative for entry in entries):
        raise ValueError(f"artifact is already indexed: {relative}")

    entry = {
        "ref": ref,
        "type": artifact_type,
        "date": date,
        "artifact": relative,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "redacted": True,
        "notes": notes.strip(),
    }
    with index.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return index, entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", required=True, help="relative redacted artifact path")
    parser.add_argument("--ref", required=True, help="unique reference, such as E-01")
    parser.add_argument("--type", required=True, choices=sorted(EVIDENCE_TYPES))
    parser.add_argument("--date", required=True, help="actual artifact date, YYYY-MM-DD")
    parser.add_argument("--notes", required=True, help="non-personal description of what it proves")
    parser.add_argument("--redacted", action="store_true", help="confirm the artifact was redacted")
    parser.add_argument("--evidence-dir", help="external evidence folder")
    args = parser.parse_args(argv)
    root = Path(args.evidence_dir).expanduser() if args.evidence_dir else default_evidence_dir()
    try:
        index, entry = index_artifact(root, args.file, args.ref, args.type,
                                      args.date, args.notes, args.redacted)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print("indexed %s -> %s" % (entry["ref"], index))
    print("sha256: %s" % entry["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
