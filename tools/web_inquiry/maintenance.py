"""Bounded, private SQLite maintenance without importing or starting the service.

Public APIs (Python 3.10+): check(database, *, timeout=30),
backup(database, backup_dir, *, timeout=30), and
restore_check(backup, restore_dir, *, timeout=30). They return JSON-compatible
dicts containing status, resolved paths, and inquiries/events/chat_caller_turns
row counts only.
Failures raise MaintenanceError with a fixed status, never a SQLite diagnostic.
The CLI exposes the same commands, with an optional --timeout in seconds.

backup_dir may be new or an existing private directory; each backup creates
backup-<random>/inquiries.sqlite3 inside it. restore_dir must not already exist.
Both destinations require an existing parent. Files are created exclusively,
with POSIX modes 0600 and directories 0700. Existing destination directories
must be private and owned by the current user; Windows ACLs are operator-owned.
Paths must be outside this repository and ancestors with .git markers, without
symlinks, Windows reparse points, traversal, or multiply linked source files.
Use trusted local ancestors: path checks cannot defeat a privileged process
concurrently replacing directories. Existing source permissions are not changed.

Sources use mode=ro (never immutable, so committed WAL writes are included).
A read transaction pins the snapshot through validation and Connection.backup;
rollback-journal writers may briefly wait, while WAL writers can keep committing.
Restoration uses that same online backup API, then compares schema, counts and
private in-memory row digests, including rowids. No actions or leases are replayed.
A backup made before the chat_caller_turns table existed (two tables:
inquiries, events) is still accepted read-only by check()/restore_check();
this module never writes to a backup or upgrades it in place. A restored
legacy copy gains the new table only the next time the server (App.__init__)
actually opens it - CREATE TABLE IF NOT EXISTS - before real use.
SQL progress, lock waits and backup retries share a finite deadline (max 300s).
An OS/storage stall or forced process termination still needs a supervisor
timeout and may leave partial artifacts. SQLite can maintain WAL shared memory
even for a read-only connection. Ordinary failures clean up only owned files
and empty owned directories, never recursively remove unexpected contents.
No retention/deletion schedule, off-host transfer, encryption, or disk monitoring
is provided; successful local checks do not establish disaster recovery readiness.
"""
from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import stat
import sys
from time import monotonic
import uuid


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIMEOUT = 30.0
MAX_TIMEOUT = 300.0
BACKUP_PAGES = 128
SIDECARS = ("-journal", "-wal", "-shm")
STATUSES = frozenset({
    "path-refused", "source-unavailable", "destination-exists",
    "destination-not-private", "schema-invalid", "integrity-failed",
    "comparison-failed", "timed-out", "invalid-timeout", "operation-failed",
    "cleanup-required", "invalid-arguments", "interrupted",
})
# name, declared type, NOT NULL, default, primary key position, hidden column.
SCHEMA = {
    "inquiries": (
        ("id", "TEXT", 0, None, 1, 0),
        ("request_key", "TEXT", 1, None, 0, 0),
        ("fingerprint", "TEXT", 1, None, 0, 0),
        ("payload", "TEXT", 1, None, 0, 0),
        ("status", "TEXT", 1, None, 0, 0),
        ("received_at", "TEXT", 1, None, 0, 0),
        ("record", "TEXT", 0, None, 0, 0),
        ("reviewed_language", "TEXT", 0, None, 0, 0),
    ),
    "events": (
        ("seq", "INTEGER", 0, None, 1, 0),
        ("inquiry_id", "TEXT", 1, None, 0, 0),
        ("at", "TEXT", 1, None, 0, 0),
        ("actor", "TEXT", 1, None, 0, 0),
        ("action", "TEXT", 1, None, 0, 0),
    ),
    "chat_caller_turns": (
        ("day", "TEXT", 1, None, 1, 0),
        ("caller", "TEXT", 1, None, 2, 0),
        ("turns", "INTEGER", 1, None, 0, 0),
    ),
}

# Pre-chat databases (backed up before chat_caller_turns existed) are still
# accepted for read-only check/restore - never created going forward, and
# never written to. A restored legacy copy gains the new table only the
# next time App.__init__ runs against it (CREATE TABLE IF NOT EXISTS);
# nothing here upgrades a backup file directly.
LEGACY_SCHEMA = {name: columns for name, columns in SCHEMA.items()
                 if name != "chat_caller_turns"}
SCHEMA_VARIANTS = (SCHEMA, LEGACY_SCHEMA)


class MaintenanceError(Exception):
    """A fixed status and, only when cleanup needs attention, an artifact path."""

    def __init__(self, status, path=None):
        self.status = status if status in STATUSES else "operation-failed"
        self.path = path
        super().__init__(self.status)


