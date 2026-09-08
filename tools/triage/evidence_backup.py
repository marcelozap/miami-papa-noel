#!/usr/bin/env python3
"""Operator-invoked backup and restore-check for the triage evidence log.

The production log is the ONLY record of genuine model-backed operation. It
lives on one machine, it can never be honestly recreated (backdating is
forbidden), and until now nothing copied it. This tool copies it and proves
the copy is readable and complete.

    python tools/triage/evidence_backup.py backup --dest D:\\private\\mpn-backups
    python tools/triage/evidence_backup.py restore-check --backup <file> --restore-dir <new dir>

Read-only on the source, always. The production log is opened for reading
and never written, moved, truncated, or overwritten - including by
restore-check, which restores into a separate new directory.

A backup on the same physical disk protects against accidental deletion and
bad edits. It does NOT protect against that disk failing. This tool can only
compare DRIVE LETTERS, which is a hint, not proof: partitions, virtual disks
and mapped network drives can share hardware. Confirm separate hardware
yourself. It creates no accounts and uploads nothing.

Standard library only. No network. Synthetic fixtures only in tests.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import triage  # noqa: E402  (log_dir/log_path - the ACTUAL configured location)

REPO_ROOT = Path(__file__).resolve().parents[2]
READ_CHUNK = 1024 * 1024


class BackupError(Exception):
    """Refusal. The message never contains a log line or customer text."""


def _private_dir(raw: str, label: str) -> Path:
    """An explicit absolute directory outside the repository."""
    if not raw or not str(raw).strip():
        raise BackupError("%s is required" % label)
    path = Path(os.path.expanduser(str(raw)))
    if not path.is_absolute():
        raise BackupError("%s must be an absolute path" % label)
    resolved = Path(os.path.realpath(path))
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        raise BackupError("%s must be outside the repository" % label)
    if str(resolved).lower() != str(path).lower():
        raise BackupError(
            "%s resolves elsewhere (link, junction, or short name); "
            "use the direct path" % label)
    return resolved


def _digest_and_scan(path: Path) -> dict:
    """Hash the file and validate every JSONL line. Never returns content."""
    sha = hashlib.sha256()
    lines = records = blank = 0
    malformed = []
    ids = set()
    with open(path, "rb") as raw:
        for chunk in iter(lambda: raw.read(READ_CHUNK), b""):
            sha.update(chunk)
    with open(path, "r", encoding="utf-8", errors="strict") as fh:
        for number, line in enumerate(fh, start=1):
            lines += 1
            if not line.strip():
                blank += 1
                continue
            try:
                row = json.loads(line)
            except ValueError:
                malformed.append(number)  # line NUMBER only, never the text
                continue
            records += 1
            if isinstance(row, dict) and row.get("inquiry_id"):
                ids.add(row["inquiry_id"])
    stat = path.stat()
    return {"sha256": sha.hexdigest(), "bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns, "lines": lines, "records": records,
            "blank_lines": blank, "malformed_lines": malformed,
            "unique_ids": len(ids), "ids": ids}


def _same_location(left: Path, right: Path) -> bool:
    """Compare two paths without requiring either to exist.

    realpath resolves links for paths that do exist; the case-insensitive
    normalised comparison catches the rest, including aliases of a
    directory that has not been created yet.
    """
    def norm(path: Path) -> str:
        return os.path.normcase(os.path.normpath(os.path.realpath(os.path.abspath(str(path)))))
    return norm(left) == norm(right)


def _refuse_live_locations(target_dir: Path, restored: Path) -> None:
    """A restore drill must never create or touch a configured log location.

    Checked even when the log or its directory does not exist yet: an
    absent live log is exactly the case where a careless drill would
    CREATE one, which would fabricate evidence state.
    """
    for real in (True, False):
        live = triage.log_path(real)
        label = "production" if real else "synthetic"
        if _same_location(restored, live):
            raise BackupError(
                "refusing to write the configured %s log location" % label)
        if _same_location(target_dir, live.parent):
            raise BackupError(
                "--restore-dir is the configured %s log directory; restore "
                "into a separate new directory" % label)


def _source_log(real: bool) -> Path:
    path = triage.log_path(real)
    if not path.is_file():
        raise BackupError(
            "no log at the configured location (%s); nothing to back up"
            % ("production" if real else "synthetic"))
    return path


def backup(dest: str, *, real: bool = True, now: dt.datetime | None = None) -> dict:
    """Copy the evidence log to a private destination and verify the copy.

    Refuses if the source changes while being read: a log written
    concurrently would produce a torn copy that silently loses records.
    """
    source = _source_log(real)
    destination = _private_dir(dest, "--dest")
    before = _digest_and_scan(source)
    if before["malformed_lines"]:
        raise BackupError(
            "source has %d malformed line(s) at %s - inspect the log before "
            "backing it up" % (len(before["malformed_lines"]),
                               before["malformed_lines"][:5]))
    moment = now or dt.datetime.now(dt.timezone.utc)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / ("%s-%s-%s.jsonl" % (
        source.stem, moment.strftime("%Y%m%dT%H%M%SZ"), before["sha256"][:12]))
    # Exclusive creation: checking exists() first would leave a window for
    # another writer to create the file and have it silently overwritten.
    # Only a file this run created is ever removed on failure.
    try:
        handle = os.open(str(target),
                         os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
    except FileExistsError:
        raise BackupError(
            "a file already exists at the backup name; not overwriting it") from None
    try:
        with os.fdopen(handle, "wb") as out, open(source, "rb") as raw:
            shutil.copyfileobj(raw, out, READ_CHUNK)   # source opened read-only
    except BaseException:
        target.unlink(missing_ok=True)       # ours: created by this run
        raise
    after = _digest_and_scan(source)
    if (after["sha256"], after["bytes"]) != (before["sha256"], before["bytes"]):
        target.unlink(missing_ok=True)
        raise BackupError(
            "the log changed while it was being copied; the partial backup was "
            "removed - stop other Santa commands and run this again")
    copied = _digest_and_scan(target)
    if copied["sha256"] != before["sha256"] or copied["records"] != before["records"]:
        target.unlink(missing_ok=True)
        raise BackupError("copy verification failed; the bad copy was removed")
    same_drive = os.path.splitdrive(str(target))[0].lower() == \
        os.path.splitdrive(str(source))[0].lower()
    return {"status": "ok", "backup": str(target), "sha256": copied["sha256"],
            "records": copied["records"], "bytes": copied["bytes"],
            "same_drive_letter_as_source": same_drive}


def restore_check(backup_path: str, restore_dir: str) -> dict:
    """Restore a backup into a NEW directory and prove it is readable.

    Never touches the production log: the source is only hashed for
    comparison when it still exists.
    """
    source_backup = Path(os.path.expanduser(str(backup_path)))
    if not source_backup.is_file():
        raise BackupError("backup file not found")
    target_dir = _private_dir(restore_dir, "--restore-dir")
    if target_dir.exists():
        raise BackupError("--restore-dir must be a new directory that does not exist yet")
    if not target_dir.parent.is_dir():
        raise BackupError("the parent of --restore-dir must already exist")
    backup_state = _digest_and_scan(source_backup)
    restored = target_dir / source_backup.name
    _refuse_live_locations(target_dir, restored)   # BEFORE any mkdir or write
    target_dir.mkdir(parents=False)
    shutil.copyfile(source_backup, restored)
    check = _digest_and_scan(restored)
    if check["sha256"] != backup_state["sha256"]:
        raise BackupError("restored copy does not match the backup")
    if check["malformed_lines"]:
        raise BackupError(
            "restored file has %d malformed line(s) at %s"
            % (len(check["malformed_lines"]), check["malformed_lines"][:5]))
    result = {"status": "ok", "restored": str(restored),
              "records": check["records"], "unique_ids": check["unique_ids"],
              "sha256": check["sha256"], "matches_live_log": None}
    live = triage.log_path(True)
    if live.is_file():
        live_state = _digest_and_scan(live)
        result["matches_live_log"] = check["sha256"] == live_state["sha256"]
        result["live_records"] = live_state["records"]
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     allow_abbrev=False)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("backup", allow_abbrev=False)
    b.add_argument("--dest", required=True,
                   help="private directory OUTSIDE this repository")
    b.add_argument("--synthetic", action="store_true",
                   help="back up the synthetic log instead (testing only)")
    r = sub.add_parser("restore-check", allow_abbrev=False)
    r.add_argument("--backup", required=True)
    r.add_argument("--restore-dir", required=True,
                   help="a NEW directory; never the live log location")
    args = parser.parse_args(argv)

    try:
        if args.command == "backup":
            result = backup(args.dest, real=not args.synthetic)
            print(json.dumps(result, indent=2))
            if result["same_drive_letter_as_source"]:
                print("\nNOTE: this backup shares a DRIVE LETTER with the log, so "
                      "it is very likely the same physical disk: that protects "
                      "against deletion and bad edits, not against the disk "
                      "failing. A different drive letter is NOT proof of "
                      "different hardware (partitions, virtual and network "
                      "drives can share a disk) - confirm that yourself, and "
                      "keep one copy on separate hardware.", file=sys.stderr)
        else:
            print(json.dumps(restore_check(args.backup, args.restore_dir), indent=2))
    except BackupError as error:
        print("REFUSED: %s" % error, file=sys.stderr)
        return 1
    except OSError:
        print("REFUSED: the file system refused the operation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
