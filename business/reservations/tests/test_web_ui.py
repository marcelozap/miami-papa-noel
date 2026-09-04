"""Operator board smoke tests — the board obeys the same gates."""

import json
import os
import sys
import threading
import urllib.request

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import store
import content_agent
import web_ui
from http.server import HTTPServer


@pytest.fixture()
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(store, "RES_PATH", str(tmp_path / "data" / "reservations.json"))
    monkeypatch.setattr(store, "EVENTS_PATH", str(tmp_path / "data" / "events.jsonl"))
    monkeypatch.setattr(content_agent, "QUEUE_DIR", str(tmp_path / "content_queue"))
    srv = HTTPServer(("127.0.0.1", 0), web_ui.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()


def call(base, path, body=None):
    if body is None:
        req = urllib.request.Request(base + path)
    else:
        req = urllib.request.Request(base + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def test_board_serves_page_and_state(server):
    with urllib.request.urlopen(server + "/") as r:
        assert b"Operator Board" in r.read()
    code, state = call(server, "/api/state")
    assert code == 200 and state["reservations"] == []
    assert "christmas_eve" in state["rates"]


def test_full_flow_through_http(server):
    code, out = call(server, "/api/new", {
        "client_name": "Web Family", "phone": "305", "package": "christmas_eve",
        "date": "2026-12-24", "start_time": "17:00", "zone": "doral",
        "duration_min": 45, "address": "1 Web St", "guest_count": 3})
    assert code == 200
    rid = out["created"]

    # approve before deposit -> the gate refuses over HTTP too
    code, out = call(server, "/api/approve", {"id": rid})
    assert code == 409 and "refused" in out

    code, _ = call(server, "/api/verify-deposit",
                   {"id": rid, "amount": 250, "memo": "12/24 Web"})
    assert code == 200
    code, out = call(server, "/api/approve", {"id": rid})
    assert code == 200 and out["confirmed"] == rid

    code, out = call(server, "/api/content", {})
    assert code == 200 and out["drafts_made"] == 1
    code, state = call(server, "/api/state")
    assert state["drafts"][0]["status"] == "draft"
    code, out = call(server, "/api/approve-post", {"id": rid})
    assert code == 200 and out["status"] == "approved"