class _Deadline:
    def __init__(self, seconds):
        if (isinstance(seconds, bool) or not isinstance(seconds, (float, int))
                or not math.isfinite(seconds) or not 0 < seconds <= MAX_TIMEOUT):
            raise MaintenanceError("invalid-timeout")
        self.end = monotonic() + seconds

    def remaining(self):
        remaining = self.end - monotonic()
        if remaining <= 0:
            raise MaintenanceError("timed-out")
        return remaining

    def progress(self):
        return int(monotonic() >= self.end)


@contextmanager
def _errors():
    try:
        yield
    except MaintenanceError:
        raise
    except Exception:
        raise MaintenanceError("operation-failed") from None


def _private_path(value):
    path = Path(value).expanduser().absolute()
    if ".." in path.parts:
        raise MaintenanceError("path-refused")
    for part in (*reversed(path.parents), path):
        if part == ROOT or ROOT in part.parents or os.path.lexists(part / ".git"):
            raise MaintenanceError("path-refused")
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
            raise MaintenanceError("path-refused")
    resolved = path.resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise MaintenanceError("path-refused")
    return resolved


def _identity(path):
    info = path.lstat()
    return info.st_dev, info.st_ino


def _source_path(value):
    path = _private_path(value)
    try:
        info = path.lstat()
    except FileNotFoundError:
        raise MaintenanceError("source-unavailable") from None
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise MaintenanceError("path-refused")
    for suffix in SIDECARS:
        sidecar = _private_path(str(path) + suffix)
        if sidecar.exists():
            info = sidecar.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise MaintenanceError("path-refused")
    return path


def _private_directory(path):
    info = path.lstat()
    if (not stat.S_ISDIR(info.st_mode) or (os.name == "posix" and
            (info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) & 0o077))):
        raise MaintenanceError("destination-not-private")


def _configure(db, deadline, *, readonly):
    milliseconds = max(1, int(min(0.25, deadline.remaining()) * 1000))
    db.execute("PRAGMA busy_timeout=%d" % milliseconds)
    db.set_progress_handler(deadline.progress, 1000)
    db.execute("PRAGMA trusted_schema=OFF")
    db.execute("PRAGMA temp_store=MEMORY")
    if readonly:
        db.execute("PRAGMA query_only=ON")


@contextmanager
def _reader(path, deadline):
    identity = _identity(path)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True,
                                timeout=min(0.25, deadline.remaining()))) as db:
        if _source_path(path) != path or _identity(path) != identity:
            raise MaintenanceError("path-refused")
        _configure(db, deadline, readonly=True)
        db.execute("BEGIN")
        try:
            yield db
        except sqlite3.Error:
            if deadline.progress():
                raise MaintenanceError("timed-out") from None
            raise


