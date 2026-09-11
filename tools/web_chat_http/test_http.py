"""Loopback HTTP integration, synthetic data and paid generation disabled."""
import http.client
import json
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.web_chat_http.adapter import ChatServer
from tools.web_chat.service import ChatService
from tools.web_chat_guard.guard import AdmissionGuard
from tools.web_inquiry.server import App


@pytest.fixture
def running(tmp_path, monkeypatch):
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = App(tmp_path / "queue", "synthetic-operator-token" * 2, "http://127.0.0.1:1")
    guard = AdmissionGuard(tmp_path / "admission.sqlite3", b"synthetic-secret" * 3)
    chat = ChatService(guard, builder=lambda *a, **k: pytest.fail("No model calls"))
    server = ChatServer(("127.0.0.1", 0), app, chat)
    app.host = "127.0.0.1:" + str(server.server_port)
    app.origin = "http://" + app.host
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    yield server
    server.shutdown()
    thread.join()
    server.server_close()
    app.close()


def request(server, path="/api/chat", payload=None, headers=None):
    body = json.dumps(payload or {"message": "Hola, visita a mi casa en Doral", "consent": True}).encode()
    config = {"Origin": server.app.origin, "Content-Type": "application/json"}
    config.update(headers or {})
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
    try:
        conn.request("POST", path, body, config)
        response = conn.getresponse()
        return response.status, dict(response.getheaders()), json.loads(response.read())
    finally:
        conn.close()


def test_browser_post_returns_spanish_template(running):
    status, headers, body = request(running)
    assert status == 200 and body["language"] == "es"
    assert body["source"] == "template" and "$325" in body["message"]
    assert body["booking_confirmed"] is False
    assert headers["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


def test_duplicate_cannot_reprocess(running):
    assert request(running)[0] == 200
    assert request(running)[0] == 409


@pytest.mark.parametrize("headers,expected", [
    ({"Origin": "https://evil.example"}, 403),
    ({"Host": "evil.example"}, 403),
    ({"Content-Type": "text/plain"}, 415),
    ({"Transfer-Encoding": "chunked"}, 400),
    ({"Content-Length": "4097"}, 413)])
def test_invalid_transport_refused(running, headers, expected):
    assert request(running, headers=headers)[0] == expected
    assert not running.chat.admission.database.exists()


def test_client_cannot_enable_ai(running):
    assert request(running, payload={"message": "hello", "consent": True,
                                    "allow_model": True})[0] == 400


def test_operator_routes_still_require_authentication(running):
    assert request(running, path="/api/draft")[0] == 401


def test_fault_sanitized(running, monkeypatch):
    def crash(*a, **k):
        raise RuntimeError("PRIVATE-CANARY")
    monkeypatch.setattr(running.chat, "respond", crash)
    status, _, body = request(running)
    assert status == 503 and "PRIVATE-CANARY" not in json.dumps(body)


def test_existing_intake_still_reaches_queue(running):
    status, _, receipt = request(running, path="/api/inquiry", payload={
        "name": "Synthetic Visitor", "contact": "test@example.test",
        "message": "Synthetic family visit", "request_key": "synthetic_request_123", "consent": True})
    assert status == 201 and receipt["status"] == "received"
    assert running.app.listing()["items"][0]["status"] == "queued"
