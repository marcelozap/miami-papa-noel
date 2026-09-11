"""Synthetic maintenance checks: no App, credentials, services, or network."""
import ast
from contextlib import closing
import json
import os
from pathlib import Path
import socket
import sqlite3
import stat
import subprocess
import sys
import time

import pytest

from tools.web_inquiry import maintenance as m


PRIVATE = "synthetic@example.invalid PRIVATE-BODY PRIVATE-DRAFT PRIVATE-TOKEN"


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    assert m.ROOT not in tmp_path.resolve().parents, "Synthetic state must stay outside the repository"
    for key in tuple(os.environ):
        if key.startswith(("OPENAI_", "MPN_")):
            monkeypatch.delenv(key)

    def no_network(*args, **kwargs):
        pytest.fail("Maintenance must not use a network or start a service")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)


@pytest.fixture
def database(tmp_path):
    # Read only Python source to keep the fixture aligned with the service schema.
    tree = ast.parse(Path(m.__file__).with_name("server.py").read_text(encoding="utf-8"))
    statements = [node.value for node in ast.walk(tree)
                  if isinstance(node, ast.Constant) and isinstance(node.value, str)
                  and node.value.startswith("CREATE TABLE IF NOT EXISTS ")]
    assert len(statements) == 3
    path = tmp_path / "source.sqlite3"
    with closing(sqlite3.connect(path)) as db:
        for statement in statements:
            db.execute(statement)
        add_row(db, 1, "drafting")
        add_row(db, 2, "approved")
        db.commit()
    return path


@pytest.fixture
def legacy_database(tmp_path):
    """A pre-chat backup: inquiries + events only, no chat_caller_turns.

    Reproduces Codex's finding: maintenance.check/restore_check must still
    accept this exact known legacy schema read-only, not just the current
    three-table one.
    """
    tree = ast.parse(Path(m.__file__).with_name("server.py").read_text(encoding="utf-8"))
    statements = [node.value for node in ast.walk(tree)
                  if isinstance(node, ast.Constant) and isinstance(node.value, str)
                  and node.value.startswith("CREATE TABLE IF NOT EXISTS ")
                  and "chat_caller_turns" not in node.value]
    assert len(statements) == 2
    path = tmp_path / "legacy-source.sqlite3"
    with closing(sqlite3.connect(path)) as db:
        for statement in statements:
            db.execute(statement)
        add_row(db, 1, "drafting")
        add_row(db, 2, "approved")
        db.commit()
    return path


def add_row(db, number, status="queued", payload=PRIVATE):
    db.execute("INSERT INTO inquiries VALUES(?,?,?,?,?,?,?,?)", (
        "synthetic-%d" % number, "key-%d" % number, "fingerprint-%d" % number,
        payload, status, "2026-09-04T00:00:00Z", PRIVATE, "en"))
    db.execute("INSERT INTO events VALUES(?,?,?,?,?)", (
        number, "synthetic-%d" % number, "2026-09-04T00:00:00Z", PRIVATE, status))


def contents(path):
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        return {table: db.execute('SELECT rowid,* FROM "%s" ORDER BY rowid' % table).fetchall()
                for table in ("inquiries", "events")}


def assert_refused(call, status=None):
    with pytest.raises(m.MaintenanceError) as caught:
        call()
    assert PRIVATE not in str(caught.value)
    if status:
        assert caught.value.status == status


def test_backup_restore_round_trip_keeps_drafting_and_approved(database, tmp_path):
    original = contents(database)
    first = m.backup(database, tmp_path / "backups")
    second = m.backup(database, tmp_path / "backups")
    assert first["backup"] != second["backup"]
    assert first["counts"] == {"inquiries": 2, "events": 2, "chat_caller_turns": 0}
    saved = Path(first["backup"])
    result = m.restore_check(saved, tmp_path / "restore")
    restored = Path(result["database"])
    assert contents(restored) == contents(saved) == contents(database) == original
    assert result["counts"] == first["counts"]
    assert list(restored.parent.iterdir()) == [restored]
    assert not (tmp_path / "server.lock").exists()
    assert not (restored.parent / "server.lock").exists()


