"""Check private storage over loopback; never call a model or follow redirects."""
from __future__ import annotations

import argparse
import http.client
import json
import os
from urllib.parse import urlsplit

STATUSES = frozenset({"queued", "drafting", "draft_ready", "blocked", "failed",
                      "approved", "rejected", "sent"})
MAX_RESPONSE = 8192


def check(origin, token, port=8226):
    if not isinstance(origin, str) or any(ord(c) < 33 or ord(c) == 127 for c in origin):
        raise ValueError("Invalid private health-check origin")
    parsed = urlsplit(origin)
    parsed.port  # Validate the optional port before building a Host header.
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in {"", "/"}
            or (parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost"})
            or not parsed.netloc.isascii() or any(ord(c) < 33 for c in parsed.netloc)
            or not isinstance(token, str) or len(token) < 32 or not token.isascii()
            or any(ord(c) < 33 or ord(c) == 127 for c in token)
            or type(port) is not int or not 1 <= port <= 65535):
        raise ValueError("Invalid private health-check configuration")
    # The origin supplies only the Host header. No credential leaves loopback.
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
    try:
        connection.request("GET", "/api/readiness", headers={
            "Host": parsed.netloc, "Authorization": "Bearer " + token,
            "X-MPN-Client-IP": "127.0.0.1",
        })
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("Private health check failed")
        raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise ValueError("Health response exceeded limit")
        data = json.loads(raw)
        if (not isinstance(data, dict) or data.get("status") != "ok"
                or data.get("scope") != "local_storage_only"
                or data.get("mode") not in {"demo", "live-enabled"}):
            raise ValueError("Unexpected health response")
        queue, errors = data.get("queue"), data.get("draft_errors")
        if (not isinstance(queue, dict) or set(queue) - STATUSES
                or any(type(n) is not int or n < 0 for n in queue.values())
                or type(errors) is not int or errors < 0):
            raise ValueError("Unexpected health counts")
        attention = bool(queue.get("failed", 0) or queue.get("blocked", 0) or errors)
        # Whitelist the output: unexpected fields can never leak private text.
        return {"status": "needs_attention" if attention else "ok",
                "scope": "local_storage_only", "mode": data["mode"],
                "queue": queue, "draft_errors": errors}
    finally:
        connection.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8226)
    args = parser.parse_args(argv)
    try:
        report = check(os.environ.get("MPN_PUBLIC_ORIGIN", ""),
                       os.environ.get("MPN_OPERATOR_TOKEN", ""), args.port)
    except (OSError, ValueError, TypeError, RecursionError, http.client.HTTPException):
        print('{"status":"unavailable","scope":"local_storage_only"}')
        return 1
    print(json.dumps(report, sort_keys=True))
    return 2 if report["status"] == "needs_attention" else 0


if __name__ == "__main__":
    raise SystemExit(main())
