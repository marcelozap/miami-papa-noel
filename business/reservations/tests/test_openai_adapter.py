"""OpenAI adapter tests — no network, transport injected."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai_adapter import OpenAIContentAdapter


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
