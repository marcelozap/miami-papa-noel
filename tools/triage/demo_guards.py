#!/usr/bin/env python3
"""Live demonstration of the safety gates.

Shows a reviewer, in about fifteen seconds, that the gates actually block rather
than warn. Feeds two deliberately unsafe drafts through the validators and
prints the result.

    python tools/triage/demo_guards.py

Nothing here touches a customer, a log, or a network.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validators  # noqa: E402

PRICING = json.loads((HERE / "pricing.json").read_text(encoding="utf-8"))

EXTRACTED = {"requested_date": "2026-12-13", "category": "family_visit", "location": "Doral"}

CASES = [
    (
        "Every rule broken at once",
        "Your date is confirmed! The visit is $999 and you can pay by Venmo. "
        "We are fully insured and your deposit received today.",
        "Su fecha esta confirmada. La visita es $999.",
    ),
    (
        "Subtle: Spanish quotes a different price than English",
        "Thank you for reaching out. The Family Visit is $325 for the first hour. "
        "Payment is by Zelle only.",
        "Gracias por escribir. La Visita Familiar es $450 la primera hora. "
        "El pago es unicamente por Zelle.",
    ),
]


def main() -> int:
    print()
    print("SAFETY GATE DEMONSTRATION")
    print("Locked price list: %s" % PRICING["price_list_version"])
    print("=" * 70)

    total_blocked = 0
    for title, en, es in CASES:
        print()
        print("CASE: %s" % title)
        print("-" * 70)
        print("  EN: %s" % en)
        print("  ES: %s" % es)
        print()
        findings = validators.run_all(EXTRACTED, en, es, PRICING, policy_verified=False)
        for f in findings:
            mark = "X" if f.level == validators.FAIL else " "
            print("   %s %-5s %-20s %s" % (mark, f.level, f.check, f.detail))
        blocking = validators.blocking(findings)
        total_blocked += len(blocking)
        print()
        print("  RESULT: %d blocking failure(s) -> draft cannot be approved"
              % len(blocking) if blocking else "  RESULT: passes")

    print()
    print("=" * 70)
    print("%d blocking failures across %d cases." % (total_blocked, len(CASES)))
    print("A draft with any FAIL is never offered to the operator for approval.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
