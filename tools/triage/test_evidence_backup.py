"""Evidence backup/restore tests: synthetic fixtures, no network, no real logs.

    python -m pytest tools/triage/test_evidence_backup.py -q
"""
from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import evidence_backup as eb  # noqa: E402

CANARY = "SYNTHETIC-CANARY family@example.invalid 305-555-0142 PRIVATE-BODY"


@pytest.fixture(autouse=True)
def sandboxed(monkeypatch, tmp_path):
    """Every log path lives in the sandbox; the real machine is never read."""
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path / "logs"))

    def no_network(*args, **kwargs):
        pytest.fail("evidence backup must never use the network")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)


def write_log(tmp_path, rows, real=True, extra=""):
    directory = tmp_path / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ("production-log.jsonl" if real else "synthetic-log.jsonl")
    body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    path.write_text(body + extra, encoding="utf-8")
    return path


def rows(count=3):
    return [{"inquiry_id": "MPN-2026090%d-AAA" % n, "notes": CANARY,
             "model": "offline-rules-v1"} for n in range(count)]


# --------------------------------------------------------- destination rules --

def test_repo_destination_refused(tmp_path):
    write_log(tmp_path, rows())
    with pytest.raises(eb.BackupError) as caught:
        eb.backup(str(eb.REPO_ROOT / "docs"))
    assert "outside the repository" in str(caught.value)


def test_relative_destination_refused(tmp_path):
    write_log(tmp_path, rows())
    with pytest.raises(eb.BackupError) as caught:
        eb.backup("backups")
    assert "absolute" in str(caught.value)


def test_symlinked_destination_refused(tmp_path):
    write_log(tmp_path, rows())
    real = tmp_path / "real-dest"
    real.mkdir()
    link = tmp_path / "linked-dest"
    try:
        os.symlink(real, link, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks unavailable on this account")
    with pytest.raises(eb.BackupError) as caught:
        eb.backup(str(link))
    assert "link" in str(caught.value)


def test_missing_log_refuses(tmp_path):
    with pytest.raises(eb.BackupError) as caught:
        eb.backup(str(tmp_path / "dest"))
    assert "nothing to back up" in str(caught.value)


# ------------------------------------------------------------------- backup --

def test_backup_verifies_and_never_mutates_the_source(tmp_path):
    source = write_log(tmp_path, rows(4))
    before = source.read_bytes()
    result = eb.backup(str(tmp_path / "dest"))
    assert result["status"] == "ok" and result["records"] == 4
    assert source.read_bytes() == before          # source untouched, byte for byte
    copy = Path(result["backup"])
    assert copy.read_bytes() == before            # copy is exact
    assert copy.parent != source.parent


def test_second_backup_does_not_overwrite_the_first(tmp_path):
    write_log(tmp_path, rows(2))
    first = eb.backup(str(tmp_path / "dest"))
    import datetime as dt
    later = dt.datetime(2026, 9, 9, 12, 0, 0, tzinfo=dt.timezone.utc)
    second = eb.backup(str(tmp_path / "dest"), now=later)
    assert first["backup"] != second["backup"]
    assert Path(first["backup"]).is_file() and Path(second["backup"]).is_file()


def test_malformed_source_refused_without_leaking_content(tmp_path):
    write_log(tmp_path, rows(2), extra="{not valid json at all " + CANARY + "\n")
    with pytest.raises(eb.BackupError) as caught:
        eb.backup(str(tmp_path / "dest"))
    message = str(caught.value)
    assert "malformed" in message and "3" in message   # the line NUMBER
    assert CANARY not in message and "PRIVATE-BODY" not in message


def test_concurrent_change_during_copy_is_detected(tmp_path, monkeypatch):
    source = write_log(tmp_path, rows(2))
    original = eb.shutil.copyfileobj

    def copy_then_mutate(src, dst, *args, **kwargs):
        result = original(src, dst, *args, **kwargs)
        # Simulate another Santa command appending mid-copy.
        with open(source, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"inquiry_id": "MPN-LATE", "notes": CANARY}) + "\n")
        return result

    monkeypatch.setattr(eb.shutil, "copyfileobj", copy_then_mutate)
    dest = tmp_path / "dest"
    with pytest.raises(eb.BackupError) as caught:
        eb.backup(str(dest))
    assert "changed while it was being copied" in str(caught.value)
    assert not any(dest.glob("*.jsonl"))          # torn copy removed


def test_same_drive_letter_flag_reported(tmp_path):
    write_log(tmp_path, rows(1))
    result = eb.backup(str(tmp_path / "dest"))
    # A drive-letter match is a hint about hardware, never proof.
    assert result["same_drive_letter_as_source"] is True


# ------------------------------------------------------------ restore-check --

def test_restore_check_into_new_directory(tmp_path):
    write_log(tmp_path, rows(3))
    made = eb.backup(str(tmp_path / "dest"))
    out = eb.restore_check(made["backup"], str(tmp_path / "drill"))
    assert out["status"] == "ok" and out["records"] == 3
    assert out["unique_ids"] == 3
    assert out["matches_live_log"] is True
    assert Path(out["restored"]).is_file()


def test_restore_check_refuses_existing_directory(tmp_path):
    write_log(tmp_path, rows(1))
    made = eb.backup(str(tmp_path / "dest"))
    existing = tmp_path / "already-here"
    existing.mkdir()
    with pytest.raises(eb.BackupError) as caught:
        eb.restore_check(made["backup"], str(existing))
    assert "does not exist yet" in str(caught.value)