def test_legacy_two_table_backup_is_accepted_read_only(legacy_database):
    result = m.check(legacy_database)
    assert result["status"] == "ok"
    assert result["counts"] == {"inquiries": 2, "events": 2}


def test_legacy_backup_and_restore_round_trip_preserves_populated_rows(legacy_database, tmp_path):
    original = contents(legacy_database)
    first = m.backup(legacy_database, tmp_path / "backups")
    assert first["counts"] == {"inquiries": 2, "events": 2}
    restored = m.restore_check(Path(first["backup"]), tmp_path / "restore")
    assert restored["counts"] == first["counts"]
    assert contents(Path(restored["database"])) == contents(Path(first["backup"])) == original


def test_a_schema_that_matches_neither_known_variant_is_refused(tmp_path):
    """Not just missing a table - an unrecognized *combination* must refuse too."""
    path = tmp_path / "unrecognized.sqlite3"
    with closing(sqlite3.connect(path)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS inquiries (
            id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL,
            fingerprint TEXT UNIQUE NOT NULL, payload TEXT NOT NULL,
            status TEXT NOT NULL, received_at TEXT NOT NULL,
            record TEXT, reviewed_language TEXT)""")
        db.execute("""CREATE TABLE IF NOT EXISTS chat_caller_turns (
            day TEXT NOT NULL, caller TEXT NOT NULL, turns INTEGER NOT NULL,
            PRIMARY KEY (day, caller))""")
        db.commit()
    assert_refused(lambda: m.check(path), "schema-invalid")


def test_wal_committed_writes_during_backup_share_one_snapshot(database, tmp_path, monkeypatch):
    original_backup = m._online_backup
    with closing(sqlite3.connect(database)) as writer:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone() == ("wal",)
        add_row(writer, 3, payload=PRIVATE * 500)
        writer.commit()
        initial = contents(database)
        committed = []

        def during_backup(source, destination, deadline):
            def progress(status, remaining, total):
                deadline.remaining()
                if not committed:
                    assert remaining > 0
                    add_row(writer, 4)
                    writer.commit()
                    committed.append(True)
            source.backup(destination, pages=1, progress=progress, sleep=0.01)

        monkeypatch.setattr(m, "_online_backup", during_backup)
        result = m.backup(database, tmp_path / "backups")
        assert committed
        assert result["counts"] == {"inquiries": 3, "events": 3, "chat_caller_turns": 0}
        assert contents(Path(result["backup"])) == initial
        assert len(contents(database)["inquiries"]) == 4
        monkeypatch.setattr(m, "_online_backup", original_backup)
        restored = m.restore_check(result["backup"], tmp_path / "restore")
        assert contents(Path(restored["database"])) == initial


def test_uncommitted_rows_are_excluded(database, tmp_path):
    with closing(sqlite3.connect(database)) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
        add_row(writer, 3)
        result = m.backup(database, tmp_path / "backups")
        writer.rollback()
    assert result["counts"] == {"inquiries": 2, "events": 2, "chat_caller_turns": 0}


@pytest.mark.parametrize("operation", ["check", "backup", "restore"])
def test_sources_are_readonly_and_never_use_creation_mode(database, tmp_path, monkeypatch, operation):
    before = database.read_bytes()
    connect = sqlite3.connect
    opened = []

    def readonly(*args, **kwargs):
        assert kwargs["uri"] is True
        db = connect(*args, **kwargs)
        if args[0].endswith("?mode=ro"):
            with pytest.raises(sqlite3.OperationalError):
                db.execute("DELETE FROM inquiries")
            db.rollback()
        else:
            assert args[0].endswith("?mode=rw")
            assert not args[0].startswith(database.as_uri() + "?")
        opened.append(args[0])
        return db

    monkeypatch.setattr(m.sqlite3, "connect", readonly)
    call = {"check": lambda: m.check(database),
            "backup": lambda: m.backup(database, tmp_path / "backups"),
            "restore": lambda: m.restore_check(database, tmp_path / "restore")}[operation]
    assert call()["counts"] == {"inquiries": 2, "events": 2, "chat_caller_turns": 0}
    assert len(opened) == (1 if operation == "check" else 3)
    assert opened[0] == database.as_uri() + "?mode=ro"
    assert database.read_bytes() == before


def test_empty_queue_and_uri_escaped_paths(database, tmp_path):
    with closing(sqlite3.connect(database)) as db:
        db.execute("DELETE FROM inquiries")
        db.execute("DELETE FROM events")
        db.commit()
    renamed = database.with_name("synthetic # 100%.sqlite3")
    database.rename(renamed)
    result = m.backup(renamed, tmp_path / "private # 100%")
    assert result["counts"] == {"inquiries": 0, "events": 0, "chat_caller_turns": 0}
    restored = m.restore_check(result["backup"], tmp_path / "restore # 100%")
    assert contents(Path(restored["database"])) == contents(renamed)


def test_rowid_gaps_nulls_and_blob_values_are_preserved(database, tmp_path):
    with closing(sqlite3.connect(database)) as db:
        db.execute("UPDATE inquiries SET rowid=99, record=NULL, reviewed_language=NULL WHERE rowid=1")
        db.execute("UPDATE inquiries SET payload=? WHERE rowid=2", (b"synthetic\x00blob",))
        db.commit()
    result = m.restore_check(database, tmp_path / "restore")
    assert contents(Path(result["database"])) == contents(database)


@pytest.mark.parametrize("operation", ["check", "backup", "restore"])
@pytest.mark.parametrize("invalid", ["missing", "empty", "corrupt", "wrong-schema"])
def test_bad_sources_never_create_destinations(tmp_path, operation, invalid):
    source = tmp_path / "bad.sqlite3"
    if invalid == "empty":
        source.touch()
    elif invalid == "corrupt":
        source.write_bytes(b"not-a-database " + PRIVATE.encode())
    elif invalid == "wrong-schema":
        with closing(sqlite3.connect(source)) as db:
            db.execute("CREATE TABLE unrelated(secret TEXT)")
    dest = tmp_path / "destination"
    call = {"check": lambda: m.check(source),
            "backup": lambda: m.backup(source, dest),
            "restore": lambda: m.restore_check(source, dest)}[operation]
    assert_refused(call)
    assert not dest.exists()
    if invalid == "missing":
        assert not source.exists()


@pytest.mark.parametrize("change", [
    "ALTER TABLE inquiries ADD COLUMN unexpected TEXT",
    "ALTER TABLE events RENAME COLUMN actor TO unexpected",
    "DROP TABLE events",
    "CREATE VIEW private_view AS SELECT payload FROM inquiries",
    "CREATE TRIGGER unexpected AFTER INSERT ON events BEGIN DELETE FROM inquiries; END",
])
def test_schema_drift_is_refused(database, change):
    with closing(sqlite3.connect(database)) as db:
        db.execute(change)
    assert_refused(lambda: m.check(database), "schema-invalid")


def test_missing_unique_constraints_refused(database):
    with closing(sqlite3.connect(database)) as db:
        db.execute("DROP TABLE inquiries")
        db.execute("""CREATE TABLE inquiries (
            id TEXT PRIMARY KEY, request_key TEXT NOT NULL,
            fingerprint TEXT NOT NULL, payload TEXT NOT NULL,
            status TEXT NOT NULL, received_at TEXT NOT NULL,
            record TEXT, reviewed_language TEXT)""")
    assert_refused(lambda: m.check(database), "schema-invalid")


@pytest.mark.parametrize("existing", ["empty-dir", "populated-dir", "file"])
def test_restore_refuses_all_existing_targets(database, tmp_path, existing):
    dest = tmp_path / "restore"
    if existing == "file":
        dest.write_text(PRIVATE)
    else:
        dest.mkdir()
        if existing == "populated-dir":
            (dest / "keep.txt").write_text(PRIVATE)
    before = contents(database)
    assert_refused(lambda: m.restore_check(database, dest), "destination-exists")
    assert dest.exists()
    if existing != "empty-dir":
        assert (dest if dest.is_file() else dest / "keep.txt").read_text() == PRIVATE
    assert contents(database) == before


def test_backup_directory_existing_files_are_preserved(database, tmp_path):
    directory = tmp_path / "backups"
    directory.mkdir(mode=0o700)
    existing = directory / "inquiries.sqlite3"
    existing.write_text(PRIVATE)
    result = m.backup(database, directory)
    assert existing.read_text() == PRIVATE
    assert Path(result["backup"]) != existing


def test_exclusive_random_directory_collision_is_refused(database, tmp_path, monkeypatch):
    directory = tmp_path / "backups"
    directory.mkdir(mode=0o700)
    collision = directory / "backup-fixed"
    collision.mkdir()
    sentinel = collision / "inquiries.sqlite3"
    sentinel.write_text(PRIVATE)
    monkeypatch.setattr(m.uuid, "uuid4", lambda: type("Fixed", (), {"hex": "fixed"})())
    assert_refused(lambda: m.backup(database, directory), "destination-exists")
    assert sentinel.read_text() == PRIVATE


@pytest.mark.parametrize("operation", ["source", "backup", "restore"])
@pytest.mark.parametrize("other_repo", [False, True])
def test_repository_paths_are_refused(database, tmp_path, monkeypatch, operation, other_repo):
    repo = tmp_path / "synthetic-repo"
    repo.mkdir()
    if other_repo:
        (repo / ".git").write_text("gitdir: synthetic-only")
    else:
        monkeypatch.setattr(m, "ROOT", repo)
    if operation == "source":
        source = repo / "source.sqlite3"
        source.write_bytes(database.read_bytes())
        call = lambda: m.check(source)
    elif operation == "backup":
        call = lambda: m.backup(database, repo / "backup")
    else:
        call = lambda: m.restore_check(database, repo / "restore")
    assert_refused(call, "path-refused")
    assert not (repo / "backup").exists() and not (repo / "restore").exists()


def symlink(link, target, *, directory=False):
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError:
        if directory and os.name == "nt":
            import _winapi
            try:
                _winapi.CreateJunction(str(target), str(link))
                return
            except OSError:
                pass
        pytest.skip("Creating this symlink requires OS permission")


@pytest.mark.parametrize("kind", ["source", "parent", "backup", "restore", "dangling", "wal"])
def test_symlinks_are_refused(database, tmp_path, kind):
    link = tmp_path / "link"
    if kind == "source":
        symlink(link, database)
        call = lambda: m.check(link)
    elif kind == "wal":
        symlink(Path(str(database) + "-wal"), tmp_path / "missing")
        call = lambda: m.check(database)
    elif kind == "dangling":
        symlink(link, tmp_path / "missing", directory=True)
        call = lambda: m.restore_check(database, link)
    else:
        target = tmp_path / "private"
        target.mkdir(mode=0o700)
        symlink(link, target, directory=True)
        if kind == "parent":
            (target / "db.sqlite3").write_bytes(database.read_bytes())
            call = lambda: m.check(link / "db.sqlite3")
        elif kind == "backup":
            call = lambda: m.backup(database, link)
        else:
            call = lambda: m.restore_check(database, link / "new")
    assert_refused(call, "path-refused")


@pytest.mark.parametrize("direction", ["into-repo", "out-of-repo"])
def test_repository_directory_links_are_refused(database, tmp_path, monkeypatch, direction):
    repo = tmp_path / "repo"
    repo.mkdir()
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    monkeypatch.setattr(m, "ROOT", repo)
    link, target = (private / "link", repo) if direction == "into-repo" else (repo / "link", private)
    symlink(link, target, directory=True)
    assert_refused(lambda: m.backup(database, link / "backups"), "path-refused")
    assert not (target / "backups").exists()


def test_hardlinked_sources_are_refused(database, tmp_path):
    alias = tmp_path / "alias.sqlite3"
    os.link(database, alias)
    assert_refused(lambda: m.check(alias), "path-refused")


def test_parent_traversal_is_refused(database, tmp_path):
    assert_refused(lambda: m.check(tmp_path / "unused" / ".." / database.name), "path-refused")


@pytest.mark.parametrize("restore", [False, True])
@pytest.mark.parametrize("phase", ["copy", "comparison", "row-count", "interrupt"])
def test_failure_cleans_only_new_artifacts(database, tmp_path, monkeypatch, restore, phase):
    dest = tmp_path / "destination"
    original = m._online_backup

    def fail(source, destination, deadline):
        original(source, destination, deadline)
        if phase == "comparison":
            destination.execute("UPDATE inquiries SET payload=? WHERE id='synthetic-1'", ("changed",))
            destination.commit()
        elif phase == "row-count":
            destination.execute("DELETE FROM events WHERE seq=1")
            destination.commit()
        elif phase == "interrupt":
            raise KeyboardInterrupt()
        else:
            raise sqlite3.OperationalError(PRIVATE)

    monkeypatch.setattr(m, "_online_backup", fail)
    call = lambda: (m.restore_check if restore else m.backup)(database, dest)
    if phase == "interrupt":
        with pytest.raises(KeyboardInterrupt):
            call()
    else:
        assert_refused(call, "comparison-failed" if phase in ("comparison", "row-count") else "operation-failed")
    assert not dest.exists()
    assert m.check(database)["counts"] == {"inquiries": 2, "events": 2, "chat_caller_turns": 0}


def test_failure_preserves_preexisting_backup_directory(database, tmp_path, monkeypatch):
    directory = tmp_path / "backups"
    directory.mkdir(mode=0o700)
    sentinel = directory / "keep.txt"
    sentinel.write_text(PRIVATE)

    def fail(*args):
        raise OSError(PRIVATE)

    monkeypatch.setattr(m, "_online_backup", fail)
    assert_refused(lambda: m.backup(database, directory))
    assert list(directory.iterdir()) == [sentinel]
    assert sentinel.read_text() == PRIVATE


def test_cleanup_keeps_unexpected_files_and_reports_private_path(database, tmp_path, monkeypatch, capsys):
    directory = tmp_path / "restore"

    def fail(*args):
        (directory / "user-owned.txt").write_text(PRIVATE)
        raise OSError(PRIVATE)

    monkeypatch.setattr(m, "_online_backup", fail)
    assert m.main(["restore-check", "--backup", str(database), "--restore-dir", str(directory)]) == 2
    output = capsys.readouterr()
    assert not output.out and PRIVATE not in output.err
    assert json.loads(output.err) == {"status": "cleanup-required", "path": str(directory.resolve())}
    assert list(directory.iterdir()) == [directory / "user-owned.txt"]


def test_cleanup_refuses_replaced_artifact(tmp_path):
    directory = tmp_path / "owned"
    artifacts = m._Artifacts()
    artifacts.directory(directory)
    path = artifacts.database(directory)
    replacement = tmp_path / "replacement.sqlite3"
    replacement.write_text(PRIVATE)
    replacement.replace(path)
    assert_refused(artifacts.cleanup, "cleanup-required")
    assert path.read_text() == PRIVATE


def test_database_file_creation_never_overwrites_existing(tmp_path):
    directory = tmp_path / "private"
    directory.mkdir(mode=0o700)
    path = directory / "inquiries.sqlite3"
    path.write_text(PRIVATE)
    artifacts = m._Artifacts()
    with pytest.raises(FileExistsError):
        artifacts.database(directory)
    artifacts.cleanup()
    assert path.read_text() == PRIVATE


@pytest.mark.skipif(os.name != "posix", reason="POSIX mode assertions; Windows requires operator ACLs")
def test_private_modes_and_refusal_of_public_directory(database, tmp_path):
    public = tmp_path / "public"
    public.mkdir(mode=0o755)
    public.chmod(0o755)
    assert_refused(lambda: m.backup(database, public), "destination-not-private")
    assert stat.S_IMODE(public.stat().st_mode) == 0o755
    result = m.backup(database, tmp_path / "backups")
    saved = Path(result["backup"])
    restored = Path(m.restore_check(saved, tmp_path / "restore")["database"])
    for path in (saved, restored):
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(saved.parent.parent.stat().st_mode) == 0o700


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan"), 301, True, "30"])
def test_invalid_deadlines_are_refused(database, timeout):
    assert_refused(lambda: m.check(database, timeout=timeout), "invalid-timeout")


def test_exclusive_lock_has_bounded_wait(database, tmp_path):
    with closing(sqlite3.connect(database)) as writer:
        writer.execute("BEGIN EXCLUSIVE")
        start = time.monotonic()
        assert_refused(lambda: m.backup(database, tmp_path / "backups", timeout=0.1))
        assert time.monotonic() - start < 2
        writer.rollback()
    assert not (tmp_path / "backups").exists()


def test_backup_retry_callback_enforces_deadline(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(m, "monotonic", lambda: clock[0])
    deadline = m._Deadline(0.2)

    class BusySource:
        def backup(self, destination, *, pages, progress, sleep):
            assert pages > 0 and 0 < sleep <= 0.1
            for attempt in range(10):
                clock[0] += 0.05
                progress(5, 10, 10)  # SQLITE_BUSY; named constant is absent in 3.10.
            pytest.fail("Backup kept retrying past its deadline")

    assert_refused(lambda: m._online_backup(BusySource(), None, deadline), "timed-out")


def test_sql_progress_interrupts_work_at_deadline(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(m, "monotonic", lambda: clock[0])
    deadline = m._Deadline(0.1)
    with closing(sqlite3.connect(":memory:")) as db:
        m._configure(db, deadline, readonly=True)
        clock[0] = 0.2
        with pytest.raises(sqlite3.OperationalError, match="interrupted"):
            db.execute("""WITH RECURSIVE n(x) AS (
                VALUES(1) UNION ALL SELECT x+1 FROM n WHERE x<1000000)
                SELECT sum(x) FROM n""").fetchone()


def test_timeout_during_copy_removes_partial_database(database, tmp_path, monkeypatch):
    original_backup = m._online_backup

    def expired(source, destination, deadline):
        deadline.end = m.monotonic() - 1
        original_backup(source, destination, deadline)

    monkeypatch.setattr(m, "_online_backup", expired)
    assert_refused(lambda: m.backup(database, tmp_path / "backups"), "timed-out")
    assert not (tmp_path / "backups").exists()


def test_cli_only_reports_counts_paths_status(database, tmp_path):
    script = str(Path(m.__file__).resolve())
    commands = [
        ["check", "--database", str(database)],
        ["backup", "--database", str(database), "--backup-dir", str(tmp_path / "backups")],
    ]
    for arguments in commands:
        result = subprocess.run([sys.executable, script, *arguments], capture_output=True,
                                text=True, timeout=10, check=False)
        assert result.returncode == 0 and not result.stderr
        report = json.loads(result.stdout)
        assert set(report) <= {"status", "database", "backup", "counts"}
        assert report["status"] == "ok" and report["counts"] == {"inquiries": 2, "events": 2, "chat_caller_turns": 0}
        assert all(secret not in result.stdout for secret in PRIVATE.split())
    result = subprocess.run([sys.executable, script, "restore-check", "--backup", report["backup"],
                             "--restore-dir", str(tmp_path / "restore")], capture_output=True,
                            text=True, timeout=10, check=False)
    assert result.returncode == 0 and not result.stderr
    assert json.loads(result.stdout)["counts"] == {"inquiries": 2, "events": 2, "chat_caller_turns": 0}
    assert all(secret not in result.stdout for secret in PRIVATE.split())


@pytest.mark.parametrize("arguments", [
    ["PRIVATE-TOKEN"], ["check", "--database", PRIVATE],
    ["check", "--database", "unused", "--timeout", PRIVATE],
    ["check", "--database", "unused", "--PRIVATE-TOKEN"],
])
def test_cli_errors_never_echo_arguments(arguments, capsys):
    assert m.main(arguments) == 2
    output = capsys.readouterr()
    assert not output.out
    assert set(json.loads(output.err)) == {"status"}
    assert all(secret not in output.err for secret in PRIVATE.split())
    assert "Traceback" not in output.err


def test_cli_unexpected_exceptions_are_sanitized(monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise RuntimeError(PRIVATE)

    monkeypatch.setattr(m, "check", fail)
    assert m.main(["check", "--database", "unused"]) == 2
    output = capsys.readouterr()
    assert not output.out and json.loads(output.err) == {"status": "operation-failed"}
