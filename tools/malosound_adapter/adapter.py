#!/usr/bin/env python3
"""Adapter boundary for MaloSound.ai content technology.

STATUS: NOT_CONFIGURED - and honest about it.

This module defines the ONLY doorway through which Miami Papa Noel content
work could ever hand facts to MaloSound.ai tooling. It exists so the boundary
is designed, reviewed, and privacy-safe BEFORE any integration is real.
No API endpoint, credential, or wire format is invented here: none exists in
local evidence, so every outbound call raises AdapterNotConfigured.

What IS real and testable today:

- `status()` reports NOT_CONFIGURED (it would report DRY-RUN or LIVE only if
  real local evidence - configuration plus a tested connection - existed).
- `content_facts(...)` distills a BOOKED reservation into the privacy-safe
  facts a content draft may use, and nothing else. Customer names, phone
  numbers, addresses, payment amounts, memo refs, and operator identities
  are stripped by construction; only coarse, publicly shareable facts leave:
  the date, the time window, the venue KIND (never the venue), and the
  package label. Refuses non-BOOKED reservations - content may only be
  generated from confirmed work.

Downstream, tools/content/queue.py remains the human-approval gate: even a
draft built from these facts cannot be published without an operator, and
publishing is blocked entirely until real social credentials exist.

Standard library only. No network code exists in this file.
"""
from __future__ import annotations

import argparse

STATUS_NOT_CONFIGURED = "NOT_CONFIGURED"
STATUS_DRY_RUN = "DRY-RUN"
STATUS_LIVE = "LIVE"

# Fields that must never cross the boundary, enforced and tested.
FORBIDDEN_FACT_KEYS = {
    "ref", "memo_ref", "amount", "verified", "operator", "name", "phone",
    "email", "address", "address_or_neighborhood", "notes", "held_until",
}

VENUE_KINDS = {
    "family_visit": ("a family home visit", "una visita familiar en casa"),
    "event_visit": ("a community event visit", "una visita a un evento"),
    "christmas_eve": ("a Christmas Eve delivery", "una entrega de Nochebuena"),
    "christmas_eve_late": ("a late Christmas Eve gift drop",
                           "una entrega tarde de Nochebuena"),
    "hoa_community": ("a residential community event",
                      "un evento de comunidad residencial"),
    "school_daycare": ("a school visit", "una visita escolar"),
    "corporate": ("a workplace holiday visit",
                  "una visita navidena de empresa"),
}


class AdapterNotConfigured(Exception):
    """No MaloSound.ai endpoint, credential, or tested connection exists.

    Do not invent one. If a real integration ever lands, its evidence
    (configuration + a tested connection) changes status() first, and only
    then may transport code be written."""


def status() -> str:
    """NOT_CONFIGURED is the only status local evidence supports. This is a
    constant on purpose: flipping it requires real configuration to exist,
    not a code edit that claims it does."""
    return STATUS_NOT_CONFIGURED


def content_facts(slot_entry: dict, catalog_slot: dict,
                  package_label_en: str = "", package_label_es: str = "") -> dict:
    """Privacy-safe facts from a BOOKED reservation, for content drafting.

    Refuses anything not BOOKED: content is generated only from confirmed
    reservations. Output carries no customer data by construction."""
    state = str(slot_entry.get("state", "")).upper()
    if state not in ("BOOKED", "CONFIRMED"):
        raise ValueError(
            "content facts come only from a BOOKED reservation; got state %r"
            % state)
    category = str(catalog_slot.get("category")
                   or catalog_slot.get("package") or "").strip()
    kind_en, kind_es = VENUE_KINDS.get(
        category, ("a private Santa visit", "una visita privada de Santa"))
    start = catalog_slot.get("start_time")
    end = catalog_slot.get("end_time")
    window = ("%s-%s" % (start, end)) if start and end else str(
        catalog_slot.get("window") or "")
    facts = {
        "date": str(catalog_slot.get("date") or ""),
        "window": window,
        "venue_kind_en": kind_en,
        "venue_kind_es": kind_es,
        "package_label_en": package_label_en,
        "package_label_es": package_label_es,
    }
    leaked = FORBIDDEN_FACT_KEYS & set(facts)
    assert not leaked, "forbidden keys in facts: %s" % leaked
    return facts


def handoff(_facts: dict) -> None:
    """The outbound call that does not exist. Always raises."""
    raise AdapterNotConfigured(
        "MaloSound.ai integration is NOT_CONFIGURED: no endpoint, credential, "
        "or tested connection exists in local evidence, and none may be "
        "invented. Use tools/content/queue.py for local draft-only content "
        "with human approval.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="report the adapter status honestly")
    args = ap.parse_args(argv)
    if args.cmd == "status":
        print("MaloSound.ai adapter: %s" % status())
        print("No endpoint, credential, or tested connection exists locally.")
        print("Content stays local and draft-only via tools/content/queue.py;")
        print("human approval is required before anything is published.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