def _inspect(db, deadline):
    deadline.remaining()
    if db.execute("PRAGMA integrity_check(1)").fetchone() != ("ok",):
        raise MaintenanceError("integrity-failed")
    schema = tuple(db.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_schema ORDER BY name"))
    objects = {(kind, name) for kind, name, _, _ in schema
               if not name.startswith("sqlite_") and kind != "index"}
    active = next((variant for variant in SCHEMA_VARIANTS
                  if objects == {("table", name) for name in variant}), None)
    if active is None:
        raise MaintenanceError("schema-invalid")
    for table, columns in active.items():
        actual = tuple(row[1:] for row in db.execute('PRAGMA table_xinfo("%s")' % table))
        if actual != columns:
            raise MaintenanceError("schema-invalid")
    unique = set()
    for row in db.execute('PRAGMA index_list("inquiries")'):
        if row[2] and not row[4]:
            columns = tuple(item[2] for item in db.execute(
                "SELECT * FROM pragma_index_info(?)", (row[1],)))
            unique.add(columns)
    if not {("id",), ("request_key",), ("fingerprint",)} <= unique:
        raise MaintenanceError("schema-invalid")
    counts, digests = {}, {}
    for table in active:
        count, digest = 0, hashlib.sha256()
        for row in db.execute('SELECT rowid,* FROM "%s" ORDER BY rowid' % table):
            deadline.remaining()
            # Tuple repr preserves SQLite scalar types, delimiters and BLOBs.
            encoded = repr(row).encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
            count += 1
        counts[table], digests[table] = count, digest.digest()
    deadline.remaining()
    return counts, digests, schema


class _Artifacts:
    """Track exact creations; cleanup never traverses or removes unknown files."""

    def __init__(self):
        self.directories = []
        self.file = None

    def directory(self, path):
        try:
            path.mkdir(mode=0o700)
        except FileExistsError:
            raise MaintenanceError("destination-exists") from None
        self.directories.append((path, _identity(path)))
        if os.name == "posix":
            path.chmod(0o700)

    def database(self, directory):
        path = _private_path(directory / "inquiries.sqlite3")
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL
                             | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            info = os.fstat(descriptor)
            self.file = (path, (info.st_dev, info.st_ino))
            if os.name == "posix":
                os.fchmod(descriptor, 0o600)
        finally:
            os.close(descriptor)
        return path

    def cleanup(self):
        pending = None
        for path, identity in ([self.file] if self.file else []) + self.directories[::-1]:
            try:
                if _private_path(path) != path or _identity(path) != identity:
                    pending = path
                    continue
                if self.file and path == self.file[0]:
                    path.unlink()
                else:
                    path.rmdir()
            except FileNotFoundError:
                pass
            except (OSError, MaintenanceError):
                pending = path
        if pending:
            raise MaintenanceError("cleanup-required", str(pending)) from None


def _online_backup(source, destination, deadline):
    def progress(status, remaining, total):
        deadline.remaining()

    source.backup(destination, pages=BACKUP_PAGES, progress=progress, sleep=0.05)
    deadline.remaining()


def _copy(source_value, directory_value, *, restore, timeout):
    artifacts = _Artifacts()
    with _errors():
        try:
            deadline = _Deadline(timeout)
            source_path = _source_path(source_value)
            directory = _private_path(directory_value)
            if restore and directory.exists():
                raise MaintenanceError("destination-exists")
            if not directory.parent.is_dir():
                raise MaintenanceError("path-refused")
            with _reader(source_path, deadline) as source:
                expected = _inspect(source, deadline)
                if not directory.exists():
                    artifacts.directory(directory)
                _private_directory(directory)
                if not restore:
                    directory = directory / ("backup-" + uuid.uuid4().hex)
                    artifacts.directory(directory)
                destination_path = artifacts.database(directory)
                with closing(sqlite3.connect(destination_path.as_uri() + "?mode=rw",
                                             uri=True, timeout=min(0.25, deadline.remaining()))) as destination:
                    _configure(destination, deadline, readonly=False)
                    _online_backup(source, destination, deadline)
                    # Produce one standalone file, even when the source uses WAL.
                    if destination.execute("PRAGMA journal_mode=DELETE").fetchone() != ("delete",):
                        raise MaintenanceError("operation-failed")
                # Reopen the actual on-disk restore, not the writer's page cache.
                with _reader(destination_path, deadline) as restored:
                    if _inspect(restored, deadline) != expected:
                        raise MaintenanceError("comparison-failed")
                deadline.remaining()
            return {"status": "ok", "backup" if restore else "database": str(source_path),
                    "database" if restore else "backup": str(destination_path),
                    "counts": expected[0]}
        except BaseException:
            artifacts.cleanup()
            raise


def check(database, *, timeout=DEFAULT_TIMEOUT):
    """Validate the current read snapshot without starting App or changing rows."""
    with _errors():
        deadline = _Deadline(timeout)
        path = _source_path(database)
        with _reader(path, deadline) as source:
            counts, _, _ = _inspect(source, deadline)
        return {"status": "ok", "database": str(path), "counts": counts}


def backup(database, backup_dir, *, timeout=DEFAULT_TIMEOUT):
    """Create and validate a unique private online backup; return its path/counts."""
    return _copy(database, backup_dir, restore=False, timeout=timeout)


def restore_check(backup, restore_dir, *, timeout=DEFAULT_TIMEOUT):
    """Restore into a strictly new directory and compare all queue rows/schema."""
    return _copy(backup, restore_dir, restore=True, timeout=timeout)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise MaintenanceError("invalid-arguments")


def main(argv=None):
    """Print one counts/paths/status JSON object; return 0, 2, or 130."""
    try:
        parser = _Parser(description="Private inquiry queue maintenance", allow_abbrev=False)
        commands = parser.add_subparsers(dest="command", required=True)
        for name in ("backup", "restore-check", "check"):
            command = commands.add_parser(name, allow_abbrev=False)
            command.add_argument("--backup" if name == "restore-check" else "--database", required=True)
            if name != "check":
                command.add_argument("--restore-dir" if name == "restore-check" else "--backup-dir", required=True)
            command.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
        args = parser.parse_args(argv)
        if args.command == "backup":
            result = backup(args.database, args.backup_dir, timeout=args.timeout)
        elif args.command == "restore-check":
            result = restore_check(args.backup, args.restore_dir, timeout=args.timeout)
        else:
            result = check(args.database, timeout=args.timeout)
        print(json.dumps(result))
        return 0
    except MaintenanceError as error:
        result = {"status": error.status}
        if error.status == "cleanup-required" and error.path:
            result["path"] = error.path
        print(json.dumps(result), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print(json.dumps({"status": "interrupted"}), file=sys.stderr)
        return 130
    except Exception:
        print(json.dumps({"status": "operation-failed"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
