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


def create_deposit_booking(server, package="christmas_eve"):
    code, out = call(server, "/api/new", {
        "client_name": "Synthetic Family", "phone": "2025550100",
        "package": package, "date": "2026-12-24", "start_time": "15:00",
        "zone": "doral", "duration_min": 45,
        "address": "1 Synthetic Ct", "guest_count": 3})
    assert code == 200
    return out["created"]


@pytest.mark.parametrize("amount", [
    None, 0, -1, 1, 249.99, True, "", "not money", [], {},
    float("nan"), float("inf"), 250.001,
])
def test_board_refuses_invalid_or_short_deposit_without_mutation(server, amount):
    rid = create_deposit_booking(server)
    before = store.load()
    with open(store.EVENTS_PATH, encoding="utf-8") as f:
        events_before = f.read()

    code, out = call(server, "/api/verify-deposit", {
        "id": rid, "amount": amount, "memo": "2026-12-24 Synthetic Family"})
    assert code == 409 and "refused" in out
    assert store.load() == before
    with open(store.EVENTS_PATH, encoding="utf-8") as f:
        assert f.read() == events_before
    code, _ = call(server, "/api/approve", {"id": rid})
    assert code == 409


@pytest.mark.parametrize("memo", [None, "", "   ", 123, ["reference"]])
def test_board_refuses_deposit_without_payment_reference(server, memo):
    rid = create_deposit_booking(server)
    code, out = call(server, "/api/verify-deposit", {
        "id": rid, "amount": 250, "memo": memo})
    assert code == 409 and "refused" in out
    assert store.find(store.load(), rid)["deposit"]["status"] == "unpaid"


@pytest.mark.parametrize("package,amount", [
    ("standard", 162.50), ("jingle", 97.50), ("school", 137.50),
    ("corporate", 225), ("hoa", 275), ("peak_evening", 212.50),
    ("christmas_eve", 250), ("sneak_a_peek", 187.50),
    ("photographer_4hr", 300), ("photographer_day", 425),
])
def test_board_enforces_each_locked_package_deposit(server, package, amount):
    rid = create_deposit_booking(server, package)
    code, _ = call(server, "/api/verify-deposit", {
        "id": rid, "amount": amount - 0.01,
        "memo": "2026-12-24 Synthetic Family"})
    assert code == 409
    code, out = call(server, "/api/verify-deposit", {
        "id": rid, "amount": amount, "memo": "2026-12-24 Synthetic Family"})
    assert code == 200 and out["deposit"]["status"] == "verified"


def test_board_rechecks_deposit_after_package_changes(server):
    rid = create_deposit_booking(server, "standard")
    code, _ = call(server, "/api/verify-deposit", {
        "id": rid, "amount": 162.50, "memo": "2026-12-24 Synthetic Family"})
    assert code == 200
    code, _ = call(server, "/api/update", {"id": rid, "package": "christmas_eve"})
    assert code == 200
    code, out = call(server, "/api/approve", {"id": rid})
    assert code == 409 and "refused" in out
    assert store.find(store.load(), rid)["status"] != "confirmed"


def test_board_cannot_verify_against_tampered_lower_price(server):
    rid = create_deposit_booking(server)
    records = store.load()
    store.find(records, rid)["price_quoted"] = 1
    store.save(records)
    code, out = call(server, "/api/verify-deposit", {
        "id": rid, "amount": 1, "memo": "2026-12-24 Synthetic Family"})
    assert code == 409 and "refused" in out


@pytest.mark.parametrize("field,value", [
    ("amount", None), ("amount", 1), ("memo", ""), ("method", "venmo"),
])
def test_board_rechecks_verified_deposit_fields_at_confirmation(server, field, value):
    rid = create_deposit_booking(server)
    code, _ = call(server, "/api/verify-deposit", {
        "id": rid, "amount": 250, "memo": "2026-12-24 Synthetic Family"})
    assert code == 200
    records = store.load()
    rec = store.find(records, rid)
    assert rec["status"] == "pending_review"
    rec["deposit"][field] = value
    store.save(records)
    code, out = call(server, "/api/approve", {"id": rid})
    assert code == 409 and "refused" in out
    assert store.find(store.load(), rid)["operator_approval"] is None


@pytest.mark.parametrize("method", ["zelle", "stripe"])
def test_board_accepts_valid_numeric_string_deposit_on_approved_rails(server, method):
    rid = create_deposit_booking(server)
    records = store.load()
    store.find(records, rid)["deposit"]["method"] = method
    store.save(records)
    code, _ = call(server, "/api/verify-deposit", {
        "id": rid, "amount": "250.00", "memo": "synthetic-receipt-reference"})
    assert code == 200
    code, out = call(server, "/api/approve", {"id": rid})
    assert code == 200 and out["confirmed"] == rid


@pytest.mark.parametrize("field,value", [
    ("date", "2026-12-25"), ("start_time", "16:00"), ("zone", "homestead"),
    ("duration_min", 120), ("setup_min", 90), ("package", "photographer_day"),
    ("address", "2 Synthetic Ct"), ("guest_count", 100),
])
def test_board_refuses_booking_changes_after_confirmation(server, field, value):
    rid = create_deposit_booking(server)
    assert call(server, "/api/verify-deposit", {
        "id": rid, "amount": 250, "memo": "synthetic-receipt-reference"})[0] == 200
    assert call(server, "/api/approve", {"id": rid})[0] == 200
    before = store.load()
    with open(store.EVENTS_PATH, encoding="utf-8") as f:
        events_before = f.read()
    code, out = call(server, "/api/update", {"id": rid, field: value})
    assert code == 409 and "operator" in out["refused"]
    assert store.load() == before
    with open(store.EVENTS_PATH, encoding="utf-8") as f:
        assert f.read() == events_before


def test_board_can_update_schedule_before_confirmation(server):
    rid = create_deposit_booking(server)
    code, _ = call(server, "/api/update", {"id": rid, "start_time": "16:00"})
    assert code == 200
    assert store.find(store.load(), rid)["start_time"] == "16:00"
