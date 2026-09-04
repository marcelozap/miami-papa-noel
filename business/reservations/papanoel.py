"""Miami Papa Noel reservation system — operator CLI.

Run from anywhere:  python business\\reservations\\papanoel.py <command>

Commands:
  new         create an inquiry (reservation agent)
  update      add data to a reservation (reservation agent)
  list        show all reservations
  logistics   check a date's route feasibility
  verify-deposit  (operator) mark a Zelle deposit verified
  review      (operator) list pending_review with logistics results
  approve     (operator) confirm a booking
  reject      (operator) send back / cancel
  complete    (operator) mark the visit done
  content     draft posts for confirmed bookings (content agent)
  approve-post (operator) approve a draft for publishing
  health      run the daily production health check
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import store
import reservation_agent
import logistics_agent
import operator_review as operator_lane
import content_agent
import health as health_lane


def _p(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="papanoel")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new")
    for f in reservation_agent.FIELDS:
        p.add_argument("--" + f.replace("_", "-"))

    p = sub.add_parser("update")
    p.add_argument("id")
    for f in reservation_agent.FIELDS:
        p.add_argument("--" + f.replace("_", "-"))

    sub.add_parser("list")

    p = sub.add_parser("logistics")
    p.add_argument("date")

    p = sub.add_parser("verify-deposit")
    p.add_argument("id")
    p.add_argument("--amount", type=float)
    p.add_argument("--memo")

    sub.add_parser("review")

    p = sub.add_parser("approve")
    p.add_argument("id")

    p = sub.add_parser("reject")
    p.add_argument("id")
    p.add_argument("reason")

    p = sub.add_parser("complete")
    p.add_argument("id")

    sub.add_parser("content")

    p = sub.add_parser("approve-post")
    p.add_argument("id")

    sub.add_parser("health")

    args = ap.parse_args(argv)
    records = store.load()

    def fields_of(a):
        out = {}
        for f in reservation_agent.FIELDS:
            v = getattr(a, f, None)
            if v is not None:
                if f in ("duration_min", "setup_min", "guest_count"):
                    v = int(v)
                out[f] = v
        return out

    try:
        if args.cmd == "new":
            rec = reservation_agent.create(records, **fields_of(args))
            _p({"created": rec["id"], "status": rec["status"]})
        elif args.cmd == "update":
            rec = reservation_agent.update(records, args.id, **fields_of(args))
            _p({"updated": rec["id"], "status": rec["status"]})
        elif args.cmd == "list":
            _p([{k: r[k] for k in ("id", "status", "client_name", "date",
                                    "start_time", "zone", "package")} for r in records])
        elif args.cmd == "logistics":
            _p(logistics_agent.check_date(records, args.date))
        elif args.cmd == "verify-deposit":
            rec = operator_lane.verify_deposit(records, args.id, args.amount, args.memo)
            reservation_agent.advance(records, args.id)
            _p({"deposit": rec["deposit"], "status": rec["status"]})
        elif args.cmd == "review":
            _p([{k: r[k] for k in ("id", "client_name", "date", "start_time",
                                    "zone", "package", "logistics")}
                for r in operator_lane.review(records)])
        elif args.cmd == "approve":
            rec = operator_lane.approve(records, args.id)
            _p({"confirmed": rec["id"], "approval": rec["operator_approval"]})
        elif args.cmd == "reject":
            rec = operator_lane.reject(records, args.id, args.reason)
            _p({"id": rec["id"], "status": rec["status"]})
        elif args.cmd == "complete":
            rec = operator_lane.complete(records, args.id)
            _p({"id": rec["id"], "status": rec["status"]})
        elif args.cmd == "content":
            adapter = None
            if os.environ.get("OPENAI_API_KEY"):
                from openai_adapter import OpenAIContentAdapter
                adapter = OpenAIContentAdapter()
            made = content_agent.draft_for_all(records, adapter)
            _p({"drafts": made,
                "adapter": adapter.name if adapter else "local-dry-run"})
        elif args.cmd == "approve-post":
            _p(content_agent.approve_draft(args.id, store.OPERATOR))
        elif args.cmd == "health":
            _p(health_lane.run(records))
    except (store.TransitionError, content_agent.ContentGateError) as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        store.save(records)
        return 2
    store.save(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
