#!/usr/bin/env python3
"""Validate premium-date slot assignments against the lead tracker."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLOTS_PATH = ROOT / "schedules" / "peak_slots_2026.json"
TRACKER_PATH = ROOT / "lead-tracker.csv"

REQUIRED_COLUMNS = {
    "target_date",
    "time_slot_id",
    "state",
    "deposit_status",
    "zelle_memo_id",
}

# Canonical state names (tools/slots/slots.py) map onto the legacy names this
# validator was built around. One state machine, two spellings accepted.
CANONICAL_ALIASES = {
    "HELD": "HOLD_48HR",
    "BOOKED": "CONFIRMED",
}
# DEPOSIT_SENT is deliberately NOT aliased to DEPOSIT_PAID: "sent" means the
# customer says money is on the way and NOTHING is verified yet. Treating it
# as PAID would demand a payment record before any human checked Zelle.

LOCKING_STATES = {"HOLD_48HR", "DEPOSIT_SENT", "DEPOSIT_PAID", "CONFIRMED"}
TERMINAL_STATES = {"DEPOSIT_PAID", "CONFIRMED"}
ACTIVE_STATES = LOCKING_STATES | {"OPEN"}
DEPOSIT_STATUSES = {
    "",
    "UNPAID",
    "REQUESTED",
    "PAID",
    "TRANSFERRED",
    "FORFEIT",
}
CUSTOMER_NAME_FIELDS = ("Business Name", "Contact Name")
CUSTOMER_CONTACT_FIELDS = ("Phone", "Email", "Instagram")
CUSTOMER_LOCATION_FIELDS = ("Area", "Notes")


def load_slots() -> dict[str, dict[str, str]]:
    with SLOTS_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    allowed_states = set(payload.get("allowed_states", []))
    missing_states = LOCKING_STATES - allowed_states
    if missing_states:
        raise ValueError(
            f"{SLOTS_PATH} is missing required states: {sorted(missing_states)}"
        )

    slots = {}
    for slot in payload.get("slots", []):
        slot_id = slot.get("slot_id")
        if not slot_id:
            raise ValueError(f"{SLOTS_PATH} contains a slot without slot_id")
        if slot_id in slots:
            raise ValueError(f"{SLOTS_PATH} contains duplicate slot_id {slot_id}")
        slots[slot_id] = slot

    return slots


def load_tracker_rows() -> tuple[list[dict[str, str]], list[str]]:
    with TRACKER_PATH.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        return list(reader), fieldnames


def row_label(row_number: int, row: dict[str, str]) -> str:
    name = row.get("Business Name") or row.get("Contact Name") or "Unnamed lead"
    return f"row {row_number} ({name})"


def has_any_value(row: dict[str, str], fields: tuple[str, ...]) -> bool:
    return any((row.get(field) or "").strip() for field in fields)


def validate() -> list[str]:
    slots = load_slots()
    rows, fieldnames = load_tracker_rows()
    errors: list[str] = []

    missing_columns = REQUIRED_COLUMNS - set(fieldnames)
    if missing_columns:
        errors.append(f"lead-tracker.csv missing columns: {sorted(missing_columns)}")
        return errors

    slots_by_date: dict[str, set[str]] = defaultdict(set)
    for slot_id, slot in slots.items():
        slots_by_date[slot.get("date", "")].add(slot_id)

    slot_locks: dict[str, list[str]] = defaultdict(list)
    date_locks: dict[str, set[str]] = defaultdict(set)
    allowed_states = {"", "OPEN", "HOLD_48HR", "DEPOSIT_SENT", "DEPOSIT_PAID", "CONFIRMED"}

    for offset, row in enumerate(rows, start=2):
        label = row_label(offset, row)
        state = (row.get("state") or "").strip()
        state = CANONICAL_ALIASES.get(state, state)
        slot_id = (row.get("time_slot_id") or "").strip()
        target_date = (row.get("target_date") or "").strip()
        deposit_status = (row.get("deposit_status") or "").strip()
        zelle_memo_id = (row.get("zelle_memo_id") or "").strip()

        if state not in allowed_states:
            errors.append(f"{label}: invalid state {state!r}")

        if deposit_status not in DEPOSIT_STATUSES:
            errors.append(f"{label}: invalid deposit_status {deposit_status!r}")

        if state in ACTIVE_STATES and state:
            if not has_any_value(row, CUSTOMER_NAME_FIELDS):
                errors.append(f"{label}: {state} requires a client or contact name")
            if not has_any_value(row, CUSTOMER_CONTACT_FIELDS):
                errors.append(f"{label}: {state} requires phone, email, or Instagram")
            if not has_any_value(row, CUSTOMER_LOCATION_FIELDS):
                errors.append(f"{label}: {state} requires area or address notes")

        if state in LOCKING_STATES and not slot_id:
            errors.append(f"{label}: {state} requires time_slot_id")

        if slot_id:
            slot = slots.get(slot_id)
            if not slot:
                errors.append(f"{label}: unknown time_slot_id {slot_id!r}")
            elif target_date and target_date != slot.get("date"):
                errors.append(
                    f"{label}: target_date {target_date!r} does not match "
                    f"{slot_id} date {slot.get('date')!r}"
                )

        if state in TERMINAL_STATES:
            if deposit_status != "PAID":
                errors.append(f"{label}: {state} requires deposit_status PAID")
            if not zelle_memo_id:
                errors.append(f"{label}: {state} requires zelle_memo_id")

        if state in LOCKING_STATES and slot_id:
            slot_locks[slot_id].append(label)
            slot_date = slots.get(slot_id, {}).get("date")
            if slot_date:
                date_locks[slot_date].add(slot_id)

    for slot_id, labels in sorted(slot_locks.items()):
        if len(labels) > 1:
            errors.append(
                f"{slot_id} is locked by multiple leads: {', '.join(labels)}"
            )

    for slot_date, locked_slots in sorted(date_locks.items()):
        capacity = len(slots_by_date.get(slot_date, set()))
        if len(locked_slots) > capacity:
            errors.append(
                f"{slot_date} has {len(locked_slots)} locked slots but only "
                f"{capacity} scheduled slots"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Slot validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Slot validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
