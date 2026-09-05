"""Production monitoring — the daily health check.

Reports: stale holds (48h+ without a verified deposit), confirmed bookings
whose route turned tight/impossible after later bookings landed, drafts
waiting on operator approval, and records failing validation. Every run is
appended to data/health.log. Failure policy everywhere in this system: on
any check failure or out-of-scope input, the lane STOPS, logs, and
escalates to the operator — it never guesses.
"""

import json
import os
from datetime import datetime, timezone

import store
import logistics_agent
import content_agent

LOG_PATH = os.path.join(store.DATA_DIR, "health.log")
STALE_HOLD_HOURS = 48


def run(records):
    now = datetime.now(timezone.utc)
    report = {
        "at": store.now_iso(),
        "counts": {},
        "stale_holds": [],
        "route_regressions": [],
        "drafts_pending_approval": [],
        "invalid_records": [],
    }
    for s in store.STATUSES:
        report["counts"][s] = sum(1 for r in records if r["status"] == s)

    for r in records:
        if r["status"] == "hold" and r["deposit"]["status"] != "verified":
            created = datetime.fromisoformat(r["created_at"])
            age_h = (now - created).total_seconds() / 3600
            if age_h >= STALE_HOLD_HOURS:
                report["stale_holds"].append(
                    {"id": r["id"], "client": r["client_name"], "age_hours": round(age_h)}
                )

    for date in sorted({r["date"] for r in records if r.get("date")}):
        logistics_agent.check_date(records, date)
    for r in records:
        if r["status"] == "confirmed" and r.get("logistics", {}).get("result") in ("tight", "impossible"):
            report["route_regressions"].append(
                {"id": r["id"], "date": r["date"], "result": r["logistics"]["result"]}
            )

    if os.path.isdir(content_agent.QUEUE_DIR):
        for rid in sorted(os.listdir(content_agent.QUEUE_DIR)):
            p = os.path.join(content_agent.QUEUE_DIR, rid, "draft.json")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    if json.load(f).get("status") == "draft":
                        report["drafts_pending_approval"].append(rid)

    for r in records:
        if r["status"] not in store.STATUSES or r["deposit"]["status"] not in store.DEPOSIT_STATUSES:
            report["invalid_records"].append(r.get("id"))

    report["needs_operator"] = bool(
        report["stale_holds"] or report["route_regressions"]
        or report["drafts_pending_approval"] or report["invalid_records"]
    )
    os.makedirs(store.DATA_DIR, exist_ok=True)
    with open(os.path.join(store.DATA_DIR, "health.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")
    return report
