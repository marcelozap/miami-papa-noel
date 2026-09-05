#!/usr/bin/env python3
"""Elf outreach - public-prospect research log and bilingual message DRAFTS.

    RESEARCHED -> DRAFTED -> APPROVED_FOR_MANUAL_SEND -> SENT_BY_HUMAN
                     DO_NOT_CONTACT (terminal, reachable from any state)

What it does: records PUBLIC business prospects (schools, HOAs, businesses,
nonprofits, community events) that were researched through a public contact
path, and generates a deterministic bilingual (EN + ES) outreach draft per
category. Every draft introduces the Miami Papa Noel santa visit service,
the bilingual offering, the public phone 786-975-9557 and the official email
santa@miamipapanoel.com, and asks who coordinates holiday events.

What it does NOT do: send, post, publish, call, or submit anything, anywhere.
There is no send path. A human sends every message manually via the prospect's
public contact path, one at a time, and records the fact afterwards with
`record-sent --operator ... --sent-via ...`. It never claims an affiliation,
partnership, endorsement, or insurance. It refuses personal-looking email
addresses (firstname.lastname at a free provider) - only public org contact
paths (info@, office@, frontdesk@, org domains, URLs, public forms) are
accepted. It refuses job-board style org names and it refuses to stockpile
drafts: at most 15 prospects may sit in DRAFTED at once (anti-spam - drafts
must be sent and recorded, not hoarded).

Prospect records and the outreach log live OUTSIDE the repository:

    %MPN_ELVES_DIR%  or  %LOCALAPPDATA%\\MiamiPapaNoel\\elves\\
        prospects.json      current record per prospect (ref P-001, P-002...)
        outreach-log.jsonl  append-only audit trail (one line per action)

Standard library only. Synthetic data only in the repository.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

PUBLIC_PHONE = "786-975-9557"
OFFICIAL_EMAIL = "santa@miamipapanoel.com"

RESEARCHED = "RESEARCHED"
DRAFTED = "DRAFTED"
APPROVED = "APPROVED_FOR_MANUAL_SEND"
SENT_BY_HUMAN = "SENT_BY_HUMAN"
DO_NOT_CONTACT = "DO_NOT_CONTACT"

STATES = [RESEARCHED, DRAFTED, APPROVED, SENT_BY_HUMAN, DO_NOT_CONTACT]

CATEGORIES = ["school", "hoa", "business", "nonprofit", "community_event"]

# Org names that indicate a scraped listing site, not a real local prospect.
FORBIDDEN_ORG_TERMS = ("job board", "indeed", "linkedin jobs", "craigslist")

# A custom line may add local color, never a claim we cannot back.
FORBIDDEN_CUSTOM_TERMS = ("affiliated", "official partner", "endorsed",
                          "on behalf of", "insured",
                          "certificate of insurance")

FREE_PROVIDERS = ("gmail.com", "yahoo.com", "hotmail.com", "outlook.com")

# Anti-spam: at most this many prospects may sit in DRAFTED at once.
DRAFTED_CAP = 15

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
URL_RE = re.compile(r"^(https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/\S*)?$")
PERSONAL_LOCAL_RE = re.compile(r"^[a-z]+[._-][a-z]+$")
# At a free provider, only clearly organizational mailbox names are accepted;
# anything else (janedoe@gmail.com, mariagonzalez1985@yahoo.com) is treated
# as a personal address and refused.
ORG_LOCALS = re.compile(
    r"^(info|office|contact|hello|admin|frontdesk|events?|bookings?|hoa|pta|"
    r"school|director|manager|community|activities|recreation|social)"
    r"[a-z0-9._-]*$")

# Category-specific opening lines. ASCII only (Windows console); the Spanish
# deliberately drops accents for that reason, matching the house style.
CATEGORY_INTROS = {
    "school": (
        "Miami Papa Noel offers bilingual (English/Spanish) Santa visits "
        "for schools and daycares around Miami.",
        "Miami Papa Noel ofrece visitas de Santa bilingues (ingles/espanol) "
        "para escuelas y guarderias en el area de Miami."),
    "hoa": (
        "Miami Papa Noel offers bilingual (English/Spanish) Santa visits "
        "for HOA and community clubhouse celebrations around Miami.",
        "Miami Papa Noel ofrece visitas de Santa bilingues (ingles/espanol) "
        "para celebraciones de HOA y comunidades en el area de Miami."),
    "business": (
        "Miami Papa Noel offers bilingual (English/Spanish) Santa visits "
        "for businesses, offices, and storefront events around Miami.",
        "Miami Papa Noel ofrece visitas de Santa bilingues (ingles/espanol) "
        "para negocios, oficinas y eventos de tiendas en el area de Miami."),
    "nonprofit": (
        "Miami Papa Noel offers bilingual (English/Spanish) Santa visits "
        "for nonprofit and community organizations around Miami.",
        "Miami Papa Noel ofrece visitas de Santa bilingues (ingles/espanol) "
        "para organizaciones sin fines de lucro en el area de Miami."),
    "community_event": (
        "Miami Papa Noel offers bilingual (English/Spanish) Santa visits "
        "for community events and festivals around Miami.",
        "Miami Papa Noel ofrece visitas de Santa bilingues (ingles/espanol) "
        "para eventos comunitarios y festivales en el area de Miami."),
}


class OutreachError(Exception):
    pass


# ------------------------------------------------------------------ storage --

def state_dir() -> Path:
    override = os.environ.get("MPN_ELVES_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "elves"


def store_path() -> Path:
    return state_dir() / "prospects.json"


def log_path() -> Path:
    return state_dir() / "outreach-log.jsonl"


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def load_store() -> dict:
    path = store_path()
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    path = store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=1, ensure_ascii=False),
                    encoding="utf-8")


def append_log(ref: str, action: str, from_state: str, to_state: str,
               operator: str, detail: str) -> None:
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": now_iso(),
        "ref": ref,
        "action": action,
        "from": from_state,
        "to": to_state,
        "operator": operator,
        "detail": detail,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


# --------------------------------------------------------------- validation --

def validate_category(category: str) -> str:
    category = (category or "").strip().lower()
    if category not in CATEGORIES:
        raise OutreachError(
            "unknown category %r - must be one of: %s"
            % (category, ", ".join(CATEGORIES)))
    return category


def validate_org_name(org_name: str) -> str:
    org_name = (org_name or "").strip()
    if not org_name:
        raise OutreachError("org_name is required")
    lowered = org_name.lower()
    for term in FORBIDDEN_ORG_TERMS:
        if term in lowered:
            raise OutreachError(
                "org name %r contains %r - job boards and classifieds "
                "listings are not outreach prospects" % (org_name, term))
    return org_name


def validate_contact_path(contact_path: str) -> str:
    """A prospect exists only through a PUBLIC contact path: a URL, a public
    form, or a public org email. Personal-looking addresses are refused."""
    contact_path = (contact_path or "").strip()
    if not contact_path:
        raise OutreachError(
            "public_contact_path is required - a prospect without a public "
            "contact path (URL, public email, or public form) is not added")
    if "@" in contact_path:
        if not EMAIL_RE.match(contact_path):
            raise OutreachError(
                "contact path %r is not a valid email address" % contact_path)
        local, domain = contact_path.rsplit("@", 1)
        if (domain.lower() in FREE_PROVIDERS
                and not ORG_LOCALS.match(local.lower())):
            raise OutreachError(
                "contact path %r looks like a PERSONAL address at a free "
                "provider - only clearly organizational mailboxes (info@, "
                "office@, frontdesk@, events@ ...) or org-domain addresses "
                "are accepted as public contact paths" % contact_path)
    elif not URL_RE.match(contact_path):
        raise OutreachError(
            "contact path %r is not a recognizable public URL, form, or "
            "email address" % contact_path)
    return contact_path


def validate_custom_line(custom_line: str) -> str:
    custom_line = (custom_line or "").strip()
    lowered = custom_line.lower()
    for term in FORBIDDEN_CUSTOM_TERMS:
        if term in lowered:
            raise OutreachError(
                "custom line refused: it contains %r - outreach never claims "
                "an affiliation, partnership, endorsement, or insurance"
                % term)
    return custom_line


# ------------------------------------------------------------------ actions --

def next_ref(store: dict) -> str:
    highest = 0
    for ref in store:
        m = re.fullmatch(r"P-(\d+)", ref)
        if m:
            highest = max(highest, int(m.group(1)))
    return "P-%03d" % (highest + 1)


def get_prospect(store: dict, ref: str) -> dict:
    if ref not in store:
        raise OutreachError("unknown prospect %r" % ref)
    return store[ref]


def require_not_suppressed(prospect: dict, ref: str, action: str) -> None:
    if prospect.get("state") == DO_NOT_CONTACT:
        raise OutreachError(
            "%s refused: prospect %s is DO_NOT_CONTACT, which is terminal - "
            "it is never drafted, approved, or contacted again" % (action, ref))


def add_prospect(store: dict, org_name: str, category: str, city: str,
                 contact_path: str, notes: str = "",
                 operator: str = "operator") -> dict:
    org_name = validate_org_name(org_name)
    category = validate_category(category)
    contact_path = validate_contact_path(contact_path)
    ref = next_ref(store)
    prospect = {
        "ref": ref,
        "org_name": org_name,
        "category": category,
        "city": (city or "").strip(),
        "public_contact_path": contact_path,
        "notes": (notes or "").strip(),
        "state": RESEARCHED,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    store[ref] = prospect
    append_log(ref, "add", "-", RESEARCHED, operator,
               "researched %s (%s) via public path %s"
               % (org_name, category, contact_path))
    return prospect


def drafted_count(store: dict) -> int:
    """Outstanding unsent messages: DRAFTED plus APPROVED_FOR_MANUAL_SEND.
    Counting only DRAFTED would let approve-hoarding stockpile unsent mail."""
    return sum(1 for p in store.values()
               if isinstance(p, dict) and p.get("state") in (DRAFTED, APPROVED))


def build_draft(prospect: dict, custom_line: str = "") -> str:
    """Deterministic bilingual draft. Same prospect + same custom line =
    byte-identical output. No affiliation claims, ever."""
    intro_en, intro_es = CATEGORY_INTROS[prospect["category"]]
    org = prospect["org_name"]
    city = prospect.get("city") or "Miami"
    lines = [
        "== DRAFT - a human sends this manually via the public contact "
        "path: %s ==" % prospect["public_contact_path"],
        "[EN] Hello %s! %s We are an independent local service and would "
        "love to bring a warm, bilingual Santa visit to %s this season. "
        "Who on your team coordinates holiday events? "
        "Phone/text/WhatsApp: %s. Email: %s. Thank you!"
        % (org, intro_en, city, PUBLIC_PHONE, OFFICIAL_EMAIL),
        "[ES] Hola %s! %s Somos un servicio local independiente y nos "
        "encantaria llevar una visita de Santa calida y bilingue a %s esta "
        "temporada. Quien en su equipo coordina los eventos navidenos? "
        "Telefono/texto/WhatsApp: %s. Correo: %s. Gracias!"
        % (org, intro_es, city, PUBLIC_PHONE, OFFICIAL_EMAIL),
    ]
    if custom_line:
        lines.append("[OPERATOR LINE - verify before sending] %s" % custom_line)
    return "\n".join(lines)


def draft(store: dict, ref: str, custom_line: str = "",
          operator: str = "operator") -> str:
    prospect = get_prospect(store, ref)
    require_not_suppressed(prospect, ref, "draft")
    if prospect["state"] != RESEARCHED:
        raise OutreachError(
            "draft refused: prospect %s is %s, not RESEARCHED"
            % (ref, prospect["state"]))
    if drafted_count(store) >= DRAFTED_CAP:
        raise OutreachError(
            "draft refused: %d prospects already sit in DRAFTED (cap %d). "
            "Anti-spam rule: drafts must be sent and recorded, not "
            "stockpiled. Approve and record-sent the existing drafts first."
            % (drafted_count(store), DRAFTED_CAP))
    custom_line = validate_custom_line(custom_line)
    text = build_draft(prospect, custom_line)
    prospect["state"] = DRAFTED
    prospect["draft"] = text
    prospect["updated_at"] = now_iso()
    append_log(ref, "draft", RESEARCHED, DRAFTED, operator,
               "bilingual draft generated (deterministic template, "
               "category %s)" % prospect["category"])
    return text


def approve(store: dict, ref: str, operator: str) -> dict:
    if not (operator or "").strip():
        raise OutreachError("approve requires --operator (a human name)")
    prospect = get_prospect(store, ref)
    require_not_suppressed(prospect, ref, "approve")
    if prospect["state"] != DRAFTED:
        raise OutreachError(
            "approve refused: prospect %s is %s, not DRAFTED"
            % (ref, prospect["state"]))
    prospect["state"] = APPROVED
    prospect["approved_by"] = operator
    prospect["updated_at"] = now_iso()
    append_log(ref, "approve", DRAFTED, APPROVED, operator,
               "approved for MANUAL send via %s"
               % prospect["public_contact_path"])
    return prospect


def record_sent(store: dict, ref: str, operator: str, sent_via: str) -> dict:
    """Recorded AFTER the fact, by the human who actually sent it. This tool
    has no send path."""
    if not (operator or "").strip():
        raise OutreachError("record-sent requires --operator (a human name)")
    if not (sent_via or "").strip():
        raise OutreachError("record-sent requires --sent-via "
                            "(how the human actually sent it)")
    prospect = get_prospect(store, ref)
    require_not_suppressed(prospect, ref, "record-sent")
    if prospect["state"] != APPROVED:
        raise OutreachError(
            "record-sent refused: prospect %s is %s, not %s"
            % (ref, prospect["state"], APPROVED))
    prospect["state"] = SENT_BY_HUMAN
    prospect["sent_via"] = sent_via
    prospect["sent_recorded_by"] = operator
    prospect["updated_at"] = now_iso()
    append_log(ref, "record-sent", APPROVED, SENT_BY_HUMAN, operator,
               "human reports the message was sent via %s" % sent_via)
    return prospect


def suppress(store: dict, ref: str, operator: str = "operator",
             reason: str = "") -> dict:
    prospect = get_prospect(store, ref)
    frm = prospect["state"]
    prospect["state"] = DO_NOT_CONTACT
    prospect["updated_at"] = now_iso()
    if reason:
        prospect["suppress_reason"] = reason
    append_log(ref, "suppress", frm, DO_NOT_CONTACT, operator,
               "suppressed (terminal): %s" % (reason or "no reason given"))
    return prospect


# ---------------------------------------------------------------------- CLI --

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="record a researched PUBLIC prospect")
    p.add_argument("--org", required=True)
    p.add_argument("--category", required=True,
                   help="|".join(CATEGORIES))
    p.add_argument("--city", required=True)
    p.add_argument("--contact", required=True,
                   help="PUBLIC contact path: URL, public form, or public "
                        "org email (info@..., never a personal address)")
    p.add_argument("--notes", default="")
    p.add_argument("--operator", default="operator")

    p = sub.add_parser("draft",
                       help="RESEARCHED -> DRAFTED; print bilingual draft")
    p.add_argument("--ref", required=True)
    p.add_argument("--custom-line", default="",
                   help="optional extra line; affiliation/insurance claims "
                        "are refused")
    p.add_argument("--operator", default="operator")

    p = sub.add_parser("approve",
                       help="DRAFTED -> APPROVED_FOR_MANUAL_SEND")
    p.add_argument("--ref", required=True)
    p.add_argument("--operator", required=True)

    p = sub.add_parser("record-sent",
                       help="APPROVED_FOR_MANUAL_SEND -> SENT_BY_HUMAN "
                            "(after the fact; the human sent it)")
    p.add_argument("--ref", required=True)
    p.add_argument("--operator", required=True)
    p.add_argument("--sent-via", required=True,
                   help="how it was actually sent, e.g. 'contact form' or "
                        "'email from santa@miamipapanoel.com'")

    p = sub.add_parser("suppress",
                       help="any state -> DO_NOT_CONTACT (terminal)")
    p.add_argument("--ref", required=True)
    p.add_argument("--reason", default="")
    p.add_argument("--operator", default="operator")

    sub.add_parser("list", help="every prospect and its state")
    sub.add_parser("audit", help="print the append-only outreach log")

    args = ap.parse_args(argv)
    store = load_store()

    try:
        if args.cmd == "add":
            prospect = add_prospect(store, args.org, args.category, args.city,
                                    args.contact, args.notes, args.operator)
            save_store(store)
            print("RESEARCHED %s: %s (%s, %s) via %s"
                  % (prospect["ref"], prospect["org_name"],
                     prospect["category"], prospect["city"],
                     prospect["public_contact_path"]))
        elif args.cmd == "draft":
            text = draft(store, args.ref, args.custom_line, args.operator)
            save_store(store)
            print(text)
            print("DRAFTED %s - nothing was sent. A human sends this "
                  "manually, one prospect at a time." % args.ref)
        elif args.cmd == "approve":
            prospect = approve(store, args.ref, args.operator)
            save_store(store)
            print("APPROVED_FOR_MANUAL_SEND %s - send manually via the "
                  "public contact path (%s); never bulk-send."
                  % (args.ref, prospect["public_contact_path"]))
        elif args.cmd == "record-sent":
            record_sent(store, args.ref, args.operator, args.sent_via)
            save_store(store)
            print("SENT_BY_HUMAN %s - recorded after the fact (sent via %s "
                  "by %s)" % (args.ref, args.sent_via, args.operator))
        elif args.cmd == "suppress":
            suppress(store, args.ref, args.operator, args.reason)
            save_store(store)
            print("DO_NOT_CONTACT %s - terminal. This prospect is never "
                  "drafted, approved, or contacted again." % args.ref)
        elif args.cmd == "list":
            if not store:
                print("(no prospects)")
            for ref in sorted(store):
                p = store[ref]
                print("%-6s %-26s %-16s %-15s %s"
                      % (ref, p["org_name"][:26], p["category"],
                         p["city"][:15], p["state"]))
        elif args.cmd == "audit":
            path = log_path()
            if path.is_file():
                sys.stdout.write(path.read_text(encoding="utf-8"))
            else:
                print("(log empty)")
    except OutreachError as exc:
        print("REFUSED: %s" % exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
