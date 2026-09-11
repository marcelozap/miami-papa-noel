"""Public chat admission only. Never calls a model or authorizes spending."""
import hashlib
import hmac
import ipaddress
import json
import sqlite3
import time
import unicodedata

from tools.triage.spend_guard import private_path

MAX_BODY_BYTES = 4096
MAX_MESSAGE_CHARS = 1000


class InvalidRequest(ValueError):
    """Sanitized input refusal; never includes visitor text."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidRequest("CHAT_INVALID_REQUEST")
        result[key] = value
    return result


def parse_request(body):
    """Accept only a message and explicit consent, not client model/history data."""
    try:
        if not isinstance(body, bytes) or len(body) > MAX_BODY_BYTES:
            raise ValueError()
        value = json.loads(body.decode("utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(value, dict) or set(value) != {"message", "consent"}:
            raise ValueError()
        if value["consent"] is not True:
            raise ValueError()
        text = value["message"]
        if not isinstance(text, str) or not 0 < len(text) <= MAX_MESSAGE_CHARS:
            raise ValueError()
        text.encode("utf-8")
        if any(unicodedata.category(c) in ("Cc", "Cf", "Cs")
               and c not in "\n\r\t" for c in text):
            raise ValueError()
        text = text.strip()
        if not text:
            raise ValueError()
        return text
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise InvalidRequest("CHAT_INVALID_REQUEST") from None


class AdmissionGuard:
    """Shared SQLite reservations across workers; no raw IP/message storage.

    Limits cover admitted turns, including free templates, not billed dollars.
    A stable server-only secret and one private database are required.
    """

    def __init__(self, database, secret, *, clock=time.time):
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("CHAT_SERVER_SECRET_REQUIRED")
        self.database = private_path(database)
        self.secret = secret
        self.clock = clock

    def _hash(self, domain, text):
        return hmac.new(self.secret, (domain + text).encode("utf-8"),
                        hashlib.sha256).hexdigest()

    def reserve(self, address, message):
        """Return None to admit, otherwise a sanitized refusal code.

        Address MUST come from the verified transport/proxy, never JSON or
        unchecked forwarding headers. Read at most MAX_BODY_BYTES+1 first.
        """
        try:
            # Direct callers cannot bypass the message limits.
            message = parse_request(json.dumps(
                {"message": message, "consent": True}, ensure_ascii=False).encode())
            if not isinstance(address, str) or "%" in address:
                raise ValueError()
            address = ipaddress.ip_address(address)
            address = getattr(address, "ipv4_mapped", None) or address
            if address.is_unspecified or address.is_multicast:
                raise ValueError()
            caller = self._hash("ip:", str(address))
            normalized = " ".join(unicodedata.normalize("NFKC", message).casefold().split())
            fingerprint = self._hash("message:", normalized)
        except (ValueError, TypeError, UnicodeError):
            return "CHAT_INVALID_REQUEST"
        db = None
        try:
            stamp = int(self.clock())
            if stamp <= 0:
                raise ValueError()
            # Recheck before opening, so changed path aliases are refused.
            path = private_path(self.database)
            path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(path, timeout=2) as db:
                db.execute("PRAGMA synchronous=FULL")
                db.execute("BEGIN IMMEDIATE")
                db.execute("CREATE TABLE IF NOT EXISTS settings (identity TEXT NOT NULL)")
                identity = self._hash("config:", "v1:6/300:200/86400")
                saved = db.execute("SELECT identity FROM settings").fetchall()
                if saved and saved != [(identity,)]:
                    return "CHAT_ACCOUNTING_UNAVAILABLE"
                if not saved:
                    db.execute("INSERT INTO settings VALUES (?)", (identity,))
                db.execute("CREATE TABLE IF NOT EXISTS turns "
                           "(at INTEGER NOT NULL, caller TEXT NOT NULL, fingerprint TEXT NOT NULL)")
                latest = db.execute("SELECT MAX(at) FROM turns").fetchone()[0]
                if latest is not None and stamp < latest:
                    return "CHAT_ACCOUNTING_UNAVAILABLE"
                db.execute("DELETE FROM turns WHERE at <= ?", (stamp - 86400,))
                if db.execute("SELECT 1 FROM turns WHERE caller=? AND fingerprint=?",
                              (caller, fingerprint)).fetchone():
                    return "CHAT_DUPLICATE"
                if db.execute("SELECT COUNT(*) FROM turns WHERE caller=? AND at>?",
                              (caller, stamp - 300)).fetchone()[0] >= 6:
                    return "CHAT_RATE_LIMITED"
                if db.execute("SELECT COUNT(*) FROM turns").fetchone()[0] >= 200:
                    return "CHAT_CAPACITY_REACHED"
                db.execute("INSERT INTO turns VALUES (?,?,?)", (stamp, caller, fingerprint))
            return None
        except (OSError, sqlite3.Error, ValueError, OverflowError):
            return "CHAT_ACCOUNTING_UNAVAILABLE"
        finally:
            if db is not None:
                db.close()
