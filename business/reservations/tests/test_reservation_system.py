"""Gate tests — these are the production contract. If any of these fail,
the release does not ship."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import store
import reservation_agent
import logistics_agent
import operator_review as operator_lane
import content_agent
from malosound_adapter import LocalDryRunAdapter
from rates import RATE_CARD


@pytest.fixture(autouse=True)
def sandbox(tmp_path, monkeypatch):
    """Point every data path at a temp dir so tests never touch real data."""
    monkeypatch.setattr(store, "DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(store, "RES_PATH", str(tmp_path / "data" / "reservations.json"))
    monkeypatch.setattr(store, "EVENTS_PATH", str(tmp_path / "data" / "events.jsonl"))
    monkeypatch.setattr(content_agent, "QUEUE_DIR", str(tmp_path / "content_queue"))


def make_booking(records, zone="doral", time="15:00", package="christmas_eve",
                 duration=45, date="2026-12-24", name="Test Family"):
    rec = reservation_agent.create(
        records, client_name=name, phone="3050000000", package=package,
        date=date, start_time=time, duration_min=duration, zone=zone,
    )
    return rec


def to_pending(records, rec):
    reservation_agent.update(records, rec["id"], address="123 Test Ct",
                             guest_count=4)
    operator_lane.verify_deposit(records, rec["id"], amount=250,
                                 memo="12/24 Test Family")
    reservation_agent.advance(records, rec["id"])
    return rec


# ---------------------------------------------------------------- gates

def test_agent_advances_to_hold_only():
    records = []
    rec = make_booking(records)
    assert rec["status"] == "hold"  # data complete -> hold, no further


def test_agent_cannot_confirm():
    records = []
    rec = to_pending(records, make_booking(records))
    assert rec["status"] == "pending_review"
    with pytest.raises(store.TransitionError):
        store.transition(records, rec["id"], "confirmed", "reservation_agent")
    with pytest.raises(store.TransitionError):
        store.transition(records, rec["id"], "confirmed", "content_agent")


def test_agent_cannot_verify_deposit():
    records = []
    rec = make_booking(records)
    with pytest.raises(store.TransitionError):
        store.verify_deposit(records, rec["id"], "reservation_agent")


def test_unverified_deposit_blocks_pending_review():
    records = []
    rec = make_booking(records)
    reservation_agent.update(records, rec["id"], address="123 Test Ct",
                             guest_count=4)
    assert rec["status"] == "hold"  # blocked: deposit not verified
    rec["deposit"]["status"] = "claimed"  # client says they paid — not enough
    with pytest.raises(store.TransitionError):
        store.transition(records, rec["id"], "pending_review", "reservation_agent")


def test_operator_approve_happy_path():
    records = []
    rec = to_pending(records, make_booking(records))
    out = operator_lane.approve(records, rec["id"])
    assert out["status"] == "confirmed"
    assert out["operator_approval"]["approved_by"] == store.OPERATOR
    assert out["logistics"]["result"] in ("ok", "tight")


def test_confirm_requires_logistics_check():
    records = []
    rec = to_pending(records, make_booking(records))
    assert rec.get("logistics") is None
    with pytest.raises(store.TransitionError):
        store.transition(records, rec["id"], "confirmed", store.OPERATOR)


# ------------------------------------------------------------- logistics

def test_christmas_eve_same_zone_passes():
    records = []
    a = to_pending(records, make_booking(records, zone="doral", time="15:00"))
    b = to_pending(records, make_booking(records, zone="doral", time="16:00",
                                         name="Second Family"))
    operator_lane.approve(records, a["id"])
    out = operator_lane.approve(records, b["id"])
    assert out["status"] == "confirmed"


def test_impossible_route_blocked():
    """Doral -> Homestead back-to-back on Christmas Eve cannot be driven."""
    records = []
    a = to_pending(records, make_booking(records, zone="doral", time="15:00"))
    b = to_pending(records, make_booking(records, zone="homestead", time="16:00",
                                         name="Homestead Family"))
    operator_lane.approve(records, a["id"])
    with pytest.raises(store.TransitionError) as e:
        operator_lane.approve(records, b["id"])
    assert "impossible" in str(e.value)


def test_overlap_blocked():
    records = []
    a = to_pending(records, make_booking(records, zone="doral", time="15:00",
                                         duration=60, package="standard"))
    b = to_pending(records, make_booking(records, zone="doral", time="15:30",
                                         duration=60, package="standard",
                                         name="Overlap Family"))
    operator_lane.approve(records, a["id"])
    with pytest.raises(store.TransitionError):
        operator_lane.approve(records, b["id"])


def test_peak_evening_spacing():
    """90-min spacing, 60-min visits: nearby zone ok, far zone blocked."""
    records = []
    a = to_pending(records, make_booking(records, zone="doral", time="17:00",
                                         duration=60, package="peak_evening",
                                         date="2026-12-12"))
    ok = to_pending(records, make_booking(records, zone="coral_gables",
                                          time="18:30", duration=60,
                                          package="peak_evening",
                                          date="2026-12-12", name="Gables"))
    operator_lane.approve(records, a["id"])
    assert operator_lane.approve(records, ok["id"])["status"] == "confirmed"
    far = to_pending(records, make_booking(records, zone="fort_lauderdale",
                                           time="20:00", duration=60,
                                           package="peak_evening",
                                           date="2026-12-12", name="FTL"))
    with pytest.raises(store.TransitionError):
        operator_lane.approve(records, far["id"])


# --------------------------------------------------------------- content

def test_hold_produces_zero_content():
    records = []
    make_booking(records)  # a hold
    made = content_agent.draft_for_all(records)
    assert made == []


def test_non_confirmed_record_raises_in_content_lane():
    records = []
    rec = make_booking(records)
    with pytest.raises(content_agent.ContentGateError):
        content_agent.draft_posts([rec])


def test_confirmed_produces_bilingual_draft_and_dry_run():
    records = []
    rec = to_pending(records, make_booking(records))
    operator_lane.approve(records, rec["id"])
    made = content_agent.draft_for_all(records, LocalDryRunAdapter())
    assert len(made) == 1
    import json
    with open(made[0], encoding="utf-8") as f:
        draft = json.load(f)
    assert draft["status"] == "draft"
    assert "Miami Papa Noel" in draft["caption_en"]
    assert "español" in draft["caption_es"]
    assert "insured" not in draft["caption_en"].lower()
    assert "123 Test Ct" not in draft["caption_en"]  # never leak the address
    assert "Test Family" not in draft["caption_en"]  # never leak the name
    manifest = os.path.join(os.path.dirname(made[0]), "manifest.json")
    with open(manifest, encoding="utf-8") as f:
        assert json.load(f)["adapter"] == "local-dry-run"


def test_captions_use_public_phone_never_zelle_account():
    records = []
    rec = to_pending(records, make_booking(records))
    operator_lane.approve(records, rec["id"])
    made = content_agent.draft_for_all(records, LocalDryRunAdapter())
    import json
    with open(made[0], encoding="utf-8") as f:
        draft = json.load(f)
    for caption in (draft["caption_en"], draft["caption_es"]):
        assert "786-975-9557" in caption  # the public booking line
        assert "305-244-0360" not in caption  # the Zelle account is not public copy


def test_hand_edited_draft_with_zelle_variant_refused_at_approval():
    records = []
    rec = to_pending(records, make_booking(records))
    operator_lane.approve(records, rec["id"])
    made = content_agent.draft_for_all(records, LocalDryRunAdapter())
    import json
    with open(made[0], encoding="utf-8") as f:
        draft = json.load(f)
    draft["caption_en"] += " Call (305) 244-0360!"  # formatted Zelle variant
    with open(made[0], "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False)
    with pytest.raises(content_agent.ContentGateError):
        content_agent.approve_draft(rec["id"], store.OPERATOR)


def test_only_operator_approves_posts():
    records = []
    rec = to_pending(records, make_booking(records))
    operator_lane.approve(records, rec["id"])
    content_agent.draft_for_all(records)
    with pytest.raises(content_agent.ContentGateError):
        content_agent.approve_draft(rec["id"], "content_agent")
    assert content_agent.approve_draft(rec["id"], store.OPERATOR)["status"] == "approved"


# ----------------------------------------------------------- misc / data

def test_rate_card_complete():
    assert len(RATE_CARD) == 10
    for tier in RATE_CARD.values():
        assert tier["price"] > 0 and tier["label_en"] and tier["label_es"]


def test_schema_roundtrip(tmp_path):
    records = []
    to_pending(records, make_booking(records))
    p = str(tmp_path / "rt.json")
    store.save(records, p)
    assert store.load(p) == records


def test_health_flags_pending_draft():
    import health as health_lane
    records = []
    rec = to_pending(records, make_booking(records))
    operator_lane.approve(records, rec["id"])
    content_agent.draft_for_all(records)
    report = health_lane.run(records)
    assert rec["id"] in report["drafts_pending_approval"]
    assert report["needs_operator"] is True
