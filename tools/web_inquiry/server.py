"""Private inquiry review over the existing triage engine, never a booking store.

Run locally; place behind a configured HTTPS proxy before any public launch.
Public intake only saves a request. Only the authenticated operator can invoke
the model, approve a draft, or attest that they sent it themselves.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import hmac
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
import uuid

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools" / "triage"))
import triage

MAX_BODY = 16384
MIN_FREE_BYTES = 16 * 1024 * 1024
ASSETS = {
    "/app.css": (HERE / "app.css", "text/css"),
    "/app.js": (HERE / "app.js", "text/javascript"),
    "/santa.jpg": (ROOT / "assets" / "optimized" / "santa-photo-2-1600.jpg", "image/jpeg"),
}


def now():
    return dt.datetime.now(dt.timezone.utc)


def draft_revision(record_json):
    return hashlib.sha256(record_json.encode()).hexdigest() if record_json else None


def parse_ip(value):
    if not isinstance(value, str) or "%" in value:
        raise ValueError("Expected one unscoped IP address")
    address = ipaddress.ip_address(value)
    address = getattr(address, "ipv4_mapped", None) or address
    if address.is_unspecified or address.is_multicast:
        raise ValueError("Expected a concrete unicast IP address")
    return address


class Refused(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def private_path(path):
    path = Path(path).expanduser().resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError("Inquiry state and evidence must be outside the repository.")
    return path


def text_field(data, name, limit, required=True):
    value = data.get(name, "")
    if not isinstance(value, str) or len(value) > limit:
        raise Refused(400, "Invalid field / Campo no válido: " + name)
    value = value.strip()
    if required and not value:
        raise Refused(400, "Required field / Campo obligatorio: " + name)
    if any(ord(c) < 32 and c not in "\n\r\t" for c in value):
        raise Refused(400, "Invalid characters / Caracteres no válidos")
    try:
        value.encode("utf-8")
    except UnicodeError:
        raise Refused(400, "Invalid text encoding / Codificación de texto no válida") from None
    return value


class App:
    def __init__(self, data_dir, token, origin, *, live=False, builder=None, trusted_proxy=None):
        if not isinstance(token, str) or len(token) < 32 or not token.isascii():
            raise ValueError("Set MPN_OPERATOR_TOKEN to a private ASCII token of at least 32 characters.")
        parsed = urlsplit(origin)
        local = parsed.hostname in ("localhost", "127.0.0.1")
        if (parsed.scheme not in ("http", "https") or not parsed.netloc
                or parsed.path not in ("", "/") or parsed.query or parsed.fragment
                or parsed.username or (not local and parsed.scheme != "https")):
            raise ValueError("Origin must be an HTTPS origin, or localhost HTTP for local use.")
        self.origin = origin.rstrip("/")
        self.host = parsed.netloc.lower()
        self.token, self.live = token, live
        self.trusted_proxy = parse_ip(trusted_proxy) if trusted_proxy else None
        self.builder = builder or triage.build_record
        self.data_dir = private_path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database = self.data_dir / "inquiries.sqlite3"
        self.lease = (self.data_dir / "server.lock").open("a+b")
        self.lease.seek(0, 2)
        if not self.lease.tell():
            self.lease.write(b"0")
            self.lease.flush()
        self.lease.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.lease.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.lease.close()
            raise ValueError("Another inquiry service is using this data directory.") from None
        self.lock = threading.RLock()
        self.request_times = {}
        self.export_lock = threading.Lock()
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS inquiries (
                id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL,
                fingerprint TEXT UNIQUE NOT NULL, payload TEXT NOT NULL,
                status TEXT NOT NULL, received_at TEXT NOT NULL,
                record TEXT, reviewed_language TEXT)""")
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY, inquiry_id TEXT NOT NULL,
                at TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL)""")
            # A process restart cannot silently count an interrupted model call.
            for row in db.execute("SELECT id FROM inquiries WHERE status='drafting'").fetchall():
                self.event(db, row["id"], "system", "draft_interrupted")
            db.execute("UPDATE inquiries SET status='failed' WHERE status='drafting'")

    def close(self):
        self.lease.close()

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def event(db, inquiry_id, actor, action):
        db.execute("INSERT INTO events(inquiry_id,at,actor,action) VALUES(?,?,?,?)",
                   (inquiry_id, now().isoformat(timespec="seconds"), actor, action))

    def throttle(self, address, *, operator=False):
        bucket = hmac.new(self.token.encode(), address.encode(), hashlib.sha256).hexdigest()
        window, limit = (60, 30) if operator else (300, 5)
        key = (bucket, operator)
        stamp = time.monotonic()
        with self.lock:
            self.request_times = {k: [t for t in v if stamp - t < 300]
                                  for k, v in self.request_times.items()
                                  if v and stamp - v[-1] < 300}
            recent = [t for t in self.request_times.get(key, []) if stamp - t < window]
            total = sum(len(v) for k, v in self.request_times.items() if not k[1])
            if len(recent) >= limit or (not operator and total >= 100):
                raise Refused(429, "Please wait before retrying / Espere antes de reintentar")
            self.request_times[key] = recent + [stamp]

    def client_ip(self, peer, forwarded):
        address = parse_ip(peer)
        if self.trusted_proxy is None:
            return str(address)
        if address != self.trusted_proxy:
            raise Refused(403, "Proxy not allowed / Proxy no permitido")
        if len(forwarded) != 1:
            raise Refused(400, "One client address required / Se requiere una dirección de cliente")
        try:
            return str(parse_ip(forwarded[0]))
        except ValueError:
            raise Refused(400, "Invalid client address / Dirección de cliente no válida") from None

    def readiness(self):
        if shutil.disk_usage(self.data_dir).free < MIN_FREE_BYTES:
            raise Refused(503, "Storage unavailable / Almacenamiento no disponible")
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                # Probe main-database allocation, then roll back even on failure.
                # No inquiry, audit event or lasting schema change is created.
                db.execute("CREATE TABLE main._mpn_readiness_probe (data BLOB)")
                db.execute("INSERT INTO main._mpn_readiness_probe VALUES(zeroblob(65536))")
                db.execute("SELECT seq FROM events LIMIT 1").fetchone()
                counts = {row["status"]: row["n"] for row in db.execute(
                    "SELECT status,COUNT(*) AS n FROM inquiries GROUP BY status")}
                draft_errors = 0
                for row in db.execute("SELECT record FROM inquiries "
                                      "WHERE status IN ('draft_ready','blocked') AND record IS NOT NULL"):
                    try:
                        record = json.loads(row["record"])
                    except (ValueError, UnicodeError, TypeError, RecursionError):
                        raise Refused(503, "Stored draft unavailable / Borrador no disponible") from None
                    if not isinstance(record, dict):
                        raise Refused(503, "Stored draft unavailable / Borrador no disponible")
                    draft_errors += bool(record.get("error_code"))
            finally:
                if db.in_transaction:
                    db.rollback()
        return {"status": "ok", "scope": "local_storage_only", "queue": counts,
                "draft_errors": draft_errors, "mode": "live-enabled" if self.live else "demo"}

    def submit(self, data):
        name = text_field(data, "name", 100)
        contact = text_field(data, "contact", 160)
        message = text_field(data, "message", 3000)
        key = text_field(data, "request_key", 100)
        if not re.fullmatch(r"[A-Za-z0-9_-]{16,100}", key):
            raise Refused(400, "Invalid request identifier / Identificador no válido")
        phone = re.fullmatch(r"[+0-9 ()-]+", contact)
        if not (re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", contact)
                or (phone and 7 <= len(re.sub(r"\D", "", contact)) <= 15)):
            raise Refused(400, "Enter a phone or email / Ingrese teléfono o correo")
        if data.get("consent") is not True:
            raise Refused(400, "Contact consent required / Se requiere permiso de contacto")
        payload = json.dumps({"name": name, "contact": contact, "message": message},
                             ensure_ascii=False, sort_keys=True)
        received = now()
        digest = hashlib.sha256((received.date().isoformat() + payload).encode()).hexdigest()
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT * FROM inquiries WHERE request_key=?", (key,)).fetchone()
            if prior and prior["payload"] != payload:
                raise Refused(409, "Request changed; submit anew / La solicitud cambió")
            duplicate = prior or db.execute(
                "SELECT * FROM inquiries WHERE fingerprint=?", (digest,)).fetchone()
            if duplicate:
                return {"request_id": duplicate["id"], "status": "received", "duplicate": True}
            inquiry_id = "MPN-WEB-" + uuid.uuid4().hex[:16].upper()
            db.execute("INSERT INTO inquiries VALUES(?,?,?,?,?,?,?,?)",
                       (inquiry_id, key, digest, payload, "queued",
                        received.isoformat(timespec="seconds"), None, None))
            self.event(db, inquiry_id, "website", "received")
        return {"request_id": inquiry_id, "status": "received", "duplicate": False}

    @staticmethod
    def row(db, inquiry_id):
        row = db.execute("SELECT * FROM inquiries WHERE id=?", (inquiry_id,)).fetchone()
        if row is None:
            raise Refused(404, "Request not found / Solicitud no encontrada")
        return row

    def listing(self, before=None):
        if before is not None and (type(before) is not int or before < 1):
            raise Refused(400, "Invalid page / Página no válida")
        with self.connect() as db:
            query = "SELECT rowid AS cursor,* FROM inquiries"
            params = ()
            if before is not None:
                query += " WHERE rowid < ?"
                params = (before,)
            rows = db.execute(query + " ORDER BY rowid DESC LIMIT 101", params).fetchall()
        next_cursor = rows[99]["cursor"] if len(rows) > 100 else None
        return {"live": self.live, "next_cursor": next_cursor, "items": [
            {"id": r["id"], "received_at": r["received_at"], "status": r["status"],
             "customer": json.loads(r["payload"]),
             "record": json.loads(r["record"]) if r["record"] else None,
             "draft_revision": draft_revision(r["record"]),
             "reviewed_language": r["reviewed_language"]} for r in rows[:100]]}

    def draft(self, inquiry_id, actor, *, regenerate=False):
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self.row(db, inquiry_id)
            allowed = ("draft_ready",) if regenerate else ("queued", "failed", "blocked")
            if row["status"] not in allowed:
                raise Refused(409, "Draft already exists or is processing / Borrador existente o en proceso")
            payload = json.loads(row["payload"])
            db.execute("UPDATE inquiries SET status='drafting' WHERE id=?", (inquiry_id,))
            self.event(db, inquiry_id, actor, "draft_requested")
        try:
            # No API cost or inquiry egress occurs until the operator requests this.
            record = self.builder(payload["message"] + "\nContact: " + payload["contact"],
                                  "web_form", real=False, pricing=triage.load_pricing(), now=now())
            record["inquiry_id"] = inquiry_id
            blocked = any(f["level"] == "FAIL" for f in record["validation"])
            state = "blocked" if blocked else "draft_ready"
            with self.lock, self.connect() as db:
                db.execute("UPDATE inquiries SET status=?,record=? WHERE id=?",
                           (state, json.dumps(record, ensure_ascii=False), inquiry_id))
                self.event(db, inquiry_id, actor, state)
        except Exception:
            with self.lock, self.connect() as db:
                db.execute("UPDATE inquiries SET status='failed' WHERE id=?", (inquiry_id,))
                self.event(db, inquiry_id, actor, "draft_failed")
            raise Refused(503, "Draft failed; request retained / Falló el borrador; solicitud guardada") from None
        return {"status": state}

    def review(self, inquiry_id, actor, action, data):
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self.row(db, inquiry_id)
            record = json.loads(row["record"]) if row["record"] else None
            # Compare the displayed snapshot inside the same write transaction.
            # Policy versions alone do not identify the text a human reviewed.
            expected = data.get("draft_revision")
            current = draft_revision(row["record"])
            if (not current or not isinstance(expected, str) or not expected.isascii()
                    or not hmac.compare_digest(expected, current)):
                raise Refused(409, "Draft changed; refresh and review / El borrador cambió; actualice y revise")
            if action == "approve":
                if row["status"] != "draft_ready" or not record:
                    raise Refused(409, "A safe draft is required / Se requiere un borrador válido")
                pricing = triage.load_pricing()
                if (record["price_list_version"] != pricing["price_list_version"]
                        or record["prompt_version"] != triage.PROMPT_VERSION):
                    raise Refused(409, "Draft version changed; manual review required / Versión desactualizada")
                checks = triage.validators.run_all(
                    record, record["draft_en"], record["draft_es"], pricing, policy_verified=False)
                if triage.validators.blocking(checks):
                    raise Refused(409, "Safety checks failed / Fallaron las validaciones")
                if data.get("language") not in ("en", "es"):
                    raise Refused(400, "Choose the reply language / Elija el idioma")
                real = data.get("real_customer", False)
                if type(real) is not bool or (real and not self.live):
                    raise Refused(400, "Demo mode cannot attest real activity / La demo no registra actividad real")
                record["real_customer"] = real
                triage.apply_approval(record, actor, now())
                state = "approved"
                db.execute("UPDATE inquiries SET reviewed_language=? WHERE id=?",
                           (data["language"], inquiry_id))
            elif action == "reject":
                if row["status"] not in ("draft_ready", "blocked", "approved") or not record:
                    raise Refused(409, "No draft to reject / No hay borrador para rechazar")
                record["outcome"] = "rejected_by_operator"
                state = "rejected"
            elif action == "sent":
                if row["status"] != "approved" or data.get("sent_manually") is not True:
                    raise Refused(409, "Approve first and confirm the manual send / Apruebe y confirme el envío manual")
                record["sent_at"] = now().isoformat(timespec="seconds")
                record["outcome"] = "approved_and_sent"
                state = "sent"
            else:
                raise Refused(404, "Unknown action / Acción desconocida")
            db.execute("UPDATE inquiries SET status=?,record=? WHERE id=?",
                       (state, json.dumps(record, ensure_ascii=False), inquiry_id))
            self.event(db, inquiry_id, actor, action)
        return {"status": state}

    def export(self):
        """Replace this queue's metadata snapshots, never append to the CLI log."""
        evidence = self.data_dir / "evidence"
        evidence.mkdir(exist_ok=True)
        with self.export_lock, self.connect() as db:
            rows = db.execute("SELECT record FROM inquiries WHERE record IS NOT NULL ORDER BY received_at,id").fetchall()
            records = [json.loads(r["record"]) for r in rows]
            for real in (False, True):
                dest = evidence / ("production-log.jsonl" if real else "synthetic-log.jsonl")
                selected = [r for r in records if r["real_customer"] is real]
                if not selected and not dest.exists():
                    continue
                tmp = dest.with_suffix(".tmp")
                with tmp.open("w", encoding="utf-8") as f:
                    for record in selected:
                        safe = {k: v for k, v in record.items() if k not in ("draft_en", "draft_es")}
                        f.write(json.dumps(safe, ensure_ascii=False) + "\n")
                os.replace(tmp, dest)
        return evidence


