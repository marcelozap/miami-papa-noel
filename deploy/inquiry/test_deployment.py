"""Synthetic health-check tests and static deployment-contract checks."""
import importlib.util
import json
from pathlib import Path
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mpn_healthcheck", HERE / "healthcheck.py")
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)
TOKEN = "synthetic-health-token-not-real-1234567890"
ORIGIN = "https://example.invalid"


@pytest.fixture
def endpoint():
    state = {"status": 200, "body": {"status": "ok", "scope": "local_storage_only",
             "queue": {"queued": 2}, "draft_errors": 0, "mode": "demo"}, "requests": []}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            state["requests"].append((self.path, dict(self.headers)))
            self.send_response(state["status"])
            self.send_header("Location", "http://example.invalid/never-follow")
            self.end_headers()
            body = state["body"]
            self.wfile.write(body if isinstance(body, bytes) else json.dumps(body).encode())
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield state, server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_private_loopback_health_and_output_whitelist(endpoint):
    state, port = endpoint
    state["body"]["private"] = "NEVER PRINT THIS"
    report = health.check(ORIGIN, TOKEN, port)
    assert report["status"] == "ok" and "private" not in report
    path, headers = state["requests"][0]
    assert path == "/api/readiness"
    assert headers["Host"] == "example.invalid"
    assert headers["Authorization"] == "Bearer " + TOKEN
    assert headers["X-MPN-Client-IP"] == "127.0.0.1"


@pytest.mark.parametrize("status", [301, 302, 307, 401, 429, 503])
def test_no_redirects_or_false_health(endpoint, status):
    state, port = endpoint
    state["status"] = status
    with pytest.raises(ValueError):
        health.check(ORIGIN, TOKEN, port)
    assert len(state["requests"]) == 1


@pytest.mark.parametrize("body", [b"x" * 8193, b"not-json", [], {"status": "ok"},
    {"status": "ok", "scope": "local_storage_only", "mode": "demo", "draft_errors": 0,
     "queue": {"private customer": 1}},
    {"status": "ok", "scope": "local_storage_only", "mode": "demo", "draft_errors": False,
     "queue": {"queued": True}}])
def test_bad_health_bodies_fail(endpoint, body):
    state, port = endpoint
    state["body"] = body
    with pytest.raises(ValueError):
        health.check(ORIGIN, TOKEN, port)


@pytest.mark.parametrize("reason", ["failed", "blocked", "model-error"])
def test_current_failures_require_attention(endpoint, reason):
    state, port = endpoint
    if reason == "model-error":
        state["body"]["draft_errors"] = 1
    else:
        state["body"]["queue"][reason] = 1
    assert health.check(ORIGIN, TOKEN, port)["status"] == "needs_attention"


@pytest.mark.parametrize("origin", ["http://remote.invalid", "https://u:p@example.invalid",
    "https://example.invalid/path", "https://example.invalid\r\nX-Forged:1", ""])
def test_bad_config_does_not_open_connection(monkeypatch, origin):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid configuration must not connect")
    monkeypatch.setattr(health.http.client, "HTTPConnection", forbidden)
    with pytest.raises(ValueError):
        health.check(origin, TOKEN)


def test_cli_sanitizes_failures_and_never_prints_token(monkeypatch, capsys):
    monkeypatch.setenv("MPN_PUBLIC_ORIGIN", ORIGIN)
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN)
    def fail(*args):
        raise OSError("PRIVATE " + TOKEN)
    monkeypatch.setattr(health, "check", fail)
    assert health.main([]) == 1
    assert json.loads(capsys.readouterr().out) == {
        "status": "unavailable", "scope": "local_storage_only"}


def test_cli_returns_nonzero_for_operator_attention(monkeypatch, capsys):
    monkeypatch.setattr(health, "check", lambda *args: {"status": "needs_attention"})
    assert health.main([]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "needs_attention"


def test_cli_sanitizes_excessively_nested_json(endpoint, monkeypatch, capsys):
    state, port = endpoint
    state["body"] = ('{"private":' + '[' * 1100 + '0' + ']' * 1100 + '}').encode()
    monkeypatch.setenv("MPN_PUBLIC_ORIGIN", ORIGIN)
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN)
    assert health.main(["--port", str(port)]) == 1
    captured = capsys.readouterr()
    assert captured.err == "" and "private" not in captured.out
    assert json.loads(captured.out)["status"] == "unavailable"


def test_deployment_contract_static_only():
    service = (HERE / "mpn-inquiry.service").read_text()
    assert "User=mpn-inquiry" in service and "Restart=on-failure" in service
    assert "server.py --offline" in service and "--live" not in service
    assert "StateDirectoryMode=0700" in service and "UMask=0077" in service
    assert "ProtectSystem=strict" in service and "KillSignal=SIGINT" in service
    env = (HERE / "inquiry.env.example").read_text()
    assert "MPN_OPERATOR_TOKEN=\n" in env and "OPENAI_API_KEY=\n" in env
    assert "MPN_TRUSTED_PROXY_IP=127.0.0.1" in env
    nginx = (HERE / "nginx.conf.example").read_text()
    assert "proxy_set_header X-MPN-Client-IP $remote_addr;" in nginx
    assert "proxy_set_header Host $host;" in nginx
    assert "$http_x" not in nginx and "proxy_add_x" not in nginx
    assert "client_max_body_size 16k;" in nginx and "access_log off;" in nginx
    assert "proxy_pass http://127.0.0.1:8226;" in nginx
    backup = (HERE / "mpn-inquiry-backup.service").read_text()
    assert "maintenance.py backup" in backup and "${MPN_INQUIRY_DIR}/inquiries.sqlite3" in backup
    assert "TimeoutStartSec=120" in backup
    assert "OnCalendar=" in (HERE / "mpn-inquiry-backup.timer").read_text()
    assert "OnUnitActiveSec=5min" in (HERE / "mpn-inquiry-health.timer").read_text()
