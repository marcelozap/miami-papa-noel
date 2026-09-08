"""Fail-closed local estimated-cost reservations; never makes network calls.

Keep the entire reservation, including after success: no usage-based refunds
or retries can accidentally restore money consumed by an uncertain request.
This is an application estimate gate, not a provider billing guarantee.
"""
import datetime as dt
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import json
import os
from pathlib import Path
import sqlite3


def private_path(raw):
    """Reject ambiguous/network aliases before any caller creates files."""
    spelling = os.fspath(raw)
    if not spelling or spelling.replace("\\", "/").startswith("//"):
        raise ValueError("network and device paths are not supported")
    path = Path(spelling)
    if not path.is_absolute():
        raise ValueError("absolute private path required")
    resolved = path.resolve()
    repo = Path(__file__).resolve().parents[2]
    if resolved.is_relative_to(repo):
        raise ValueError("repository storage refused")
    if os.path.normcase(str(resolved)) != os.path.normcase(str(path)):
        raise ValueError("use direct paths, not links or short names")
    return resolved


def _positive(value):
    number = Decimal(str(value))
    if not number.is_finite() or number <= 0:
        raise ValueError("invalid amount")
    return number


def reserve_cost(payload, directory):
    """Return None if reserved, otherwise a sanitized refusal code.

Policy is a private JSON file referenced by MPN_API_COST_POLICY. No default
budget or prices. UTF-8 envelope bytes plus 4096 protocol tokens conservatively
estimate text input including instructions/schema; not a measured token count.
Only these two bounded text endpoints are supported, without tools or media.
"""
    policy_path = os.environ.get("MPN_API_COST_POLICY")
    if not policy_path:
        return "COST_POLICY_REQUIRED"
    try:
        path = private_path(policy_path)
        root = private_path(directory)
        with path.open(encoding="utf-8") as stream:
            policy = json.loads(stream.read(65537))
        today = dt.datetime.now(dt.timezone.utc).date()
        verified = dt.date.fromisoformat(policy["verified_on"])
        if not 0 <= (today - verified).days <= 7:
            raise ValueError("rates stale")
        budget = _positive(policy["daily_cents"]) * 10000
        if budget != budget.to_integral_value() or budget > 100000000:
            raise ValueError("budget precision or size")
        model = payload["model"]
        rates = policy["models"][model]
        input_rate = _positive(rates["input_usd_per_million"])
        output_rate = _positive(rates["output_usd_per_million"])
        if not str(rates["source"]).startswith("https://developers.openai.com/"):
            raise ValueError("official pricing source required")
        # A payload must belong to exactly one endpoint. Never validate one
        # spelling while allowing another unchecked field to be dispatched.
        if "input" in payload:
            allowed = {"model", "store", "input", "text", "max_output_tokens"}
            messages = payload["input"]
            limit = payload.get("max_output_tokens")
        else:
            allowed = {"model", "store", "messages", "response_format", "max_completion_tokens"}
            messages = payload.get("messages")
            limit = payload.get("max_completion_tokens")
        if set(payload) - allowed:
            raise ValueError("unsupported billing feature")
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError("unsupported messages")
        for message in messages:
            if set(message) != {"role", "content"}:
                raise ValueError("unsupported message")
            content = message["content"]
            if not isinstance(content, str):
                if not isinstance(content, list) or not content:
                    raise ValueError("unsupported content")
                for item in content:
                    if (set(item) != {"type", "text"}
                            or item["type"] != "input_text"
                            or not isinstance(item["text"], str)):
                        raise ValueError("non-text content")
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if type(limit) is not int or not 0 < limit <= 4096 or len(encoded) > 65536:
            raise ValueError("unbounded payload")
        # USD/million tokens numerically equals microdollars/token. Charge
        # uncached input with 25% headroom, including potential cache writes.
        cost = int(((len(encoded) + 4096) * input_rate * Decimal("1.25")
                    + limit * output_rate).to_integral_value(rounding=ROUND_CEILING))
        if cost <= 0 or cost > int(budget):
            return "COST_BUDGET_REACHED"
    except (OSError, ValueError, TypeError, KeyError, InvalidOperation, OverflowError, RuntimeError):
        return "COST_POLICY_INVALID"

    connection = None
    try:
        root.mkdir(parents=True, exist_ok=True)
        database = private_path(root / "cost-reservations.sqlite3")
        connection = sqlite3.connect(str(database), timeout=5)
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("CREATE TABLE IF NOT EXISTS daily "
                           "(day TEXT PRIMARY KEY, budget INTEGER NOT NULL, "
                           "reserved INTEGER NOT NULL)")
        day = today.isoformat()
        row = connection.execute("SELECT budget, reserved FROM daily WHERE day=?", (day,)).fetchone()
        if row is None:
            ceiling, used = int(budget), 0
            connection.execute("INSERT INTO daily VALUES (?, ?, 0)", (day, ceiling))
        else:
            ceiling, used = row
            if (type(ceiling) is not int or type(used) is not int
                    or ceiling <= 0 or used < 0 or used > ceiling):
                raise ValueError("corrupt accounting")
            # Never silently raise today's already established allowance.
            if int(budget) != ceiling:
                return "COST_POLICY_CHANGED_TODAY"
        if used + cost > ceiling:
            return "COST_BUDGET_REACHED"
        connection.execute("UPDATE daily SET reserved=? WHERE day=?", (used + cost, day))
        connection.commit()
        return None
    except (OSError, sqlite3.Error, ValueError, OverflowError, RuntimeError):
        return "COST_ACCOUNTING_UNAVAILABLE"
    finally:
        if connection is not None:
            connection.close()
