#!/usr/bin/env python3
"""One command for the whole Miami Papa Noel local gauntlet.

    python scripts/ops_check.py            # everything
    python scripts/ops_check.py --fast     # skip the OPN preflight

Runs, in order: the full pytest battery (every suite in the repo), the slot
validator, the Ms. Claus public-page review, the committed-tracker privacy
scan, git diff --check, and (unless --fast) the OPN submission preflight.
Prints one PASS/FAIL line per step and exits non-zero if anything failed.

Standard library only. Read-only: changes nothing, sends nothing.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SUITES = [
    "tools/triage/test_triage.py",
    "scripts/test_validate_opn_submission.py",
    "scripts/test_evidence_index.py",
    "scripts/test_build_opn_packet.py",
    "tools/ms_claus/test_ms_claus.py",
    "tools/slots/test_slots.py",
    "tools/mrs_claus_office/test_intake.py",
    "tools/comms/test_comms.py",
    "tools/content/test_content.py",
    "tools/elves/test_elves.py",
    "tools/test_integration_season.py",
]


def run(label: str, cmd: list, timeout: int = 600) -> tuple:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, cwd=str(ROOT))
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, "%s: could not run (%s)" % (label, exc)
    tail = ((proc.stdout or "").strip().splitlines() or [""])[-1]
    return proc.returncode == 0, "%s: %s" % (label, tail or "exit %d" % proc.returncode)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fast", action="store_true",
                    help="skip the OPN submission preflight")
    args = ap.parse_args(argv)

    existing = [s for s in SUITES if (ROOT / s).is_file()]
    skipped = [s for s in SUITES if s not in existing]

    steps = [
        ("pytest battery",
         [sys.executable, "-m", "pytest", *existing, "-q"]),
        ("slot validator",
         [sys.executable, "scripts/validate_slot_confirmations.py"]),
        ("ms_claus review",
         [sys.executable, "tools/ms_claus/ms_claus.py"]),
        ("tracker privacy",
         [sys.executable, "tools/slots/slots.py", "check-tracker-privacy"]),
        ("git diff --check",
         ["git", "diff", "--check"]),
    ]
    if not args.fast:
        steps.append(("OPN preflight",
                      [sys.executable, "scripts/validate_opn_submission.py",
                       "--preflight"]))

    print("MIAMI PAPA NOEL OPS CHECK")
    print("=" * 60)
    failed = 0
    for label, cmd in steps:
        ok, detail = run(label, cmd)
        print("  %-4s %s" % ("PASS" if ok else "FAIL", detail))
        if not ok:
            failed += 1
    for s in skipped:
        print("  WARN suite missing: %s" % s)
    print("=" * 60)
    if failed:
        print("RESULT: FAIL - %d step(s) failed. Fix before operating." % failed)
        return 1
    print("RESULT: PASS - all steps green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
