#!/usr/bin/env python3
"""Santa content queue for Miami Papa Noel - drafts only, nothing ever posts.

    DRAFT -> PENDING_APPROVAL -> APPROVED -> SCHEDULED_DRY_RUN

A PUBLISHED state exists in the enum so the vocabulary is stable, but every
path to it raises: publishing requires configured social credentials AND an
explicit operator approval at publish time, and neither exists in this
version. This tool never sends, posts, publishes, calls, or submits anything
anywhere. Every artifact it produces is a DRAFT a human posts manually.

Queue items reference performer-recorded videos by FILE PATH ONLY. The path
may point outside the repository; the tool never copies, moves, or reads the
video file.

The `draft` command generates DETERMINISTIC bilingual script and caption
drafts from the topic using fixed template strings - no model, no network,
same topic in, same text out. Templates mention only: Santa visits, Miami,
bilingual EN/ES service, the public phone 786-975-9557, and booking via text.
Topics that smell like fabricated social proof or unverified affiliations
(testimonial, review from, customer said, partnered with, official partner,
sponsored by, guaranteed) are refused outright - we never fabricate
testimonials, customers, affiliations, or credentials.

`schedule` (APPROVED only) assigns a suggested_post_time deterministically:
the next Tue/Thu/Sat strictly after today, at 10:00 or 18:00 local, chosen
round-robin across scheduled items. The item becomes SCHEDULED_DRY_RUN and
the tool says so plainly: DRY RUN - no account connected, post manually.

Queue state lives OUTSIDE the repository:

    %MPN_CONTENT_DIR%  or  %LOCALAPPDATA%\\MiamiPapaNoel\\content\\
        queue.json          current queue items
        content-log.jsonl   append-only audit trail (one line per action)

Standard library only. Synthetic data only in the repository.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

DRAFT = "DRAFT"
PENDING_APPROVAL = "PENDING_APPROVAL"
APPROVED = "APPROVED"
SCHEDULED_DRY_RUN = "SCHEDULED_DRY_RUN"
PUBLISHED = "PUBLISHED"  # exists in the enum; unreachable in this version

STATES = [DRAFT, PENDING_APPROVAL, APPROVED, SCHEDULED_DRY_RUN, PUBLISHED]

# The only legal transitions. PUBLISHED appears in no row on purpose.
TRANSITIONS = {
    (DRAFT, PENDING_APPROVAL): "submit",
    (PENDING_APPROVAL, APPROVED): "approve",
    (APPROVED, SCHEDULED_DRY_RUN): "schedule",
}

PUBLIC_PHONE = "786-975-9557"

PUBLISH_BLOCK_MESSAGE = (
    "publishing is blocked in this version: it requires configured social "
    "credentials AND explicit operator approval at publish time - neither "
    "exists here. There is no account connected and no send path. Post the "
    "approved draft manually.")

# Fabricated social proof and unverified affiliations are forbidden. Any topic
# containing one of these phrases is refused before a draft exists.
# Stems, not exact phrases: "our new partner Publix", "we guarantee smiles",
# "reviews from real customers" must all be refused. Over-refusal is fine -
# the operator can rephrase a legitimate topic; fabricated social proof and
# unverified affiliations can never be rephrased into being true.
FORBIDDEN_TOPIC_PHRASES = [
    "testimonial",
    "review",
    "customer",
    "client said",
    "partner",
    "sponsor",
    "guarantee",
    "endorse",
    "official",
    "affiliat",
    "on behalf of",
]

POST_WEEKDAYS = (1, 3, 5)  # Tue, Thu, Sat
POST_HOURS = (10, 18)      # 10:00 and 18:00 local, round-robin


class QueueError(Exception):
    pass


class TransitionError(QueueError):
    pass


class PublishBlockedError(TransitionError):
    pass


class ForbiddenTopicError(QueueError):
    pass


# ------------------------------------------------------------------ storage --

def state_dir() -> Path:
    override = os.environ.get("MPN_CONTENT_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "content"


def queue_path() -> Path:
    return state_dir() / "queue.json"


def log_path() -> Path:
    return state_dir() / "content-log.jsonl"


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def load_store() -> dict:
    path = queue_path()
    if not path.is_file():
        return {"items": {}, "schedule_seq": 0}
    store = json.loads(path.read_text(encoding="utf-8"))
    store.setdefault("items", {})
    store.setdefault("schedule_seq", 0)
    return store


def save_store(store: dict) -> None:
    path = queue_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=1, ensure_ascii=False),
                    encoding="utf-8")


def append_log(item_id: str, action: str, from_state: str, to_state: str,
               operator: str, detail: str) -> None:
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": now_iso(),
        "item_id": item_id,
        "action": action,
        "from": from_state,
        "to": to_state,
        "operator": operator,
        "detail": detail,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def get_item(store: dict, item_id: str) -> dict:
    item = store["items"].get(item_id)
    if item is None:
        raise TransitionError("unknown item %s" % item_id)
    return item


def next_item_id(store: dict) -> str:
    highest = 0
    for item_id in store["items"]:
        try:
            highest = max(highest, int(item_id.split("-", 1)[1]))
        except (IndexError, ValueError):
            continue
    return "C-%03d" % (highest + 1)


# ----------------------------------------------------------------- drafting --

def check_topic(topic: str) -> str:
    """Refuse topics that would fabricate social proof or affiliations."""
    topic = topic.strip()
    if not topic:
        raise ForbiddenTopicError("draft requires a non-empty --topic")
    folded = " ".join(topic.lower().split())
    for phrase in FORBIDDEN_TOPIC_PHRASES:
        if phrase in folded:
            raise ForbiddenTopicError(
                "topic refused: contains %r - fabricated social proof and "
                "unverified affiliations are forbidden. We never invent "
                "testimonials, customers, partners, or guarantees." % phrase)
    return topic


def draft_texts(topic: str) -> dict:
    """Deterministic bilingual drafts. Pure function of the topic - no model,
    no network, no randomness. Mentions only: Santa visits, Miami, bilingual
    EN/ES service, the public phone, and booking via text."""
    return {
        "script_en": (
            "Ho ho ho, Miami! Today Santa is talking about %s. "
            "We bring Santa visits all across Miami, fully bilingual in "
            "English and Spanish. To book your visit, send a text to %s."
            % (topic, PUBLIC_PHONE)),
        "script_es": (
            "Jo jo jo, Miami! Hoy Santa les habla de %s. "
            "Llevamos visitas de Santa por todo Miami, con servicio bilingue "
            "en ingles y espanol. Para reservar su visita, envie un texto al "
            "%s." % (topic, PUBLIC_PHONE)),
        "caption_en": (
            "Santa visits in Miami - bilingual EN/ES. %s. "
            "Book by text: %s" % (topic, PUBLIC_PHONE)),
        "caption_es": (
            "Visitas de Santa en Miami - servicio bilingue EN/ES. %s. "
            "Reserve por texto: %s" % (topic, PUBLIC_PHONE)),
    }


def create_draft(store: dict, video_path: str, topic: str) -> dict:
    """Create a DRAFT item. The video is referenced by path only and is never
    opened, read, or copied."""
    topic = check_topic(topic)
    if not video_path.strip():
        raise QueueError("draft requires a non-empty --video path")
    texts = draft_texts(topic)
    item_id = next_item_id(store)
    item = {
        "item_id": item_id,
        "video_path": video_path,
        "topic": topic,
        "created_at": now_iso(),
        "state": DRAFT,
        "script_en": texts["script_en"],
        "script_es": texts["script_es"],
        "caption_en": texts["caption_en"],
        "caption_es": texts["caption_es"],
        "suggested_post_time": None,
        "approvals": [],
    }
    store["items"][item_id] = item
    append_log(item_id, "draft", "-", DRAFT, "",
               "drafted from topic %r (video referenced by path only)" % topic)
    return item


# -------------------------------------------------------------- transitions --

def transition(store: dict, item_id: str, to_state: str, operator: str,
               detail: str = "") -> dict:
    item = get_item(store, item_id)
    frm = item["state"]
    if to_state == PUBLISHED:
        # Every path to PUBLISHED is blocked, from every state, always.
        append_log(item_id, "publish-refused", frm, frm, operator,
                   PUBLISH_BLOCK_MESSAGE)
        raise PublishBlockedError(PUBLISH_BLOCK_MESSAGE)
    action = TRANSITIONS.get((frm, to_state))
    if action is None:
        raise TransitionError(
            "illegal transition %s -> %s for item %s (legal path: DRAFT -> "
            "PENDING_APPROVAL -> APPROVED -> SCHEDULED_DRY_RUN)"
            % (frm, to_state, item_id))
    item["state"] = to_state
    item["updated_at"] = now_iso()
    append_log(item_id, action, frm, to_state, operator, detail)
    return item


def submit(store: dict, item_id: str, operator: str = "") -> dict:
    return transition(store, item_id, PENDING_APPROVAL, operator,
                      "submitted for operator approval")


def approve(store: dict, item_id: str, operator: str) -> dict:
    if not (operator or "").strip():
        raise TransitionError(
            "approve requires --operator (a human name); drafts are never "
            "self-approved")
    item = transition(store, item_id, APPROVED, operator,
                      "operator approved the draft")
    item["approvals"].append({
        "operator": operator,
        "at": now_iso(),
        "action": "approve",
    })
    return item


def next_post_time(seq: int, now: dt.datetime) -> dt.datetime:
    """Deterministic slot picker. Slot `seq` is the seq-th Tue/Thu/Sat
    strictly after now's date; the hour round-robins 10:00, 18:00."""
    day = now.date() + dt.timedelta(days=1)
    remaining = seq
    while True:
        if day.weekday() in POST_WEEKDAYS:
            if remaining == 0:
                break
            remaining -= 1
        day += dt.timedelta(days=1)
    hour = POST_HOURS[seq % len(POST_HOURS)]
    return dt.datetime.combine(day, dt.time(hour, 0))


