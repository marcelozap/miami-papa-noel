"""Synthetic, offline admission tests. No model calls or customer state."""
import concurrent.futures
import json
from pathlib import Path
import sqlite3
import socket
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.web_chat_guard import guard


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refused(*args, **kwargs):
        pytest.fail("Admission tests must not access the network")
    monkeypatch.setattr(socket, "create_connection", refused)
    monkeypatch.setattr(socket.socket, "connect", refused)


def body(message="Hola", **extras):
    return json.dumps({"message": message, "consent": True, **extras}).encode()


@pytest.mark.parametrize("payload", [b"", b"[]", b"x" * 4097,
    b'{"message":"a","message":"b","consent":true}',
    body(consent=1), body(consent=False), body(message=" "), body(message=12),
    body(message="x" * 1001), body(message="hi\x00"), body(message="hi\u202e"),
    body(model="expensive"), body(history=[]), body(role="system"),
    b'{"message":"\\ud800","consent":true}'])
def test_rejects_invalid_payload(payload):
    with pytest.raises(guard.InvalidRequest, match="^CHAT_INVALID_REQUEST$"):
        guard.parse_request(payload)


def test_spanish_and_whitespace():
    assert guard.parse_request(body("  Hola, visita a mi casa?\n")) == "Hola, visita a mi casa?"


@pytest.fixture
def gate(tmp_path):
    return guard.AdmissionGuard(tmp_path / "chat.sqlite3", b"synthetic-secret-" * 3,
                                clock=lambda: 100000)


def test_duplicate_across_instances_and_ip_alias(gate):
    assert gate.reserve("192.0.2.1", "Hello  Santa") is None
    other = guard.AdmissionGuard(gate.database, gate.secret, clock=gate.clock)
    assert other.reserve("::ffff:192.0.2.1", " hello santa ") == "CHAT_DUPLICATE"
    assert other.reserve("192.0.2.2", "hello santa") is None


def test_atomic_parallel_limit(gate):
    def send(i):
        other = guard.AdmissionGuard(gate.database, gate.secret, clock=gate.clock)
        return other.reserve("192.0.2.1", "question " + str(i))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(send, range(16)))
    assert results.count(None) == 6
    assert results.count("CHAT_RATE_LIMITED") == 10


def test_global_limit_and_expiry(gate):
    for i in range(200):
        assert gate.reserve("192.0.2." + str(i + 1), "hello") is None
    assert gate.reserve("198.51.100.1", "hello") == "CHAT_CAPACITY_REACHED"
    gate.clock = lambda: 186400
    assert gate.reserve("198.51.100.1", "hello") is None


def test_clock_rollback_and_secret_change_refuse(gate):
    assert gate.reserve("192.0.2.1", "hello") is None
    gate.clock = lambda: 99999
    assert gate.reserve("192.0.2.2", "other") == "CHAT_ACCOUNTING_UNAVAILABLE"
    gate.clock = lambda: 100000
    gate.secret = b"different-secret-" * 3
    assert gate.reserve("192.0.2.2", "other") == "CHAT_ACCOUNTING_UNAVAILABLE"


def test_failure_closed_and_no_plaintext(gate):
    assert gate.reserve("192.0.2.1", "synthetic-private-message") is None
    with sqlite3.connect(gate.database) as db:
        dump = "\n".join(db.iterdump())
    assert "192.0.2.1" not in dump and "synthetic-private-message" not in dump
    gate.database.write_bytes(b"corrupted")
    assert gate.reserve("192.0.2.1", "other") == "CHAT_ACCOUNTING_UNAVAILABLE"


def test_invalid_direct_calls_do_not_create_state(gate):
    assert gate.reserve("untrusted-header", "hi") == "CHAT_INVALID_REQUEST"
    assert gate.reserve("192.0.2.1", "x" * 1001) == "CHAT_INVALID_REQUEST"
    assert not gate.database.exists()


@pytest.mark.parametrize("address", ["fe80::1%abc", "192.0.2.1, 192.0.2.2", 1, "0.0.0.0"])
def test_untrusted_address_forms_refused(gate, address):
    assert gate.reserve(address, "hello") == "CHAT_INVALID_REQUEST"
    assert not gate.database.exists()


def test_window_boundary_keeps_duplicate_protection(gate):
    for i in range(6):
        assert gate.reserve("192.0.2.1", str(i)) is None
    gate.clock = lambda: 100299
    assert gate.reserve("192.0.2.1", "new") == "CHAT_RATE_LIMITED"
    gate.clock = lambda: 100300
    assert gate.reserve("192.0.2.1", "0") == "CHAT_DUPLICATE"
    assert gate.reserve("192.0.2.1", "new") is None


def test_repo_and_relative_paths_refused():
    for path in ("relative.sqlite3", Path(__file__).parent / "private.sqlite3"):
        with pytest.raises(ValueError):
            guard.AdmissionGuard(path, b"x" * 32)
