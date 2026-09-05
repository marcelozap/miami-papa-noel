"""Lane 4 — Content agent (MaloSound creative lane).

Drafts bilingual (EN+ES) captions and a video brief for Facebook /
Instagram / TikTok — from CONFIRMED reservations ONLY. The gate is code,
not convention: any non-confirmed record reaching draft_posts raises
ContentGateError. Drafts land in content_queue/<id>/ with status 'draft';
only the operator marks them approved, and nothing here ever publishes.

Copy rules baked in: brand is "Miami Papa Noel" (unaccented — only the
character is "Papá Noel"); never claim "insured" (policy not purchased);
never include the client's address or family name in public copy; public
contact is 786-975-9557 — the Zelle account 305-244-0360 is a payment
rail, never a public contact line.
"""

import json
import os
import re

import store
from malosound_adapter import LocalDryRunAdapter
from rates import RATE_CARD
from zones import zone_map

BASE = os.path.dirname(os.path.abspath(__file__))
QUEUE_DIR = os.path.join(BASE, "content_queue")

ACTOR = "content_agent"

BANNED_PHRASES = ("insured", "asegurado", "Papá Noel llega con Miami Papá",
                  "305-244-0360")  # the Zelle account is not a contact line

ZELLE_DIGITS = "3052440360"


class ContentGateError(Exception):
    """A non-confirmed reservation reached the content lane."""


def _banned_phrase_in(text):
    """Return the banned phrase found in the text, or None.

    Phone numbers are compared with separators stripped, so formatted
    variants of the Zelle account — "(305) 244-0360", "3052440360",
    "+1 305 244 0360" — are caught the same as the literal.
    """
    low = text.lower()
    for banned in BANNED_PHRASES:
        if banned.lower() in low:
            return banned
    if ZELLE_DIGITS in re.sub(r"[\s().+\-]", "", text):
        return "305-244-0360 (formatted variant)"
    return None


def _caption(rec):
    pkg = RATE_CARD[rec["package"]]
    zone = zone_map()[rec["zone"]]
    en = (
        "Confirmed! Miami Papa Noel is coming to {zone} on {date}. "
        "{label}. Bilingual visit — English y español. "
        "December dates are filling: 786-975-9557 / miamipapanoel.com"
    ).format(zone=zone, date=rec["date"], label=pkg["label_en"])
    es = (
        "¡Confirmado! Papá Noel llega a {zone} el {date}. "
        "{label}. Visita bilingüe — español e inglés. "
        "Diciembre se está llenando: 786-975-9557 / miamipapanoel.com"
    ).format(zone=zone, date=rec["date"], label=pkg["label_es"])
    return en, es


def draft_posts(records, adapter=None):
    """Draft EN+ES content for confirmed reservations that have no draft
    yet. Raises ContentGateError if handed anything not confirmed."""
    for r in records:
        if r["status"] != "confirmed":
            raise ContentGateError(
                "record %s has status '%s' — only confirmed reservations may "
                "produce content; a hold or inquiry never triggers a public "
                "announcement" % (r["id"], r["status"])
            )
    adapter = adapter or LocalDryRunAdapter()
    made = []
    for rec in records:
        out_dir = os.path.join(QUEUE_DIR, rec["id"])
        draft_path = os.path.join(out_dir, "draft.json")
        if os.path.exists(draft_path):
            continue
        en, es = _caption(rec)
        for text in (en, es):
            hit = _banned_phrase_in(text)
            if hit:
                raise ContentGateError("banned phrase in draft: %s" % hit)
        os.makedirs(out_dir, exist_ok=True)
        draft = {
            "reservation": rec["id"],
            "status": "draft",   # -> approved (operator) -> published (operator)
            "platforms": ["facebook", "instagram", "tiktok"],
            "caption_en": en,
            "caption_es": es,
            "created_at": store.now_iso(),
        }
        with open(draft_path, "w", encoding="utf-8") as f:
            json.dump(draft, f, indent=2, ensure_ascii=False)
        brief = {
            "reservation": rec["id"],
            "kind": "short-form vertical video",
            "language": ["es", "en"],
            "caption_en": en,
            "caption_es": es,
        }
        adapter.generate(brief, out_dir)
        store.append_event(ACTOR, rec["id"], "confirmed", "confirmed",
                           "content drafted (awaiting operator approval)")
        made.append(draft_path)
    return made


def draft_for_all(records, adapter=None):
    """Safe entry point: filters to confirmed itself."""
    return draft_posts(store.confirmed_only(records), adapter)


def approve_draft(res_id, actor):
    """Only the operator approves a draft for publishing."""
    if actor != store.OPERATOR:
        raise ContentGateError("only the operator approves posts")
    draft_path = os.path.join(QUEUE_DIR, res_id, "draft.json")
    with open(draft_path, "r", encoding="utf-8") as f:
        draft = json.load(f)
    # Re-check at approval: a hand-edited draft obeys the same copy rules.
    for caption in (draft.get("caption_en", ""), draft.get("caption_es", "")):
        hit = _banned_phrase_in(caption)
        if hit:
            raise ContentGateError("banned phrase in draft: %s" % hit)
    draft["status"] = "approved"
    draft["approved_at"] = store.now_iso()
    with open(draft_path, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=2, ensure_ascii=False)
    return draft
