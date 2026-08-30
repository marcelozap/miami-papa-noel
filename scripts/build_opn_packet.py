#!/usr/bin/env python3
"""Build a safe, reproducible OpenAI Partner Network submission ZIP.

The source allowlist is deliberately explicit. Customer evidence remains in
the external evidence folder; only its privacy-checked index can be included.
Preflight builds a draft packet. Final mode refuses to build until the local
validator passes every production and evidence requirement.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = "opn-submission-packet.zip"
PACKET_FILES = (
    "docs/OPN-SUBMISSION.md",
    "docs/production-deployment-record.md",
    "docs/agent-workflow-architecture.md",
    "docs/release-monitoring-and-failure-handling.md",
    "docs/evidence-index.md",
    "docs/gap-report.md",
    "docs/operator-attestation-2025-season.md",
    "docs/evidence-intake.md",
    "docs/evidence-manifest-schema.md",
    "docs/OPN-VALIDATION.md",
    "docs/release-checklist.md",
    "docs/15-day-evidence-checklist.md",
    "tools/triage/triage.py",
    "tools/triage/validators.py",
    "tools/triage/pricing.json",
    "tools/triage/README.md",
    "tools/triage/log-schema.md",
    "tools/triage/test_triage.py",
    "tools/triage/examples/inquiry-redacted.jsonl",
    "scripts/validate_slot_confirmations.py",
    "scripts/validate_opn_submission.py",
    "scripts/evidence_index.py",
    "scripts/test_validate_opn_submission.py",
    "scripts/test_evidence_index.py",
    "scripts/test_build_opn_packet.py",
)


def default_evidence_dir() -> Path:
    override = os.environ.get("MPN_EVIDENCE_DIR")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "evidence"


def default_log_dir() -> Path:
    override = os.environ.get("MPN_LOG_DIR")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "triage"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(root: Path) -> list[tuple[str, Path]]:
    missing = [relative for relative in PACKET_FILES if not (root / relative).is_file()]
    if missing:
        raise ValueError("missing packet source(s): " + ", ".join(missing))
    return [(relative, root / relative) for relative in PACKET_FILES]


def git_commit(root: Path) -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"could not resolve source commit: {exc}") from exc
    return result.stdout.strip()


def run_validation(root: Path, mode: str, log_dir: Path, evidence_dir: Path) -> str:
    command = [sys.executable, str(root / "scripts/validate_opn_submission.py"),
               f"--{mode}", "--repo-root", str(root),
               "--log-dir", str(log_dir), "--evidence-dir", str(evidence_dir)]
    completed = subprocess.run(command, cwd=root, capture_output=True, text=True)
    output = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode:
        raise ValueError(f"{mode} validation failed; packet not built\n{output.strip()}")
    return output.strip()


def safe_external_index(evidence_dir: Path) -> Path | None:
    index = evidence_dir / "evidence-index.jsonl"
    if not index.is_file():
        return None
    if not any(line.strip() and not line.lstrip().startswith("#")
               for line in index.read_text(encoding="utf-8").splitlines()):
        return None
    return index


def build_packet(root: Path, output: Path, mode: str, log_dir: Path | None = None,
                 evidence_dir: Path | None = None, validate: bool = True) -> Path:
    root = root.resolve()
    output = output.expanduser().resolve()
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("output must be outside the repository")

    log_dir = log_dir or default_log_dir()
    evidence_dir = evidence_dir or default_evidence_dir()
    validation_output = "validation skipped by library caller"
    if validate:
        validation_output = run_validation(root, mode, log_dir, evidence_dir)
    files = source_files(root)
    external_index = safe_external_index(evidence_dir)
    if external_index:
        files.append(("external-evidence/evidence-index.jsonl", external_index))

    manifest = {
        "packet_schema": 1,
        "mode": mode,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_commit": git_commit(root),
        "customer_evidence_included": False,
        "validation": "passed" if validate else "skipped",
        "files": [{"path": relative, "sha256": sha256(path)} for relative, path in files],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        temp_zip = Path(temp) / "packet.zip"
        with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for relative, path in files:
                archive.write(path, arcname=relative)
            archive.writestr("PACKET-MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
            archive.writestr("VALIDATION-OUTPUT.txt", validation_output + "\n")
        temp_zip.replace(output)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true", help="build a validated draft packet")
    mode.add_argument("--final", action="store_true", help="build only after final validation passes")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--output", help="ZIP path outside the repository")
    parser.add_argument("--log-dir")
    parser.add_argument("--evidence-dir")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).expanduser().resolve()
    output = Path(args.output).expanduser() if args.output else (
        Path(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"))
        / "MiamiPapaNoel" / "packets" / DEFAULT_OUTPUT
    )
    try:
        packet = build_packet(
            root, output, "final" if args.final else "preflight",
            log_dir=Path(args.log_dir).expanduser() if args.log_dir else None,
            evidence_dir=Path(args.evidence_dir).expanduser() if args.evidence_dir else None,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"packet: {packet}")
    print("customer evidence included: no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