class Server(ThreadingHTTPServer):
    daemon_threads = False
    def __init__(self, address, app):
        self.app = app
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(40)

    def log_message(self, *args):
        pass  # Access logs must not retain tokens, contacts, or inquiry bodies.

    def reply(self, status, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        for name, value in {
            "Content-Type": ctype + ("; charset=utf-8" if not ctype.startswith("image/") else ""),
            "Content-Length": str(len(data)), "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        }.items():
            self.send_header(name, value)
        if status == 429:
            self.send_header("Retry-After", "300")
        self.end_headers()
        self.wfile.write(data)

    def check_host(self):
        if self.headers.get("Host", "").lower() != self.server.app.host:
            raise Refused(403, "Host not allowed / Host no permitido")
        self.rate_address = self.server.app.client_ip(
            self.client_address[0], self.headers.get_all("X-MPN-Client-IP", []))

    def authenticate(self):
        value = self.headers.get("Authorization", "")
        expected = "Bearer " + self.server.app.token
        if not value.isascii() or not hmac.compare_digest(value, expected):
            raise Refused(401, "Operator sign-in required / Se requiere acceso del operador")

    def do_GET(self):
        try:
            self.check_host()
            if self.path in ("/", "/operator"):
                return self.reply(200, (HERE / "index.html").read_bytes(), "text/html")
            if self.path in ASSETS:
                path, ctype = ASSETS[self.path]
                return self.reply(200, path.read_bytes(), ctype)
            if self.path == "/api/inquiries" or self.path.startswith("/api/inquiries?"):
                self.authenticate()
                match = re.fullmatch(r"/api/inquiries(?:\?before=([1-9][0-9]{0,15}))?", self.path)
                if not match:
                    raise Refused(400, "Invalid page / Página no válida")
                before = int(match[1]) if match[1] else None
                return self.reply(200, self.server.app.listing(before))
            if self.path == "/health":
                return self.reply(200, {"status": "ok", "mode": "live-enabled" if self.server.app.live else "demo"})
            if self.path == "/api/readiness":
                self.authenticate()
                self.server.app.throttle(self.rate_address, operator=True)
                return self.reply(200, self.server.app.readiness())
            raise Refused(404, "Not found / No encontrado")
        except Refused as e:
            self.reply(e.status, {"error": e.message})
        except (OSError, sqlite3.Error, json.JSONDecodeError):
            self.reply(503, {"error": "Service unavailable / Servicio no disponible"})

    def do_POST(self):
        try:
            self.check_host()
            if self.headers.get("Origin") != self.server.app.origin:
                raise Refused(403, "Origin not allowed / Origen no permitido")
            operator = self.path != "/api/inquiry"
            if operator:
                self.authenticate()
            self.server.app.throttle(self.rate_address, operator=operator)
            if self.headers.get("Transfer-Encoding"):
                raise Refused(400, "Unsupported transfer / Transferencia no admitida")
            if self.headers.get_content_type() != "application/json":
                raise Refused(415, "JSON required / Se requiere JSON")
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise Refused(400, "Invalid request size / Tamaño no válido") from None
            if not 0 < size <= MAX_BODY:
                raise Refused(413, "Request too large or empty / Solicitud demasiado grande o vacía")
            try:
                data = json.loads(self.rfile.read(size))
            except (ValueError, UnicodeError, RecursionError):
                raise Refused(400, "Invalid request / Solicitud no válida") from None
            if not isinstance(data, dict):
                raise Refused(400, "Expected an object / Se requiere un objeto")
            if not operator:
                return self.reply(201, self.server.app.submit(data))
            actor = text_field(data, "reviewer", 100)
            if self.path == "/api/export":
                self.server.app.export()
                return self.reply(200, {"status": "exported"})
            inquiry_id = text_field(data, "id", 64)
            if self.path in ("/api/draft", "/api/redraft"):
                result = self.server.app.draft(inquiry_id, actor, regenerate=self.path == "/api/redraft")
            elif self.path in ("/api/approve", "/api/sent", "/api/reject"):
                result = self.server.app.review(inquiry_id, actor, self.path[5:], data)
            else:
                raise Refused(404, "Not found / No encontrado")
            self.reply(200, result)
        except Refused as e:
            self.reply(e.status, {"error": e.message})
        except (OSError, sqlite3.Error, json.JSONDecodeError):
            self.reply(503, {"error": "Not completed; retry safely / No se completó; puede reintentar"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8226)
    parser.add_argument("--data-dir", default=os.environ.get("MPN_INQUIRY_DIR") or str(
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MiamiPapaNoel" / "web-inquiries"))
    parser.add_argument("--live", action="store_true", help="Allow operator attestation of genuine customer use; not a launch claim")
    parser.add_argument("--offline", action="store_true", help="Disable API calls in this process")
    parser.add_argument("--export", action="store_true", help="Export metadata snapshots, then exit")
    args = parser.parse_args()
    if args.offline:
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("MPN_MODEL", None)
    origin = os.environ.get("MPN_PUBLIC_ORIGIN", "http://127.0.0.1:%d" % args.port)
    try:
        app = App(args.data_dir, os.environ.get("MPN_OPERATOR_TOKEN", ""), origin, live=args.live,
                  trusted_proxy=os.environ.get("MPN_TRUSTED_PROXY_IP"))
        if args.export:
            print("Evidence snapshots: %s" % app.export())
            app.close()
            return
        server = Server(("127.0.0.1", args.port), app)
    except (ValueError, OSError) as exc:
        parser.exit(2, "Startup refused: %s\n" % exc)
    print("Inquiry form: %s\nOperator review: %s/operator" % (origin, origin), flush=True)
    print("Local listener only. No automatic messages, payments, or bookings.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        app.close()


if __name__ == "__main__":
    main()
