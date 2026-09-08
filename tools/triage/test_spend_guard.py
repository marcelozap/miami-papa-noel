"""Synthetic cost accounting and adapter integration; no paid traffic."""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "business" / "reservations"))
import spend_guard
import triage
import openai_adapter


def payload():
    return {"model": "synthetic-model", "max_output_tokens": 900,
            "input": [{"role": "system", "content": "synthetic instructions"},
                      {"role": "user", "content": "synthetic question"}]}


@pytest.fixture
def policy(tmp_path, monkeypatch):
    settings = {"daily_cents": "1", "verified_on": dt.datetime.now(dt.timezone.utc).date().isoformat(),
                "models": {"synthetic-model": {"input_usd_per_million": "0.2",
                           "output_usd_per_million": "1.2",
                           "source": "https://developers.openai.com/synthetic-test-only"}}}
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(settings), encoding="utf-8")
    monkeypatch.setenv("MPN_API_COST_POLICY", str(path))
    monkeypatch.setenv("MPN_API_QUOTA_DIR", str(tmp_path / "quota"))
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "100")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key")
    monkeypatch.setenv("MPN_MODEL", "synthetic-model")
    monkeypatch.setenv("MPN_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr(triage.urllib.request, "urlopen",
                        lambda *a, **k: pytest.fail("unexpected network request"))
    return path, tmp_path / "quota", settings


def test_default_off_even_with_call_allowance(policy, monkeypatch, tmp_path):
    monkeypatch.delenv("MPN_API_COST_POLICY")
    assert triage.call_openai_triage("synthetic", triage.load_pricing())[2] == "COST_POLICY_REQUIRED"
    adapter = openai_adapter.OpenAIContentAdapter(
        model="synthetic-model", transport=lambda p: pytest.fail("must not dispatch"))
    result = adapter.generate({}, str(tmp_path / "out"))
    assert json.loads(Path(result["manifest"]).read_text())["rejected"] == ["COST_POLICY_REQUIRED"]


@pytest.mark.parametrize("field,value", [
    ("daily_cents", "0"), ("daily_cents", "-1"), ("daily_cents", "NaN"),
    ("daily_cents", "Infinity"), ("daily_cents", "0.000001"),
    ("verified_on", "2020-01-01"), ("verified_on", "2999-01-01"),
    ("models", {}),
])
def test_invalid_policy_refuses_without_accounting(policy, field, value):
    path, directory, settings = policy
    settings[field] = value
    path.write_text(json.dumps(settings))
    assert spend_guard.reserve_cost(payload(), directory) == "COST_POLICY_INVALID"
    assert not directory.exists()


@pytest.mark.parametrize("rate", ["NaN", "0", "-1", "Infinity", "oops"])
def test_bad_rate_refuses(policy, rate):
    path, directory, settings = policy
    settings["models"]["synthetic-model"]["input_usd_per_million"] = rate
    path.write_text(json.dumps(settings))
    assert spend_guard.reserve_cost(payload(), directory) == "COST_POLICY_INVALID"


@pytest.mark.parametrize("mutation", [
    lambda p: p.update(tools=[{"type": "web_search"}]),
    lambda p: p.update(max_output_tokens=100000),
    lambda p: p.update(max_output_tokens=True),
    lambda p: p["input"][0].update(content="x" * 65537),
    lambda p: p["input"][1].update(content=[{"type": "input_image", "image_url": "secret"}]),
])
def test_unbounded_or_nontext_refused(policy, mutation):
    _, directory, _ = policy
    request = payload()
    mutation(request)
    assert spend_guard.reserve_cost(request, directory) == "COST_POLICY_INVALID"


def test_reservations_survive_restart_and_never_refund(policy):
    _, directory, _ = policy
    results = [spend_guard.reserve_cost(payload(), directory) for _ in range(12)]
    assert results.count(None) > 0
    assert results[-1] == "COST_BUDGET_REACHED"
    with sqlite3.connect(directory / "cost-reservations.sqlite3") as db:
        budget, used = db.execute("SELECT budget,reserved FROM daily").fetchone()
    assert 0 < used <= budget == 10000
    assert spend_guard.reserve_cost(payload(), directory) == "COST_BUDGET_REACHED"


def test_changes_to_daily_allowance_refuse(policy):
    path, directory, settings = policy
    assert spend_guard.reserve_cost(payload(), directory) is None
    for amount in ("2", "0.8"):
        settings["daily_cents"] = amount
        path.write_text(json.dumps(settings))
        assert spend_guard.reserve_cost(payload(), directory) == "COST_POLICY_CHANGED_TODAY"


def test_corrupt_or_unwritable_accounting_refuses(policy, monkeypatch):
    _, directory, _ = policy
    directory.mkdir()
    (directory / "cost-reservations.sqlite3").write_bytes(b"not a database")
    assert spend_guard.reserve_cost(payload(), directory) == "COST_ACCOUNTING_UNAVAILABLE"
    monkeypatch.setattr(spend_guard.sqlite3, "connect", lambda *a, **k: (_ for _ in ()).throw(sqlite3.OperationalError("secret")))
    assert spend_guard.reserve_cost(payload(), directory) == "COST_ACCOUNTING_UNAVAILABLE"


