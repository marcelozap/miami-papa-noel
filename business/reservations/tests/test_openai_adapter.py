"""OpenAI adapter tests — no network, transport injected."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai_adapter
from openai_adapter import OpenAIContentAdapter


@pytest.fixture(autouse=True)
def sandboxed_quota(monkeypatch, tmp_path):
    """Shared paid-call quota stays in the sandbox and is opted in for the
    generation tests; paid generation is disabled by default otherwise."""
    monkeypatch.setenv("MPN_API_QUOTA_DIR", str(tmp_path / "quota"))
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "10")


def fake_transport_for(reply):
    calls = []

    def transport(payload):
        calls.append(payload)
        return {"choices": [{"message": {"content": json.dumps(reply)}}]}

    transport.calls = calls
    return transport


BRIEF = {
    "reservation": "abc123",
    "kind": "short-form vertical video",
    "client_name": "Gomez Family",
    "address": "123 NW 1st St, Doral",
    "caption_en": "template en",
    "caption_es": "template es",
}


def test_requires_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        OpenAIContentAdapter()


def test_good_generation_written(tmp_path):
    reply = {
        "caption_en": "Santa is coming to Doral! English y español. 786-975-9557",
        "caption_es": "¡Papá Noel llega a Doral! Español e inglés. 786-975-9557",
        "video_brief": "20s vertical clip, suit, Spanish greeting first.",
    }
    t = fake_transport_for(reply)
    a = OpenAIContentAdapter(api_key="test-key", model="test-model", transport=t)
    out = a.generate(BRIEF, str(tmp_path / "q"))
    assert out["asset"] and os.path.exists(out["asset"])
    manifest = json.load(open(out["manifest"], encoding="utf-8"))
    assert manifest["model"] == "test-model"
    assert "rejected" not in manifest
    # request shape: system prompt + brief went out
    assert t.calls[0]["model"] == "test-model"
    assert t.calls[0]["max_completion_tokens"] == 800  # spending bound
    assert "Miami Papa Noel" in t.calls[0]["messages"][0]["content"]


@pytest.mark.parametrize("bad_reply,flag", [
    ({"caption_en": "Fully insured Santa visits!", "caption_es": "x", "video_brief": "x"}, "claims insured"),
    ({"caption_en": "Miami Papá Noel is here", "caption_es": "x", "video_brief": "x"}, "wrong brand accent"),
    ({"caption_en": "Visiting the Gomez Family tonight", "caption_es": "x", "video_brief": "x"}, "leaks client_name"),
    ({"caption_en": "", "caption_es": "x", "video_brief": "x"}, "missing caption_en"),
    ({"caption_en": "Call 305-244-0360 to book!", "caption_es": "x", "video_brief": "x"}, "carries the Zelle account number"),
    ({"caption_en": "Call (305) 244-0360 to book!", "caption_es": "x", "video_brief": "x"}, "carries the Zelle account number"),
    ({"caption_en": "Text 3052440360 today", "caption_es": "x", "video_brief": "x"}, "carries the Zelle account number"),
    ({"caption_en": "Llame al +1 305 244 0360", "caption_es": "x", "video_brief": "x"}, "carries the Zelle account number"),
])
def test_copy_rule_violations_rejected(tmp_path, bad_reply, flag):
    t = fake_transport_for(bad_reply)
    a = OpenAIContentAdapter(api_key="test-key", transport=t)
    out = a.generate(BRIEF, str(tmp_path / "q"))
    assert out["asset"] is None
    manifest = json.load(open(out["manifest"], encoding="utf-8"))
    assert flag in manifest["rejected"]
    assert not os.path.exists(str(tmp_path / "q" / "generated.json"))


# ------------------------------------------- shared paid-call quota ----------

def _refusal_case(tmp_path, transport):
    a = OpenAIContentAdapter(api_key="test-key", model="test-model", transport=transport)
    out = a.generate(BRIEF, str(tmp_path / "q"))
    manifest = json.load(open(out["manifest"], encoding="utf-8"))
    return out, manifest


def test_default_and_zero_cap_disable_paid_generation(tmp_path, monkeypatch):
    def must_not_call(payload):
        pytest.fail("no transport call may happen with paid generation disabled")
    for value in (None, "0", "banana"):
        if value is None:
            monkeypatch.delenv("MPN_API_DAILY_CALL_CAP", raising=False)
        else:
            monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", value)
        out, manifest = _refusal_case(tmp_path / ("case-%s" % value), must_not_call)
        assert out["asset"] is None
        assert any("disabled by default" in r for r in manifest["rejected"])
        assert "no API request was made" in manifest["note"]


def test_shared_slots_from_other_adapter_reduce_this_allowance(tmp_path, monkeypatch):
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "1")
    quota = tmp_path / "quota"
    quota.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("MPN_API_QUOTA_DIR", str(quota))
    import datetime as _dt
    day = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    # A slot already claimed by the TRIAGE stack (same naming scheme).
    (quota / ("%s-slot-000.json" % day)).write_text('{"adapter": "triage"}', encoding="utf-8")

    def must_not_call(payload):
        pytest.fail("the shared allowance is spent; no request may be sent")

    out, manifest = _refusal_case(tmp_path, must_not_call)
    assert out["asset"] is None
    assert any("budget cap reached" in r for r in manifest["rejected"])


def test_accounting_failure_refuses_spending(tmp_path, monkeypatch):
    blocked = tmp_path / "quota-as-file"
    blocked.write_text("not a directory", encoding="utf-8")
    monkeypatch.setenv("MPN_API_QUOTA_DIR", str(blocked))

    def must_not_call(payload):
        pytest.fail("accounting failure must refuse the paid call")

    out, manifest = _refusal_case(tmp_path, must_not_call)
    assert out["asset"] is None
    assert any("accounting unavailable" in r for r in manifest["rejected"])


def test_successful_generation_claims_exactly_one_shared_slot(tmp_path):
    reply = {"caption_en": "Santa is coming! 786-975-9557",
             "caption_es": "¡Papá Noel llega! 786-975-9557",
             "video_brief": "20s vertical clip."}
    t = fake_transport_for(reply)
    a = OpenAIContentAdapter(api_key="test-key", model="test-model", transport=t)
    a.generate(BRIEF, str(tmp_path / "q"))
    quota = openai_adapter._api_quota_dir()
    slots = [p for p in os.listdir(quota) if "-slot-" in p]
    assert len(slots) == 1 and len(t.calls) == 1
    stored = open(os.path.join(quota, slots[0]), encoding="utf-8").read()
    assert "test-key" not in stored