def schedule(store: dict, item_id: str, operator: str,
             now: dt.datetime | None = None) -> dict:
    """APPROVED -> SCHEDULED_DRY_RUN. Assigns suggested_post_time; posts
    nothing. There is no account connected and no send path."""
    if now is None:
        now = dt.datetime.now()
    item = get_item(store, item_id)
    if item["state"] != APPROVED:
        raise TransitionError(
            "schedule refused: item %s is %s, not APPROVED. Only an "
            "operator-approved draft may be scheduled." % (item_id, item["state"]))
    seq = int(store.get("schedule_seq", 0))
    post_time = next_post_time(seq, now)
    item = transition(store, item_id, SCHEDULED_DRY_RUN, operator,
                      "DRY RUN scheduled for %s - no account connected, "
                      "post manually" % post_time.isoformat(timespec="seconds"))
    item["suggested_post_time"] = post_time.isoformat(timespec="seconds")
    store["schedule_seq"] = seq + 1
    return item


def publish(store: dict, item_id: str, operator: str = "") -> dict:
    """Always raises. Kept as an explicit command so the refusal is loud,
    logged, and explained instead of silently absent."""
    return transition(store, item_id, PUBLISHED, operator)


# ---------------------------------------------------------------- rendering --

def render_item(item: dict) -> str:
    lines = [
        "item        : %s" % item["item_id"],
        "state       : %s" % item["state"],
        "topic       : %s" % item["topic"],
        "video (ref) : %s" % item["video_path"],
        "created     : %s" % item["created_at"],
        "post time   : %s" % (item["suggested_post_time"] or "-- not scheduled --"),
        "approvals   : %s" % (", ".join(
            "%s at %s" % (a["operator"], a["at"]) for a in item["approvals"])
            or "none"),
        "",
        "-- SCRIPT (EN) --",
        item["script_en"],
        "",
        "-- SCRIPT (ES) --",
        item["script_es"],
        "",
        "-- CAPTION (EN) --",
        item["caption_en"],
        "",
        "-- CAPTION (ES) --",
        item["caption_es"],
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------- CLI --

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("draft", help="create a DRAFT with deterministic bilingual texts")
    p.add_argument("--video", required=True,
                   help="path to the performer-recorded video (never read or copied)")
    p.add_argument("--topic", required=True)

    p = sub.add_parser("submit", help="DRAFT -> PENDING_APPROVAL")
    p.add_argument("--item", required=True)
    p.add_argument("--operator", default="")

    p = sub.add_parser("approve", help="PENDING_APPROVAL -> APPROVED (human required)")
    p.add_argument("--item", required=True)
    p.add_argument("--operator", required=True)

    p = sub.add_parser("schedule",
                       help="APPROVED -> SCHEDULED_DRY_RUN; assigns a post time, posts nothing")
    p.add_argument("--item", required=True)
    p.add_argument("--operator", default="")

    p = sub.add_parser("publish",
                       help="always refused: no credentials, no publish-time approval")
    p.add_argument("--item", required=True)
    p.add_argument("--operator", default="")

    p = sub.add_parser("show", help="print one item with all draft texts")
    p.add_argument("--item", required=True)

    sub.add_parser("status", help="state of every queue item")
    sub.add_parser("audit", help="print the append-only log")

    args = ap.parse_args(argv)
    store = load_store()

    try:
        if args.cmd == "draft":
            item = create_draft(store, args.video, args.topic)
            save_store(store)
            print("DRAFT %s created. Nothing is posted anywhere." % item["item_id"])
            print(render_item(item))
        elif args.cmd == "submit":
            submit(store, args.item, args.operator)
            save_store(store)
            print("PENDING_APPROVAL %s - awaiting a human operator." % args.item)
        elif args.cmd == "approve":
            approve(store, args.item, args.operator)
            save_store(store)
            print("APPROVED %s by %s. Schedule with: queue.py schedule "
                  "--item %s" % (args.item, args.operator, args.item))
        elif args.cmd == "schedule":
            item = schedule(store, args.item, args.operator)
            save_store(store)
            print("SCHEDULED_DRY_RUN %s for %s"
                  % (args.item, item["suggested_post_time"]))
            print("DRY RUN - no account connected, post manually.")
        elif args.cmd == "publish":
            publish(store, args.item, args.operator)
        elif args.cmd == "show":
            print(render_item(get_item(store, args.item)))
        elif args.cmd == "status":
            if not store["items"]:
                print("(queue empty)")
            for item_id in sorted(store["items"]):
                item = store["items"][item_id]
                print("%-8s %-18s %-22s %s"
                      % (item_id, item["state"],
                         item["suggested_post_time"] or "-", item["topic"]))
        elif args.cmd == "audit":
            path = log_path()
            if path.is_file():
                sys.stdout.write(path.read_text(encoding="utf-8"))
            else:
                print("(log empty)")
    except QueueError as exc:
        print("REFUSED: %s" % exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
