"""Synthetic-only intake/review regressions; no provider credentials or sends."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from http.client import HTTPConnection
import json
import hashlib
import ipaddress
from pathlib import Path
import shutil
import subprocess
import sqlite3
import threading
import uuid

import pytest

from tools.web_inquiry import server as web

TOKEN = "synthetic-test-token-not-for-production-2026"
ACTOR = "Synthetic Operator"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MPN_MODEL", raising=False)


@pytest.fixture
def app(tmp_path):
    application = web.App(tmp_path / "private", TOKEN, "http://127.0.0.1:8226")
    yield application
    application.close()


def payload(**changes):
    data = {"name": "Synthetic Family", "contact": "synthetic@example.invalid",
            "message": "Synthetic test: family visit in Doral on December 10, 2026.",
            "consent": True, "request_key": uuid.uuid4().hex}
    data.update(changes)
    return data


def ready(app, **changes):
    identifier = app.submit(payload(**changes))["request_id"]
    app.draft(identifier, ACTOR)
    assert app.listing()["items"][0]["status"] == "draft_ready"
    return identifier


def approve(app, identifier, real=False):
    return review(app, identifier, "approve", {"language": "en", "real_customer": real})


def review(app, identifier, action, data):
    return app.review(identifier, ACTOR, action,
                      {"draft_revision": stored_revision(app, identifier), **data})


def stored_revision(app, identifier):
    with app.connect() as db:
        value = app.row(db, identifier)["record"]
    return hashlib.sha256(value.encode()).hexdigest() if value else None


def test_stale_tab_cannot_approve_unseen_regenerated_draft(app):
    identifier = ready(app)
    original = stored_revision(app, identifier)
    def revised(*args, **kwargs):
        record = web.triage.build_record(*args, **kwargs)
        record["draft_en"] += " Thank you."
        record["draft_es"] += " Gracias."
        return record
    app.builder = revised
    app.draft(identifier, ACTOR, regenerate=True)
    assert stored_revision(app, identifier) != original
    refused(409, lambda: app.review(identifier, ACTOR, "approve", {
        "language": "en", "draft_revision": original,
    }))
    row = app.listing()["items"][0]
    assert row["status"] == "draft_ready" and row["record"]["approved_at"] is None
    with app.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM events WHERE action='approve'").fetchone()[0] == 0


@pytest.mark.parametrize("revision", [None, "", "0" * 64, [], True])
def test_missing_or_wrong_review_revision_is_refused(app, revision):
    identifier = ready(app)
    refused(409, lambda: app.review(identifier, ACTOR, "approve", {
        "language": "en", "draft_revision": revision,
    }))


def refused(status, call):
    with pytest.raises(web.Refused) as error:
        call()
    assert error.value.status == status


@pytest.fixture
def http(app):
    service = web.Server(("127.0.0.1", 0), app)
    port = service.server_address[1]
    app.origin = "http://127.0.0.1:%d" % port
    app.host = "127.0.0.1:%d" % port
    thread = threading.Thread(target=service.serve_forever)
    thread.start()

    def request(path, data=None, auth=False, headers=None, raw=None):
        h = {"Origin": app.origin, "Content-Type": "application/json"}
        if auth:
            h["Authorization"] = "Bearer " + TOKEN
        h.update(headers or {})
        conn = HTTPConnection("127.0.0.1", port, timeout=5)
        body = raw if raw is not None else json.dumps(data) if data is not None else None
        conn.request("POST" if body is not None else "GET", path, body=body, headers=h)
        response = conn.getresponse()
        content = response.read()
        result = (response.status, dict(response.getheaders()), content)
        conn.close()
        return result

    yield request
    service.shutdown()
    service.server_close()
    thread.join()


# ---------------------------------------------------------------- chat -----

SESSION = "synthetic-session-key-0001"


@pytest.fixture
def chat_secret(monkeypatch):
    secret = "ab" * 32
    monkeypatch.setenv("MPN_CHAT_SECRET", secret)
    return secret


def test_chat_is_disabled_without_a_configured_secret(app):
    assert app.chat_service is None
    refused(503, lambda: app.chat_reply(SESSION, "Hola", "203.0.113.5"))


def test_chat_requires_a_well_formed_session_key(chat_secret, tmp_path):
    live = web.App(tmp_path / "chat-private", TOKEN, "http://127.0.0.1:8226")
    try:
        refused(400, lambda: live.chat_reply("short", "Hola", "203.0.113.5"))
        refused(400, lambda: live.chat_reply(None, "Hola", "203.0.113.5"))
    finally:
        live.close()


@pytest.fixture
def chat_app(chat_secret, tmp_path):
    application = web.App(tmp_path / "chat-private", TOKEN, "http://127.0.0.1:8226")
    yield application
    application.close()


def test_chat_rejects_empty_or_oversized_messages(chat_app):
    refused(400, lambda: chat_app.chat_reply(SESSION, "", "203.0.113.5"))
    refused(400, lambda: chat_app.chat_reply(SESSION, "x" * 1001, "203.0.113.5"))


def test_chat_never_confirms_a_booking_and_uses_locked_pricing(chat_app):
    result = chat_app.chat_reply(SESSION, "Family visit in Doral", "203.0.113.5")
    assert result["booking_confirmed"] is False
    assert result["status"] == "reply"
    assert "$325" in result["message"]


def test_chat_gathers_missing_details_progressively_across_turns(chat_app):
    first = chat_app.chat_reply(SESSION, "Family visit in Doral", "203.0.113.6")
    assert "?" in first["message"]  # still asks for date and contact
    second = chat_app.chat_reply(SESSION, "December 20 2026, phone 305-555-1212",
                                 "203.0.113.6")
    # Having accumulated both prior facts plus a phone number, the running
    # transcript no longer needs to ask the customer to repeat themselves.
    assert "confirm" not in second["message"].lower()


def test_chat_escalates_payment_questions_to_a_human_without_a_template_quote(chat_app):
    result = chat_app.chat_reply(SESSION, "Did you get my Zelle payment, refund please?",
                                 "203.0.113.7")
    assert result["status"] == "human_required"
    assert "786-975-9557" in result["message"]
    assert "$" not in result["message"]


def test_chat_sessions_are_isolated_by_session_key(chat_app):
    chat_app.chat_reply(SESSION, "Family visit in Doral", "203.0.113.8")
    # A second, unrelated visitor must not inherit the first one's category -
    # a vague message alone should still get the generic "depends on visit
    # type" line, not the $325 family-visit price the first session earned.
    other = chat_app.chat_reply("synthetic-session-key-0002", "How much is it",
                                "203.0.113.9")
    assert "$325" not in other["message"]
    assert "depends on the type of visit" in other["message"].lower()


def test_chat_session_key_reuse_by_a_different_caller_cannot_mix_contexts(chat_app):
    """Codex finding 2: same session_key, two different IPs."""
    first = chat_app.chat_reply(SESSION, "Family visit in Doral", "203.0.113.30")
    assert "$325" in first["message"]
    hijack = chat_app.chat_reply(SESSION, "How much is it", "203.0.113.31")
    assert "$325" not in hijack["message"]
    assert "depends on the type of visit" in hijack["message"].lower()
    # The original owner's context must survive the attempted takeover: it
    # still remembers the category from the first turn (still $325 priced)
    # and, once given a phone number, stops asking for contact info too.
    still_first = chat_app.chat_reply(SESSION, "phone 305-555-1212", "203.0.113.30")
    assert "$325" in still_first["message"]
    assert "phone" not in still_first["message"].lower() and "email" not in still_first["message"].lower()


def test_chat_daily_cap_survives_a_restart(chat_secret, tmp_path):
    """Codex finding 1: the personal allowance must not reset on restart."""
    address = "203.0.113.40"
    app = web.App(tmp_path / "restart-private", TOKEN, "http://127.0.0.1:8226")
    try:
        for _ in range(web.CHAT_DAILY_TURNS_PER_CALLER):
            result = app.chat_reply(SESSION, "Family visit in Doral", address)
            assert result["status"] != "CHAT_PERSONAL_DAILY_LIMIT"
    finally:
        app.close()
    restarted = web.App(tmp_path / "restart-private", TOKEN, "http://127.0.0.1:8226")
    try:
        capped = restarted.chat_reply(SESSION, "One more, please", address)
        assert capped["status"] == "CHAT_PERSONAL_DAILY_LIMIT"
    finally:
        restarted.close()


def test_chat_daily_cap_reservation_is_atomic_under_concurrency(chat_app):
    """CHAT_DAILY_TURNS_PER_CALLER must never be exceeded by a race."""
    address = "203.0.113.41"
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(
            lambda _: chat_app.chat_reply(SESSION, "Family visit in Doral", address),
            range(8)))
    admitted = [r for r in results if r["status"] != "CHAT_PERSONAL_DAILY_LIMIT"]
    assert len(admitted) == web.CHAT_DAILY_TURNS_PER_CALLER
    with chat_app.connect() as db:
        row = db.execute("SELECT turns FROM chat_caller_turns").fetchone()
    assert row["turns"] == web.CHAT_DAILY_TURNS_PER_CALLER


def test_chat_daily_cap_accounting_failure_refuses_rather_than_grants(chat_app, monkeypatch):
    def fail(*a, **k):
        raise sqlite3.OperationalError("PRIVATE DATABASE PATH")
    monkeypatch.setattr(chat_app, "connect", fail)
    result = chat_app.chat_reply(SESSION, "Family visit in Doral", "203.0.113.42")
    assert result["status"] == "CHAT_ACCOUNTING_UNAVAILABLE"
    assert b"PRIVATE" not in json.dumps(result).encode()


def test_chat_caps_one_visitor_well_under_the_shared_daily_pool(chat_app):
    address = "203.0.113.20"
    for _ in range(web.CHAT_DAILY_TURNS_PER_CALLER):
        result = chat_app.chat_reply(SESSION, "Family visit in Doral", address)
        assert result["status"] != "CHAT_PERSONAL_DAILY_LIMIT"
    capped = chat_app.chat_reply(SESSION, "One more question", address)
    assert capped["status"] == "CHAT_PERSONAL_DAILY_LIMIT"
    assert "786-975-9557" in capped["message"]
    assert "tomorrow" not in capped["message"].lower()  # this is a per-person cap, not the shared daily one


def test_chat_personal_daily_cap_does_not_affect_other_visitors(chat_app):
    address = "203.0.113.21"
    for _ in range(web.CHAT_DAILY_TURNS_PER_CALLER):
        chat_app.chat_reply(SESSION, "Family visit in Doral", address)
    other = chat_app.chat_reply("synthetic-session-key-0003", "Family visit in Doral",
                                "203.0.113.22")
    assert other["status"] != "CHAT_PERSONAL_DAILY_LIMIT"


def test_chat_personal_daily_cap_resets_on_a_new_day(chat_app, monkeypatch):
    address = "203.0.113.23"
    for _ in range(web.CHAT_DAILY_TURNS_PER_CALLER):
        chat_app.chat_reply(SESSION, "Family visit in Doral", address)
    assert chat_app.chat_reply(SESSION, "One more", address)["status"] == "CHAT_PERSONAL_DAILY_LIMIT"
    tomorrow = web.now() + web.dt.timedelta(days=1)
    monkeypatch.setattr(web, "now", lambda: tomorrow)
    fresh = chat_app.chat_reply(SESSION, "Family visit in Doral", address)
    assert fresh["status"] != "CHAT_PERSONAL_DAILY_LIMIT"


def test_chat_daily_capacity_shows_a_check_back_tomorrow_message(chat_app):
    chat_app.chat_service.admission.reserve = lambda address, message: "CHAT_CAPACITY_REACHED"
    result = chat_app.chat_reply(SESSION, "Family visit in Doral", "203.0.113.10")
    assert result["status"] == "CHAT_CAPACITY_REACHED"
    assert "tomorrow" in result["message"].lower()
    assert "786-975-9557" in result["message"]
    assert "$" not in result["message"]


def test_chat_rate_limit_message_says_wait_not_tomorrow(chat_app):
    chat_app.chat_service.admission.reserve = lambda address, message: "CHAT_RATE_LIMITED"
    result = chat_app.chat_reply(SESSION, "Family visit in Doral", "203.0.113.11")
    assert "tomorrow" not in result["message"].lower()
    assert "wait" in result["message"].lower()


def test_chat_capacity_message_is_translated_for_spanish_speakers(chat_app):
    chat_app.chat_service.admission.reserve = lambda address, message: "CHAT_CAPACITY_REACHED"
    result = chat_app.chat_reply(SESSION, "Hola, quiero una visita familiar", "203.0.113.12")
    assert result["language"] == "es"
    assert "mañana" in result["message"].lower()


def test_chat_guard_invalid_request_is_refused_cleanly_not_uncaught(chat_app):
    def explode(body, address):
        raise web.web_chat_guard.InvalidRequest("CHAT_INVALID_REQUEST")
    chat_app.chat_service.respond = explode
    refused(400, lambda: chat_app.chat_reply(SESSION, "Hola", "203.0.113.13"))


def test_chat_http_endpoint_round_trips_and_enforces_limits(chat_app):
    service = web.Server(("127.0.0.1", 0), chat_app)
    port = service.server_address[1]
    chat_app.origin = "http://127.0.0.1:%d" % port
    chat_app.host = "127.0.0.1:%d" % port
    thread = threading.Thread(target=service.serve_forever)
    thread.start()
    try:
        def post(path, body_bytes, origin=None):
            conn = HTTPConnection("127.0.0.1", port, timeout=5)
            conn.request("POST", path, body=body_bytes, headers={
                "Origin": origin or chat_app.origin, "Content-Type": "application/json"})
            resp = conn.getresponse()
            data = resp.read()
            conn.close()
            return resp.status, data

        status, body = post("/api/chat", json.dumps(
            {"session_key": SESSION, "message": "Family visit in Doral"}).encode())
        assert status == 200
        payload = json.loads(body)
        assert payload["booking_confirmed"] is False

        status, body = post("/api/chat", json.dumps(
            {"session_key": SESSION, "message": "Family visit in Doral"}).encode(),
            origin="http://evil.example.invalid")
        assert status == 403

        status, body = post("/api/chat", (b'{"session_key":"%s","message":"%s"}'
                                          % (SESSION.encode(), b"x" * 5000)))
        assert status == 413
    finally:
        service.shutdown()
        service.server_close()
        thread.join()


def test_submit_is_durable_and_never_calls_model(app):
    app.builder = lambda *a, **k: pytest.fail("Public intake must not invoke model")
    receipt = app.submit(payload())
    assert receipt["status"] == "received"
    assert app.listing()["items"][0]["record"] is None
    app.close()
    restored = web.App(app.data_dir, TOKEN, app.origin)
    try:
        assert restored.listing()["items"][0]["id"] == receipt["request_id"]
    finally:
        restored.close()


def test_one_process_owns_state_and_releases_on_close(app):
    with pytest.raises(ValueError, match="Another inquiry"):
        web.App(app.data_dir, TOKEN, app.origin)
    app.close()
    restored = web.App(app.data_dir, TOKEN, app.origin)
    restored.close()


@pytest.mark.parametrize("changes", [
    {"name": ""}, {"name": "x" * 101}, {"contact": "not-a-contact"},
    {"contact": []}, {"message": "x" * 3001}, {"message": "a\x00b"},
    {"consent": False}, {"consent": "true"}, {"request_key": "short"},
    {"message": "bad\ud800text"},
])
def test_bad_input_not_stored(app, changes):
    refused(400, lambda: app.submit(payload(**changes)))
    assert app.listing()["items"] == []


def test_duplicate_keys_and_payloads_return_same_receipt(app):
    data = payload()
    first = app.submit(data)
    assert app.submit(data)["request_id"] == first["request_id"]
    assert app.submit(payload())["request_id"] == first["request_id"]
    refused(409, lambda: app.submit({**data, "message": "A different message"}))
    assert len(app.listing()["items"]) == 1


def test_concurrent_duplicates_store_one_request(app):
    data = payload()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: app.submit(data), range(8)))
    assert len({r["request_id"] for r in results}) == 1
    assert len(app.listing()["items"]) == 1


def test_spanish_bilingual_draft_and_explicit_review_send(app):
    identifier = ready(app, message="Prueba: Hola, quiero una visita familiar en Doral el 10 de diciembre de 2026.")
    row = app.listing()["items"][0]
    record = row["record"]
    assert record["language"] == "es"
    assert record["draft_en"] and "Gracias" in record["draft_es"]
    assert record["fallback_used"] and record["model"] == "offline-rules-v1"
    assert record["approved_at"] is None and record["sent_at"] is None
    refused(409, lambda: review(app, identifier, "sent", {"sent_manually": True}))
    review(app, identifier, "approve", {"language": "es"})
    row = app.listing()["items"][0]
    assert row["reviewed_language"] == "es"
    assert row["record"]["outcome"] == "approved_awaiting_send"
    refused(409, lambda: review(app, identifier, "sent", {}))
    review(app, identifier, "sent", {"sent_manually": True})
    assert app.listing()["items"][0]["record"]["outcome"] == "approved_and_sent"
    refused(409, lambda: review(app, identifier, "sent", {"sent_manually": True}))


def test_demo_cannot_record_real_and_requires_language(app):
    identifier = ready(app)
    refused(400, lambda: approve(app, identifier, real=True))
    refused(400, lambda: review(app, identifier, "approve", {}))
    refused(400, lambda: approve(app, identifier, real="true"))
    assert app.listing()["items"][0]["status"] == "draft_ready"


def test_no_approval_without_draft_and_no_unrequested_redraft(app):
    identifier = app.submit(payload())["request_id"]
    refused(409, lambda: approve(app, identifier))
    app.draft(identifier, ACTOR)
    refused(409, lambda: app.draft(identifier, ACTOR))
    assert app.draft(identifier, ACTOR, regenerate=True)["status"] == "draft_ready"
    approve(app, identifier)
    refused(409, lambda: app.draft(identifier, ACTOR, regenerate=True))


def test_version_drift_refuses_approval_and_can_regenerate(app, monkeypatch):
    identifier = ready(app)
    monkeypatch.setattr(web.triage, "PROMPT_VERSION", "synthetic-new-version")
    refused(409, lambda: approve(app, identifier))
    app.draft(identifier, ACTOR, regenerate=True)
    assert approve(app, identifier)["status"] == "approved"


def test_approval_reruns_gates_instead_of_trusting_saved_pass(app):
    identifier = ready(app)
    with app.connect() as db:
        record = json.loads(app.row(db, identifier)["record"])
        record["draft_es"] += " Su reserva esta confirmada."
        db.execute("UPDATE inquiries SET record=? WHERE id=?", (json.dumps(record), identifier))
    refused(409, lambda: approve(app, identifier))
    assert app.listing()["items"][0]["status"] == "draft_ready"


def test_rejected_draft_cannot_be_sent(app):
    identifier = ready(app)
    approve(app, identifier)
    assert review(app, identifier, "reject", {})["status"] == "rejected"
    refused(409, lambda: review(app, identifier, "sent", {"sent_manually": True}))
    assert app.listing()["items"][0]["record"]["outcome"] == "rejected_by_operator"


def test_builder_exception_retains_request_without_secret_error(app):
    identifier = app.submit(payload())["request_id"]
    def fail(*a, **k):
        raise RuntimeError("PRIVATE PROVIDER BODY")
    app.builder = fail
    with pytest.raises(web.Refused) as error:
        app.draft(identifier, ACTOR)
    assert error.value.status == 503 and "PRIVATE" not in error.value.message
    assert app.listing()["items"][0]["status"] == "failed"
    app.builder = web.triage.build_record
    assert app.draft(identifier, ACTOR)["status"] == "draft_ready"


def test_concurrent_model_request_invokes_once(app):
    identifier = app.submit(payload())["request_id"]
    started, release = threading.Event(), threading.Event()
    def builder(*a, **k):
        started.set()
        assert release.wait(5)
        return web.triage.build_record(*a, **k)
    app.builder = builder
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(app.draft, identifier, ACTOR)
        try:
            assert started.wait(5)
            refused(409, lambda: app.draft(identifier, ACTOR))
        finally:
            release.set()
        assert pending.result()["status"] == "draft_ready"


def test_restart_marks_interrupted_draft_failed(app):
    identifier = app.submit(payload())["request_id"]
    with app.connect() as db:
        db.execute("UPDATE inquiries SET status='drafting' WHERE id=?", (identifier,))
    app.close()
    restored = web.App(app.data_dir, TOKEN, app.origin)
    try:
        assert restored.listing()["items"][0]["status"] == "failed"
    finally:
        restored.close()


def test_exports_are_private_unique_and_do_not_promote_test_activity(app):
    identifier = ready(app)
    approve(app, identifier)
    review(app, identifier, "sent", {"sent_manually": True})
    evidence = app.export()
    app.export()
    data = (evidence / "synthetic-log.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in data.splitlines()]
    assert len(rows) == 1 and rows[0]["inquiry_id"] == identifier
    assert "draft_en" not in data and "draft_es" not in data
    assert "synthetic@example.invalid" not in data and "Synthetic Family" not in data
    assert not (evidence / "production-log.jsonl").exists()
    assert rows[0]["real_customer"] is False


def test_live_capability_still_requires_separate_explicit_attestation(app):
    app.live = True
    first = ready(app)
    approve(app, first)
    second = ready(app, name="Synthetic Second Family")
    approve(app, second, real=True)  # Synthetic fixture exercising the live branch only.
    evidence = app.export()
    production = json.loads((evidence / "production-log.jsonl").read_text(encoding="utf-8"))
    assert production["inquiry_id"] == second
    assert production["sent_at"] is None
    assert production["fallback_used"] is True
    assert production["outcome"] == "approved_awaiting_send"


@pytest.mark.parametrize("path", [web.ROOT, web.ROOT / "test-private-inquiry"])
def test_repo_storage_forbidden(path):
    with pytest.raises(ValueError, match="outside"):
        web.App(path, TOKEN, "http://localhost:8226")


@pytest.mark.parametrize("origin", ["http://example.com", "https://user@example.com", "https://example.com/path"])
def test_unsafe_origin_forbidden(tmp_path, origin):
    with pytest.raises(ValueError, match="Origin"):
        web.App(tmp_path, TOKEN, origin)


def test_weak_token_forbidden(tmp_path):
    with pytest.raises(ValueError, match="token"):
        web.App(tmp_path, "short", "http://localhost:8226")


def test_http_public_and_protected_routes(http, app):
    for path in ("/", "/operator", "/app.js", "/app.css", "/santa.jpg", "/health"):
        status, headers, body = http(path)
        assert status == 200 and body
        assert headers["Cache-Control"] == "no-store"
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert http("/api/inquiries")[0] == 401
    assert http("/api/inquiries", auth=True)[0] == 200
    assert http("/inquiries.sqlite3")[0] == 404
    assert http("/../server.py")[0] == 404
    assert http("/", headers={"Host": "evil.invalid"})[0] == 403


@pytest.mark.parametrize("path", ["/api/draft", "/api/approve", "/api/sent", "/api/reject", "/api/redraft", "/api/export"])
def test_operator_posts_require_authentication(http, path):
    assert http(path, {"reviewer": ACTOR, "id": "guess"})[0] == 401


def test_http_intake_origin_and_validation(http, app):
    assert http("/api/inquiry", payload(), headers={"Origin": "https://evil.invalid"})[0] == 403
    assert http("/api/inquiry", payload(), headers={"Origin": ""})[0] == 403
    assert http("/api/inquiry", raw="{")[0] == 400
    assert http("/api/inquiry", raw="[]")[0] == 400
    assert http("/api/inquiry", payload(), headers={"Content-Type": "text/plain"})[0] == 415
    assert http("/api/inquiry", raw="x" * (web.MAX_BODY + 1))[0] == 413
    assert app.listing()["items"] == []


@pytest.mark.parametrize("path,auth", [("/api/inquiry", False), ("/api/draft", True)])
@pytest.mark.parametrize("shape", ["array", "object"])
def test_deep_request_json_returns_private_bilingual_error(http, app, capsys, path, auth, shape):
    marker = '"SYNTHETIC_PRIVATE_INPUT"'
    if shape == "array":
        nested = "[" * 1100 + marker + "]" * 1100
    else:
        nested = '{"x":' * 1100 + marker + "}" * 1100
    raw = '{"unused":' + nested + "}"
    assert len(raw.encode()) < web.MAX_BODY
    app.builder = lambda *a, **k: pytest.fail("Malformed input must not invoke model")

    status, _, body = http(path, raw=raw, auth=auth)
    assert status == 400
    assert json.loads(body) == {"error": "Invalid request / Solicitud no válida"}
    assert b"SYNTHETIC_PRIVATE_INPUT" not in body
    assert app.listing()["items"] == []
    with app.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0
    assert "Traceback" not in capsys.readouterr().err
    assert http("/health")[0] == 200
    assert http("/api/inquiry", payload())[0] == 201


def test_http_submission_and_draft_approval(http, app):
    status, _, body = http("/api/inquiry", payload())
    assert status == 201
    identifier = json.loads(body)["request_id"]
    assert app.listing()["items"][0]["record"] is None
    fields = {"id": identifier, "reviewer": ACTOR}
    assert http("/api/draft", fields, auth=True)[0] == 200
    fields["draft_revision"] = app.listing()["items"][0]["draft_revision"]
    assert http("/api/approve", {**fields, "language": "en"}, auth=True)[0] == 200
    assert app.listing()["items"][0]["record"]["sent_at"] is None
    fields["draft_revision"] = app.listing()["items"][0]["draft_revision"]
    assert http("/api/sent", {**fields, "sent_manually": True}, auth=True)[0] == 200
    assert http("/api/export", {"reviewer": ACTOR}, auth=True)[0] == 200


def test_failed_storage_never_reports_acceptance(http, app, monkeypatch):
    def fail(*a, **k):
        raise sqlite3.OperationalError("PRIVATE DATABASE PATH")
    monkeypatch.setattr(app, "connect", fail)
    status, _, body = http("/api/inquiry", payload())
    assert status == 503 and b"PRIVATE" not in body


def test_public_rate_limit_does_not_block_operator(http):
    for _ in range(5):
        assert http("/api/inquiry", payload())[0] == 201
    status, headers, _ = http("/api/inquiry", payload())
    assert status == 429 and headers["Retry-After"] == "300"
    assert http("/api/export", {"reviewer": ACTOR}, auth=True)[0] == 200


def test_older_requests_remain_accessible_without_duplicate_pages(app, http):
    ids = [app.submit(payload(name="Synthetic family %d" % n))["request_id"] for n in range(105)]
    first = app.listing()
    assert len(first["items"]) == 100 and first["next_cursor"]
    status, _, body = http("/api/inquiries?before=%d" % first["next_cursor"], auth=True)
    second = json.loads(body)
    assert status == 200 and len(second["items"]) == 5 and second["next_cursor"] is None
    assert {r["id"] for r in first["items"] + second["items"]} == set(ids)
    assert http("/api/inquiries?before=-1", auth=True)[0] == 400
    assert http("/api/inquiries?before=1&unexpected=1", auth=True)[0] == 400


def test_validation_failure_blocks_draft_then_allows_operator_retry(app):
    identifier = app.submit(payload())["request_id"]
    def blocked(*a, **k):
        record = web.triage.build_record(*a, **k)
        record["validation"] = [{"level": "FAIL", "check": "synthetic", "detail": "synthetic failure"}]
        return record
    app.builder = blocked
    assert app.draft(identifier, ACTOR)["status"] == "blocked"
    refused(409, lambda: approve(app, identifier))
    app.builder = web.triage.build_record
    assert app.draft(identifier, ACTOR)["status"] == "draft_ready"


def test_mock_model_id_retained_without_inventing_production_use(app):
    def mock_model(*a, **k):
        record = web.triage.build_record(*a, **k)
        record.update(model="mock-model-not-production", fallback_used=False, error_code=None)
        return record
    app.builder = mock_model
    ready(app)
    evidence = app.export()
    data = json.loads((evidence / "synthetic-log.jsonl").read_text(encoding="utf-8"))
    assert data["model"] == "mock-model-not-production"
    assert data["real_customer"] is False
    assert data["sent_at"] is None
    assert not (evidence / "production-log.jsonl").exists()


def test_client_uses_text_nodes_and_no_persistent_token_storage():
    script = (web.HERE / "app.js").read_text(encoding="utf-8")
    assert "innerHTML" not in script
    assert "localStorage" not in script and "sessionStorage" not in script
    assert "record.language==='es'?'es':'en'" in script


def test_client_session_and_revision_regressions():
    node = shutil.which("node")
    assert node, "Node.js is required for the browser-client regression tests"
    result = subprocess.run([node, "--test", str(Path(__file__).with_name("client-tests.cjs"))],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("action", ["reject", "sent"])
def test_post_approval_action_must_match_approved_snapshot(app, action):
    identifier = ready(app)
    old = stored_revision(app, identifier)
    approve(app, identifier)
    refused(409, lambda: app.review(identifier, ACTOR, action, {
        "draft_revision": old, "sent_manually": True,
    }))
    assert app.listing()["items"][0]["status"] == "approved"
    assert review(app, identifier, action, {"sent_manually": True})["status"] == (
        "sent" if action == "sent" else "rejected")


def test_http_stale_revision_is_rejected_without_approval(http, app):
    identifier = ready(app)
    fields = {"id": identifier, "reviewer": ACTOR, "language": "en", "draft_revision": "0" * 64}
    assert http("/api/approve", fields, auth=True)[0] == 409
    row = json.loads(http("/api/inquiries", auth=True)[2])["items"][0]
    assert row["status"] == "draft_ready" and row["record"]["approved_at"] is None
    fields["draft_revision"] = row["draft_revision"]
    assert http("/api/approve", fields, auth=True)[0] == 200


def test_trusted_proxy_has_separate_client_buckets(http, app):
    app.trusted_proxy = ipaddress.ip_address("127.0.0.1")
    for index in range(6):
        assert http("/api/inquiry", payload(),
                    headers={"X-MPN-Client-IP": "192.0.2.%d" % (index + 1)})[0] == 201
    headers = {"X-MPN-Client-IP": "192.0.2.1"}
    for _ in range(4):
        assert http("/api/inquiry", payload(), headers=headers)[0] == 201
    assert http("/api/inquiry", payload(), headers=headers)[0] == 429
    assert http("/api/export", {"reviewer": ACTOR}, auth=True, headers=headers)[0] == 200


def test_forwarding_headers_cannot_bypass_default_limits(http):
    for index in range(6):
        headers = {"X-MPN-Client-IP": "192.0.2.%d" % (index + 1),
                   "X-Forwarded-For": "198.51.100.%d" % (index + 1)}
        assert http("/api/inquiry", payload(), headers=headers)[0] == (201 if index < 5 else 429)


@pytest.mark.parametrize("value", ["", "unknown", "192.0.2.1, 192.0.2.2", "fe80::1%eth0", "0.0.0.0"])
def test_trusted_proxy_refuses_missing_or_invalid_identity(http, app, value):
    app.trusted_proxy = ipaddress.ip_address("127.0.0.1")
    assert http("/api/inquiry", payload(), headers={"X-MPN-Client-IP": value})[0] == 400
    assert app.listing()["items"] == []


def test_readiness_is_authenticated_and_checks_storage(http, app, monkeypatch):
    assert http("/api/readiness")[0] == 401
    status, _, body = http("/api/readiness", auth=True)
    assert status == 200 and json.loads(body)["scope"] == "local_storage_only"
    def fail(*args, **kwargs):
        raise sqlite3.OperationalError("PRIVATE STORAGE DETAILS")
    monkeypatch.setattr(app, "connect", fail)
    status, _, body = http("/api/readiness", auth=True)
    assert status == 503 and b"PRIVATE" not in body


@pytest.mark.parametrize("proxy", ["0.0.0.0", "::", "127.0.0.0/8", "localhost", "127.0.0.1,::1", "fe80::1%eth0"])
def test_proxy_configuration_requires_one_concrete_ip(tmp_path, proxy):
    with pytest.raises(ValueError):
        web.App(tmp_path, TOKEN, "https://example.invalid", trusted_proxy=proxy)
    assert not (tmp_path / "inquiries.sqlite3").exists()


def test_proxy_peer_and_duplicate_identity_are_rejected(app):
    app.trusted_proxy = ipaddress.ip_address("127.0.0.1")
    refused(403, lambda: app.client_ip("192.0.2.1", ["198.51.100.1"]))
    refused(400, lambda: app.client_ip("127.0.0.1", []))
    refused(400, lambda: app.client_ip("127.0.0.1", ["192.0.2.1", "192.0.2.2"]))
    assert app.client_ip("127.0.0.1", ["::ffff:192.0.2.1"]) == "192.0.2.1"
    assert app.client_ip("127.0.0.1", ["2001:0db8:0:0:0:0:0:1"]) == "2001:db8::1"


def test_global_rate_limit_survives_client_rotation_and_expires(app, monkeypatch):
    stamp = web.time.monotonic()
    monkeypatch.setattr(web.time, "monotonic", lambda: stamp)
    for n in range(100):
        app.throttle("192.0.2.%d" % (n + 1))
    refused(429, lambda: app.throttle("192.0.2.101"))
    app.throttle("192.0.2.101", operator=True)
    assert all("192.0.2." not in repr(key) for key in app.request_times)
    monkeypatch.setattr(web.time, "monotonic", lambda: stamp + 301)
    app.throttle("192.0.2.101")


def test_readiness_does_not_create_customer_events_and_detects_readonly(app, monkeypatch):
    identifier = ready(app)
    with app.connect() as db:
        before = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    report = app.readiness()
    assert report["scope"] == "local_storage_only"
    assert report["queue"] == {"draft_ready": 1}
    assert report["draft_errors"] == 0
    assert identifier not in json.dumps(report) and "synthetic@example.invalid" not in json.dumps(report)
    with app.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == before
    @contextmanager
    def readonly():
        db = sqlite3.connect(app.database.as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        try:
            yield db
        finally:
            db.close()
    monkeypatch.setattr(app, "connect", readonly)
    with pytest.raises(sqlite3.OperationalError):
        app.readiness()


def test_readiness_surfaces_draft_errors_without_message_bodies(http, app):
    identifier = ready(app)
    with app.connect() as db:
        record = json.loads(app.row(db, identifier)["record"])
        record["error_code"] = "MODEL_HTTP_ERROR"
        db.execute("UPDATE inquiries SET record=? WHERE id=?", (json.dumps(record), identifier))
    status, _, body = http("/api/readiness", auth=True)
    assert status == 200 and json.loads(body)["draft_errors"] == 1
    assert b"synthetic@example.invalid" not in body and b"draft_en" not in body
    with app.connect() as db:
        db.execute("UPDATE inquiries SET record='bad-json' WHERE id=?", (identifier,))
    assert http("/api/readiness", auth=True)[0] == 503


@pytest.mark.parametrize("value", ["null", "[]", '"PRIVATE"', "1", "true", b"\xff",
    '{"error_code":' + '[' * 1100 + '0' + ']' * 1100 + '}'])
def test_readiness_refuses_bad_record_types_without_traceback(http, app, capsys, value):
    identifier = ready(app)
    with app.connect() as db:
        db.execute("UPDATE inquiries SET record=? WHERE id=?", (value, identifier))
    status, _, body = http("/api/readiness", auth=True)
    assert status == 503 and b"PRIVATE" not in body
    assert "Traceback" not in capsys.readouterr().err


def test_readiness_detects_sqlite_capacity_limit(http, app, monkeypatch):
    connect = app.connect
    @contextmanager
    def constrained():
        with connect() as db:
            pages = db.execute("PRAGMA page_count").fetchone()[0]
            db.execute("PRAGMA max_page_count=%d" % pages)
            yield db
    monkeypatch.setattr(app, "connect", constrained)
    assert http("/api/readiness", auth=True)[0] == 503


def test_readiness_probe_rolls_back_schema_and_rows(app):
    with app.connect() as db:
        before = list(db.execute("SELECT * FROM sqlite_schema"))
    assert app.readiness()["status"] == "ok"
    with app.connect() as db:
        assert list(db.execute("SELECT * FROM sqlite_schema")) == before
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0


def test_readiness_refuses_low_disk_without_mutating_queue(http, app, monkeypatch):
    usage = web.shutil.disk_usage(app.data_dir)
    monkeypatch.setattr(web.shutil, "disk_usage", lambda path: usage._replace(free=web.MIN_FREE_BYTES - 1))
    assert http("/api/readiness", auth=True)[0] == 503
    assert app.listing()["items"] == []