def test_process_concurrency_cannot_overshoot(policy):
    _, directory, _ = policy
    script = ("import sys,json; sys.path.insert(0,sys.argv[1]); "
              "from spend_guard import reserve_cost; "
              "print(reserve_cost(json.loads(sys.argv[2]),sys.argv[3]))")
    def run(_):
        return subprocess.run([sys.executable, "-B", "-c", script, str(HERE),
                               json.dumps(payload()), str(directory)],
                              text=True, capture_output=True, check=True).stdout.strip()
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(run, range(24)))
    assert "None" in results and "COST_BUDGET_REACHED" in results
    assert set(results) <= {"None", "COST_BUDGET_REACHED"}
    with sqlite3.connect(directory / "cost-reservations.sqlite3") as db:
        budget, used = db.execute("SELECT budget,reserved FROM daily").fetchone()
    assert 0 < used <= budget == 10000


def test_both_real_adapters_share_money_and_retain_failed_attempt(policy, monkeypatch, tmp_path):
    _, directory, _ = policy
    calls = []
    def failed_http(*args, **kwargs):
        calls.append("triage")
        raise TimeoutError("synthetic failure")
    monkeypatch.setattr(triage.urllib.request, "urlopen", failed_http)
    assert triage.call_openai_triage("synthetic", triage.load_pricing())[2] == "MODEL_UNAVAILABLE"
    def content_http(p):
        calls.append("content")
        return {"choices": [{"message": {"content": json.dumps({
            "caption_en": "synthetic English", "caption_es": "synthetic Spanish",
            "video_brief": "synthetic"})}}]}
    adapter = openai_adapter.OpenAIContentAdapter(model="synthetic-model", transport=content_http)
    for i in range(10):
        adapter.generate({}, str(tmp_path / str(i)))
    assert calls[0] == "triage" and "content" in calls
    assert len(calls) < 11
    with sqlite3.connect(directory / "cost-reservations.sqlite3") as db:
        budget, used = db.execute("SELECT budget,reserved FROM daily").fetchone()
    assert 0 < used <= budget


def test_full_prompt_and_schema_affect_reservation(policy):
    _, directory, _ = policy
    p = payload()
    p["text"] = {"format": {"schema": {"description": "x" * 40000}}}
    assert spend_guard.reserve_cost(p, directory) == "COST_BUDGET_REACHED"


def test_no_customer_or_key_in_accounting(policy):
    _, directory, _ = policy
    p = payload()
    p["input"][1]["content"] = "synthetic-private-canary"
    assert spend_guard.reserve_cost(p, directory) is None
    for item in directory.iterdir():
        raw = item.read_bytes()
        assert b"synthetic-private-canary" not in raw and b"synthetic-key" not in raw


@pytest.mark.parametrize("extra", [
    {"messages": [{"role": "user", "content": [{"type": "image_url"}]}]},
    {"max_completion_tokens": 100000},
    {"max_completion_tokens": 1},
])
def test_mixed_endpoint_fields_refused(policy, extra):
    _, directory, _ = policy
    request = payload()
    request.update(extra)
    assert spend_guard.reserve_cost(request, directory) == "COST_POLICY_INVALID"
    assert not directory.exists()


@pytest.mark.parametrize("spelling", ["repo", "device", "unc", "relative"])
def test_call_slots_validate_paths_before_any_write(policy, monkeypatch, spelling):
    repo = HERE.parents[1]
    slash = chr(92)
    paths = {"repo": str(repo / "never-created-quota"),
             "device": slash * 2 + "?" + slash + str(repo / "never-created-quota"),
             "unc": slash * 2 + "localhost" + slash + "C$" + slash + "XIV" + slash + "santa" + slash + "never-created-quota",
             "relative": "never-created-quota"}
    monkeypatch.setenv("MPN_API_QUOTA_DIR", paths[spelling])
    def no_write(*args, **kwargs):
        pytest.fail("invalid quota path must be refused before any filesystem write")
    monkeypatch.setattr(Path, "mkdir", no_write)
    monkeypatch.setattr(openai_adapter.os, "makedirs", no_write)
    assert triage.reserve_paid_call(1, "triage") == (False, "BUDGET_ACCOUNTING_UNAVAILABLE")
    assert openai_adapter._reserve_paid_call(1, "content") == (False, "paid-call accounting unavailable")


@pytest.mark.parametrize("prefix", ["//", "//?/", "//./"])
def test_private_paths_refuse_aliases_before_resolution(monkeypatch, prefix):
    def no_resolve(*args, **kwargs):
        pytest.fail("network/device spelling must be refused before resolution")
    monkeypatch.setattr(Path, "resolve", no_resolve)
    for spelling in (prefix + "C:/private", (prefix + "C:/private").replace("/", chr(92))):
        with pytest.raises(ValueError):
            spend_guard.private_path(spelling)


@pytest.mark.parametrize("field", ["policy", "quota"])
def test_cost_guard_refuses_windows_aliases(policy, monkeypatch, field):
    path, directory, _ = policy
    alias = chr(92) * 2 + "?" + chr(92) + str(path if field == "policy" else directory)
    if field == "policy":
        monkeypatch.setenv("MPN_API_COST_POLICY", alias)
    else:
        directory = alias
    assert spend_guard.reserve_cost(payload(), directory) == "COST_POLICY_INVALID"


def test_other_endpoint_fields_refused(policy):
    _, directory, _ = policy
    request = {"model": "synthetic-model", "max_completion_tokens": 900,
               "messages": payload()["input"], "text": {"format": {}}}
    assert spend_guard.reserve_cost(request, directory) == "COST_POLICY_INVALID"