def test_restore_check_never_touches_the_live_log(tmp_path):
    live = write_log(tmp_path, rows(2))
    before = live.read_bytes()
    made = eb.backup(str(tmp_path / "dest"))
    eb.restore_check(made["backup"], str(tmp_path / "drill"))
    assert live.read_bytes() == before


def test_restore_check_detects_a_damaged_backup(tmp_path):
    write_log(tmp_path, rows(2))
    made = eb.backup(str(tmp_path / "dest"))
    Path(made["backup"]).write_text('{"broken": tru\n', encoding="utf-8")
    with pytest.raises(eb.BackupError) as caught:
        eb.restore_check(made["backup"], str(tmp_path / "drill"))
    assert "malformed" in str(caught.value)


def test_restore_check_flags_divergence_from_the_live_log(tmp_path):
    write_log(tmp_path, rows(2))
    made = eb.backup(str(tmp_path / "dest"))
    write_log(tmp_path, rows(5))                  # log grew after the backup
    out = eb.restore_check(made["backup"], str(tmp_path / "drill"))
    assert out["matches_live_log"] is False
    assert out["records"] == 2 and out["live_records"] == 5


# ------------------------------------------------------------------- CLI ----

def test_cli_backup_and_restore_round_trip(tmp_path, capsys):
    write_log(tmp_path, rows(2))
    assert eb.main(["backup", "--dest", str(tmp_path / "dest")]) == 0
    made = json.loads(capsys.readouterr().out)
    assert eb.main(["restore-check", "--backup", made["backup"],
                    "--restore-dir", str(tmp_path / "drill")]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ok"


def test_cli_refusal_exits_1_without_leaking(tmp_path, capsys):
    write_log(tmp_path, rows(1))
    assert eb.main(["backup", "--dest", str(eb.REPO_ROOT / "docs")]) == 1
    captured = capsys.readouterr()
    assert "REFUSED" in captured.err and CANARY not in captured.err


# ----------------------------- defects reported by Codex (handoff 003) -------

def test_competing_file_at_target_is_never_overwritten(tmp_path):
    """A file appearing at the backup name must survive untouched."""
    import datetime as dt
    write_log(tmp_path, rows(2))
    fixed = dt.datetime(2026, 9, 8, 6, 0, 0, tzinfo=dt.timezone.utc)
    first = eb.backup(str(tmp_path / "dest"), now=fixed)
    competing = Path(first["backup"])
    competing.write_text("SOMEONE-ELSES-FILE " + CANARY, encoding="utf-8")
    with pytest.raises(eb.BackupError) as caught:
        eb.backup(str(tmp_path / "dest"), now=fixed)      # same name again
    assert "not overwriting" in str(caught.value)
    assert competing.read_text(encoding="utf-8").startswith("SOMEONE-ELSES-FILE")


def test_writer_racing_between_check_and_create_cannot_be_overwritten(tmp_path, monkeypatch):
    """Simulate the intervening writer: exclusive creation must refuse."""
    write_log(tmp_path, rows(2))
    real_open = os.open
    created = {}

    def racing_open(path, flags, *args, **kwargs):
        # Another process wins the race immediately before our open.
        if str(path).endswith(".jsonl") and not created:
            created["path"] = str(path)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("RACER-WON " + CANARY)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(eb.os, "open", racing_open)
    with pytest.raises(eb.BackupError) as caught:
        eb.backup(str(tmp_path / "dest"))
    assert "not overwriting" in str(caught.value)
    assert Path(created["path"]).read_text(encoding="utf-8").startswith("RACER-WON")


def test_restore_check_refuses_to_create_the_absent_live_log(tmp_path, monkeypatch):
    """The live log's directory is missing: a drill must NOT create it."""
    source_logs = tmp_path / "logs"
    write_log(tmp_path, rows(2))
    made = eb.backup(str(tmp_path / "dest"))
    # The backup file carries the live log's own name.
    named = Path(made["backup"]).with_name("production-log.jsonl")
    Path(made["backup"]).rename(named)

    missing_live = tmp_path / "missing-live-dir"
    monkeypatch.setenv("MPN_LOG_DIR", str(missing_live))
    live = missing_live / "production-log.jsonl"
    assert not live.exists() and not missing_live.exists()

    with pytest.raises(eb.BackupError) as caught:
        eb.restore_check(str(named), str(missing_live))
    assert "log directory" in str(caught.value) or "log location" in str(caught.value)
    assert not live.exists(), "restore-check must never create the live log"
    assert source_logs.exists()


def test_restore_check_refuses_an_alias_of_the_absent_live_log_dir(tmp_path, monkeypatch):
    """The same missing directory spelled differently must also be refused."""
    write_log(tmp_path, rows(1))
    made = eb.backup(str(tmp_path / "dest"))
    missing_live = tmp_path / "aliased-live"
    monkeypatch.setenv("MPN_LOG_DIR", str(missing_live))
    alias = tmp_path / "sub" / ".." / "aliased-live"      # same place, spelled around
    (tmp_path / "sub").mkdir()
    # Refused by whichever guard sees it first (path normalisation catches the
    # ".." spelling; the live-location guard catches the direct one). What
    # matters is that the live directory is never created either way.
    with pytest.raises(eb.BackupError):
        eb.restore_check(made["backup"], str(alias))
    assert not missing_live.exists()
    with pytest.raises(eb.BackupError) as direct:
        eb.restore_check(made["backup"], str(missing_live))
    assert "log directory" in str(direct.value)
    assert not missing_live.exists()
