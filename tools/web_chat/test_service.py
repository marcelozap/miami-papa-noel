"""Offline website reply and real private-queue integration checks."""
import json
from pathlib import Path
import socket
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.web_chat import service
from tools.web_chat_guard.guard import AdmissionGuard, InvalidRequest
from tools.web_inquiry.server import App


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    def deny(*args, **kwargs):
        pytest.fail("No network permitted")
    monkeypatch.setattr(socket.socket, "connect", deny)


@pytest.fixture
def gate(tmp_path):
    return AdmissionGuard(tmp_path / "chat.sqlite3", b"synthetic-secret" * 3)


def body(message):
    return json.dumps({"message": message, "consent": True}).encode()


@pytest.mark.parametrize("message,language", [
    ("Family visit in Doral on December 10, 2026", "en"),
    ("Hola, una visita a mi casa en Doral el 10 de diciembre de 2026", "es")])
def test_service_inquiries_always_free(gate, message, language):
    def never(*args, **kwargs):
        pytest.fail("Recognized services must not call a model")
    result = service.ChatService(gate, allow_model=True, builder=never).respond(body(message), "192.0.2.1")
    assert result["language"] == language
    assert "$325" in result["message"]
    assert result["source"] == "template"
    assert result["booking_confirmed"] is False


def test_default_never_calls_model(gate):
    def never(*args, **kwargs):
        pytest.fail("Default is free")
    result = service.ChatService(gate, builder=never).respond(body("Unusual question"), "192.0.2.1")
    assert result["source"] == "template"


@pytest.mark.parametrize("message", ["I paid a deposit", "Are you available?",
    "Please cancel", "Hola, necesito un reembolso", "Hay disponibilidad?", "Quiero un descuento"])
def test_sensitive_topics_handoff_without_model(gate, message):
    def never(*args, **kwargs):
        pytest.fail("Sensitive request must go to operator")
    result = service.ChatService(gate, allow_model=True, builder=never).respond(body(message), "192.0.2.1")
    assert result["status"] == "human_required"
    assert result["source"] == "template" and "786-975-9557" in result["message"]


def test_valid_mocked_model_and_public_projection(gate):
    def fake(message, channel, **kwargs):
        assert kwargs["real"] is False
        record = service.triage.build_record(message, channel, **kwargs)
        record.update(model="synthetic-test-model", fallback_used=False, error_code=None,
                      reviewer="PRIVATE-CANARY", sent_at="PRIVATE-CANARY")
        return record
    result = service.ChatService(gate, allow_model=True, builder=fake).respond(body("Hola"), "192.0.2.1")
    assert result["source"] == "ai"
    assert set(result) == {"language", "message", "source", "status", "booking_confirmed"}
    assert "PRIVATE-CANARY" not in json.dumps(result)


@pytest.mark.parametrize("mode", ["failure", "fallback", "unsafe", "missing_gate"])
def test_model_failure_falls_back_once(gate, mode, monkeypatch):
    calls = []
    def fake(message, channel, **kwargs):
        calls.append(1)
        if mode == "failure":
            raise RuntimeError("PRIVATE-CANARY")
        record = service.triage.build_record(message, channel, **kwargs)
        if mode != "fallback":
            record.update(model="synthetic-test-model", fallback_used=False, error_code=None)
        if mode == "unsafe":
            record["draft_en"] = "Your booking is confirmed."
        if mode == "missing_gate":
            original = service.triage.validators.run_all
            monkeypatch.setattr(service.triage.validators, "run_all", lambda *a, **k: original(*a, **k)[:-1])
        return record
    result = service.ChatService(gate, allow_model=True, builder=fake).respond(body("Hola"), "192.0.2.1")
    assert result["source"] == "template" and len(calls) == 1
    assert "PRIVATE-CANARY" not in json.dumps(result)


def test_duplicate_cannot_repeat_model(gate):
    calls = []
    def fake(*args, **kwargs):
        calls.append(1)
        raise RuntimeError("fail")
    chat = service.ChatService(gate, allow_model=True, builder=fake)
    chat.respond(body("Hola"), "192.0.2.1")
    result = chat.respond(body("Hola"), "192.0.2.1")
    assert result["status"] == "CHAT_DUPLICATE" and len(calls) == 1


def test_invalid_request_never_invokes_builder(gate):
    with pytest.raises(InvalidRequest):
        service.ChatService(gate).respond(b'{"message":"hi","consent":false}', "192.0.2.1")
    assert not gate.database.exists()


def test_real_queue_handoff_is_not_approval_or_send(tmp_path):
    app = App(tmp_path / "operator", "synthetic-token" * 3, "http://127.0.0.1:8226")
    try:
        fields = dict(name="Synthetic Visitor", contact="synthetic@example.test",
                      message="Synthetic family visit inquiry", request_key="synthetic_key_12345", consent=True)
        first = service.submit_inquiry(app, **fields)
        assert service.submit_inquiry(app, **fields) == first
        assert first["booking_confirmed"] is False
        items = app.listing()["items"]
        assert len(items) == 1 and items[0]["status"] == "queued"
        assert items[0]["record"] is None
    finally:
        app.close()
