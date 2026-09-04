"""Lane 3 — Operator review. The ONLY code paths that verify deposits and
confirm bookings. Every action lands in the event log."""

import store
import logistics_agent


def review(records):
    """Everything waiting on the operator, with its logistics result."""
    out = []
    for r in records:
        if r["status"] == "pending_review":
            if r.get("date"):
                logistics_agent.check_date(records, r["date"])
            out.append(r)
    return out


def verify_deposit(records, res_id, amount=None, memo=None):
    return store.verify_deposit(records, res_id, store.OPERATOR, amount, memo)


def approve(records, res_id):
    """Confirm a booking. Re-runs logistics first; store.py enforces the
    rest (verified deposit, operator actor, non-impossible route)."""
    logistics_agent.check_reservation(records, res_id)
    return store.transition(records, res_id, "confirmed", store.OPERATOR,
                            "operator approved")


def reject(records, res_id, reason):
    rec = store.find(records, res_id)
    if rec["status"] == "pending_review":
        return store.transition(records, res_id, "hold", store.OPERATOR,
                                "operator rejected: " + reason)
    return store.transition(records, res_id, "cancelled", store.OPERATOR,
                            "operator rejected: " + reason)


def complete(records, res_id):
    return store.transition(records, res_id, "completed", store.OPERATOR,
                            "visit done")


def cancel(records, res_id, reason=""):
    return store.transition(records, res_id, "cancelled", store.OPERATOR,
                            reason or "operator cancelled")
